using System.Windows;
using System.Windows.Documents;
using System.Windows.Threading;
namespace PdfPrototype;
public sealed partial class EditorWindow
{
 async Task RunClipboardProbe()
 {
  var rows=new List<object>();
  for(int i=0;i<5;i++)
  {
   try{string? previous=UnicodeClipboard.Read();UnicodeClipboard.Write("Phase 3 clipboard probe");bool matches=UnicodeClipboard.Read()=="Phase 3 clipboard probe";if(previous!=null)UnicodeClipboard.Write(previous);rows.Add(new{iteration=i,readWriteReadMatches=matches});}
   catch(Exception e){rows.Add(new{iteration=i,error=e.Message});}
   await Task.Delay(200);
  }
  File.WriteAllText(Path.Combine(auditFolder??work,"clipboard-probe.json"),Wire.Write(rows));
 }
 async Task RunDiscoveryControlTests()
 {
  var results=new List<object>();int failures=0;string folder=auditFolder??work;
  void Assert(bool value,string message){if(!value)throw new InvalidOperationException(message);}
  async Task Check(string name,Func<Task<object>> test){try{results.Add(new{name,status="pass",metrics=await test()});}catch(Exception ex){failures++;results.Add(new{name,status="fail",error=ex.Message,draft,statusText=status.Text});}}
  async Task Pump(){await Dispatcher.InvokeAsync(()=>{},DispatcherPriority.ApplicationIdle);editor.UpdateLayout();await Task.Delay(50);}
  void Replace(string text){editor.BeginChange();editor.SelectAll();editor.Selection.Text=text;editor.EndChange();}
  string Corpus(string name)=>Path.Combine(AppContext.BaseDirectory,"corpus",name+".pdf");
  async Task Choose(string prefix){var target=info!.Regions.First(r=>r.OriginalText.StartsWith(prefix));await SelectRegionAt(target.X+10,target.Baseline-3);await Pump();Assert(active&&info!.Region!.Id==target.Id,"Click-selection path did not activate intended region.");}
  await Check("automatic-discovery-click-selection-and-original-text",async()=>
  {
   await Open(Corpus("01-letter"));await Choose("This ordinary");Assert(draft.StartsWith("This ordinary")&&info!.Region!.Objects.Length==2,"Wrong paragraph text/grouping");WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"discovered-inline.png"),true);return new{objects=info!.Region!.Objects,glyphs=info.Glyphs.Length,active};
  });
  await Check("discovered-paragraph-edit-save-reopen-and-second-edit",async()=>
  {
   Replace("First WPF edit remains genuine PDF content.");await Pump();await ValidateDraft();Assert(verifiedRevision==revision,"First UI candidate rejected");
   string one=Path.Combine(folder,"UI-generation-one-"+Guid.NewGuid().ToString("N")+".pdf");var first=await ExportTo(one);Assert(first?.Safe==true,"First UI save failed");
   await Open(one);await Choose("First WPF");Assert(draft=="First WPF edit remains genuine PDF content.","Reopened draft differs");Replace(draft+" Second WPF edit survives.");await Pump();string two=Path.Combine(folder,"UI-generation-two-"+Guid.NewGuid().ToString("N")+".pdf");var second=await ExportTo(two);Assert(second?.Safe==true,"Second UI save failed");WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"second-edit.png"),true);return new{one,two,second!.Verification};
  });
  await Check("discovered-bold-and-colour-control-style",async()=>
  {
   await Open(Corpus("02-report"));await Choose("Bold summary");Assert(editor.FontWeight.ToOpenTypeWeight()>=600,"Bold original displayed as regular");
   await Open(Corpus("02-report"));await Choose("A blue note");Assert(Math.Abs(editor.FontSize-10*Dip)<.001,"Font size changed");WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"colour-inline.png"),true);return new{weight="bold verified before switching",fontSizeDip=editor.FontSize};
  });
  await Check("missing-glyph-and-failed-save-preserve-region-draft",async()=>
  {
   Replace("Retain this snowman \u2603 draft.");await Pump();Assert(draft.Contains('\u2603')&&layout?.Safe==false,"Missing-glyph draft lost");PersistDraft();Assert(Wire.Read<DraftRecovery>(File.ReadAllText(RecoveryPath())).Text==draft,"Per-region recovery mismatch");var saved=await ExportTo(Path.Combine(folder,"must-not-save.pdf"));Assert(saved?.Safe==false&&draft.Contains('\u2603'),"Failed export lost draft");
   await SelectRegionAt(65,130);Assert(draft.Contains('\u2603')&&status.Text.Contains("Working draft retained"),"Region switch discarded working draft");return new{draft,sourcePreserved=Wire.Hash(info!.Path)==info.Hash,recovery=RecoveryPath()};
  });
  await Check("unsupported-region-feedback-without-editor",async()=>
  {
   await Open(Corpus("06-ambiguous"));await SelectRegionAt(65,127);Assert(!active&&status.Text.StartsWith("Limited:"),"Limited region became editable");return new{active,status=status.Text};
  });
  File.WriteAllText(Path.Combine(folder,"discovery-control-tests.json"),Wire.Write(new{scope="WPF control integration and shared click-selection path; not physical input",tests=results.Count,failures,results}));Status($"Discovery control tests: {results.Count-failures}/{results.Count} passed.",failures>0);WriteAudit();
 }
}
