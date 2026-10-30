using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Media;
namespace PdfPrototype;
public sealed partial class EditorWindow
{
 readonly Dictionary<string,(string Source,string Identity,string Text,double Offset)> retainedViewports=[];
 DocumentSession? viewportOwner;
 void RememberRetainedViewport()
 {
  if(session==null||info?.Region is not Region r||!active||!IsRetainedDraft(r,draft,ParagraphLayout.Plan(r,draft)))return;
  if(viewportOwner!=session){retainedViewports.Clear();viewportOwner=session;}
  retainedViewports[ActiveKey]=(session.SourceHash,r.SourceIdentity,draft,editor.VerticalOffset);
 }
 double RememberedRetainedOffset(Region r,string text)
 {
  return session==viewportOwner&&retainedViewports.TryGetValue(DocumentSession.Key(r.Page,r.Id),out var v)&&v.Source==session!.SourceHash&&v.Identity==r.SourceIdentity&&v.Text==text?v.Offset:0;
 }
 readonly FontFamily retainedReviewFamily=new("Segoe UI");
 readonly Dictionary<string,FontFamily> originalPresentationFamilies=[];
 FontFamily OriginalPresentationFamily(Region r)
 {
  if(!originalPresentationFamilies.TryGetValue(r.FontFile,out var family))
  {
   string asset=Path.Combine(AppContext.BaseDirectory,"assets",r.FontFile);var face=new GlyphTypeface(new Uri(asset));
   originalPresentationFamilies[r.FontFile]=family=new FontFamily(new Uri(Path.GetDirectoryName(asset)+Path.DirectorySeparatorChar),"./#"+face.FamilyNames.Values.First());
  }
  return family;
 }
 readonly Border retainedDraftFrame=new(){Visibility=Visibility.Collapsed,IsHitTestVisible=false,BorderThickness=new Thickness(1),BorderBrush=Brushes.DarkGoldenrod,Background=new SolidColorBrush(Color.FromArgb(34,255,192,64)),ClipToBounds=true};
 bool IsRetainedDraft(Region r,string text,Layout plan)
 {
  return PresentationState(r,text,plan)=="Rejected";
 }
 bool UsesPositionedPresentation=>active&&info?.Region is Region r&&r.Positioned!=null&&!IsRetainedDraft(r,draft,ParagraphLayout.Plan(r,draft))&&ParagraphLayout.Plan(r,draft).Positioned!=null;
 Box RetainedDraftBounds(Region r)
 {
  // An editing surface, never permission to paint a proposed PDF outside its
  // verified source envelope. No extra blank-page space or neighbour is owned.
  double right=Math.Min(info?.Width??r.X+r.Width,r.Positioned?.SafeRight??r.X+r.Width),bottom=r.SafeBottom,top=Math.Max(r.Top,r.ObservedBounds?.Y??r.Top);
  var owned=r.Objects.ToHashSet();var observed=r.ObservedBounds??new Box(r.X,top,1,1);
  foreach(var o in info?.PageObjects??[])
  {
   var b=o.Bounds;if(owned.Contains(o.Index)||b.Width<=0||b.Height<=0)continue;
   if(b.Y<bottom&&b.Bottom>top&&b.X>observed.Right+.5)right=Math.Min(right,b.X-.5);
   if(b.X<right&&b.Right>r.X&&b.Y>observed.Bottom+.5)bottom=Math.Min(bottom,b.Y-.5);
  }
  return new(r.X,top,Math.Max(1,right-r.X),Math.Max(1,bottom-top));
 }
 static void ConfigureRetainedText(RichTextBox view,Region r)
 {
  view.HorizontalScrollBarVisibility=ScrollBarVisibility.Disabled;view.VerticalScrollBarVisibility=ScrollBarVisibility.Auto;view.ClipToBounds=true;
  view.Document.PageWidth=double.NaN;view.Document.ColumnWidth=double.NaN;
  double leading=r.FontSize*Dip*1.25;view.Document.LineHeight=leading;
  foreach(var paragraph in view.Document.Blocks.OfType<Paragraph>())paragraph.LineHeight=leading;
 }
 string DraftReason(Region r,string text,Layout plan)
 {
  string reason=plan.ReasonCodes.FirstOrDefault()??"";
  if(text.Contains('\n')||text.Contains('\r'))return "Hard line break in the current draft. Explicit paragraph breaks are not supported for PDF export; all breaks are retained.";
  if(reason.Contains("VERTICAL")||reason.Contains("LINE_LIMIT"))return "Insufficient vertical space in this paragraph.";
  if(plan.GlyphIssues.FirstOrDefault() is CharacterCompatibility issue)return $"Original-font mapping unavailable for U+{issue.Unicode:X4}: {issue.State} ({issue.Reason}). The current character is retained.";
  if(reason.Contains("CHARACTER"))return "Current text contains an unsupported original-font character. "+plan.Diagnostic;
  if(reason.Contains("LENGTH"))return "Position recalculation exceeds the supported 512-character limit.";
  if(reason.Contains("HORIZONTAL")||reason.Contains("GLYPH_WIDTH"))return "Text exceeds the supported horizontal width.";
  if(reason.Contains("PROTECTED"))return "The proposed text collides with protected content.";
  if(reason.Contains("OVERLAP"))return "The proposed glyph ink overlaps.";
  if(CurrentEvidence(r,text) is DraftEvidence evidence&&evidence.Revision==session!.Revision&&evidence.Message.Length>0)
  {
   if(evidence.Message.Contains("complete draft",StringComparison.OrdinalIgnoreCase)||evidence.Message.Contains("extraction",StringComparison.OrdinalIgnoreCase))return "Exact text extraction could not be verified.";
   return evidence.Message;
  }
  return plan.Diagnostic;
 }
 void ConfigureDraftPresentation()
 {
  if(info?.Region is not Region r)return;layout=ParagraphLayout.Plan(r,draft);
  bool retained=IsRetainedDraft(r,draft,layout);retainedDraftFrame.Visibility=active&&retained?Visibility.Visible:Visibility.Collapsed;
  bool previous=suppress;suppress=true;
  try
  {
   if(retained)
   {
    var box=RetainedDraftBounds(r);double width=box.Width*Dip,height=box.Height*Dip;
    editor.FontFamily=retainedReviewFamily;editor.Document.FontFamily=retainedReviewFamily;
    retainedDraftFrame.Width=width;retainedDraftFrame.Height=height;Canvas.SetLeft(retainedDraftFrame,box.X*Dip);Canvas.SetTop(retainedDraftFrame,box.Y*Dip);
    editor.Width=Math.Max(1,width-4);editor.Height=Math.Max(1,height-4);Canvas.SetLeft(editor,box.X*Dip+2);Canvas.SetTop(editor,box.Y*Dip+2);ConfigureRetainedText(editor,r);
    editor.ToolTip=$"Retained draft · {draft.Length} characters · review font Segoe UI, not a PDF layout. Scroll here to review and correct all text. "+DraftReason(r,draft,layout);
   }
   else
   {
    editor.FontFamily=OriginalPresentationFamily(r);editor.Document.FontFamily=editor.FontFamily;
    editor.ToolTip=null;editor.Document.PageWidth=double.NaN;editor.Document.ColumnWidth=1000000;editor.Document.LineHeight=r.LineHeight*Dip;
    foreach(var paragraph in editor.Document.Blocks.OfType<Paragraph>())paragraph.LineHeight=r.LineHeight*Dip;
    editor.Width=(r.Positioned!=null?Math.Max(r.Width,ParagraphLayout.Width(r,draft))+24:r.Width)*Dip;editor.Height=Math.Max(r.LineHeight*Dip+12,layout.Height*Dip+12);
    Canvas.SetLeft(editor,r.X*Dip);Canvas.SetTop(editor,r.Top*Dip);
    if(active&&editor.Visibility==Visibility.Visible){editor.UpdateLayout();var first=Position(0).GetCharacterRect(LogicalDirection.Forward);if(!first.IsEmpty&&double.IsFinite(first.X)&&double.IsFinite(first.Y)){editor.Width+=first.X*2;Canvas.SetLeft(editor,r.X*Dip-first.X);Canvas.SetTop(editor,r.Top*Dip-first.Y);}}
   }
  }
  finally{suppress=previous;}
 }
 Border RetainedDraftPreview(Region r,string text)
 {
  var family=retainedReviewFamily;var face=new GlyphTypeface(new Uri(Path.Combine(AppContext.BaseDirectory,"assets",r.FontFile)));
  var paragraph=new Paragraph(new Run(text)){Margin=new Thickness(0),Padding=new Thickness(0)};
  var view=new RichTextBox{Document=new FlowDocument(paragraph){Focusable=false,PagePadding=new Thickness(0),FontFamily=family,FontSize=r.FontSize*Dip,FontStyle=face.Style,FontWeight=face.Weight},IsReadOnly=true,IsUndoEnabled=false,IsHitTestVisible=false,Focusable=false,IsTabStop=false,BorderThickness=new Thickness(0),Padding=new Thickness(0),Background=Brushes.Transparent,Foreground=new SolidColorBrush(Color.FromRgb((byte)r.R,(byte)r.G,(byte)r.B)),FontFamily=family,FontSize=r.FontSize*Dip};
  Typography.SetKerning(view.Document,false);Typography.SetStandardLigatures(view.Document,false);TextOptions.SetTextFormattingMode(view,TextFormattingMode.Ideal);ConfigureRetainedText(view,r);
  double offset=RememberedRetainedOffset(r,text);view.Loaded+=(sender,args)=>view.Dispatcher.BeginInvoke(()=>view.ScrollToVerticalOffset(offset),System.Windows.Threading.DispatcherPriority.Loaded);
  var bounds=RetainedDraftBounds(r);return new Border{Child=view,Padding=new Thickness(1),BorderThickness=new Thickness(1),BorderBrush=Brushes.DarkGoldenrod,Background=retainedDraftFrame.Background,Width=bounds.Width*Dip,Height=bounds.Height*Dip,ClipToBounds=true,Tag=new{source=r.SourceHash,identity=r.SourceIdentity,revision=session?.Revision,text},ToolTip=$"Retained draft · {text.Length} characters · review font Segoe UI, not exportable. Click to edit and scroll through the complete text."};
 }
 void RefreshDraftPresentation()
 {
  if(info?.Region==null)return;ConfigureDraftPresentation();UpdatePositionedInk();PaintInactiveDrafts();UpdateDocumentStatus();
 }
}
