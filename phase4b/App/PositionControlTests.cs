using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Threading;
namespace PdfPrototype;
public sealed partial class EditorWindow
{
 async Task RunPositionControlTests()
 {
  string folder=auditFolder??work;var results=new List<object>();int failures=0;
  void Assert(bool b,string m){if(!b)throw new Exception(m);}
  async Task Check(string name,Func<Task<object>> f){try{results.Add(new{name,status="pass",metrics=await f()});}catch(Exception e){failures++;results.Add(new{name,status="fail",error=e.ToString(),draft});}}
  async Task Pump(){await Dispatcher.InvokeAsync(()=>{},DispatcherPriority.ApplicationIdle);editor.UpdateLayout();await Task.Delay(80);}
  void Replace(string t){editor.BeginChange();editor.SelectAll();editor.Selection.Text=t.EndsWith('\n')?t[..^1]:t;if(t.EndsWith('\n')){editor.CaretPosition=editor.Document.ContentEnd;System.Windows.Documents.EditingCommands.EnterParagraphBreak.Execute(null,editor);}editor.EndChange();}
  string source=Path.Combine(AppContext.BaseDirectory,"corpus","11-word-letter.pdf");string? saved=null;
  await Check("Word-click-original-position-presentation",async()=>
  {
   await Open(source,0,"p0-o0");var r=info!.Region!;Assert(r.Positioned!=null,"No position model");await SelectRegionAt(r.X+4,r.Baseline-3);await Pump();Assert(active&&draft==r.OriginalText&&positionedInk.Visibility==Visibility.Visible,"Activation/presentation failed");
   var measures=new List<object>();double max=0;
   foreach(int z in new[]{0,1,2,3}){zoom.SelectedIndex=z;await Pump();for(int i=0;i<draft.Length;i++){editor.CaretPosition=Position(i);var rect=editor.CaretPosition.GetCharacterRect(LogicalDirection.Forward);double error=(Canvas.GetLeft(editor)+rect.X)/Dip-r.Positioned!.OriginalGlyphs[i].OriginX;max=Math.Max(max,Math.Abs(error));measures.Add(new{zoom=zoomFactor,index=i,nativeCaretErrorPt=error});}}
   Assert(max<.75,"Native caret exceeds measured tolerance: "+max);zoom.SelectedIndex=1;await Pump();ActivateAt(0);WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"word-original.png"),true);return new{maxNativeCaretErrorPt=max,positionedGlyphOriginErrorPt=0,measurements=measures};
  });
  await Check("Word-native-undo-redo-live-candidate-and-save",async()=>
  {
   Replace("Phace 3 Office letter");await Pump();await UndoDocument(false);Assert(draft=="Phase 3 Office letter","Undo lost source");await UndoDocument(true);Assert(draft=="Phace 3 Office letter","Redo lost change");await ValidateDraft();Assert(verifiedRevision==revision,"Live candidate failed: "+status.Text);saved=Path.Combine(folder,"word-ui-first.pdf");var result=await ExportTo(saved);Assert(result?.Safe==true,"Real save failed: "+status.Text);WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"word-edited.png"),true);return new{saved,result};
  });
  await Check("Word-reopen-second-native-edit",async()=>
  {
   Assert(saved!=null,"First export unavailable");await Open(saved!);var r=info!.Regions.Single(x=>x.OriginalText=="Phace 3 Office letter");await SelectRegionAt(r.X+3,r.Baseline-3);Assert(active,"Saved title not rediscovered");Replace("Phace 3 Oflice letter");await Pump();var result=await ExportTo(Path.Combine(folder,"word-ui-second.pdf"));Assert(result?.Safe==true,"Second edit failed: "+status.Text);return result!;
  });
  await Check("Word-longer-unmapped-wider-drafts-history-recovery-refusal",async()=>
  {
   await Open(source,0,"p0-o0");ActivateAt(0);var rejected=new List<object>();
   foreach(string t in new[]{"Phase 3 Office letter extra","Phase 3 Office lett!r","Phase 3 Office lettWr","Phase 3 Office lett\n"}){Replace(t);await Pump();Assert(draft==t&&layout?.Safe==false,"Unsupported draft not retained");PersistDraft();Assert(DocumentSession.Restore(SessionRecoveryPath(session!.SourceHash),session.SourceHash).Regions[ActiveKey].Text==t,"Recovery lost draft");var v=await ExportTo(Path.Combine(folder,Guid.NewGuid()+"-refused.pdf"));Assert(v?.Safe==false&&draft==t,"Unsafe save/draft loss");rejected.Add(new{t,v});}
   await UndoDocument(false);await UndoDocument(true);Assert(draft=="Phase 3 Office lett\n","Refused undo/redo lost newline");WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"word-refused.png"),true);return rejected;
  });
  await Check("candidate-failure-retains-complete-draft",async()=>
  {
   await Open(Path.Combine(AppContext.BaseDirectory,"font-corpus","Word-Arial.pdf"));var r=info!.Regions[0];await SelectRegionAt(r.X+3,r.Baseline-3);Replace("cafe call. cafe calm.");await Pump();Assert(layout?.Safe==true,"Candidate-stage negative did not reach verifier");var result=await ExportTo(Path.Combine(folder,"must-not-serialize-gap.pdf"));Assert(result==null&&draft=="cafe call. cafe calm."&&status.Text.Contains("draft retained",StringComparison.OrdinalIgnoreCase),"Failed candidate lost draft");PersistDraft();Assert(DocumentSession.Restore(SessionRecoveryPath(session!.SourceHash),session.SourceHash).Regions[ActiveKey].Text==draft,"Failed candidate recovery lost text");return new{draft,status=status.Text};
  });
  await Check("shared-paste-retains-terminal-newlines-and-history",async()=>
  {
   await Open(source,0,"p0-o0");ActivateAt(0);string expected="Phase 3 Office letter\n\n";editor.SelectAll();InsertDraftText(expected);await Pump();Assert(draft==expected&&layout?.Safe==false,"Terminal paste newlines lost");await UndoDocument(false);await UndoDocument(true);Assert(draft==expected,"Terminal paste history lost text");PersistDraft();Assert(DocumentSession.Restore(SessionRecoveryPath(session!.SourceHash),session.SourceHash).Regions[ActiveKey].Text==expected,"Terminal paste recovery lost text");return new{draft,retainedTerminalBreaks=2};
  });
  File.WriteAllText(Path.Combine(folder,"position-control-tests.json"),Wire.Write(new{scope="actual WPF controls, shared selection/editor/history/export; not hardware input or file pickers",tests=results.Count,failures,results}));Status($"Position controls: {results.Count-failures}/{results.Count} passed.",failures>0);WriteAudit();
 }
}
