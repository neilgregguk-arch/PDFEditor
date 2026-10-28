namespace PdfPrototype;
public sealed partial class EditorWindow
{
 async Task RunProcessRecoveryTest(bool second)
 {
  string folder=auditFolder??work;
  try
  {
   void Assert(bool value,string message){if(!value)throw new Exception(message);}
   async Task Choose(Region r){await SelectRegionAt(r.X+3,r.Baseline-3);}
   void Replace(string text){editor.SelectAll();InsertDraftText(text);}
   if(!second)
   {
    var rs=info!.Regions.Where(r=>r.Eligibility=="Editable").ToArray();await Choose(rs[0]);Replace("First process recovery draft.");await Choose(rs[1]);Replace("Second process recovery draft.");await ChangePage(1);await Choose(info!.Regions.First(r=>r.Eligibility=="Editable"));Replace("Another page process recovery draft.");PersistDraft();
    File.WriteAllText(Path.Combine(folder,"process-stage1.json"),Wire.Write(new{success=true,pid=Environment.ProcessId,source=session!.Source,sourceHash=session.SourceHash,changes=session.Changes(),session.Cursor,session.Revision}));
   }
   else
   {
    Assert(session?.Modified.Length==3,"New process did not restore all three drafts");int count=session!.Cursor;Assert(count>=3,"History not restored");await Choose(info!.Regions.First(r=>r.Eligibility=="Editable"));Assert(draft=="First process recovery draft.","First recovered text differs");await UndoDocument(false);Assert(draft==info!.Region!.OriginalText,"Recovered global undo failed");await UndoDocument(true);Assert(draft=="Another page process recovery draft.","Recovered redo failed");
    var changes=session.Changes();string source=session.Source;var result=await ExportTo(Path.Combine(folder,"process-recovered.pdf"));Assert(result?.Safe==true,"Recovered transaction did not export");File.WriteAllText(Path.Combine(folder,"process-stage2.json"),Wire.Write(new{success=true,pid=Environment.ProcessId,source,changes,result,session.Cursor,session.Revision}));
   }
  }
  catch(Exception e){File.WriteAllText(Path.Combine(folder,second?"process-stage2.json":"process-stage1.json"),Wire.Write(new{success=false,error=e.ToString()}));}
  Close();
 }
}
