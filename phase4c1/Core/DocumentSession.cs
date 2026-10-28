using System.Security.Cryptography;
using System.Text;
namespace PdfPrototype;
public record RegionChange(int Page,string RegionId,string Identity,string Text);
public record RegionValidation(string Key,string State,string Message);
public record HistoryChange(string Key,string Before,string After,int BeforeCaret,int AfterCaret);
public sealed record RegionDraft
{
 public required Region Original {get;init;}
 public required string Identity {get;init;}
 public required string Text {get;set;}
 public int Caret {get;set;}
 public int SelectionEnd {get;set;}
 public string Validation {get;set;}="Unchanged";
 public string Message {get;set;}="";
 public bool Compatible {get;set;}=true;
 public string Key=>DocumentSession.Key(Original.Page,Original.Id);
 public bool Modified=>Text!=Original.OriginalText;
}
public sealed class DocumentSession
{
 public int Schema {get;set;}=1;
 public required string Source {get;set;}
 public required string SourceHash {get;init;}
 public long Revision {get;set;}
 public long VerifiedRevision {get;set;}=-1;
 public int CurrentPage {get;set;}
 public int PageCount {get;set;}
 public Dictionary<int,Box> PageSizes {get;set;}=new();
 public string ActiveKey {get;set;}="";
 public Dictionary<string,RegionDraft> Regions {get;set;}=new();
 public List<HistoryChange> History {get;set;}=[];
 public int Cursor {get;set;}
 public int EvictedHistory {get;set;}
 public const int MaxHistory=2000,MaxHistoryCharacters=2_000_000,MaxRecoveryBytes=16_000_000;
 public static string Key(int page,string id)=>page+":"+id;
 public static string Identity(Region r)=>Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(Wire.Write(new{r.SourceHash,r.Page,r.Id,r.Objects,r.OriginalText,r.FontHash,r.FontSize,r.R,r.G,r.B,r.X,r.Baseline,r.Width,r.SafeBottom,r.LineHeight,r.Ascent,positions=r.Positioned?.RelativePositions,safeRight=r.Positioned?.SafeRight})))).ToLowerInvariant();
 public void Register(IEnumerable<Region> regions)
 {
  foreach(var r in regions.Where(r=>r.Eligibility=="Editable"))
  {
   string key=Key(r.Page,r.Id),identity=Identity(r);
   if(Regions.TryGetValue(key,out var old))
   {
    bool compatible=old.Identity==identity;
    Regions[key]=old with{Original=compatible?r:old.Original,Compatible=compatible,Validation=compatible?old.Validation:"Blocked",Message=compatible?old.Message:"Recovered text no longer matches the supported source area. Its draft is retained."};
   }
   else Regions[key]=new(){Original=r,Identity=identity,Text=r.OriginalText};
  }
 }
 [System.Text.Json.Serialization.JsonIgnore]
 public RegionDraft[] Modified=>Regions.Values.Where(r=>r.Modified).ToArray();
 public bool CanUndo=>Cursor>0;
 public bool CanRedo=>Cursor<History.Count;
 public bool MatchesResponse(DocumentSession? owner,long revision,string sourceHash)=>ReferenceEquals(this,owner)&&Revision==revision&&SourceHash==sourceHash;
 public void Change(string key,string text,int caret)
 {
  var r=Regions[key];if(r.Text==text)return;
  if(Cursor<History.Count)History.RemoveRange(Cursor,History.Count-Cursor);
  History.Add(new(key,r.Text,text,r.Caret,caret));Cursor++;
  r.Text=text;r.Caret=caret;r.SelectionEnd=caret;Invalidate(r);
  long size=History.Sum(x=>(long)x.Before.Length+x.After.Length);
  while(History.Count>MaxHistory||size>MaxHistoryCharacters)
  {size-=History[0].Before.Length+History[0].After.Length;History.RemoveAt(0);Cursor--;EvictedHistory++;}
 }
 void Invalidate(RegionDraft r){Revision++;VerifiedRevision=-1;r.Validation=r.Modified?"Pending":"Unchanged";r.Message="";}
 public HistoryChange? MoveHistory(bool redo)
 {
  if(redo?!CanRedo:!CanUndo)return null;
  var h=History[redo?Cursor++:--Cursor];var r=Regions[h.Key];
  r.Text=redo?h.After:h.Before;r.Caret=redo?h.AfterCaret:h.BeforeCaret;r.SelectionEnd=r.Caret;Invalidate(r);return h;
 }
 public RegionChange[] Changes()=>Modified.Select(r=>new RegionChange(r.Original.Page,r.Original.Id,r.Identity,r.Text)).ToArray();
 public string Summary()
 {
  int count=Modified.Length,warnings=Modified.Count(r=>!r.Compatible||r.Validation=="Blocked");
  return count==0?"No unsaved text changes.":$"{count} text area(s) changed · {warnings} need attention · "+(VerifiedRevision==Revision?"ready to export":"draft preview; not yet verified");
 }
 public void Persist(string path)
 {
  byte[] bytes=Encoding.UTF8.GetBytes(Wire.Write(this));if(bytes.Length>MaxRecoveryBytes)throw new IOException("Session exceeds the 16 MB recovery limit. Drafts remain in memory; the previous recovery file is preserved.");
  Directory.CreateDirectory(Path.GetDirectoryName(path)!);string temp=path+".tmp";
  try{using(var f=new FileStream(temp,FileMode.Create,FileAccess.Write,FileShare.None)){f.Write(bytes);f.Flush(true);}File.Move(temp,path,true);}
  finally{if(File.Exists(temp))File.Delete(temp);}
 }
 public static DocumentSession Restore(string path,string sourceHash)
 {
  var f=new FileInfo(path);if(f.Length>MaxRecoveryBytes)throw new IOException("Recovery is too large; retained for inspection.");
  var s=Wire.Read<DocumentSession>(File.ReadAllText(path));
  if(s.Schema!=1||s.SourceHash!=sourceHash||s.Cursor<0||s.Cursor>s.History.Count||s.History.Count>MaxHistory||s.History.Any(h=>!s.Regions.ContainsKey(h.Key)))throw new IOException("Recovery is incompatible; retained for inspection.");
  if(s.Regions.Any(kv=>kv.Key!=kv.Value.Key||kv.Value.Original.SourceHash!=sourceHash||kv.Value.Identity!=Identity(kv.Value.Original)))throw new IOException("Recovery region identity is invalid; file retained.");
  if(s.History.Sum(h=>(long)h.Before.Length+h.After.Length)>MaxHistoryCharacters)throw new IOException("Recovery history exceeds its bound; file retained.");
  var texts=s.Regions.ToDictionary(kv=>kv.Key,kv=>kv.Value.Text);
  for(int i=s.Cursor-1;i>=0;i--){var h=s.History[i];if(texts[h.Key]!=h.After)throw new IOException("Recovery history disagrees with its current draft; file retained.");texts[h.Key]=h.Before;}
  foreach(var h in s.History){if(texts[h.Key]!=h.Before)throw new IOException("Recovery history is inconsistent; file retained.");texts[h.Key]=h.After;}
  s.VerifiedRevision=-1;foreach(var r in s.Regions.Values){r.Compatible=false;r.Validation=r.Modified?"Pending":"Unchanged";}
  return s;
 }
}
