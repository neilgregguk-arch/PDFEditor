using System.Text.Json;
using System.Windows.Documents;
namespace PdfPrototype;
public sealed partial class EditorWindow
{
 async Task RunMultiRegionRecoveryCheck()
 {
  using var expected=JsonDocument.Parse(File.ReadAllText(Path.Combine(auditFolder!,"..","recovery-reopen-expectation.json")));
  var root=expected.RootElement;string source=root.GetProperty("source").GetString()!;var checks=new List<object>();int failures=0;
  try
  {
   await Open(source);debounce.Stop();
   if(session!.VerifiedRevision!=-1||saveButton!.IsEnabled)throw new Exception("Recovery reused approval");
   if(session.Cursor!=root.GetProperty("cursor").GetInt32()||session.History.Count!=root.GetProperty("history").GetInt32())throw new Exception("Recovery history differs");
   foreach(var pair in root.GetProperty("texts").EnumerateObject())
   {
    var s=session.Regions[pair.Name];if(s.Text!=pair.Value.GetString())throw new Exception("Recovered text differs");
    await Open(source,s.Original.Page,s.Original.Id);await SelectRegionAt(s.Original.ObservedBounds!.X+4,s.Original.Baseline-3);debounce.Stop();
    if(!active||draft!=pair.Value.GetString()||new TextRange(editor.Document.ContentStart,editor.Document.ContentEnd).Text.Replace("\r\n","\n").TrimEndOneNewline()!=draft)throw new Exception("Recovered WPF draft differs");
    checks.Add(new{key=pair.Name,text=draft,active,sourceIdentity=s.Identity});
   }
   await ValidateDraft();if(session.VerifiedRevision!=-1)throw new Exception("Invalid recovered text approved");
   if(Wire.Hash(source)!=root.GetProperty("hash").GetString())throw new Exception("Source modified");
  }
  catch(Exception ex){failures++;checks.Add(new{error=ex.ToString()});}
  WriteAudit();File.WriteAllText(Path.Combine(auditFolder!,"multi-region-recovery-tests.json"),Wire.Write(new{tests=1,failures,checks,process=Environment.ProcessId,scope="New OS process, retained exact two-region drafts and global history; no approval recovery"}));Close();
 }
}
