using System.Windows;
using System.Windows.Documents;
using System.Windows.Threading;
using System.Diagnostics;
namespace PdfPrototype;
public sealed partial class EditorWindow
{
 async Task RunInsertionControlTests()
 {
  string folder=auditFolder??work;var rows=new List<object>();int failures=0;
  void Assert(bool b,string m){if(!b)throw new Exception(m);}
  async Task Pump(){await Dispatcher.InvokeAsync(()=>{},DispatcherPriority.ApplicationIdle);editor.UpdateLayout();await Task.Delay(60);}
  async Task Check(string name,Func<Task<object>> f){try{rows.Add(new{name,status="pass",detail=await f()});}catch(Exception ex){failures++;rows.Add(new{name,status="fail",error=ex.ToString(),draft,summary=session?.Summary()});}}
  async Task Choose(Region r){await SelectRegionAt(r.X+3,r.Baseline-3);await Pump();Assert(active&&info!.Region?.Id==r.Id,"Region activation failed");}
  void Replace(string text){editor.SelectAll();InsertDraftText(text);}
  string source=Path.Combine(AppContext.BaseDirectory,"corpus","11-word-letter.pdf");string? first=null;
  await Check("A-B-C-D-E-native-insertion-deletion-selection",async()=>
  {
   await Open(source);await Choose(info!.Regions[0]);Replace(info.Region!.OriginalText);editor.CaretPosition=Position(4);InsertDraftText("s");Assert(draft=="Phasse 3 Office letter","Middle insertion");
   editor.Selection.Select(Position(0),Position(6));InsertDraftText("Phase");Assert(draft=="Phase 3 Office letter","Range deletion");
   editor.Selection.Select(Position(8),Position(14));InsertDraftText("letter");Assert(draft=="Phase 3 letter letter","Different word replacement");
   editor.Selection.Select(Position(8),Position(15));System.Windows.Documents.EditingCommands.Delete.Execute(null,editor);Assert(draft=="Phase 3 letter","Whole word delete");
   await UndoDocument(false);Assert(draft=="Phase 3 letter letter","Global undo");await UndoDocument(true);Assert(draft=="Phase 3 letter","Global redo");
   var result=await ExportTo(Path.Combine(folder,"insertion-selection-ui.pdf"));Assert(result?.Safe==true,status.Text);return result!;
  });
  await Check("L-proposed-caret-hit-and-native-caret-four-zooms",async()=>
  {
   await Open(source);await Choose(info!.Regions[0]);Replace("Phasse 3 Office letter letter");await Pump();var r=info.Region!;var proposed=PositionLayout.Plan(r,draft).Positioned!;var measures=new List<object>();double max=0;
   foreach(int z in new[]{0,1,2,3}){zoom.SelectedIndex=z;await Pump();for(int i=0;i<=draft.Length;i++){editor.CaretPosition=Position(i);var rect=editor.CaretPosition.GetCharacterRect(LogicalDirection.Forward);double expected=PositionLayout.CaretX(r,draft,i),error=(System.Windows.Controls.Canvas.GetLeft(editor)+rect.X)/Dip-expected;max=Math.Max(max,Math.Abs(error));var hit=ParagraphLayout.Hit(r,draft,expected+.01,r.Baseline-3);Assert(hit.Index==i,"Proposed hit index mismatch");measures.Add(new{zoom=zoomFactor,index=i,nativeCaretErrorPt=error});}}
   zoom.SelectedIndex=1;await Pump();WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"insertion-caret.png"),true);Assert(max<.75,"Native caret error exceeds .75 pt: "+max);var result=await ExportTo(Path.Combine(folder,"insertion-caret-ui.pdf"));Assert(result?.Safe==true,status.Text);first=result!.Destination;
   return new{maxNativeCaretErrorPt=max,measurements=measures,dpi=System.Windows.Media.VisualTreeHelper.GetDpi(this),result};
  });
  await Check("L-Arial-Calibri-caret-and-selection-geometry",async()=>
  {
   var samples=new List<object>();
   foreach(string font in new[]{"Arial","Calibri"})
   {
    await Open(Path.Combine(AppContext.BaseDirectory,"font-corpus","Word-"+font+".pdf"));await Choose(info!.Regions[0]);Replace("cafe calm. cafe calm. cafe");await Pump();var r=info.Region!;double max=0;var measurements=new List<object>();
    foreach(int z in new[]{0,1,2,3}){zoom.SelectedIndex=z;await Pump();for(int n=0;n<=draft.Length;n++){editor.CaretPosition=Position(n);var rect=editor.CaretPosition.GetCharacterRect(LogicalDirection.Forward);double error=(System.Windows.Controls.Canvas.GetLeft(editor)+rect.X)/Dip-PositionLayout.CaretX(r,draft,n);max=Math.Max(max,Math.Abs(error));measurements.Add(new{zoom=zoomFactor,index=n,errorPt=error});}}
    editor.Selection.Select(Position(5),Position(9));Assert(editor.Selection.Text=="calm","Selection offset mismatch");Assert(editor.CaretBrush==System.Windows.Media.Brushes.Transparent,"Native caret still visible");
    double displayMax=0;foreach(int z in new[]{0,1,2,3}){zoom.SelectedIndex=z;await Pump();for(int n=0;n<=draft.Length;n++){editor.CaretPosition=Position(n);double desired=PositionLayout.CaretX(r,draft,n);double observed=positionedInk.TranslatePoint(new Point((positionedInk.CaretOriginPt-r.X)*Dip,0),page).X/Dip;displayMax=Math.Max(displayMax,Math.Abs(observed-desired));}}
    Assert(displayMax<=.01,"Visible caret differs from proposed PDF positions");
    double a=PositionLayout.CaretX(r,draft,5),b=PositionLayout.CaretX(r,draft,9);Assert(BeginPositionSelection(new Point((a+.01)*Dip,(r.Top+3)*Dip),1,false),"Mapped mouse path refused");ExtendPositionSelection(new Point((b+.01)*Dip,(r.Top+3)*Dip));positionDragging=false;editor.ReleaseMouseCapture();Assert(editor.Selection.Text=="calm","Mapped drag selection differs");
    samples.Add(new{font,maxHiddenNativeCaretErrorPt=max,maxVisibleCaretErrorPt=displayMax,measurements});await Pump();WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,font+"-position-selection.png"),true);
   }
   zoom.SelectedIndex=1;return new{samples,dpi=System.Windows.Media.VisualTreeHelper.GetDpi(this),scope="actual workstation DPI; no OS display-scale changes"};
  });
  await Check("F-G-M-blocked-drafts-and-other-region-history-recovery",async()=>
  {
   await Open(source);var rs=info!.Regions;await Choose(rs[0]);Replace("Phase 3 Office letter"+new string('e',100));await Pump();Assert(layout?.Safe==false,"Overflow accepted");await Choose(rs[2]);Replace(rs[2].OriginalText.Replace("should ",""));await Choose(rs[0]);Assert(draft.Length>100&&session!.Modified.Length==2,"Overflow draft lost after switch");
   var rejected=await ExportTo(Path.Combine(folder,"must-not-partially-save.pdf"));Assert(rejected?.Safe==false&&!File.Exists(Path.Combine(folder,"must-not-partially-save.pdf")),"Partial save");Replace("Phase 3 Office letter\u2603");await Pump();Assert(layout?.Safe==false&&draft.EndsWith('\u2603'),"Unmapped draft lost");PersistDraft();var restored=DocumentSession.Restore(SessionRecoveryPath(session!.SourceHash),session.SourceHash);Assert(restored.Modified.Length==2&&restored.Regions[ActiveKey].Text==draft,"Recovery lost blocked text");WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"insertion-blocked.png"),true);return new{changes=session.Changes(),rejected};
  });
  await Check("H-mixed-pages-switch-global-undo-export",async()=>
  {
   await Open(Path.Combine(AppContext.BaseDirectory,"document-corpus","mixed-multipage.pdf"));var rs=info!.Regions;await Choose(rs[0]);Replace("Phasse 3 Office letter");await Choose(rs[2]);Replace(rs[2].OriginalText.Replace("should ",""));await ChangePage(1);await Choose(info!.Regions.First(r=>r.Eligibility=="Editable"));Replace("First changed working paragraph.");
   await UndoDocument(false);Assert(info!.Page==1,"Natural undo page");await UndoDocument(false);Assert(info.Page==0&&draft==rs[2].OriginalText,"Deletion undo not chronological");await UndoDocument(true);await UndoDocument(true);Assert(session!.Modified.Length==3&&info.Page==1,"Mixed redo");var result=await ExportTo(Path.Combine(folder,"insertion-mixed-ui.pdf"));Assert(result?.Safe==true,status.Text);return result!;
  });
  await Check("J-second-generation-ui",async()=>
  {
   Assert(first!=null,"No first output");await Open(first!);var r=info!.Regions.First(r=>r.OriginalText=="Phasse 3 Office letter letter");Assert(r.Eligibility=="Editable","Rediscovery gated");await Choose(r);Replace("Phasse 3 Office letter");var result=await ExportTo(Path.Combine(folder,"insertion-second-ui.pdf"));Assert(result?.Safe==true,status.Text);return result!;
  });
  await Check("K-empty-line-preserves-other-objects",async()=>
  {
   await Open(source);await Choose(info!.Regions[0]);Replace("Phase 3 Office letter");Replace("");var result=await ExportTo(Path.Combine(folder,"insertion-empty-ui.pdf"));Assert(result?.Safe==true,status.Text);await UndoDocument(false);Assert(draft=="Phase 3 Office letter","Empty-line undo lost original");return result!;
  });
  await Check("input-and-position-calculation-cost",async()=>
  {
   await Open(source);await Choose(info!.Regions[0]);long calls=worker.Calls;var input=new List<double>();var calc=new List<double>();for(int i=0;i<30;i++){long start=Stopwatch.GetTimestamp();Replace("Phase 3 Office letter"+new string('e',i+1));input.Add(Stopwatch.GetElapsedTime(start).TotalMilliseconds);start=Stopwatch.GetTimestamp();PositionLayout.Plan(info.Region!,draft);calc.Add(Stopwatch.GetElapsedTime(start).TotalMilliseconds);}
   Assert(worker.Calls==calls,"Input requested worker immediately");return new{operations=30,medianInputMs=input.Order().ElementAt(15),maxInputMs=input.Max(),medianCalculationMs=calc.Order().ElementAt(15),workerRequests=worker.Calls-calls,scope="synchronous programmatic WPF input and shared model; no physical input"};
  });
  File.WriteAllText(Path.Combine(folder,"insertion-control-tests.json"),Wire.Write(new{tests=rows.Count,failures,rows,scope="actual WPF controls/routed commands; no physical input or file picker"}));Status($"Insertion controls: {rows.Count-failures}/{rows.Count} passed.",failures>0);WriteAudit();
 }
}
