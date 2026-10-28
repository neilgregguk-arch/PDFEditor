from pathlib import Path
p=Path('phase4c1/Core/PositionLayout.cs');s=p.read_text(encoding='utf-8');tail=s[s.index('public sealed partial class PdfEngine'):];header='''namespace PdfPrototype;
// Original observations are never rewritten by draft planning.
public sealed record PositionedSource(Glyph[] OriginalGlyphs, float[] RelativePositions,
 string Strategy,string MappingEvidence,PageObjectObservation[] ProtectedObjects)
{
 public int[] CoexistingWhitespace {get;init;}=[];
 public double SafeRight {get;init;}
 public Box?[] InkOffsets {get;init;}=[];
}
public record PositionedDraft(double[] Origins,float[] RelativePositions,int[] OriginalIndices,
 string[] Kinds,int[] DeletedOriginalIndices,Box[] InkBounds,string Policy,bool Ambiguous);
public static class PositionLayout
{
 public const int MaxCharacters=512;
 public static Layout Plan(Region r,string text)
 {
  Layout Fail(string code,string message,CharacterCompatibility[]? issues=null)=>new([text],r.LineHeight,false,message+" Your complete draft has been kept.",[]){ReasonCodes=[code],GlyphIssues=issues??[]};
  if(text.Length>MaxCharacters||r.OriginalText.Length>MaxCharacters)return Fail("POSITION_LENGTH_LIMIT","This single-line prototype supports up to 512 characters.");
  var issues=text.Distinct().Where(c=>c<32||c>126||r.Advances[c-32]<0).Select(c=>c<32||c>126?new CharacterCompatibility(c,"UnsupportedCharacter","POSITION_ASCII_ONLY",null,-1):r.Characters[c-32]).ToArray();
  if(issues.Length>0)return Fail("POSITION_CHARACTER_MAPPING_UNSUPPORTED","The original font cannot safely display this character or line break.",issues);
  var p=r.Positioned!;var old=r.OriginalText;int[] map=Enumerable.Repeat(-1,text.Length).ToArray();bool ambiguous=false;
  bool fixedOrigins=text.Length==old.Length&&Enumerable.Range(0,text.Length).All(i=>text[i]==old[i]||r.Advances[text[i]-32]<=r.Advances[old[i]-32]+.001);
  if(fixedOrigins){for(int i=0;i<map.Length;i++)if(text[i]==old[i])map[i]=i;}
  else
  {
   // Bounded LCS; equal symbols match immediately, ties skip an original symbol.
   // This deterministic alignment claims no knowledge of author intent.
   var dp=new ushort[old.Length+1,text.Length+1];
   for(int i=old.Length-1;i>=0;i--)for(int j=text.Length-1;j>=0;j--)dp[i,j]=(ushort)(old[i]==text[j]?1+dp[i+1,j+1]:Math.Max(dp[i+1,j],dp[i,j+1]));
   int a=0,b=0;while(a<old.Length&&b<text.Length){if(old[a]==text[b]){map[b++]=a++;}else{if(dp[a+1,b]==dp[a,b+1])ambiguous=true;if(dp[a+1,b]>=dp[a,b+1])a++;else b++;}}
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
   kinds[i]=map[i]>=0?"Surviving":fixedOrigins?"Replaced":"InsertedOrReplaced";
   if(text[i]==' '){ink[i]=new(xs[i],r.Baseline,0,0);continue;}
   Box? offset=map[i]>=0?p.OriginalGlyphs[map[i]].Bounds with{X=p.OriginalGlyphs[map[i]].Bounds.X-p.OriginalGlyphs[map[i]].OriginX,Y=p.OriginalGlyphs[map[i]].Bounds.Y-r.Baseline}:p.InkOffsets.ElementAtOrDefault(text[i]-32);
   if(offset==null)return Fail("POSITION_INK_UNAVAILABLE","This glyph's original-font ink could not be measured.");
   ink[i]=offset with{X=xs[i]+offset.X,Y=r.Baseline+offset.Y};
  }
  double right=p.SafeRight>0?p.SafeRight:r.X+r.Width;
  double end=text.Length==0?r.X:xs[^1]+r.Advances[text[^1]-32];
  if(end>right+.001||ink.Any(b=>b.X<r.X-2||b.Right>right+.001||b.Y<r.Top-2||b.Bottom>r.Top+r.LineHeight+2))return Fail("POSITION_HORIZONTAL_OVERFLOW","The line reaches the safe horizontal boundary. Shorten it; positioned text cannot wrap.");
  for(int i=0;i<ink.Length;i++)for(int j=i+1;j<ink.Length;j++)
   if(text[i]!=' '&&text[j]!=' '&&ink[i].Intersects(ink[j])&&!(map[i]>=0&&map[j]==map[i]+j-i))return Fail("POSITION_NEW_GLYPH_OVERLAP","The proposed spacing overlaps letters at an edited join.");
  var data=new PositionedDraft(xs,xs.Skip(1).Select(x=>(float)(x-r.X)).ToArray(),map,kinds,Enumerable.Range(0,old.Length).Where(i=>!map.Contains(i)).ToArray(),ink,fixedOrigins?"FixedOriginsEqualOrNarrowerSubstitution":"SurvivingAdjacentPairsAndVerifiedAdvances",ambiguous);
  // Logical line envelope includes spaces and saved ink, without claiming unused page space.
  double left=Math.Min(r.X,ink.Length==0?r.X:ink.Min(b=>b.X));double extent=Math.Max(end,ink.Length==0?r.X:ink.Max(b=>b.Right));
  var box=new Box(left,r.Top,Math.Max(0,extent-left),r.LineHeight);
  bool collision=p.ProtectedObjects.Where(o=>!p.CoexistingWhitespace.Contains(o.Index)).Any(o=>box.Intersects(o.Bounds,.5));
  return new([text],r.LineHeight,!collision,collision?"This line reaches protected content. All drafts have been kept.":"Single-line positions proposed; checking the complete PDF candidate.",[box]){Positioned=data,ReasonCodes=collision?["POSITION_PROTECTED_CONTENT"]:[]};
 }
 public static double CaretX(Region r,string text,int index)
 {
  var p=Plan(r,text).Positioned;if(p==null)return r.X+ParagraphLayout.Width(r,text[..Math.Clamp(index,0,text.Length)]);
  if(p.Origins.Length==0)return r.X;return index>=p.Origins.Length?p.Origins[^1]+r.Advances[text[^1]-32]:p.Origins[Math.Max(0,index)];
 }
}
''';s=header+tail
s=s.replace('r.Positioned=new(gs.ToArray(),positions,"FixedOriginsEqualOrNarrowerSubstitution",','var ink=new Box?[95];\n        foreach(var c in r.Characters.Where(c=>c.Advance>=0&&c.Unicode!=32))ink[c.Unicode-32]=MeasureGlyphInk(document,page,font,(char)c.Unicode,r.FontSize);\n        r.Positioned=new(gs.ToArray(),positions,"SurvivingAdjacentPairsAndVerifiedAdvances",')
s=s.replace('[]);\n        r.Width=', '[]){SafeRight=r.X+r.Width,InkOffsets=ink};\n        r.Width=')
# add native measured ink before TryPositioned
where='    static bool TryPositioned('
method='''    static Box? MeasureGlyphInk(IntPtr document,IntPtr page,IntPtr font,char c,double size)
    {
        var o=N.FPDFPageObj_CreateTextObj(document,font,(float)size);if(o==IntPtr.Zero)return null;bool inserted=false;
        try
        {
            if(N.FPDFText_SetText(o,System.Text.Encoding.Unicode.GetBytes(c+"\\0"))==0)return null;
            N.FPDFPageObj_Transform(o,1,0,0,1,20,36);N.FPDFPage_InsertObject(page,o);inserted=true;
            var tp=N.FPDFText_LoadPage(page);
            try{for(int i=0;i<N.FPDFText_CountChars(tp);i++)if(N.FPDFText_GetTextObject(tp,i)==o&&N.FPDFText_GetUnicode(tp,i)==c&&N.FPDFText_GetCharBox(tp,i,out var l,out var right,out var b,out var top)!=0)return new(l-20,36-top,right-l,top-b);}
            finally{N.FPDFText_ClosePage(tp);}return null;
        }
        finally{if(inserted)N.FPDFPage_RemoveObject(page,o);N.FPDFPageObj_Destroy(o);}
    }
'''
s=s.replace(where,method+where);p.write_text(s,encoding='utf-8',newline='\n')
p=Path('phase4c1/Core/Models.cs');s=p.read_text(encoding='utf-8').replace('public string[] ReasonCodes {get;init;}=[];public CharacterCompatibility[] GlyphIssues','public PositionedDraft? Positioned {get;init;}\n public string[] ReasonCodes {get;init;}=[];public CharacterCompatibility[] GlyphIssues');
s=s.replace('var p=Plan(r,text); var lines=', '''if(r.Positioned!=null){int n=0;for(int i=0;i<text.Length;i++){double a=PositionLayout.CaretX(r,text,i),b=PositionLayout.CaretX(r,text,i+1);if(x<(a+b)/2)break;n++;}return(n,PositionLayout.CaretX(r,text,n),0);}
        var p=Plan(r,text); var lines=''');p.write_text(s,encoding='utf-8',newline='\n')
p=Path('phase4c1/Core/DocumentSession.cs');s=p.read_text(encoding='utf-8').replace('positions=r.Positioned?.RelativePositions','positions=r.Positioned?.RelativePositions,safeRight=r.Positioned?.SafeRight');p.write_text(s,encoding='utf-8',newline='\n')
