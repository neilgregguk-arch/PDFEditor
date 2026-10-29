using System.Windows;
using System.Windows.Media;
using System.Windows.Threading;
namespace PdfPrototype;
// RichTextBox owns text, logical selection and history. This layer paints the
// original-font glyphs, selection and caret at the shared proposed PDF positions.
sealed class PositionedInk : FrameworkElement
{
 Region? region;string text="",fontFile="";GlyphTypeface? face;PositionedDraft? proposal;
 int start,end,caret;int? affinity;bool showCaret,blink=true;
 readonly DispatcherTimer timer=new(){Interval=TimeSpan.FromMilliseconds(530)};
 public PositionedInk(){IsHitTestVisible=false;timer.Tick+=(s,e)=>{blink=!blink;InvalidateVisual();};Unloaded+=(s,e)=>timer.Stop();}
 public double CaretOriginPt=>Point(caret,affinity).X;
 public double CaretTopPt=>Point(caret,affinity).Y;
 public int CaretRow=>Point(caret,affinity).Row;
 (double X,double Y,int Row) Point(int index,int? preferred=null)
 {
  if(region==null||proposal==null||proposal.Lines.Length==0)return(region?.X??0,region?.Top??0,0);index=Math.Clamp(index,0,text.Length);
  int row=preferred is int p&&p>=0&&p<proposal.Lines.Length&&index>=proposal.Lines[p].Start&&index<=proposal.Lines[p].Start+proposal.Lines[p].Text.Length?p:Math.Max(0,Array.FindLastIndex(proposal.Lines,l=>l.Start<=index));var line=proposal.Lines[row];int n=index-line.Start;
  return(n>=line.Text.Length?(line.Text.Length==0?region.X:line.Origins[^1]+region.Advances[line.Text[^1]-32]):line.Origins[n],region.Top+line.Baseline-region.Baseline,row);
 }
 public void Set(Region r,string draft)
 {
  region=r;text=draft;proposal=PositionLayout.Plan(r,draft).Positioned;
  if(fontFile!=r.FontFile){fontFile=r.FontFile;face=new GlyphTypeface(new Uri(fontFile));}
  Width=Math.Max(r.Width,proposal?.Lines.Select(l=>Point(l.Start+l.Text.Length,Array.IndexOf(proposal.Lines,l)).X-r.X).DefaultIfEmpty(0).Max()??0)*4/3+10;Height=Math.Max(r.LineHeight,proposal?.Lines.Select(l=>l.Baseline-r.Baseline+r.LineHeight).DefaultIfEmpty(r.LineHeight).Max()??r.LineHeight)*4/3+12;InvalidateVisual();
 }
 public void Select(int from,int to,int active,bool focused,int? row=null)
 {
  affinity=row;start=Math.Clamp(Math.Min(from,to),0,text.Length);end=Math.Clamp(Math.Max(from,to),0,text.Length);caret=Math.Clamp(active,0,text.Length);showCaret=focused&&start==end;blink=true;
  if(showCaret)timer.Start();else timer.Stop();InvalidateVisual();
 }
 protected override void OnRender(DrawingContext dc)
 {
  if(region is not Region r||proposal==null||face==null||text.Any(c=>!face.CharacterToGlyphMap.ContainsKey(c)))return;
  const double dip=4.0/3;var brush=new SolidColorBrush(Color.FromRgb((byte)r.R,(byte)r.G,(byte)r.B));
  foreach(var line in proposal.Lines)
  {
   int row=Array.IndexOf(proposal.Lines,line);double y=line.Baseline-r.Baseline;
   int a=Math.Max(start,line.Start),b=Math.Min(end,line.Start+line.Text.Length);
   if(a<b)dc.DrawRectangle(new SolidColorBrush(Color.FromArgb(90,51,142,230)),null,new Rect((Point(a,row).X-r.X)*dip,y*dip,Math.Max(1,(Point(b,row).X-Point(a,row).X)*dip),r.LineHeight*dip));
   for(int j=0;j<line.Text.Length;j++)
   {
    ushort gid=face.CharacterToGlyphMap[line.Text[j]];var run=new GlyphRun(face,0,false,r.FontSize*dip,1,new[]{gid},new Point((line.Origins[j]-r.X)*dip,(r.Ascent+y)*dip),new[]{face.AdvanceWidths[gid]*r.FontSize*dip},null,null,null,null,null,null);dc.DrawGlyphRun(brush,run);
   }
  }
  if(showCaret&&blink){var p=Point(caret,affinity);double x=(p.X-r.X)*dip,y=(p.Y-r.Top)*dip;dc.DrawLine(new Pen(brush,1),new System.Windows.Point(x,y),new System.Windows.Point(x,y+r.FontSize*dip));}
 }
}
