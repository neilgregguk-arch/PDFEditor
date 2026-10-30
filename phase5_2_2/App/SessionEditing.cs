using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Threading;
namespace PdfPrototype;
public sealed partial class EditorWindow
{
 DocumentSession? session;long navigation;
 readonly Canvas inactiveDrafts=new(){IsHitTestVisible=false};
 readonly TextBlock documentStatus=new(){Margin=new Thickness(20,4,20,5),TextWrapping=TextWrapping.Wrap,Foreground=Brushes.SlateGray};
 readonly DispatcherTimer recoveryTimer=new(){Interval=TimeSpan.FromMilliseconds(350)};
 string ActiveKey=>info?.Region is Region r?DocumentSession.Key(r.Page,r.Id):"";
 string SessionRecoveryPath(string hash)=>Path.Combine(recovery,hash+".session.json");
 void InitializeSessionEditing(DockPanel root)
 {
  var indicator=new Border{Child=documentStatus};DockPanel.SetDock(indicator,Dock.Bottom);root.Children.Insert(0,indicator);
  InitializeRegionPicker(root);page.Children.Insert(1,inactiveDrafts);editor.IsUndoEnabled=false;
  recoveryTimer.Tick+=(s,e)=>{recoveryTimer.Stop();PersistDraft();};
  foreach(var command in new[]{ApplicationCommands.Undo,ApplicationCommands.Redo})
   editor.CommandBindings.Add(new CommandBinding(command,async(s,e)=>{e.Handled=true;await UndoDocument(e.Command==ApplicationCommands.Redo);},(s,e)=>{e.CanExecute=command==ApplicationCommands.Undo?session?.CanUndo==true:session?.CanRedo==true;e.Handled=true;}));
  PreviewMouseLeftButtonDown+=async(s,e)=>
  {
   if(info==null||!active)return;var pt=EventPagePoint(e);
   var target=FindRegionAt(pt.X/Dip,pt.Y/Dip);if(target?.Id==info.Region?.Id)target=null;
   if(target!=null){e.Handled=true;var task=SelectRegionAt(pt.X/Dip,pt.Y/Dip);if(routedPagePointForControlTest!=null)routedTaskForControlTest=task;await task;return;}
   if(BeginPositionSelection(pt,e.ClickCount,Keyboard.Modifiers.HasFlag(ModifierKeys.Shift)))e.Handled=true;
  };
  PreviewMouseMove+=(s,e)=>{if(positionDragging&&e.LeftButton==MouseButtonState.Pressed){ExtendPositionSelection(e.GetPosition(page));e.Handled=true;}};
  PreviewMouseLeftButtonUp+=(s,e)=>{if(positionDragging){positionDragging=false;editor.ReleaseMouseCapture();e.Handled=true;}};
  editor.LostMouseCapture+=(s,e)=>positionDragging=false;
 }
 Region? FindRegionAt(double x,double y)
 {
  if(info==null)return null;
  var observed=info.Regions.Where(r=>r.ObservedBounds?.Contains(x,y)==true).OrderBy(r=>r.ObservedBounds!.Width*r.ObservedBounds.Height).ThenBy(r=>r.Id,StringComparer.Ordinal).FirstOrDefault();if(observed!=null)return observed;
  return session?.Regions.Values.Where(s=>s.Original.Page==info.Page&&s.Compatible&&s.Modified).OrderBy(s=>s.Original.ObservedBounds?.Y??s.Original.Top).ThenBy(s=>s.Key,StringComparer.Ordinal).FirstOrDefault(s=>(IsRetainedDraft(s.Original,s.Text,ParagraphLayout.Plan(s.Original,s.Text))?RetainedDraftBounds(s.Original).Contains(x,y):ParagraphLayout.Plan(s.Original,s.Text).LineBoxes.Any(b=>b.Contains(x,y))))?.Original;
 }
 void CaptureSelection()
 {
  RememberRetainedViewport();
  if(!active||session==null||!session.Regions.TryGetValue(ActiveKey,out var state))return;
  state.Caret=Math.Clamp(new TextRange(editor.Document.ContentStart,editor.Selection.Start).Text.Replace("\r\n","\n").Length,0,draft.Length);
  state.SelectionEnd=Math.Clamp(new TextRange(editor.Document.ContentStart,editor.Selection.End).Text.Replace("\r\n","\n").Length,0,draft.Length);
 }
 void UpdateDocumentStatus()
 {
  if(session==null)return;documentStatus.Text=PresentationSummary();
  var blocked=session.Modified.Where(s=>PresentationState(s.Original,s.Text,ParagraphLayout.Plan(s.Original,s.Text))=="Rejected").ToArray();
  if(blocked.Length>0)documentStatus.Text+=" · Retained drafts in amber: "+string.Join(" ",blocked.Select(s=>DraftReason(s.Original,s.Text,ParagraphLayout.Plan(s.Original,s.Text))).Distinct());
  if(saveButton!=null)saveButton.IsEnabled=!opening&&!saving&&session.Modified.Length>0&&session.VerifiedRevision==session.Revision&&session.Modified.All(s=>s.Validation=="Verified"&&s.Compatible);
 }
 void PaintInactiveDrafts()
 {
  inactiveDrafts.Children.Clear();if(session==null||info==null)return;
  var states=session.Regions.Values.Where(s=>s.Original.Page==info.Page&&s.Compatible&&(s.Modified||s.Key==ActiveKey)).ToArray();
  foreach(var state in states)
  {
   if(active&&state.Key==ActiveKey)continue;
   Region r=state.Original;var layout=ParagraphLayout.Plan(r,state.Text);
   if(IsRetainedDraft(r,state.Text,layout)){var retained=RetainedDraftPreview(r,state.Text);var bounds=RetainedDraftBounds(r);Canvas.SetLeft(retained,bounds.X*Dip);Canvas.SetTop(retained,bounds.Y*Dip);inactiveDrafts.Children.Add(retained);continue;}
   if(r.Positioned!=null&&layout.Positioned!=null)
   {
    var ink=new PositionedInk();ink.Set(r,state.Text);Canvas.SetLeft(ink,r.X*Dip);Canvas.SetTop(ink,r.Top*Dip);inactiveDrafts.Children.Add(ink);continue;
   }
   string asset=Path.Combine(AppContext.BaseDirectory,"assets",r.FontFile);var face=new GlyphTypeface(new Uri(asset));var family=new FontFamily(new Uri(Path.GetDirectoryName(asset)+Path.DirectorySeparatorChar),"./#"+face.FamilyNames.Values.First());
   var paragraph=new Paragraph(new Run(state.Text)){Margin=new Thickness(0),Padding=new Thickness(0),LineHeight=r.LineHeight*Dip,LineStackingStrategy=LineStackingStrategy.BlockLineHeight};
   var view=new RichTextBox{IsReadOnly=true,IsUndoEnabled=false,IsHitTestVisible=false,Focusable=false,IsTabStop=false,BorderThickness=new Thickness(0),Padding=new Thickness(0),Background=Brushes.Transparent,FontFamily=family,FontSize=r.FontSize*Dip,FontWeight=face.Weight,FontStyle=face.Style,Foreground=new SolidColorBrush(Color.FromRgb((byte)r.R,(byte)r.G,(byte)r.B)),Width=(r.Positioned!=null?Math.Max(r.Width,Math.Min(info.Width-r.X-12,ParagraphLayout.Width(r,state.Text)+24)):r.Width)*Dip,Height=Math.Max(r.LineHeight*Dip+12,Math.Min((info.Height-r.Top)*Dip,(layout.Safe?layout.Height:r.LineHeight*Math.Max(1,state.Text.Split('\n').Length))*Dip+12)),Document=new FlowDocument(paragraph){Focusable=false,FontFamily=family,FontWeight=face.Weight,FontStyle=face.Style,FontSize=r.FontSize*Dip,PagePadding=new Thickness(0),ColumnWidth=1000000,LineHeight=r.LineHeight*Dip,LineStackingStrategy=LineStackingStrategy.BlockLineHeight}};
   Typography.SetKerning(view.Document,false);Typography.SetStandardLigatures(view.Document,false);TextOptions.SetTextFormattingMode(view,TextFormattingMode.Ideal);
   inactiveDrafts.Children.Add(view);Canvas.SetLeft(view,r.X*Dip);Canvas.SetTop(view,r.Top*Dip);view.UpdateLayout();
   var first=view.Document.ContentStart.GetInsertionPosition(LogicalDirection.Forward)!.GetCharacterRect(LogicalDirection.Forward);view.Width+=first.X*2;Canvas.SetLeft(view,r.X*Dip-first.X);Canvas.SetTop(view,r.Top*Dip-first.Y);
  }
 }
 async Task UndoDocument(bool redo)
 {
  if(session==null)return;CaptureSelection();var changed=session.MoveHistory(redo);if(changed==null)return;
  revision=session.Revision;verifiedRevision=-1;var state=session.Regions[changed.Key];int caret=state.Caret;string source=session.Source;
  await Open(source,state.Original.Page,state.Original.Id);if(session?.Source!=source)return;ActivateAt(Math.Clamp(caret,0,draft.Length));PaintInactiveDrafts();PersistDraft();debounce.Start();UpdateDocumentStatus();
 }
 void ApplyValidation(EditResult result)
 {
  if(session==null)return;session.VerifiedRevision=result.Safe?session.Revision:-1;
  EnsureEvidenceOwner();
  foreach(var state in session.Modified)
  {
   var response=result.Regions.FirstOrDefault(v=>v.Key==state.Key);
   string outcome=result.Safe?"Verified":response?.State=="Blocked"?"Rejected":"Pending";
   currentEvidence[state.Key]=new(session.SourceHash,state.Identity,state.Text,session.Revision,outcome,response?.Message??result.Diagnostic);
   state.Validation=outcome=="Rejected"?"Blocked":outcome;
   state.Message=response?.Message??result.Diagnostic;
  }
  RefreshDraftPresentation();
 }
 void CleanupWork()
 {
  string root=Path.GetFullPath(Path.Combine(Path.GetTempPath(),"PdfEditorPrototype"))+Path.DirectorySeparatorChar;
  string target=Path.GetFullPath(work);
  if(!target.StartsWith(root,StringComparison.OrdinalIgnoreCase)||!Guid.TryParseExact(Path.GetFileName(target),"N",out _))return;
  try{Directory.Delete(target,true);}catch(IOException){}catch(UnauthorizedAccessException){}
 }
 void AuditExport(EditRequest request,EditResult result)
 {
  if(auditFolder==null)return;
  try
  {
   File.WriteAllText(Path.Combine(auditFolder,"last-save.json"),Wire.Write(result));
   File.WriteAllText(Path.Combine(auditFolder,"export-record-"+Guid.NewGuid().ToString("N")+".json"),Wire.Write(new{source=request.Source,sourceHash=request.ExpectedHash,changes=request.Changes,destination=result.Destination,result}));
  }
  catch(IOException){/* A test audit failure cannot turn a committed PDF into a failed save. */}
  catch(UnauthorizedAccessException){}
 }
}
