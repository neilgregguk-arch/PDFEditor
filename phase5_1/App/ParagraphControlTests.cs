using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Threading;
using System.Diagnostics;
namespace PdfPrototype;
public sealed partial class EditorWindow
{
 async Task RunParagraphControlTests(int stage,string shared)
 {
  var rows=new List<object>();int failures=0;string folder=auditFolder!;Directory.CreateDirectory(shared);
  void Assert(bool v,string m){if(!v)throw new Exception(m);}
  async Task Pump(){await Dispatcher.InvokeAsync(()=>{},DispatcherPriority.ApplicationIdle);editor.UpdateLayout();await Task.Delay(50);}
  async Task Check(string name,Func<Task<object>> f){try{rows.Add(new{name,status="pass",detail=await f()});}catch(Exception ex){failures++;rows.Add(new{name,status="fail",error=ex.ToString(),draft});}}
  void Replace(string value){editor.SelectAll();InsertDraftText(value);editor.CaretPosition=Position(value.Length);editor.Selection.Select(editor.CaretPosition,editor.CaretPosition);}
  async Task Choose(Region r,int row=0)
  {
   await Open(info!.Path,r.Page,r.Id);var plan=ParagraphLayout.Plan(info!.Region!,draft);double y=r.Top+(plan.Positioned?.Lines[row].Baseline-r.Baseline??row*r.LineHeight)+r.LineHeight/2;
   await SelectRegionAt(r.X+4,y);await Pump();Assert(active&&info!.Region!.Id==r.Id,"Row failed to activate the coherent region");
  }
  string two=string.Join(" ",Enumerable.Repeat("Phase 3 letter",9)),three=string.Join(" ",Enumerable.Repeat("Phase 3 letter",15));
  if(stage==1)
  await Check("generation-1-genuine-Word-wrap-save",async()=>
  {
   await Choose(info!.Regions[2]);Replace(two);await Pump();Assert(layout!.Safe&&layout.Lines.Length==2,"Initial wrap");var result=await ExportTo(Path.Combine(shared,"ui-generation1.pdf"));Assert(result?.Safe==true,status.Text);return result!;
  });
  if(stage is 2 or 3 or 4)
  {
   var g=info!.Regions.Single(r=>r.Paragraph!=null);string expected=stage==2?two:stage==3?three:"A separate letter.";int expectedRows=stage==2?2:stage==3?3:1;
   await Check("fresh-process-new-source-bound-paragraph",async()=>
   {
    Assert(g.Eligibility=="Editable"&&g.OriginalText==expected&&g.OriginalLines.Length==expectedRows,"Full paragraph not rediscovered");Assert(session!.SourceHash==Wire.Hash(info.Path)&&session.History.Count==0&&session.Modified.Length==0,"Old session/recovery attached");
    var timings=new List<double>();for(int row=0;row<expectedRows;row++){long t=Stopwatch.GetTimestamp();await Choose(g,row);timings.Add(Stopwatch.GetElapsedTime(t).TotalMilliseconds);Assert(draft==expected&&ActiveKey.EndsWith(g.Id)&&positionedInk.CaretRow==row,"Click did not map to full paragraph row");}
    return new{source=info.Path,sourceHash=session.SourceHash,paragraph=g.Paragraph,rows=expectedRows,activationMs=timings,pid=Environment.ProcessId,recoveryStore=recovery};
   });
   if(stage is 2 or 3)
   await Check("reopened-caret-selection-four-zooms-and-navigation",async()=>
   {
    await Choose(g);var plan=PositionLayout.Plan(g,draft).Positioned!;double max=0;
    foreach(int z in new[]{0,1,2,3}){zoom.SelectedIndex=z;await Pump();for(int i=0;i<=draft.Length;i++){positionCaretRow=null;editor.CaretPosition=Position(i);UpdatePositionedSelection();var desired=PositionLayout.Caret(g,draft,i);var actual=positionedInk.TranslatePoint(new Point((positionedInk.CaretOriginPt-g.X)*Dip,(positionedInk.CaretTopPt-g.Top)*Dip),page);max=Math.Max(max,Math.Max(Math.Abs(actual.X/Dip-desired.X),Math.Abs(actual.Y/Dip-desired.Y)));Assert(max<=.01,"Reopened visible caret shifted");Assert(PositionLayout.Hit(g,draft,desired.X+.001,desired.Y+g.LineHeight/2).Index==i,"Logical source-row hit offset differs");}}
    zoom.SelectedIndex=1;await Pump();positionCaretRow=null;editor.CaretPosition=Position(0);EditingCommands.MoveDownByLine.Execute(null,editor);Assert(positionedInk.CaretRow==1,"Down row");EditingCommands.MoveToLineEnd.Execute(null,editor);Assert(positionedInk.CaretRow==1,"End affinity");EditingCommands.MoveToLineStart.Execute(null,editor);Assert(new TextRange(editor.Document.ContentStart,editor.CaretPosition).Text.Length==plan.Lines[1].Start,"Home offset");EditingCommands.MoveUpByLine.Execute(null,editor);EditingCommands.SelectDownByLine.Execute(null,editor);Assert(editor.Selection.Text==draft[..plan.Lines[1].Start],"Shift cross-row selection");
    var start=PositionLayout.Caret(g,draft,3);Assert(BeginPositionSelection(new Point(start.X*Dip,(start.Y+3)*Dip),1,false),"Mapped drag start");var end=PositionLayout.Caret(g,draft,plan.Lines[^1].Start+3);ExtendPositionSelection(new Point((end.X+.001)*Dip,(end.Y+3)*Dip));positionDragging=false;editor.ReleaseMouseCapture();Assert(editor.Selection.Text==draft[3..(plan.Lines[^1].Start+3)],"Mapped drag logical text");await Pump();viewport.ScrollToHome();await Pump();WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"reopened-selection.png"),true);return new{maxVisibleCaretErrorPt=max,zooms=4,dpi=System.Windows.Media.VisualTreeHelper.GetDpi(this)};
   });
   if(stage is 2 or 3)
   await Check("viewport-follows-proposed-caret-at-four-zooms",async()=>
   {
    await Choose(g);var positions=PositionLayout.Plan(g,draft).Positioned!.Lines.Select(l=>l.Start).Append(draft.Length).ToArray();var measured=new List<object>();
    foreach(int z in new[]{0,1,2,3})
    {
     zoom.SelectedIndex=z;await Pump();
     foreach(int n in positions)
     {
      positionCaretRow=null;editor.Selection.Select(Position(n),Position(n));UpdatePositionedSelection();await Pump();
      var point=positionedInk.TranslatePoint(new Point((positionedInk.CaretOriginPt-g.X)*Dip,(positionedInk.CaretTopPt-g.Top)*Dip),viewport);
      Assert(point.X>=-1&&point.X<=viewport.ViewportWidth+2&&point.Y>=-1&&point.Y+g.FontSize*Dip*zoomFactor<=viewport.ViewportHeight+2,$"Proposed caret off viewport at zoom {zoomFactor}, index {n}: {point}");
      measured.Add(new{zoom=zoomFactor,index=n,x=point.X,y=point.Y,viewport.ViewportWidth,viewport.ViewportHeight});
     }
    }
    zoom.SelectedIndex=1;await Pump();return new{measurements=measured,scope="Actual visual viewport coordinates, not only page-relative alignment"};
   });
   await Check("reopened-boundary-delete-insert-undo-redo",async()=>
   {
    await Choose(g);string before=draft;int boundary=expectedRows>1?PositionLayout.Plan(g,draft).Positioned!.Lines[1].Start:3;editor.Selection.Select(Position(boundary),Position(boundary));EditingCommands.Backspace.Execute(null,editor);await Pump();Assert(draft==before.Remove(boundary-1,1),"Backspace boundary");await UndoDocument(false);Assert(draft==before,"Boundary undo");await UndoDocument(true);Assert(draft==before.Remove(boundary-1,1),"Boundary redo");await UndoDocument(false);
    editor.Selection.Select(Position(boundary),Position(boundary));EditingCommands.Delete.Execute(null,editor);await Pump();Assert(draft==before.Remove(boundary,1),"Delete boundary");await UndoDocument(false);
    foreach(int offset in new[]{0,before.Length}){editor.CaretPosition=Position(offset);editor.Selection.Select(editor.CaretPosition,editor.CaretPosition);editor.RaiseEvent(new TextCompositionEventArgs(InputManager.Current.PrimaryKeyboardDevice,new TextComposition(InputManager.Current,editor,"e")){RoutedEvent=TextCompositionManager.TextInputEvent});await Pump();Assert(draft==before.Insert(offset,"e"),"Insertion at endpoint");await UndoDocument(false);Assert(draft==before,"Endpoint undo");}
    return new{boundary,restored=draft,scope="WPF commands and dispatched TextInput; no physical input"};
   });
   if(stage is 2 or 3)
   await Check("reopened-rewrap-and-save-next-generation",async()=>
   {
    await Choose(g);Replace(stage==2?three:"A separate letter.");await Pump();Assert(layout!.Safe&&layout.Lines.Length==(stage==2?3:1),"Rewrap row count");string desired=draft;await UndoDocument(false);Assert(draft==expected,"Rewrap undo");await UndoDocument(true);Assert(draft==desired,"Rewrap redo");var result=await ExportTo(Path.Combine(shared,"ui-generation"+(stage==2?2:3)+".pdf"));Assert(result?.Safe==true,status.Text);WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"reopened-rewrapped.png"),true);return result!;
   });
  }
  if(stage==5)
  await Check("reopened-group-mixed-page-drafts-persist-before-exit",async()=>
  {
   var g=info!.Regions.Single(r=>r.Paragraph!=null&&r.OriginalLines.Length==2);var other=info.Regions.First(r=>r.Eligibility=="Editable"&&r.Id!=g.Id);await Choose(g,1);Replace(three);await Choose(other);Replace("Phase 3 letter");await ChangePage(1);await Choose(info!.Regions[0]);Replace("First working paragraph.");Assert(session!.Modified.Length==3,"Mixed drafts");PersistDraft();var expectation=new{source=session.Source,hash=session.SourceHash,changes=session.Changes(),history=session.History.Count};File.WriteAllText(Path.Combine(shared,"mixed-expected.json"),Wire.Write(expectation));return expectation;
  });
  if(stage==6)
  {
   await Check("exited-process-group-mixed-history-and-recovery",async()=>
   {
    using var expected=System.Text.Json.JsonDocument.Parse(File.ReadAllText(Path.Combine(shared,"mixed-expected.json")));Assert(session!.SourceHash==expected.RootElement.GetProperty("hash").GetString()&&Wire.Write(session.Changes())==expected.RootElement.GetProperty("changes").GetRawText(),"Recovery changes differ");Assert(session.Modified.Length==3&&session.History.Count==expected.RootElement.GetProperty("history").GetInt32(),"Recovery/history lost");
    await UndoDocument(false);await UndoDocument(false);await UndoDocument(false);Assert(session.Modified.Length==0,"Global undo across recovered groups/pages");await UndoDocument(true);await UndoDocument(true);await UndoDocument(true);Assert(session.Modified.Length==3,"Global recovered redo");await ChangePage(-1);var g=info!.Regions.Single(r=>r.Paragraph!=null&&r.OriginalLines.Length==2);await Choose(g,1);Assert(draft==three&&inactiveDrafts.Children.Count>0,"Group switch/return lost state");return new{source=session.Source,hash=session.SourceHash,history=session.History.Count,changes=session.Changes(),pid=Environment.ProcessId};
   });
   await Check("recovered-mixed-groups-combined-export",async()=>
   {var result=await ExportTo(Path.Combine(shared,"ui-mixed-recovered.pdf"));Assert(result?.Safe==true&&session!.Modified.Length==3,status.Text);return result!;});
  }
  File.WriteAllText(Path.Combine(folder,"paragraph-control-tests.json"),Wire.Write(new{stage,tests=rows.Count,failures,rows,pid=Environment.ProcessId,source=info?.Path,scope="actual WPF controls/routed events/shared mouse mapping; no hardware/file-picker automation"}));WriteAudit();Close();
 }
}
