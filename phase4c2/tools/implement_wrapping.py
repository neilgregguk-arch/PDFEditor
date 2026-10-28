from pathlib import Path
r=Path('phase4c2');p=r/'Core/PositionLayout.cs';s=p.read_text(encoding='utf-8').replace('string Policy,bool Ambiguous);','''string Policy,bool Ambiguous)
{public PositionedLine[] Lines {get;init;}=[];public Box? SafeArea {get;init;}}
public record PositionedLine(int Start,string Text,double Baseline,double[] Origins,float[] RelativePositions,Box[] InkBounds);''').replace(' public static Layout Plan(Region r,string text)',' static Layout PlanSingle(Region r,string text)',1)
i=s.index(' public static double CaretX(');end=s.index('\n}\npublic sealed partial class PdfEngine',i)
s=s[:i]+''' public const int MaxLines=8;
 public static Layout Plan(Region r,string text)
 {
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
   if(line.Text[a]!=' '&&line.Text[b]!=' '&&line.InkBounds[a].Intersects(line.InkBounds[b])&&!(line.Start==0&&SurvivingSequence(original.OriginalIndices,a,b)))overlaps=true;
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
'''+s[end:];p.write_text(s,encoding='utf-8',newline='\n')
p=r/'Core/Models.cs';s=p.read_text(encoding='utf-8');a=s.index('if(r.Positioned!=null){var model=');b=s.index('\n\n        var p=Plan(r,text);',a) if '\n\n        var p=Plan(r,text);' in s[a:] else s.index('\n        var p=Plan(r,text);',a);s=s[:a]+'if(r.Positioned!=null)return PositionLayout.Hit(r,text,x,y);'+s[b:];p.write_text(s,encoding='utf-8',newline='\n')
p=r/'Core/DocumentTransaction.cs';s=p.read_text(encoding='utf-8').replace('t.Layout.Positioned!.RelativePositions,(nuint)t.Layout.Positioned.RelativePositions.Length','t.Layout.Positioned!.Lines[i].RelativePositions,(nuint)t.Layout.Positioned.Lines[i].RelativePositions.Length').replace('h-r.Baseline-i*r.LineHeight','h-(t.Layout.Positioned?.Lines[i].Baseline??(r.Baseline+i*r.LineHeight))')
s=s.replace('t.Layout.Positioned?.RelativePositions','t.Layout.Positioned?.Lines[lines[i].row].RelativePositions').replace('t.Layout.Positioned?.Origins[j]','t.Layout.Positioned?.Lines[lines[i].row].Origins[j]').replace('Math.Abs(g.Y-(r.Baseline+lines[i].row*r.LineHeight))>.15','Math.Abs(g.Y-(t.Layout.Positioned?.Lines[lines[i].row].Baseline??(r.Baseline+lines[i].row*r.LineHeight)))>(r.Positioned!=null?.01:.15)').replace('var predicted=plan.InkBounds[j];','var predicted=plan.Lines[lines[i].row].InkBounds[j];').replace('PositionLayout.SurvivingSequence(plan.OriginalIndices,j,k)','lines[i].row==0&&PositionLayout.SurvivingSequence(plan.OriginalIndices,j,k)');p.write_text(s,encoding='utf-8',newline='\n')
