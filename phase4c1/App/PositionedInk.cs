using System.Windows;
using System.Windows.Media;
using System.Windows.Threading;
namespace PdfPrototype;
// RichTextBox owns text, logical selection and history. This layer paints the
// original-font glyphs, selection and caret at the shared proposed PDF positions.
sealed class PositionedInk : FrameworkElement
{
 Region? region;string text="",fontFile="";GlyphTypeface? face;PositionedDraft? proposal;
 int start,end,caret;bool showCaret,blink=true;
 readonly DispatcherTimer timer=new(){Interval=TimeSpan.FromMilliseconds(530)};
 public PositionedInk(){IsHitTestVisible=false;timer.Tick+=(s,e)=>{blink=!blink;InvalidateVisual();};Unloaded+=(s,e)=>timer.Stop();}
 public double CaretOriginPt=>Origin(caret);
 double Origin(int index){if(region==null||proposal==null||proposal.Origins.Length==0)return region?.X??0;return index>=text.Length?proposal.Origins[^1]+region.Advances[text[^1]-32]:proposal.Origins[Math.Clamp(index,0,text.Length-1)];}
 public void Set(Region r,string draft)
 {
  region=r;text=draft;proposal=PositionLayout.Plan(r,draft).Positioned;
  if(fontFile!=r.FontFile){fontFile=r.FontFile;face=new GlyphTypeface(new Uri(fontFile));}
  Width=Math.Max(r.Width,Origin(text.Length)-r.X)*4/3+10;Height=r.LineHeight*4/3+12;InvalidateVisual();
 }
 public void Select(int from,int to,int active,bool focused)
 {
  start=Math.Clamp(Math.Min(from,to),0,text.Length);end=Math.Clamp(Math.Max(from,to),0,text.Length);caret=Math.Clamp(active,0,text.Length);showCaret=focused&&start==end;blink=true;
  if(showCaret)timer.Start();else timer.Stop();InvalidateVisual();
 }
 protected override void OnRender(DrawingContext dc)
 {
  if(region is not Region r||proposal==null||face==null||text.Any(c=>!face.CharacterToGlyphMap.ContainsKey(c)))return;
  const double dip=4.0/3;var brush=new SolidColorBrush(Color.FromRgb((byte)r.R,(byte)r.G,(byte)r.B));
  if(start<end)dc.DrawRectangle(new SolidColorBrush(Color.FromArgb(90,51,142,230)),null,new Rect((Origin(start)-r.X)*dip,0,Math.Max(1,(Origin(end)-Origin(start))*dip),r.LineHeight*dip));
  for(int i=0;i<text.Length;i++)
  {
   ushort gid=face.CharacterToGlyphMap[text[i]];var run=new GlyphRun(face,0,false,r.FontSize*dip,1,new[]{gid},new Point((proposal.Origins[i]-r.X)*dip,r.Ascent*dip),new[]{face.AdvanceWidths[gid]*r.FontSize*dip},null,null,null,null,null,null);dc.DrawGlyphRun(brush,run);
  }
  if(showCaret&&blink){double x=(Origin(caret)-r.X)*dip;dc.DrawLine(new Pen(brush,1),new Point(x,0),new Point(x,r.FontSize*dip));}
 }
}
