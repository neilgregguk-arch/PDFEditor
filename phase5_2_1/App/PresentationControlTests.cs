using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
namespace PdfPrototype;
public sealed partial class EditorWindow
{
 async Task RunPresentationControlTests(bool baseline)
 {
  var rows=new List<object>();int failures=0;string folder=auditFolder!;
  void Assert(bool condition,string message){if(!condition)throw new Exception(message);}
  async Task Pump(){await Dispatcher.InvokeAsync(()=>{},DispatcherPriority.ApplicationIdle);editor.UpdateLayout();await Task.Delay(90);}
  async Task Check(string name,Func<Task<object>> test){try{rows.Add(new{name,status="pass",detail=await test()});}catch(Exception ex){failures++;rows.Add(new{name,status="fail",error=ex.ToString(),draft});}}
  string source=Path.Combine(AppContext.BaseDirectory,"original-paragraphs","Word-cafe-paragraph.pdf"),hash=Wire.Hash(source);
  async Task<Region> ChooseOriginal()
  {
   await Open(source);var g=info!.Regions.Single(r=>r.Paragraph?.Evidence=="ExistingDocumentParagraphSingleMcid");await Open(source,0,g.Id);await SelectRegionAt(g.X+4,g.Baseline-3);await Pump();Assert(active,"Original activation failed");return g;
  }
  void Replace(string text){editor.SelectAll();InsertDraftText(text);}
  void Capture(string name){viewport.ScrollToHome();WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,name+".png"),true);File.Copy(Path.Combine(folder,"state.json"),Path.Combine(folder,name+".json"),true);}
  object Metrics(Region g)=>new{draftLength=draft.Length,textExact=Text()==draft,active,editorWidth=editor.ActualWidth,editorHeight=editor.ActualHeight,pageWidth=page.ActualWidth,editorRight=Canvas.GetLeft(editor)+editor.ActualWidth,nativeVisible=editor.Foreground is SolidColorBrush brush&&brush.Color.A>0,positionedVisible=positionedInk.Visibility==Visibility.Visible,layoutSafe=layout?.Safe,proposedRows=layout?.Positioned?.Lines.Length,sourceSafeBottom=g.SafeBottom,sourceTop=g.Top,sourceRight=g.Positioned!.SafeRight,inactive=inactiveDrafts.Children.OfType<FrameworkElement>().Select(v=>new{type=v.GetType().Name,width=v.ActualWidth,height=v.ActualHeight,left=Canvas.GetLeft(v),top=Canvas.GetTop(v)}).ToArray(),sessionRevision=session?.Revision,verifiedRevision=session?.VerifiedRevision};
  void Bounded(Region g)
  {
   Assert(!status.Text.StartsWith("Open failed"),status.Text);Assert(draft==Text(),"Native text differs");Assert(retainedDraftFrame.Visibility==Visibility.Visible&&positionedInk.Visibility!=Visibility.Visible,"Unsafe PDF ink still painted");
   Assert(Canvas.GetLeft(editor)+editor.ActualWidth<=g.Positioned!.SafeRight*Dip+.01&&Canvas.GetTop(editor)+editor.ActualHeight<=g.SafeBottom*Dip+.01,"Retained editor leaves envelope");Assert(page.ClipToBounds&&editor.ClipToBounds,"Missing containment");Assert(saveButton?.IsEnabled==false,"Blocked draft can appear ready");
   Assert(double.IsNaN(editor.Document.ColumnWidth),"Native preview did not wrap");
  }
  foreach(int repeats in new[]{30,70})foreach(bool append in new[]{false,true})
  await Check((append?"append-":"replace-")+repeats,async()=>
  {
   var g=await ChooseOriginal();Replace(g.OriginalText);string text=string.Join(" ",Enumerable.Repeat("cafe calm.",repeats));if(append){editor.Selection.Select(Position(draft.Length),Position(draft.Length));InsertDraftText(" "+text);text=g.OriginalText+" "+text;}else Replace(text);await Pump();Assert(draft==text,"Input differs");layout=ParagraphLayout.Plan(g,draft);Assert(!layout.Safe,"Expected bounded refusal");if(!baseline)Bounded(g);Capture((append?"append-":"replace-")+repeats+"-active");var activeMetrics=Metrics(g);
   await ValidateDraft();Assert(session!.VerifiedRevision==-1,"Invalid draft verified");string denied=Path.Combine(folder,"must-not-save-"+repeats+append+".pdf");var refused=await ExportTo(denied);Assert(refused?.Safe!=true&&!File.Exists(denied),"Invalid export succeeded");Assert(draft==text,"Refusal lost draft");
   var other=info!.Regions.First(r=>r.Id!=g.Id&&r.Eligibility=="Editable");await Open(source,0,other.Id);await Pump();Assert(session.Regions[DocumentSession.Key(0,g.Id)].Text==text,"Focus transition lost text");if(!baseline){Assert(!status.Text.StartsWith("Open failed"),status.Text);var preview=inactiveDrafts.Children.OfType<Border>().Single();Assert(new TextRange(((RichTextBox)preview.Child).Document.ContentStart,((RichTextBox)preview.Child).Document.ContentEnd).Text.Replace("\r\n","\n").TrimEndOneNewline()==text,"Inactive text differs");Assert(Math.Abs(preview.Width-retainedDraftFrame.Width)<.01&&Math.Abs(preview.Height-retainedDraftFrame.Height)<.01,"Active/inactive bounds differ");}Capture((append?"append-":"replace-")+repeats+"-inactive");var inactiveMetrics=Metrics(g);await Open(source,0,g.Id);await SelectRegionAt(g.X+4,g.Baseline-3);await Pump();Assert(draft==text,"Return lost text");if(!baseline){Bounded(g);Capture((append?"append-":"replace-")+repeats+"-returned");}return new{length=text.Length,activeMetrics,inactiveMetrics,refused=refused?.Diagnostic};
  });
  if(!baseline)
  {
   await Check("valid-pending-verified-active-inactive-save-reopen",async()=>
   {
    var g=await ChooseOriginal();Replace(g.OriginalText);await Pump();Capture("original-unmodified");string text=string.Join(" ",Enumerable.Repeat("calm cafe.",11));Replace(text);Assert(layout!.Safe&&saveButton!.IsEnabled==false&&session!.VerifiedRevision==-1,"Pending draft mislabelled");Capture("active-valid-pending");await ValidateDraft();Assert(session!.VerifiedRevision==session.Revision&&saveButton.IsEnabled,"Verified draft not exportable");Capture("active-valid-verified");
    var other=info!.Regions.First(r=>r.Id!=g.Id&&r.Eligibility=="Editable");await Open(source,0,other.Id);await Pump();Assert(!status.Text.StartsWith("Open failed"),status.Text);Assert(inactiveDrafts.Children.OfType<Border>().Count()==0,"Valid ink switched to retained fallback");Capture("inactive-valid");await Open(source,0,g.Id);await SelectRegionAt(g.X+3,g.Baseline-3);Assert(draft==text,"Valid focus return changed text");string dest=Path.Combine(folder,"presentation-safe-export.pdf");var result=await ExportTo(dest);Assert(result?.Safe==true,"Safe export failed");await Open(dest);var reopened=info!.Regions.Single(r=>r.Paragraph!=null);await SelectRegionAt(reopened.X+3,reopened.Baseline-3);await Pump();Assert(draft==text&&reopened.Paragraph!.Evidence=="ValidatedEmbeddedParagraphDeclaration","Reopened edit failed");Capture("saved-reopened");return new{result,rows=reopened.OriginalLines.Length};
   });
   foreach(int z in new[]{0,1,2,3})foreach(var size in new[]{(780.0,650.0),(1120.0,900.0)})
   await Check($"invalid-contained-zoom-{z}-window-{size.Item1}",async()=>
   {
    Width=size.Item1;Height=size.Item2;zoom.SelectedIndex=z;var g=await ChooseOriginal();var measurements=new List<object>();
    foreach(int repeats in new[]{15,30,70})
    {
     string text=string.Join(" ",Enumerable.Repeat("cafe calm.",repeats));Replace(text);await Pump();Bounded(g);Assert(draft==text,"Resize/zoom changes text");editor.Selection.Select(Position(draft.Length),Position(draft.Length));editor.ScrollToEnd();await Pump();var rect=editor.CaretPosition.GetCharacterRect(LogicalDirection.Forward);Assert(!rect.IsEmpty&&rect.X>=-1&&rect.Right<=editor.ActualWidth+1&&rect.Y>=-1&&rect.Bottom<=editor.ActualHeight+3,"Retained endpoint caret not visible");Assert(viewport.ExtentWidth<=page.Width*zoomFactor+100,"Page extent follows unwrapped draft");measurements.Add(new{length=text.Length,editor.ActualWidth,editor.ActualHeight,editor.VerticalOffset,caretX=rect.X,caretY=rect.Y});
    }
    Capture($"matrix-z{z}-w{size.Item1}");return measurements;
   });
   Width=1120;Height=900;zoom.SelectedIndex=1;
   foreach(string where in new[]{"beginning","middle","end"})
   await Check("paste-"+where+"-undo-redo",async()=>
   {
    var g=await ChooseOriginal();Replace(g.OriginalText);int at=where=="beginning"?0:where=="middle"?g.OriginalText.Length/2:g.OriginalText.Length;string insert=string.Join(" ",Enumerable.Repeat("cafe calm.",12))+" ";editor.Selection.Select(Position(at),Position(at));InsertDraftText(insert);await Pump();string expected=g.OriginalText.Insert(at,insert);Assert(draft==expected,"Paste changed content");Bounded(g);await UndoDocument(false);Assert(draft==g.OriginalText,"Paste undo");await UndoDocument(true);await Pump();Assert(draft==expected,"Paste redo");Bounded(g);return new{at,length=draft.Length};
   });
   await Check("character-input-equivalent-to-shared-paste",async()=>
   {
    var g=await ChooseOriginal();Replace("");string text=string.Join(" ",Enumerable.Repeat("cafe calm.",30));foreach(char c in text){editor.RaiseEvent(new TextCompositionEventArgs(InputManager.Current.PrimaryKeyboardDevice,new TextComposition(InputManager.Current,editor,c.ToString())){RoutedEvent=TextCompositionManager.TextInputEvent});}await Pump();Assert(draft==text,"Character input differs");Bounded(g);var typed=Metrics(g);Replace(g.OriginalText);editor.SelectAll();InsertDraftText(text);await Pump();Assert(draft==text,"Paste differs from typing");Bounded(g);return new{typed,pasted=Metrics(g),scope="Programmatic character TextInput, not physical typing"};
   });
   await Check("incremental-height-threshold-with-unchanged-envelope",async()=>
   {
    var g=await ChooseOriginal();var data=new List<object>();int firstBlocked=0,lastSafe=0;double bottom=g.SafeBottom;
    for(int n=8;n<=18;n++){Replace(string.Join(" ",Enumerable.Repeat("cafe calm.",n)));await Pump();bool safe=ParagraphLayout.Plan(g,draft).Safe;if(safe)lastSafe=n;else{firstBlocked=firstBlocked==0?n:firstBlocked;Bounded(g);}data.Add(new{repeats=n,length=draft.Length,safe});Assert(info!.Region!.SafeBottom==bottom,"Envelope expanded");}Assert(lastSafe>0&&firstBlocked>lastSafe,"Did not cross a safe height threshold");return new{lastSafe,firstBlocked,bottom,data};
   });
   await Check("invalid-native-navigation-selection-and-source-bound-recovery",async()=>
   {
    var g=await ChooseOriginal();string text=string.Join(" ",Enumerable.Repeat("cafe calm.",30));Replace(text);await Pump();Bounded(g);editor.Selection.Select(Position(text.Length),Position(text.Length));EditingCommands.MoveToDocumentEnd.Execute(null,editor);EditingCommands.MoveToLineStart.Execute(null,editor);EditingCommands.SelectUpByLine.Execute(null,editor);Assert(!editor.Selection.IsEmpty&&text.Contains(editor.Selection.Text),"Native shift/Up selection failed");
    editor.ScrollToHome();await Pump();var a=editor.GetPositionFromPoint(new Point(12,8),true)!;var b=editor.GetPositionFromPoint(new Point(80,35),true)!;Assert(a!=null&&b!=null,"Native hit mapping absent");Assert(!BeginPositionSelection(new Point(g.X*Dip+12,g.Top*Dip+10),1,false),"PDF hit mapping intercepted retained input");editor.Selection.Select(a,b);string selected=editor.Selection.Text;Assert(selected.Length>0&&text.Contains(selected),"Native multi-row selection");InsertDraftText("cafe ");await Pump();await UndoDocument(false);Assert(draft==text,"Retained selected replacement undo");PersistDraft();var restored=DocumentSession.Restore(SessionRecoveryPath(session!.SourceHash),session.SourceHash);Assert(restored.Regions[ActiveKey].Text==text,"Recovery changed invalid text");bool foreign=false;try{DocumentSession.Restore(SessionRecoveryPath(session.SourceHash),new string('f',64));}catch{foreign=true;}Assert(foreign,"Foreign recovery accepted");Capture("invalid-native-selection");return new{selected,restoredCharacters=text.Length};
   });
   foreach(bool changeDocument in new[]{false,true})
   await Check(changeDocument?"late-worker-response-after-document-switch":"late-worker-response-after-newer-edit",async()=>
   {
    var g=await ChooseOriginal();Replace(string.Join(" ",Enumerable.Repeat("cafe calm.",30)));debounce.Stop();var arrived=new TaskCompletionSource();var release=new TaskCompletionSource();
    worker.BeforeDeliveryForControlTest=async req=>{if(req.Command=="preview"){worker.BeforeDeliveryForControlTest=null;arrived.SetResult();await release.Task;}};
    Task validation=ValidateDraft();await arrived.Task.WaitAsync(TimeSpan.FromSeconds(10));
    if(changeDocument){Task opening=Open(Path.Combine(AppContext.BaseDirectory,"font-corpus","Word-Arial.pdf"));release.SetResult();await validation;await opening;Assert(info!.Path.EndsWith("Word-Arial.pdf")&&!status.Text.Contains("wrapped draft reaches"),"Old response overwrote new document");}
    else{Replace("calm cafe.");long current=revision;release.SetResult();await validation;Assert(draft=="calm cafe."&&revision==current&&session!.VerifiedRevision==-1,"Old response overwrote current draft");await ValidateDraft();Assert(session!.VerifiedRevision==session.Revision&&!IsRetainedDraft(g,draft,layout!),"Current validation failed");}
    worker.BeforeDeliveryForControlTest=null;return new{source=info!.Path,draft,revision,session!.VerifiedRevision};
   });
  }
  Assert(Wire.Hash(source)==hash,"Source changed");File.WriteAllText(Path.Combine(folder,"presentation-tests.json"),Wire.Write(new{baseline,tests=rows.Count,failures,rows,scope="Actual WPF controls/shared paste and focus paths; not physical input or clipboard; exact user text/screenshots unavailable"}));Close();
 }
}
