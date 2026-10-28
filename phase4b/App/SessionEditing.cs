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
  page.Children.Insert(1,inactiveDrafts);editor.IsUndoEnabled=false;
  recoveryTimer.Tick+=(s,e)=>{recoveryTimer.Stop();PersistDraft();};
  foreach(var command in new[]{ApplicationCommands.Undo,ApplicationCommands.Redo})
   editor.CommandBindings.Add(new CommandBinding(command,async(s,e)=>{e.Handled=true;await UndoDocument(e.Command==ApplicationCommands.Redo);},(s,e)=>{e.CanExecute=command==ApplicationCommands.Undo?session?.CanUndo==true:session?.CanRedo==true;e.Handled=true;}));
  PreviewMouseLeftButtonDown+=async(s,e)=>
  {
   if(info==null||!active)return;var pt=e.GetPosition(page);
   var target=info.Regions.FirstOrDefault(r=>r.Id!=info.Region?.Id&&r.ObservedBounds?.Contains(pt.X/Dip,pt.Y/Dip)==true);
   if(target!=null){e.Handled=true;await SelectRegionAt(pt.X/Dip,pt.Y/Dip);}
  };
 }
 void CaptureSelection()
 {
  if(!active||session==null||!session.Regions.TryGetValue(ActiveKey,out var state))return;
  state.Caret=Math.Clamp(new TextRange(editor.Document.ContentStart,editor.Selection.Start).Text.Replace("\r\n","\n").Length,0,draft.Length);
  state.SelectionEnd=Math.Clamp(new TextRange(editor.Document.ContentStart,editor.Selection.End).Text.Replace("\r\n","\n").Length,0,draft.Length);
 }
 void UpdateDocumentStatus(){if(session!=null)documentStatus.Text=session.Summary();}
 void PaintInactiveDrafts()
 {
  inactiveDrafts.Children.Clear();if(session==null||info==null)return;
  var states=session.Regions.Values.Where(s=>s.Original.Page==info.Page&&s.Compatible&&(s.Modified||s.Key==ActiveKey)).ToArray();
  foreach(var state in states)
  {
   if(active&&state.Key==ActiveKey)continue;
   Region r=state.Original;var layout=ParagraphLayout.Plan(r,state.Text);
   if(r.Positioned!=null&&layout.Safe)
   {
    var ink=new PositionedInk();ink.Set(r,state.Text);Canvas.SetLeft(ink,r.X*Dip);Canvas.SetTop(ink,r.Top*Dip);inactiveDrafts.Children.Add(ink);continue;
   }
   string asset=Path.Combine(AppContext.BaseDirectory,"assets",r.FontFile);var face=new GlyphTypeface(new Uri(asset));var family=new FontFamily(new Uri(Path.GetDirectoryName(asset)+Path.DirectorySeparatorChar),"./#"+face.FamilyNames.Values.First());
   var paragraph=new Paragraph(new Run(state.Text)){Margin=new Thickness(0),Padding=new Thickness(0),LineHeight=r.LineHeight*Dip,LineStackingStrategy=LineStackingStrategy.BlockLineHeight};
   var view=new RichTextBox{IsReadOnly=true,IsUndoEnabled=false,IsHitTestVisible=false,BorderThickness=new Thickness(0),Padding=new Thickness(0),Background=Brushes.Transparent,FontFamily=family,FontSize=r.FontSize*Dip,FontWeight=face.Weight,FontStyle=face.Style,Foreground=new SolidColorBrush(Color.FromRgb((byte)r.R,(byte)r.G,(byte)r.B)),Width=r.Width*Dip,Height=Math.Max(r.LineHeight*Dip+12,Math.Min((info.Height-r.Top)*Dip,(layout.Safe?layout.Height:r.LineHeight*Math.Max(1,state.Text.Split('\n').Length))*Dip+12)),Document=new FlowDocument(paragraph){FontFamily=family,FontWeight=face.Weight,FontStyle=face.Style,FontSize=r.FontSize*Dip,PagePadding=new Thickness(0),ColumnWidth=1000000,LineHeight=r.LineHeight*Dip,LineStackingStrategy=LineStackingStrategy.BlockLineHeight}};
   Typography.SetKerning(view.Document,false);Typography.SetStandardLigatures(view.Document,false);TextOptions.SetTextFormattingMode(view,TextFormattingMode.Ideal);
   inactiveDrafts.Children.Add(view);Canvas.SetLeft(view,r.X*Dip);Canvas.SetTop(view,r.Top*Dip);view.UpdateLayout();
   var first=view.Document.ContentStart.GetInsertionPosition(LogicalDirection.Forward)!.GetCharacterRect(LogicalDirection.Forward);view.Width=r.Width*Dip+first.X*2;Canvas.SetLeft(view,r.X*Dip-first.X);Canvas.SetTop(view,r.Top*Dip-first.Y);
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
  foreach(var state in session.Modified){state.Validation=result.Safe?"Verified":(!state.Compatible||!ParagraphLayout.Plan(state.Original,state.Text).Safe?"Blocked":"Pending");state.Message=result.Diagnostic;if(result.Safe)state.Compatible=true;}
  foreach(var v in result.Regions)if(session.Regions.TryGetValue(v.Key,out var state)){state.Validation=v.State;state.Message=v.Message;if(v.State=="Verified")state.Compatible=true;}
  UpdateDocumentStatus();
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
