using System.Windows;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Controls;
using System.Windows.Threading;
using System.Diagnostics;
namespace PdfPrototype;
public sealed partial class EditorWindow
{
 async Task RunWrapControlTests()
 {
  string folder=auditFolder??work;var rows=new List<object>();int failures=0;
  void Assert(bool v,string m){if(!v)throw new Exception(m);}
  async Task Pump(){await Dispatcher.InvokeAsync(()=>{},DispatcherPriority.ApplicationIdle);editor.UpdateLayout();await Task.Delay(80);}
  async Task Check(string name,Func<Task<object>> f){try{rows.Add(new{name,status="pass",detail=await f()});}catch(Exception e){failures++;rows.Add(new{name,status="fail",error=e.ToString(),draft});}}
  async Task Choose(Region r){await SelectRegionAt(r.X+3,r.Baseline-3);await Pump();Assert(active&&info!.Region?.Id==r.Id,"Activation failed");}
  void Replace(string text){editor.SelectAll();InsertDraftText(text);}
  string source=Path.Combine(AppContext.BaseDirectory,"corpus","11-word-letter.pdf"),two=string.Join(" ",Enumerable.Repeat("Phase 3 letter",9)),many=string.Join(" ",Enumerable.Repeat("Phase 3 letter",20));string? saved=null;
  await Check("wrap-typing-history-and-shared-presentation",async()=>
  {
   await Open(source);await Choose(info!.Regions[0]);Replace(info.Region!.OriginalText);int before=session!.History.Count;Replace(two);await Pump();Assert(draft==two&&!draft.Contains('\n')&&layout!.Lines.Length==2,"Soft wrap changed logical text");Assert(session.History.Count==before+1,"Wrap added history entries");await UndoDocument(false);Assert(draft=="Phase 3 Office letter","Undo wrap");await UndoDocument(true);Assert(draft==two&&layout!.Lines.Length==2,"Redo wrap");await ValidateDraft();Assert(verifiedRevision==revision,"Candidate not verified");Assert(positionedInk.Height>info.Region!.LineHeight*Dip+12,"Live layer not multi-line");WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"wrapped-Word.png"),true);var result=await ExportTo(Path.Combine(folder,"wrap-two-ui.pdf"));Assert(result?.Safe==true,status.Text);saved=result!.Destination;return result!;
  });
  await Check("continuous-routed-typing-through-soft-wrap",async()=>
  {
   await Choose(info!.Regions[0]);Replace(info.Region!.OriginalText);Activate();editor.Focus();await Pump();editor.SelectAll();int before=session!.History.Count;long requests=worker.Calls;var timings=new List<double>();
   for(int i=0;i<two.Length;i++){long t=Stopwatch.GetTimestamp();editor.RaiseEvent(new TextCompositionEventArgs(InputManager.Current.PrimaryKeyboardDevice,new TextComposition(InputManager.Current,editor,two[i].ToString())){RoutedEvent=TextCompositionManager.TextInputEvent});await Dispatcher.InvokeAsync(()=>{},DispatcherPriority.ApplicationIdle);timings.Add(Stopwatch.GetElapsedTime(t).TotalMilliseconds);Assert(draft==two[..(i+1)],"Typing lost or duplicated a character at "+i+"; focus="+editor.IsKeyboardFocusWithin+"; enabled="+editor.IsEnabled+"; control="+Text());}
   Assert(session.History.Count==before+two.Length&&worker.Calls==requests,"Soft wrap added history or synchronous worker calls");long immediateRequests=worker.Calls-requests;await Pump();Assert(layout!.Lines.Length==2&&draft==two,"Continuous wrap layout differs");var result=await ExportTo(Path.Combine(folder,"wrap-continuous-ui.pdf"));Assert(result?.Safe==true,status.Text);return new{result,characters=two.Length,medianInputMs=timings.Order().ElementAt(timings.Count/2),maxInputMs=timings.Max(),immediateWorkerRequests=immediateRequests,scope="WPF routed TextInput per character; no physical keyboard"};
  });
  await Check("click-inactive-second-wrapped-line",async()=>
  {
   await Choose(info!.Regions[0]);Replace(two);await Pump();var title=info!.Region!;var plan=PositionLayout.Plan(title,two).Positioned!;await Choose(info.Regions[2]);Assert(inactiveDrafts.Children.Count>0,"No inactive wrap");var second=plan.Lines[1];await SelectRegionAt(title.X+2,title.Top+second.Baseline-title.Baseline+3);await Pump();Assert(active&&info!.Region!.Id==title.Id&&positionedInk.CaretRow==1,"Inactive second-line click did not reactivate its draft");return new{region=info!.Region!.Id,caretRow=positionedInk.CaretRow,draft};
  });
  await Check("caret-selection-navigation-four-zooms",async()=>
  {
   await Choose(info!.Regions[0]);Replace(two);await Pump();var r=info!.Region!;var plan=PositionLayout.Plan(r,draft).Positioned!;var measurements=new List<object>();double max=0;
   foreach(int z in new[]{0,1,2,3}){zoom.SelectedIndex=z;await Pump();for(int i=0;i<=draft.Length;i++){positionCaretRow=null;editor.CaretPosition=Position(i);UpdatePositionedSelection();var expected=PositionLayout.Caret(r,draft,i);var actual=positionedInk.TranslatePoint(new Point((positionedInk.CaretOriginPt-r.X)*Dip,(positionedInk.CaretTopPt-r.Top)*Dip),page);double error=Math.Max(Math.Abs(actual.X/Dip-expected.X),Math.Abs(actual.Y/Dip-expected.Y));max=Math.Max(max,error);Assert(error<=.01,"Visible caret differs");var hit=PositionLayout.Hit(r,draft,expected.X+.001,expected.Y+r.LineHeight/2);Assert(hit.Index==i,"Hit logical offset "+i+" differs at wrap");}measurements.Add(new{zoom=zoomFactor,maxVisibleCaretErrorPt=max});}
   zoom.SelectedIndex=1;positionCaretRow=null;editor.CaretPosition=Position(0);EditingCommands.MoveDownByLine.Execute(null,editor);Assert(positionedInk.CaretRow==1,"Down did not follow proposed row");EditingCommands.MoveToLineEnd.Execute(null,editor);Assert(positionedInk.CaretRow==1&&new TextRange(editor.Document.ContentStart,editor.CaretPosition).Text.Length==draft.Length,"End row");EditingCommands.MoveToLineStart.Execute(null,editor);Assert(new TextRange(editor.Document.ContentStart,editor.CaretPosition).Text.Length==plan.Lines[1].Start,"Home row");EditingCommands.MoveUpByLine.Execute(null,editor);Assert(positionedInk.CaretRow==0,"Up row");EditingCommands.SelectDownByLine.Execute(null,editor);Assert(editor.Selection.Text==draft[..plan.Lines[1].Start],"Shift selection across wrap");
   double x=PositionLayout.Caret(r,draft,3).X;Assert(BeginPositionSelection(new Point(x*Dip,(r.Top+3)*Dip),1,false),"Mapped mouse start");var end=PositionLayout.Caret(r,draft,plan.Lines[1].Start+4);ExtendPositionSelection(new Point((end.X+.001)*Dip,(end.Y+3)*Dip));positionDragging=false;editor.ReleaseMouseCapture();Assert(editor.Selection.Text==draft[3..(plan.Lines[1].Start+4)],"Drag selection logical span");await Pump();WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"wrapped-selection.png"),true);return new{measurements,maxVisibleCaretErrorPt=max,dpi=System.Windows.Media.VisualTreeHelper.GetDpi(this)};
  });
  await Check("delete-soft-boundary-keeps-exact-text",async()=>
  {
   await Choose(info!.Regions[0]);Replace(two);await Pump();int boundary=layout!.Positioned!.Lines[1].Start;string expected=draft.Remove(boundary-1,1);editor.Selection.Select(Position(boundary),Position(boundary));EditingCommands.Backspace.Execute(null,editor);Assert(draft==expected&&!draft.Contains('\n'),"Boundary delete added/removed unexpected characters");await UndoDocument(false);Assert(draft==two,"Boundary deletion undo");return new{boundary,restored=draft};
  });
  await Check("multi-line-draft-switches-pages-and-global-history",async()=>
  {
   await Open(Path.Combine(AppContext.BaseDirectory,"document-corpus","mixed-multipage.pdf"));var rs=info!.Regions;await Choose(rs[0]);Replace(rs[0].OriginalText);await Choose(rs[2]);Replace(rs[2].OriginalText);await ChangePage(1);await Choose(info!.Regions[0]);Replace(info.Region!.OriginalText);await ChangePage(-1);await Choose(rs[0]);Replace(two);await Choose(rs[2]);Replace(two);Assert(layout!.Lines.Length==2,"Second paragraph not wrapped");await ChangePage(1);await Choose(info!.Regions[0]);Replace("First changed working paragraph.");await UndoDocument(false);await UndoDocument(false);Assert(info!.Page==0&&draft==rs[2].OriginalText,"Chronological wrap undo");await UndoDocument(true);await UndoDocument(true);Assert(session!.Modified.Length==3,"Redo drafts");await ChangePage(-1);await Choose(info!.Regions[0]);Assert(draft==two&&inactiveDrafts.Children.Count>0,"Inactive wrapped draft lost");var result=await ExportTo(Path.Combine(folder,"wrap-mixed-ui.pdf"));Assert(result?.Safe==true,status.Text);return result!;
  });
  await Check("vertical-and-hard-break-failure-keeps-all-drafts",async()=>
  {
   Replace(string.Join(" ",Enumerable.Repeat("Phase 3 letter",16)));await Pump();Assert(!layout!.Safe,"Vertical overflow accepted");var result=await ExportTo(Path.Combine(folder,"must-not-save-wrap.pdf"));Assert(result?.Safe==false&&session!.Modified.Length==3,"Failure discarded another draft");Replace("Phase 3\nletter");await Pump();Assert(!layout!.Safe&&draft.Contains('\n'),"Hard break silently normalized");PersistDraft();var recovered=DocumentSession.Restore(SessionRecoveryPath(session!.SourceHash),session.SourceHash);Assert(recovered.Regions[ActiveKey].Text==draft&&recovered.Modified.Length==3,"Recovery lost unsafe text");WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"wrap-warning.png"),true);return new{result,changes=session.Changes()};
  });
  await Check("rediscovered-whole-paragraph-reedit-with-validated-ownership",async()=>
  {
   Assert(saved!=null,"No wrapped export");await Open(saved!);var r=info!.Regions.First(r=>r.Eligibility=="Editable"&&r.Paragraph!=null&&r.OriginalText==two);await Choose(r);Replace("Phace"+r.OriginalText[5..]);var result=await ExportTo(Path.Combine(folder,"wrap-second-ui.pdf"));Assert(result?.Safe==true,status.Text);return new{result,scope="Complete paragraph rediscovered through validated embedded declaration; no proximity merging"};
  });
  await Check("individually-valid-wrapped-regions-conflict-retains-both",async()=>
  {
   await Open(Path.Combine(AppContext.BaseDirectory,"wrap-corpus","combined-collision.pdf"));var a=info!.Regions.First(r=>r.OriginalText.StartsWith("A separate"));var b=info.Regions.First(r=>r.OriginalText=="..");await Choose(a);Replace(string.Join(" ",Enumerable.Repeat("gyp",35)));var box=b.ObservedBounds!;await SelectRegionAt(box.X+box.Width/2,box.Y+box.Height/2);Assert(active&&info!.Region!.Id==b.Id,"Small second region not selected");Replace(string.Join(" ",Enumerable.Repeat("fictional letter",12)));var result=await ExportTo(Path.Combine(folder,"must-not-save-collision.pdf"));Assert(result?.Safe==false&&result.Regions.Length==2&&session!.Modified.Length==2&&!File.Exists(Path.Combine(folder,"must-not-save-collision.pdf")),"Combined wrap collision lost a draft or exported");return new{result,changes=session!.Changes()};
  });
  await Check("Calibri-wrapped-caret-and-selection",async()=>
  {
   await Open(Path.Combine(AppContext.BaseDirectory,"font-corpus","Word-Calibri.pdf"));await Choose(info!.Regions[0]);string text=string.Join(" ",Enumerable.Repeat("cafe calm.",12));Replace(text);await Pump();var r=info.Region!;var p=PositionLayout.Plan(r,text).Positioned!;Assert(layout!.Safe&&p.Lines.Length==2,"Calibri wrap restricted");double max=0;
   foreach(int z in new[]{0,1,2,3}){zoom.SelectedIndex=z;await Pump();foreach(int n in new[]{0,p.Lines[1].Start-1,p.Lines[1].Start,p.Lines[1].Start+3,text.Length}){positionCaretRow=null;editor.CaretPosition=Position(n);UpdatePositionedSelection();var expected=PositionLayout.Caret(r,text,n);var actual=positionedInk.TranslatePoint(new Point((positionedInk.CaretOriginPt-r.X)*Dip,(positionedInk.CaretTopPt-r.Top)*Dip),page);max=Math.Max(max,Math.Max(Math.Abs(actual.X/Dip-expected.X),Math.Abs(actual.Y/Dip-expected.Y)));}}
   Assert(max<=.01,"Calibri visible caret differs");zoom.SelectedIndex=1;editor.Selection.Select(Position(3),Position(p.Lines[1].Start+4));Assert(editor.Selection.Text==text[3..(p.Lines[1].Start+4)],"Calibri selected logical text differs");await Pump();WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"Calibri-wrapped-selection.png"),true);var result=await ExportTo(Path.Combine(folder,"Calibri-wrap-ui.pdf"));Assert(result?.Safe==true,status.Text);return new{result,maxVisibleCaretErrorPt=max};
  });
  await Check("three-plus-lines-and-input-cost",async()=>
  {
   await Open(source);await Choose(info!.Regions[0]);Replace(info.Region!.OriginalText);await Choose(info.Regions[2]);Replace(many);await Pump();Assert(layout!.Safe&&layout.Lines.Length>=3,"Multi-line source not safe");var result=await ExportTo(Path.Combine(folder,"wrap-many-ui.pdf"));Assert(result?.Safe==true,status.Text);WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"wrap-many.png"),true);
   long calls=worker.Calls;var input=new List<double>();var calculation=new List<double>();for(int i=0;i<30;i++){long t=Stopwatch.GetTimestamp();Replace(i%2==0?many:"A separate letter.");input.Add(Stopwatch.GetElapsedTime(t).TotalMilliseconds);t=Stopwatch.GetTimestamp();PositionLayout.Plan(info.Region!,draft);calculation.Add(Stopwatch.GetElapsedTime(t).TotalMilliseconds);}Assert(worker.Calls==calls,"Input blocked on worker");return new{result,operations=30,medianInputMs=input.Order().ElementAt(15),maxInputMs=input.Max(),medianCalculationMs=calculation.Order().ElementAt(15),immediateWorkerRequests=worker.Calls-calls};
  });
  File.WriteAllText(Path.Combine(folder,"wrap-control-tests.json"),Wire.Write(new{tests=rows.Count,failures,rows,scope="actual WPF controls/routed commands/shared mouse mapping; no hardware or file-picker automation"}));Status($"Wrap controls: {rows.Count-failures}/{rows.Count} passed.",failures>0);WriteAudit();
 }
}
