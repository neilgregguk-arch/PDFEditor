namespace PdfPrototype;
// Original observations are never rewritten by draft planning.
public sealed record PositionedSource(Glyph[] OriginalGlyphs, float[] RelativePositions,
 string Strategy,string MappingEvidence,PageObjectObservation[] ProtectedObjects)
{
 public PositionedLine[] SourceLines {get;init;}=[];
 public int[] CoexistingWhitespace {get;init;}=[];
 public double SafeRight {get;init;}
 public Box?[] InkOffsets {get;init;}=[];
}
public record PositionedDraft(double[] Origins,float[] RelativePositions,int[] OriginalIndices,
 string[] Kinds,int[] ReplacementOriginalIndices,int[] DeletedOriginalIndices,Box[] InkBounds,string Policy,bool Ambiguous)
{public PositionedLine[] Lines {get;init;}=[];public Box? SafeArea {get;init;}}
public record PositionedLine(int Start,string Text,double Baseline,double[] Origins,float[] RelativePositions,Box[] InkBounds);
public static class PositionLayout
{
 public const int MaxCharacters=512;
 public static bool SurvivingSequence(int[] map,int i,int j){int a=Math.Min(i,j),b=Math.Max(i,j);return map[a]>=0&&Enumerable.Range(a,b-a+1).All(k=>map[k]==map[a]+k-a);}
 public static bool SourceSequence(Region r,int[] map,int i,int j)
 {
  if(!SurvivingSequence(map,i,j))return false;if(r.Paragraph==null)return true;
  int a=map[Math.Min(i,j)],b=map[Math.Max(i,j)];return r.Positioned!.SourceLines.Any(l=>a>=l.Start&&b<l.Start+l.Text.Length);
 }
 public static Layout SourceLayout(Region r)
 {
  var p=r.Positioned!;var lines=p.SourceLines;var gs=p.OriginalGlyphs;var boxes=lines.Select(l=>new Box(r.X,r.Top+l.Baseline-r.Baseline,Math.Max(l.Origins[^1]+r.Advances[l.Text[^1]-32],l.InkBounds.Max(b=>b.Right))-r.X,r.LineHeight)).ToArray();
  var data=new PositionedDraft(gs.Select(g=>g.OriginX).ToArray(),lines[0].RelativePositions,Enumerable.Range(0,gs.Length).ToArray(),Enumerable.Repeat("Surviving",gs.Length).ToArray(),Enumerable.Repeat(-1,gs.Length).ToArray(),[],gs.Select(g=>g.Bounds).ToArray(),"ValidatedSourceRows",false){Lines=lines,SafeArea=r.Paragraph!.Envelope};
  return new(lines.Select(l=>l.Text).ToArray(),lines[^1].Baseline-r.Baseline+r.LineHeight,true,"Validated editor paragraph source geometry.",boxes){Positioned=data};
 }
 static Region FlattenSource(Region r)
 {
  var p=r.Positioned!;var gs=new Glyph[p.OriginalGlyphs.Length];double x=r.X;
  for(int i=0;i<gs.Length;i++)
  {
   var g=p.OriginalGlyphs[i];if(i>0)x+=g.Baseline==p.OriginalGlyphs[i-1].Baseline?g.OriginX-p.OriginalGlyphs[i-1].OriginX:r.Advances[r.OriginalText[i-1]-32];
   gs[i]=g with{OriginX=x,Baseline=r.Baseline,Bounds=g.Bounds with{X=x+g.Bounds.X-g.OriginX,Y=r.Baseline+g.Bounds.Y-g.Baseline}};
  }
  return r with{Positioned=p with{OriginalGlyphs=gs,RelativePositions=gs.Skip(1).Select(g=>(float)(g.OriginX-r.X)).ToArray()}};
 }
 static Layout PlanSingle(Region r,string text)
 {
  Layout Fail(string code,string message,CharacterCompatibility[]? issues=null)=>new([text],r.LineHeight,false,message+" Your complete draft has been kept.",[]){ReasonCodes=[code],GlyphIssues=issues??[]};
  var issues=text.Distinct().Where(c=>c<32||c>126||r.Advances[c-32]<0).Select(c=>c<32||c>126?new CharacterCompatibility(c,"UnsupportedCharacter","POSITION_ASCII_ONLY",null,-1):r.Characters[c-32]).ToArray();
  if(issues.Length>0)return Fail("POSITION_CHARACTER_MAPPING_UNSUPPORTED","The original font cannot safely display this character or line break.",issues);
  var p=r.Positioned!;var old=r.OriginalText;int[] map=Enumerable.Repeat(-1,text.Length).ToArray();bool ambiguous=false;
  bool fixedOrigins=text.Length==old.Length&&Enumerable.Range(0,text.Length).All(i=>text[i]==old[i]||r.Advances[text[i]-32]<=r.Advances[old[i]-32]+.001);
  if(!fixedOrigins&&(text.Length>MaxCharacters||old.Length>MaxCharacters))return Fail("POSITION_LENGTH_LIMIT","Spacing recalculation supports up to 512 characters per line; the existing fixed-origin substitution path is retained.");
  if(fixedOrigins){for(int i=0;i<map.Length;i++)if(text[i]==old[i])map[i]=i;}
  else
  {
   // Bounded LCS; equal symbols match immediately, ties skip an original symbol.
   // This deterministic alignment claims no knowledge of author intent.
   var dp=new ushort[old.Length+1,text.Length+1];
   for(int i=old.Length-1;i>=0;i--)for(int j=text.Length-1;j>=0;j--)dp[i,j]=(ushort)(old[i]==text[j]?1+dp[i+1,j+1]:Math.Max(dp[i+1,j],dp[i,j+1]));
   int a=0,b=0;while(a<old.Length&&b<text.Length){if(old[a]==text[b]){if(dp[a+1,b]==dp[a,b]||dp[a,b+1]==dp[a,b])ambiguous=true;map[b++]=a++;}else{if(dp[a+1,b]==dp[a,b+1])ambiguous=true;if(dp[a+1,b]>=dp[a,b+1])a++;else b++;}}
  }
  int[] replacements=Enumerable.Repeat(-1,text.Length).ToArray();
  if(fixedOrigins){for(int i=0;i<text.Length;i++)if(map[i]<0)replacements[i]=i;}
  else
  {
   int oldStart=0,newStart=0;
   foreach(int next in Enumerable.Range(0,text.Length).Where(i=>map[i]>=0).Append(text.Length))
   {
    int oldEnd=next==text.Length?old.Length:map[next];int count=Math.Min(oldEnd-oldStart,next-newStart);
    for(int i=0;i<count;i++)replacements[newStart+i]=oldStart+i;
    oldStart=oldEnd+1;newStart=next+1;
   }
  }
  double[] xs=new double[text.Length];var ink=new Box[text.Length];var kinds=new string[text.Length];
  for(int i=0;i<text.Length;i++)
  {
   if(fixedOrigins)xs[i]=p.OriginalGlyphs[i].OriginX;
   else if(i==0)xs[i]=r.X;
   else
   {
    double adjustment=map[i-1]>=0&&map[i]==map[i-1]+1?p.OriginalGlyphs[map[i]].OriginX-p.OriginalGlyphs[map[i-1]].OriginX-r.Advances[text[i-1]-32]:0;
    xs[i]=xs[i-1]+r.Advances[text[i-1]-32]+adjustment;
   }
   kinds[i]=map[i]>=0?"Surviving":replacements[i]>=0?"Replaced":"Inserted";
   if(text[i]==' '){ink[i]=new(xs[i],r.Baseline,0,0);continue;}
   Box? offset=map[i]>=0?p.OriginalGlyphs[map[i]].Bounds with{X=p.OriginalGlyphs[map[i]].Bounds.X-p.OriginalGlyphs[map[i]].OriginX,Y=p.OriginalGlyphs[map[i]].Bounds.Y-r.Baseline}:p.InkOffsets.ElementAtOrDefault(text[i]-32);
   if(offset==null)return Fail("POSITION_INK_UNAVAILABLE","This glyph's original-font ink could not be measured.");
   ink[i]=offset with{X=xs[i]+offset.X,Y=r.Baseline+offset.Y};
  }
  double right=p.SafeRight>0?p.SafeRight:r.X+r.Width;
  double end=text.Length==0?r.X:xs[^1]+r.Advances[text[^1]-32];
  if(end>right+.001||ink.Any(b=>b.X<r.X-2||b.Right>right+.001||b.Y<r.Top-2||b.Bottom>r.Top+r.LineHeight+2))return Fail("POSITION_HORIZONTAL_OVERFLOW","The line reaches the safe horizontal boundary. Shorten it; positioned text cannot wrap.");
  for(int i=0;i<ink.Length;i++)for(int j=i+1;j<ink.Length;j++)
   if((!fixedOrigins||map[i]<0||map[j]<0)&&text[i]!=' '&&text[j]!=' '&&ink[i].Intersects(ink[j])&&!(SourceSequence(r,map,i,j)))return Fail("POSITION_NEW_GLYPH_OVERLAP","The proposed spacing overlaps letters at an edited join.");
  var data=new PositionedDraft(xs,xs.Skip(1).Select(x=>(float)(x-r.X)).ToArray(),map,kinds,replacements,Enumerable.Range(0,old.Length).Where(i=>!map.Contains(i)&&!replacements.Contains(i)).ToArray(),ink,fixedOrigins?"FixedOriginsEqualOrNarrowerSubstitution":"SurvivingAdjacentPairsAndVerifiedAdvances",ambiguous);
  // Logical line envelope includes spaces and saved ink, without claiming unused page space.
  double left=Math.Min(r.X,ink.Length==0?r.X:ink.Min(b=>b.X));double extent=Math.Max(end,ink.Length==0?r.X:ink.Max(b=>b.Right));
  var box=new Box(left,r.Top,Math.Max(0,extent-left),r.LineHeight);
  bool collision=p.ProtectedObjects.Where(o=>!p.CoexistingWhitespace.Contains(o.Index)).Any(o=>box.Intersects(o.Bounds,.5));
  return new([text],r.LineHeight,!collision,collision?"This line reaches protected content. All drafts have been kept.":"Single-line positions proposed; checking the complete PDF candidate.",[box]){Positioned=data,ReasonCodes=collision?["POSITION_PROTECTED_CONTENT"]:[]};
 }
 public const int MaxLines=8;
 public static Layout Plan(Region r,string text)
 {
  if(r.Paragraph!=null&&text==r.OriginalText)return SourceLayout(r);
  if(r.Paragraph!=null)r=FlattenSource(r);
  var initial=PlanSingle(r,text);
  Layout Attach(Layout l)=>l.Positioned==null?l:l with{Positioned=l.Positioned with{Lines=[new(0,text,r.Baseline,l.Positioned.Origins,l.Positioned.RelativePositions,l.Positioned.InkBounds)]}};
  if(initial.Safe)return Attach(initial);
  if(!initial.ReasonCodes.Any(c=>c=="POSITION_HORIZONTAL_OVERFLOW"||c=="POSITION_PROTECTED_CONTENT"))return Attach(initial);
  var source=r.Positioned!;var obstacles=source.ProtectedObjects.Where(o=>!source.CoexistingWhitespace.Contains(o.Index)).ToArray();
  double right=source.SafeRight;
  foreach(var o in obstacles.Where(o=>o.Bounds.X>r.ObservedBounds!.Right&&o.Bounds.Y<r.Top+r.LineHeight&&o.Bounds.Bottom>r.Top))right=Math.Min(right,o.Bounds.X-.5);
  double bottom=r.SafeBottom;
  foreach(var o in obstacles.Where(o=>o.Bounds.X<right&&o.Bounds.Right>r.X&&o.Bounds.Y>r.Baseline))bottom=Math.Min(bottom,o.Bounds.Y-3);
  double inkHeight=source.InkOffsets.Where(b=>b!=null).Select(b=>b!.Bottom).DefaultIfEmpty(0).Max()-source.InkOffsets.Where(b=>b!=null).Select(b=>b!.Y).DefaultIfEmpty(-r.FontSize).Min();
  double leading=Math.Max(2*r.FontSize,inkHeight+3);bottom=Math.Min(bottom,r.Top+(MaxLines-1)*leading+r.LineHeight);
  var safe=new Box(r.X,r.Top,Math.Max(0,right-r.X),Math.Max(0,bottom-r.Top));
  // Pure clone used only to obtain source-bound alignment and measured glyph ink.
  // It grants no ownership; final plans below are checked against the real area/objects.
  var raw=PlanSingle(r with{Positioned=source with{SafeRight=1e9,ProtectedObjects=[]}},text);
  if(raw.Positioned==null||!raw.Safe)return raw;
  var original=raw.Positioned;var lines=new List<PositionedLine>();var xs=new double[text.Length];var bounds=new Box[text.Length];int start=0;
  while(start<text.Length)
  {
   int row=lines.Count;if(row>=MaxLines)return new([text],0,false,"The wrapped draft exceeds this version's bounded line capacity. Your complete draft is retained.",[]){ReasonCodes=["POSITION_WRAP_LINE_LIMIT"]};
   double baseline=r.Baseline+row*leading,x=r.X;int cursor=start,lastSpace=-1;
   var localX=new List<double>();var localInk=new List<Box>();
   while(cursor<text.Length)
   {
    if(cursor>start)x=row==0?original.Origins[cursor]:x+r.Advances[text[cursor-1]-32];
    double offsetX=original.InkBounds[cursor].X-original.Origins[cursor],offsetY=original.InkBounds[cursor].Y-r.Baseline;
    var box=original.InkBounds[cursor] with{X=x+offsetX,Y=baseline+offsetY};
    if(x+r.Advances[text[cursor]-32]>right+.001||box.Right>right+.001)break;
    localX.Add(x);localInk.Add(box);if(text[cursor]==' ')lastSpace=cursor+1;cursor++;
   }
   if(cursor==start)return new([text],0,false,"A glyph cannot fit the conservatively available width. Complete draft retained.",[]){ReasonCodes=["POSITION_WRAP_GLYPH_WIDTH"]};
   int stop=cursor<text.Length&&lastSpace>start?lastSpace:cursor;int n=stop-start;string part=text[start..stop];var origins=localX.Take(n).ToArray();var ink=localInk.Take(n).ToArray();
   for(int j=0;j<n;j++){xs[start+j]=origins[j];bounds[start+j]=ink[j];}
   lines.Add(new(start,part,baseline,origins,origins.Skip(1).Select(v=>(float)(v-r.X)).ToArray(),ink));start=stop;
  }
  var boxes=lines.Select(l=>new Box(r.X,r.Top+l.Baseline-r.Baseline,Math.Max(l.Origins[^1]+r.Advances[l.Text[^1]-32],l.InkBounds.Max(b=>b.Right))-r.X,r.LineHeight)).ToArray();
  bool vertical=boxes.Any(b=>b.Bottom>bottom+.001)||bounds.Any(b=>b.Bottom>bottom+.001||b.Y<r.Top-2);
  bool collision=boxes.Any(b=>obstacles.Any(o=>b.Intersects(o.Bounds,.5)));
  bool overlaps=false;
  foreach(var line in lines)for(int a=0;a<line.Text.Length;a++)for(int b=a+1;b<line.Text.Length;b++)
   if(line.Text[a]!=' '&&line.Text[b]!=' '&&line.InkBounds[a].Intersects(line.InkBounds[b])&&!(line.Start==0&&SourceSequence(r,original.OriginalIndices,a,b)))overlaps=true;
  var data=original with{Origins=xs,RelativePositions=lines[0].RelativePositions,InkBounds=bounds,Lines=lines.ToArray(),SafeArea=safe,Policy="ControlledSoftWrapFirstLinePairsNewLineFontAdvances"};
  string code=vertical?"POSITION_VERTICAL_OVERFLOW":collision?"POSITION_WRAP_PROTECTED_CONTENT":overlaps?"POSITION_WRAP_INK_OVERLAP":"";
  return new(lines.Select(l=>l.Text).ToArray(),(lines.Count-1)*leading+r.LineHeight,code.Length==0,code.Length==0?"Wrapped draft proposed; checking the complete PDF candidate.":"This wrapped draft reaches protected space or unsafe glyph ink. All text has been kept.",boxes){Positioned=data,ReasonCodes=code.Length==0?[]:[code]};
 }
 public static (double X,double Y,int Row) Caret(Region r,string text,int index,int? affinity=null)
 {
  var p=Plan(r,text).Positioned;if(p==null||p.Lines.Length==0)return(r.X+ParagraphLayout.Width(r,text[..Math.Clamp(index,0,text.Length)]),r.Top,0);
  index=Math.Clamp(index,0,text.Length);int row=affinity is int a&&a>=0&&a<p.Lines.Length&&index>=p.Lines[a].Start&&index<=p.Lines[a].Start+p.Lines[a].Text.Length?a:Math.Max(0,Array.FindLastIndex(p.Lines,l=>l.Start<=index));
  var line=p.Lines[row];int n=index-line.Start;double x=n>=line.Text.Length?(line.Text.Length==0?r.X:line.Origins[^1]+r.Advances[line.Text[^1]-32]):line.Origins[n];return(x,r.Top+line.Baseline-r.Baseline,row);
 }
 public static double CaretX(Region r,string text,int index)=>Caret(r,text,index).X;
 public static (int Index,double X,int Line) Hit(Region r,string text,double x,double y)
 {
  var p=Plan(r,text).Positioned;if(p==null||p.Lines.Length==0)return(0,r.X,0);
  int row=Enumerable.Range(0,p.Lines.Length).MinBy(i=>Math.Abs(y-(r.Top+p.Lines[i].Baseline-r.Baseline+r.LineHeight/2)));
  var line=p.Lines[row];for(int j=0;j<line.Text.Length;j++){double end=j+1<line.Text.Length?line.Origins[j+1]:line.Origins[j]+r.Advances[line.Text[j]-32];if(x<(line.Origins[j]+end)/2)return(line.Start+j,line.Origins[j],row);}return(line.Start+line.Text.Length,line.Text.Length==0?r.X:line.Origins[^1]+r.Advances[line.Text[^1]-32],row);
 }

}
public sealed partial class PdfEngine
{
    const string PositionBinaryHash="bede3932ce96a2e1ed9a7e6cae71aec8914efd2907d37ab44b1b81f9c8a6d04e";
    static int[] ObserveNonPaintingSpaces(IntPtr page)
    {
        var result=new List<int>();var objects=Objects(page);var tp=N.FPDFText_LoadPage(page);
        byte[]? baseline=null;
        try
        {
            for(int i=0;i<objects.Length;i++)
            {
                var o=objects[i];if(N.FPDFPageObj_GetType(o)!=1||N.FPDFTextObj_GetTextRenderMode(o)!=0)continue;
                string text=N.Text(o,tp);if(text.Any(c=>c!=' '))continue;
                N.FPDFPageObj_GetFillColor(o,out var r,out var g,out var b,out var a);
                if(a!=255||N.FPDFPageObj_HasTransparency(o)!=0)continue;
                // Coexistence evidence, never ownership: separately retained text/semantics.
                // PDFium may omit standalone space extraction. Empty extraction is not
                // proof of whitespace semantics: require zero extent AND no page paint.
                // Retain this object verbatim in the candidate, never absorb or delete it.
                var bounds=Bounds(o,N.FPDF_GetPageHeight(page));if(bounds.Width!=0||bounds.Height!=0)continue;
                baseline??=Pixels(page,2,out _,out _);
                try
                {
                    N.Check(N.FPDFPageObj_SetFillColor(o,r,g,b,0),"test space paint");
                    if(baseline.SequenceEqual(Pixels(page,2,out _,out _)))result.Add(i);
                }
                finally{N.Check(N.FPDFPageObj_SetFillColor(o,r,g,b,a),"restore space paint");}
            }
        }
        finally{N.FPDFText_ClosePage(tp);}
        return result.ToArray();
    }
    static Box? MeasureGlyphInk(IntPtr document,IntPtr page,IntPtr font,char c,double size)
    {
        var o=N.FPDFPageObj_CreateTextObj(document,font,(float)size);if(o==IntPtr.Zero)return null;bool inserted=false;
        try
        {
            if(N.FPDFText_SetText(o,System.Text.Encoding.Unicode.GetBytes(c+"\0"))==0)return null;
            N.FPDFPageObj_Transform(o,1,0,0,1,20,36);N.FPDFPage_InsertObject(page,o);inserted=true;
            var tp=N.FPDFText_LoadPage(page);
            try{for(int i=0;i<N.FPDFText_CountChars(tp);i++)if(N.FPDFText_GetTextObject(tp,i)==o&&N.FPDFText_GetUnicode(tp,i)==c&&N.FPDFText_GetCharBox(tp,i,out var l,out var right,out var b,out var top)!=0)return new(l-20,36-top,right-l,top-b);}
            finally{N.FPDFText_ClosePage(tp);}return null;
        }
        finally{if(inserted)N.FPDFPage_RemoveObject(page,o);N.FPDFPageObj_Destroy(o);}
    }
    static bool TryPositioned(IntPtr document,IntPtr page,IntPtr o,Region r,N.Matrix m,List<string> reasons)
    {
        if(!reasons.Contains("NON_NATURAL_GLYPH_SPACING")&&!reasons.Contains("INITIAL_OBJECT_RECONSTRUCTION_DIFFERS"))return false;
        if(reasons.Any(x=>x!="NON_NATURAL_GLYPH_SPACING"&&x!="INITIAL_OBJECT_RECONSTRUCTION_DIFFERS"))return false;
        var gs=r.Glyphs;
        if(gs.Length<2||gs.Length!=r.OriginalText.Length||Math.Abs(gs[0].OriginX-r.X)>.01||gs.Any(g=>Math.Abs(g.Baseline-r.Baseline)>.01))return false;
        if(gs.Zip(gs.Skip(1)).Any(p=>p.Second.OriginX<=p.First.OriginX))return false;
        // Additional position-path guard: PDF width rounding can make readers
        // disagree despite PDFium's own exact-origin roundtrip (ReportLab case).
        var font=N.FPDFTextObj_GetFont(o);
        foreach(char c in r.Characters.Where(c=>c.Advance>=0).Select(c=>(char)c.Unicode))
            if(N.FPDFFont_GetGlyphWidth(font,c,(float)r.FontSize,out var width)==0||Math.Abs(width-r.Advances[c-32])>.01)
            {reasons.Add("POSITION_FONT_METRIC_ROUNDING_UNSUPPORTED");return false;}
        if(Wire.Hash(Path.Combine(AppContext.BaseDirectory,"pdfium.dll"))!=PositionBinaryHash)return false;
        float[] positions=gs.Skip(1).Select(g=>(float)(g.OriginX-r.X)).ToArray();
        if(!OriginalReconstructionMatches(document,page,o,r.OriginalText,m,r.R,r.G,r.B,positions))return false;
        var ink=new Box?[95];
        foreach(var c in r.Characters.Where(c=>c.Advance>=0&&c.Unicode!=32))ink[c.Unicode-32]=MeasureGlyphInk(document,page,font,(char)c.Unicode,r.FontSize);
        r.Positioned=new(gs.ToArray(),positions,"SurvivingAdjacentPairsAndVerifiedAdvances",
            "Unicode reverse mapping, original embedded cmap GID, outline, width, roundtrip and exact positioned object bitmap verified; no raw codes guessed.",[]){SafeRight=r.X+r.Width,InkOffsets=ink};
        r.Width=Math.Max(.01,r.ObservedBounds!.Right-r.X);
        reasons.RemoveAll(x=>x=="NON_NATURAL_GLYPH_SPACING"||x=="INITIAL_OBJECT_RECONSTRUCTION_DIFFERS");
        r.Observed=r.Observed.Append("POSITIONED_ORIGINAL_BITMAP_IDENTICAL_144DPI").ToArray();
        return true;
    }
}
