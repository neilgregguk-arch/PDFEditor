using System.Windows;
using System.Windows.Documents;
using System.Windows.Threading;
namespace PdfPrototype;
public sealed partial class EditorWindow
{
 async Task RunSessionControlTests()
 {
  var results=new List<object>();int failures=0;string folder=auditFolder??work;
  void Assert(bool b,string m){if(!b)throw new Exception(m);}
  async Task Check(string name,Func<Task<object>> f){try{results.Add(new{name,status="pass",detail=await f()});}catch(Exception e){failures++;results.Add(new{name,status="fail",error=e.ToString(),draft,summary=session?.Summary()});}}
  async Task Pump(){await Dispatcher.InvokeAsync(()=>{},DispatcherPriority.ApplicationIdle);await Task.Delay(80);}
  void Replace(string text){editor.SelectAll();InsertDraftText(text);}
  string source=Path.Combine(AppContext.BaseDirectory,"document-corpus","multi-natural.pdf");string? saved=null;
  Region[] areas=[];
  async Task Choose(Region r){await SelectRegionAt(r.X+3,r.Baseline-3);await Pump();Assert(active&&info?.Region?.Id==r.Id,"Region did not activate");}
  await Check("A-switch-keeps-two-drafts-and-inactive-presentation",async()=>
  {
   await Open(source);areas=info!.Regions.Where(r=>r.Eligibility=="Editable").ToArray();Assert(areas.Length>=3,"Three regions not discovered");await Choose(areas[0]);Replace("First changed working paragraph.");await Pump();await Choose(areas[1]);Replace("Second changed working paragraph.");await Pump();await Choose(areas[0]);Assert(draft=="First changed working paragraph."&&session!.Modified.Length==2,"Switch lost drafts");Assert(inactiveDrafts.Children.Count>0,"Inactive changes invisible");WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"two-drafts.png"),true);return session!.Changes();
  });
  await Check("B-three-region-global-history-redo-invalidation",async()=>
  {
   await Choose(areas[2]);Replace("Third changed working paragraph.");await Pump();Assert(!editor.IsUndoEnabled,"Independent native undo still enabled");await UndoDocument(false);Assert(draft==areas[2].OriginalText,"Undo C");await UndoDocument(false);Assert(draft==areas[1].OriginalText,"Undo B");await UndoDocument(false);Assert(draft==areas[0].OriginalText,"Undo A");
   await UndoDocument(true);await UndoDocument(true);await UndoDocument(true);Assert(session!.Modified.Length==3&&draft=="Third changed working paragraph.","Redo order");await UndoDocument(false);Replace("Third revised working paragraph.");Assert(!session.CanRedo,"New edit retained stale redo");return new{session.Cursor,entries=session.History.Count,session.Revision};
  });
  await Check("C-H-one-combined-multipage-save",async()=>
  {
   await ChangePage(1);var r=info!.Regions.First(x=>x.Eligibility=="Editable");await Choose(r);Replace("Another page has changed text.");await Pump();await ValidateDraft();Assert(verifiedRevision==revision,"Combined preview failed: "+status.Text);saved=Path.Combine(folder,"combined-ui.pdf");var result=await ExportTo(saved);Assert(result?.Safe==true&&session!.Modified.Length==4,"Combined export failed/cleared drafts: "+status.Text);return result!;
  });
  await Check("G-invalid-region-does-not-block-switch-or-partially-save",async()=>
  {
   await ChangePage(-1);await Choose(areas[0]);Replace("First changed working paragraph. \u2603");await Pump();await Choose(areas[1]);Assert(draft=="Second changed working paragraph.","Valid draft lost");var result=await ExportTo(Path.Combine(folder,"must-not-partial.pdf"));Assert(result?.Safe==false&&!File.Exists(Path.Combine(folder,"must-not-partial.pdf"))&&session!.Modified.Length==4,"Partial export or lost draft");await Choose(areas[0]);Assert(draft.EndsWith('\u2603'),"Invalid draft lost");Replace("First changed working paragraph.");return session!.Changes();
  });
  await Check("I-session-recovery-history-and-source-binding",async()=>
  {
   PersistDraft();var restored=DocumentSession.Restore(SessionRecoveryPath(session!.SourceHash),session.SourceHash);Assert(restored.Modified.Length==4&&restored.Cursor==session.Cursor,"Recovery omitted drafts/history");session=null;await Open(source);Assert(session!.Modified.Length==4&&draft=="First changed working paragraph.","Window did not recover");await UndoDocument(false);Assert(draft.EndsWith('\u2603'),"Recovered undo unavailable");await UndoDocument(true);return new{session.Modified.Length,session.Cursor};
  });
  await Check("J-failure-protects-source-existing-output-and-all-drafts",async()=>
  {
   string before=Wire.Write(session!.Changes()),hash=Wire.Hash(source);var result=await ExportTo(source);Assert(result==null&&Wire.Hash(source)==hash&&before==Wire.Write(session.Changes()),"Source failure lost drafts");result=await ExportTo(saved!);Assert(result==null&&before==Wire.Write(session.Changes()),"Existing destination overwritten");return new{drafts=session.Modified.Length};
  });
  await Check("K-reopen-multi-output-and-second-combined-edit",async()=>
  {
   Assert(saved!=null,"No output");await Open(saved!);var rs=info!.Regions.Where(r=>r.Eligibility=="Editable").ToArray();Assert(rs.Length>=3,"Rediscovery failed");await Choose(rs[0]);Replace("First changed working paragraph again.");await Choose(rs[1]);Replace("Second changed working paragraph again.");var v=await ExportTo(Path.Combine(folder,"combined-ui-second.pdf"));Assert(v?.Safe==true,"Second combined generation failed: "+status.Text);return v!;
  });
  await Check("D-two-Word-areas-and-zoom-keeps-inactive-draft",async()=>
  {
   await Open(Path.Combine(AppContext.BaseDirectory,"corpus","11-word-letter.pdf"));var rs=info!.Regions;await Choose(rs[0]);Replace("Phace 3 Office letter");await Choose(rs[2]);Replace(rs[2].OriginalText.Replace("should","chould"));
   foreach(int z in new[]{0,1,2,3}){zoom.SelectedIndex=z;await Pump();Assert(session!.Modified.Length==2&&inactiveDrafts.Children.Count>0,"Zoom lost Word drafts");}
   zoom.SelectedIndex=1;await Choose(rs[0]);Assert(draft=="Phace 3 Office letter","Word return lost draft");var result=await ExportTo(Path.Combine(folder,"combined-word-ui.pdf"));Assert(result?.Safe==true,"Word combined UI export failed: "+status.Text);return result!;
  });
  await Check("E-mixed-strategy-through-same-inline-controls",async()=>
  {
   await Open(Path.Combine(AppContext.BaseDirectory,"document-corpus","mixed.pdf"));var p=info!.Regions.First(r=>r.Positioned!=null);var n=info.Regions.First(r=>r.Positioned==null&&r.Eligibility=="Editable");await Choose(p);Replace("Phace 3 Office letter");await Choose(n);Replace("Neutral paragraph retains its original font.");var result=await ExportTo(Path.Combine(folder,"combined-mixed-ui.pdf"));Assert(result?.Safe==true,"Mixed UI export failed: "+status.Text);return result!;
  });
  await Check("F-collision-warning-preserves-both-working-drafts",async()=>
  {
   await Open(Path.Combine(AppContext.BaseDirectory,"document-corpus","collision.pdf"));var rs=info!.Regions;await Choose(rs[0]);Replace("alpha area.\nalpha area.\nalpha area.");var b=rs[1].ObservedBounds!;await SelectRegionAt(b.X+b.Width/2,b.Y+b.Height/2);Assert(active&&info.Region?.Id==rs[1].Id,"Small second area not selectable");Replace("alpha area.");
   var result=await ExportTo(Path.Combine(folder,"must-not-collide.pdf"));Assert(result?.Safe==false&&result.Regions.Length==2&&session!.Modified.Length==2&&!File.Exists(Path.Combine(folder,"must-not-collide.pdf")),"Collision exported or dropped a draft");return new{result,changes=session!.Changes()};
  });
  await Check("typing-burst-keeps-worker-off-the-immediate-input-path",async()=>
  {
   await Open(source);await Choose(info!.Regions[0]);long before=worker.Calls;var costs=new List<double>();
   for(int i=0;i<30;i++){var start=System.Diagnostics.Stopwatch.GetTimestamp();Replace("First changed working paragraph "+i+".");costs.Add(System.Diagnostics.Stopwatch.GetElapsedTime(start).TotalMilliseconds);}
   Assert(worker.Calls==before,"Immediate keystroke processing started a worker render");Replace("First changed working paragraph.");return new{operations=costs.Count,medianHandlerMs=costs.Order().ElementAt(costs.Count/2),maxHandlerMs=costs.Max(),workerRequestsDuringBurst=worker.Calls-before,scope="synchronous text insertion/change handler, not physical or end-to-end frame latency"};
  });
  await Check("changed-source-reopen-keeps-old-recovery-without-applying-it",async()=>
  {
   string path=Path.Combine(folder,"external-source-change.pdf");File.WriteAllBytes(path,File.ReadAllBytes(source).Concat(System.Text.Encoding.ASCII.GetBytes("\n% unique initial source\n")).ToArray());await Open(path);await Choose(info!.Regions[0]);Replace("First external source working draft.");PersistDraft();string previous=session!.SourceHash;string store=SessionRecoveryPath(previous);string recoveryHash=Wire.Hash(store);
   using(var stream=new FileStream(path,FileMode.Append,FileAccess.Write))stream.Write(System.Text.Encoding.ASCII.GetBytes("\n% externally changed source\n"));await Open(path,deliberate:true);Assert(session!.SourceHash!=previous&&session.Modified.Length==0&&Wire.Hash(store)==recoveryHash,"Stale recovery applied or discarded");return new{oldSourceHash=previous,newSourceHash=session.SourceHash,oldRecoveryPreserved=true};
  });
  File.WriteAllText(Path.Combine(folder,"session-control-tests.json"),Wire.Write(new{scope="actual WPF controls/shared click/editor/document history/atomic export; not physical input",tests=results.Count,failures,results}));Status($"Session control tests: {results.Count-failures}/{results.Count} passed.",failures>0);WriteAudit();
 }
}
