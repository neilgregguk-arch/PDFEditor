using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Threading;
namespace PdfPrototype;
public sealed partial class EditorWindow
{
 async Task RunFontControlTests()
 {
  string folder=auditFolder??work;var results=new List<object>();int failures=0;
  void Assert(bool value,string message){if(!value)throw new InvalidOperationException(message);}
  async Task Check(string name,Func<Task<object>> test){try{results.Add(new{name,status="pass",metrics=await test()});}catch(Exception e){failures++;results.Add(new{name,status="fail",error=e.Message,draft,statusText=status.Text});}}
  async Task Pump(){await Dispatcher.InvokeAsync(()=>{},DispatcherPriority.ApplicationIdle);editor.UpdateLayout();await Task.Delay(50);}
  void Replace(string text){editor.BeginChange();editor.SelectAll();editor.Selection.Text=text;editor.EndChange();}
  string FontPdf(string name)=>Path.Combine(AppContext.BaseDirectory,"font-corpus",name+".pdf");
  async Task Choose(){var r=info!.Regions[0];await SelectRegionAt(r.X+3,r.Baseline-3);await Pump();Assert(active,"Subset region did not activate");}
  await Check("subset-click-caret-at-four-zooms",async()=>
  {
   await Open(FontPdf("J-partial-encoding"));await Choose();var measurements=new List<object>();
   foreach(int z in new[]{0,1,2,3})foreach(int index in new[]{0,2,4,9})
   {
    zoom.SelectedIndex=z;await Pump();ActivateAt(index);await Pump();var rect=editor.CaretPosition.GetCharacterRect(LogicalDirection.Forward);double expected=info!.Region!.X+ParagraphLayout.Width(info.Region,draft[..index]);double error=(Canvas.GetLeft(editor)+rect.X)/Dip-expected;Assert(Math.Abs(error)<.75,"Subset caret displaced: "+error);measurements.Add(new{zoom=zoomFactor,index,errorPt=error});
   }
   zoom.SelectedIndex=1;WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"subset-caret.png"),true);return measurements;
  });
  await Check("subset-native-history-and-real-save",async()=>
  {
   Replace("face calm.");await Pump();await UndoDocument(false);Assert(draft=="cafe calm.","Subset undo");await UndoDocument(true);Assert(draft=="face calm.","Subset redo");await ValidateDraft();Assert(verifiedRevision==revision,"Subset candidate not verified: "+status.Text);
   string destination=Path.Combine(folder,"subset-UI-"+Guid.NewGuid().ToString("N")+".pdf");var result=await ExportTo(destination);Assert(result?.Safe==true,"Subset real save failed");Assert(draft=="face calm.","Save changed draft");return new{destination,result!.Verification};
  });
  await Check("unsupported-character-typing-history-recovery-and-export",async()=>
  {
   Replace("face calm. Z");await Pump();Assert(draft.EndsWith('Z')&&layout?.Safe==false&&status.Text.Contains("U+005A")&&status.Text.Contains("mapping unavailable")&&Text()==draft,"Glyph warning/draft missing");
   Replace("face calm. Z cafe");await Pump();Assert(draft.EndsWith("Z cafe"),"Continued typing blocked");await UndoDocument(false);Assert(draft=="face calm. Z","Invalid draft undo lost text");await UndoDocument(true);Assert(draft=="face calm. Z cafe","Invalid draft redo lost text");PersistDraft();Assert(DocumentSession.Restore(SessionRecoveryPath(session!.SourceHash),session.SourceHash).Regions[ActiveKey].Text==draft,"Subset recovery mismatch");
   var result=await ExportTo(Path.Combine(folder,"must-not-export.pdf"));Assert(result?.Safe==false&&draft=="face calm. Z cafe","Rejected export lost draft");WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"subset-glyph-warning.png"),true);return new{draft,status=status.Text,result!.ProposedTextEligibility,result.ExportEligibility,result.GlyphIssues};
  });
  await Check("subset-bold-style-and-word-position-activation",async()=>
  {
   await Open(FontPdf("C-subset-bold"));await Choose();Assert(editor.FontWeight.ToOpenTypeWeight()>=600,"Subset bold displayed regular");
   await Open(Path.Combine(AppContext.BaseDirectory,"corpus","11-word-letter.pdf"));var r=info!.Regions[0];await SelectRegionAt(r.X+5,r.Baseline-3);Assert(active&&info.Region?.Positioned!=null,"Word position activation missing");return new{wordReasons=r.Reasons,status=status.Text};
  });
  File.WriteAllText(Path.Combine(folder,"font-control-tests.json"),Wire.Write(new{scope="actual WPF controls/shared click path, not physical input",tests=results.Count,failures,results}));Status($"Font control tests: {results.Count-failures}/{results.Count} passed.",failures>0);WriteAudit();
 }
}
