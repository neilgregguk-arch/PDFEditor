using System.Globalization;
using System.Text;
using System.IO.Compression;
using System.Text.RegularExpressions;
namespace PdfPrototype;
// Deliberately narrow, bounded structural cross-check. This is NOT a general PDF
// interpreter. PDFium remains the content/font/render parser. Unsupported xref or
// object syntax refuses new original grouping, without disabling 5.1 declarations.
internal sealed class OriginalStructureProof
{
 record Ref(int Number,int Generation);
 record Name(string Value);
 readonly string data;
 readonly Dictionary<int,(int Offset,int Generation,bool Live)> offsets=[];
 readonly Dictionary<Ref,object> cache=[];
 readonly Dictionary<int,(int Stream,int Index)> compressed=[];
 readonly Dictionary<int,Dictionary<int,object>> objectStreams=[];
 int inflatedBytes;
 Dictionary<string,object> trailer=[];
 int resolutions;
 sealed class Reader(string data,int start)
 {
  public int Position=start;int tokens;
  public void Skip(){while(Position<data.Length){char c=data[Position];if(c=='%'){while(Position<data.Length&&data[Position]!='\n'&&data[Position]!='\r')Position++;}else if(c is '\0' or '\t' or '\n' or '\f' or '\r' or ' ')Position++;else break;}}
  public string Token(){Skip();if(++tokens>65536)throw new InvalidDataException("Structural token budget.");int a=Position;while(Position<data.Length&&!char.IsWhiteSpace(data[Position])&&data[Position] is not ('<' or '>' or '[' or ']' or '(' or ')' or '/' or '%'))Position++;if(a==Position)throw new InvalidDataException("Structural token expected.");return data[a..Position];}
  public void Expect(string t){if(Token()!=t)throw new InvalidDataException("Structural keyword differs.");}
  public object Value(int depth=0)
  {
   if(depth>24)throw new InvalidDataException("Structural nesting budget.");Skip();if(Position>=data.Length)throw new InvalidDataException("Structural EOF.");char c=data[Position];
   if(c=='<'&&Position+1<data.Length&&data[Position+1]=='<')
   {
    Position+=2;var d=new Dictionary<string,object>();while(true){Skip();if(Position+1<data.Length&&data[Position]=='>'&&data[Position+1]=='>'){Position+=2;return d;}if(Value(depth+1) is not Name k||!d.TryAdd(k.Value,Value(depth+1)))throw new InvalidDataException("Structural dictionary key.");if(d.Count>4096)throw new InvalidDataException("Structural dictionary budget.");}
   }
   if(c=='['){Position++;var a=new List<object>();while(true){Skip();if(Position>=data.Length)throw new InvalidDataException("Structural array EOF.");if(data[Position]==']'){Position++;return a;}a.Add(Value(depth+1));if(a.Count>65536)throw new InvalidDataException("Structural array budget.");}}
   if(c=='/'){Position++;int a=Position;while(Position<data.Length&&!char.IsWhiteSpace(data[Position])&&data[Position] is not ('<' or '>' or '[' or ']' or '(' or ')' or '/' or '%'))Position++;string name=data[a..Position];if(name.Contains('#'))throw new InvalidDataException("Escaped structural names unsupported.");return new Name(name);}
   if(c=='('){Position++;int level=1;while(Position<data.Length&&level>0){char v=data[Position++];if(v=='\\'){if(Position<data.Length)Position++;}else if(v=='(')level++;else if(v==')')level--;if(level>24)throw new InvalidDataException("Structural string budget.");}if(level!=0)throw new InvalidDataException("Structural string EOF.");return "opaque-string";}
   if(c=='<'){Position++;while(Position<data.Length&&data[Position]!='>')Position++;if(Position>=data.Length)throw new InvalidDataException("Structural hex EOF.");Position++;return "opaque-bytes";}
   string t=Token();if(int.TryParse(t,NumberStyles.AllowLeadingSign,CultureInfo.InvariantCulture,out int n))
   {
    int saved=Position;try{string next=Token();if(int.TryParse(next,out int gen)&&Token()=="R")return new Ref(n,gen);}catch(InvalidDataException){}Position=saved;return n;
   }
   if(double.TryParse(t,NumberStyles.Float,CultureInfo.InvariantCulture,out double f)&&double.IsFinite(f))return f;
   if(t is "true" or "false" or "null")return t;throw new InvalidDataException("Unsupported structural value.");
  }
 }
 static void Check(bool b,string why){if(!b)throw new InvalidDataException("ORIGINAL_STRUCTURE_"+why);}
 static Dictionary<string,object> Dict(object o)=>o as Dictionary<string,object>??throw new InvalidDataException("Structural dictionary required.");
 static List<object> Array(object o)=>o as List<object>??throw new InvalidDataException("Structural array required.");
 static Ref Reference(object o)=>o as Ref??throw new InvalidDataException("Structural indirect reference required.");
 static int Integer(object o)=>o is int n&&n>=0?n:throw new InvalidDataException("Structural nonnegative integer required.");
 static string Type(Dictionary<string,object> d,string key)=>d.GetValueOrDefault(key) is Name n?n.Value:"";
 Dictionary<string,object> Resolve(object value)=>Dict(ResolveValue(value));
 object ResolveValue(object value)
 {
  if(value is not Ref r)return value;if(cache.TryGetValue(r,out var hit))return hit;
  Check(++resolutions<=4096,"OBJECT_BUDGET");
  if(compressed.TryGetValue(r.Number,out var entry))
  {
   Check(r.Generation==0,"COMPRESSED_GENERATION");
   if(!objectStreams.TryGetValue(entry.Stream,out var contents))
   {
    Check(objectStreams.Count<16&&offsets.TryGetValue(entry.Stream,out var sx)&&sx.Live,"OBJECT_STREAM_XREF");
    var (dictionary,bytes)=StreamAt(offsets[entry.Stream].Offset,entry.Stream);Check(Type(dictionary,"Type")=="ObjStm","OBJECT_STREAM_TYPE");
    int first=Integer(dictionary["First"]),count=Integer(dictionary["N"]);Check(count<=4096&&first<=bytes.Length,"OBJECT_STREAM_BUDGET");
    string decoded=Encoding.Latin1.GetString(bytes);var header=new Reader(decoded,0);var indexes=new List<(int Id,int Offset)>();
    for(int i=0;i<count;i++)indexes.Add((int.Parse(header.Token(),CultureInfo.InvariantCulture),int.Parse(header.Token(),CultureInfo.InvariantCulture)));
    Check(header.Position<=first,"OBJECT_STREAM_HEADER");contents=[];
    for(int i=0;i<count;i++)
    {
     var item=indexes[i];int end=i+1<count?first+indexes[i+1].Offset:decoded.Length;Check(item.Offset>=0&&first+item.Offset<end&&end<=decoded.Length,"OBJECT_STREAM_OFFSETS");
     var parser=new Reader(decoded,first+item.Offset);object obj=parser.Value();parser.Skip();Check(parser.Position==end&&contents.TryAdd(item.Id,obj),"OBJECT_STREAM_MEMBER");
     Check(compressed.TryGetValue(item.Id,out var own)&&own.Stream==entry.Stream&&own.Index==i,"OBJECT_STREAM_INDEX");
    }
    objectStreams.Add(entry.Stream,contents);
   }
   Check(contents.ContainsKey(r.Number),"OBJECT_STREAM_MISSING");cache[r]=contents[r.Number];return contents[r.Number];
  }
  Check(offsets.TryGetValue(r.Number,out var x)&&x.Live&&x.Generation==r.Generation,"UNRESOLVED_XREF");
  var reader=new Reader(data,x.Offset);reader.Expect(r.Number.ToString(CultureInfo.InvariantCulture));reader.Expect(r.Generation.ToString(CultureInfo.InvariantCulture));reader.Expect("obj");var result=reader.Value();reader.Expect("endobj");cache.Add(r,result);return result;
 }
 (Dictionary<string,object>,byte[]) StreamAt(int at,int? expected=null)
 {
  var reader=new Reader(data,at);int number=int.Parse(reader.Token(),CultureInfo.InvariantCulture);Check(expected==null||expected==number,"STREAM_NUMBER");reader.Expect("0");reader.Expect("obj");var dictionary=Dict(reader.Value());reader.Expect("stream");
  int begin=reader.Position;if(begin<data.Length&&data[begin]=='\r')begin++;Check(begin<data.Length&&data[begin]=='\n',"STREAM_EOL");begin++;
  int length=Integer(dictionary["Length"]);Check(length<=8_388_608&&(long)begin+length<=data.Length,"STREAM_LENGTH");reader.Position=begin+length;reader.Expect("endstream");reader.Expect("endobj");
  Check(Type(dictionary,"Filter")=="FlateDecode"&&!dictionary.ContainsKey("DecodeParms"),"STREAM_FILTER");
  byte[] encoded=Encoding.Latin1.GetBytes(data.Substring(begin,length));using var input=new MemoryStream(encoded);using var zip=new ZLibStream(input,CompressionMode.Decompress);using var output=new MemoryStream();byte[] block=new byte[8192];int read;
  while((read=zip.Read(block))>0){Check(output.Length+read<=8_388_608&&(inflatedBytes+=read)<=16_777_216,"INFLATE_BUDGET");output.Write(block,0,read);}
  return(dictionary,output.ToArray());
 }
 void Hybrid(int at,HashSet<int> local)
 {
  var (d,bytes)=StreamAt(at);Check(Type(d,"Type")=="XRef","XREF_STREAM_TYPE");var widths=Array(d["W"]).Select(Integer).ToArray();Check(widths.Length==3&&widths.All(n=>n<=4)&&widths.Sum()>0,"XREF_WIDTHS");
  var ranges=d.TryGetValue("Index",out var ix)?Array(ix).Select(Integer).ToArray():[0,Integer(d["Size"])];Check(ranges.Length%2==0&&ranges.Length<=8192,"XREF_RANGES");int cursor=0;
  uint Field(int width,uint absent){if(width==0)return absent;Check(cursor+width<=bytes.Length,"XREF_STREAM_LENGTH");uint v=0;for(int i=0;i<width;i++)v=(v<<8)|bytes[cursor++];return v;}
  for(int k=0;k<ranges.Length;k+=2)
  {
   Check((long)ranges[k]+ranges[k+1]<=65536,"XREF_STREAM_BUDGET");
   for(int j=0;j<ranges[k+1];j++)
   {
    int id=ranges[k]+j;uint type=Field(widths[0],1),a=Field(widths[1],0),b=Field(widths[2],0);Check(a<=int.MaxValue&&b<=int.MaxValue&&type<=2,"XREF_STREAM_VALUE");
    // The hybrid stream overrides this revision's classic free placeholders.
    // Earlier revisions never override a newer resolved entry.
    if(type==1&&(local.Contains(id)||!offsets.ContainsKey(id)))offsets[id]=((int)a,(int)b,true);
    if(type==2&&(local.Contains(id)||!offsets.ContainsKey(id)))
    {compressed.TryAdd(id,((int)a,(int)b));offsets[id]=(0,0,false);}
   }
  }
  Check(cursor==bytes.Length,"XREF_STREAM_TRAILING_DATA");
 }
 public OriginalStructureProof(string path)
 {
  Check(new FileInfo(path).Length<=16_777_216,"FILE_BUDGET");byte[] bytes=File.ReadAllBytes(path);Check(bytes.Length<=16_777_216,"FILE_BUDGET");data=Encoding.Latin1.GetString(bytes);
  string tail=data[Math.Max(0,data.Length-2048)..];var match=Regex.Match(tail,@"startxref\s+(\d+)\s+%%EOF\s*$",RegexOptions.CultureInvariant,TimeSpan.FromMilliseconds(50));Check(match.Success,"CLASSIC_XREF_REQUIRED");
  int at=int.Parse(match.Groups[1].Value,CultureInfo.InvariantCulture);var visited=new HashSet<int>();int entries=0;
  for(int revision=0;;revision++)
  {
   Check(revision<8&&visited.Add(at)&&at>=0&&at<data.Length,"XREF_CHAIN_BUDGET");var reader=new Reader(data,at);reader.Expect("xref");var local=new HashSet<int>();
   while(true)
   {
    string t=reader.Token();if(t=="trailer")break;int first=Integer(int.Parse(t,CultureInfo.InvariantCulture)),count=Integer(int.Parse(reader.Token(),CultureInfo.InvariantCulture));Check((long)first+count<=65536&&(entries+=count)<=131072,"XREF_ENTRY_BUDGET");
    for(int j=0;j<count;j++){int offset=int.Parse(reader.Token(),CultureInfo.InvariantCulture),gen=int.Parse(reader.Token(),CultureInfo.InvariantCulture);string flag=reader.Token();Check(flag is "n" or "f"&&offset>=0&&gen>=0&&local.Add(first+j),"XREF_ENTRY");offsets.TryAdd(first+j,(offset,gen,flag=="n"));}
   }
   var tr=Dict(reader.Value());if(revision==0)trailer=tr;
   if(tr.TryGetValue("XRefStm",out var hybrid))Hybrid(Integer(hybrid),local);
   // Only bounded hybrid Flate xref/object streams are supported; other syntax refuses.
   if(!tr.TryGetValue("Prev",out var prev))break;at=Integer(prev);
  }
 }
 public HashSet<int> Mcids(int pageIndex)
 {
  var catalog=Resolve(trailer["Root"]);var treeRef=Reference(catalog["StructTreeRoot"]);var tree=Resolve(treeRef);
  Check(Type(tree,"Type")=="StructTreeRoot","ROOT_TYPE");var top=tree["K"] is List<object> list?list:[tree["K"]];Check(top.Count==1,"DOCUMENT_ROOT_COUNT");var documentRef=Reference(top[0]);var document=Resolve(documentRef);
  Check(Type(document,"S")=="Document"&&Reference(document["P"])==treeRef&&!document.ContainsKey("ActualText"),"DOCUMENT_SCOPE");
  var pageRefs=new List<Ref>();var seen=new HashSet<Ref>();
  void Walk(object node,int depth,Ref? parent)
  {
   var r=Reference(node);Check(depth<=24&&seen.Add(r)&&seen.Count<=4096,"PAGE_TREE_BUDGET");var d=Resolve(r);if(parent!=null)Check(Reference(d["Parent"])==parent,"PAGE_PARENT");
   if(Type(d,"Type")=="Page"){pageRefs.Add(r);Check(pageRefs.Count<=256,"PAGE_COUNT");return;}Check(Type(d,"Type")=="Pages","PAGE_TREE_TYPE");foreach(var child in Array(d["Kids"]))Walk(child,depth+1,r);
  }
  Walk(catalog["Pages"],0,null);Check(pageIndex>=0&&pageIndex<pageRefs.Count,"PAGE_INDEX");var pageRef=pageRefs[pageIndex];var page=Resolve(pageRef);int parentKey=Integer(page["StructParents"]);
  var nums=new Dictionary<int,object>();var numberSeen=new HashSet<Ref>();int nodes=0;
  void NumberTree(object node,int depth)
  {
   Check(depth<=24&&++nodes<=4096,"PARENT_TREE_BUDGET");if(node is Ref nr)Check(numberSeen.Add(nr),"PARENT_TREE_CYCLE");var d=Resolve(node);
   Check(d.ContainsKey("Nums")!=d.ContainsKey("Kids"),"PARENT_TREE_SHAPE");
   if(d.TryGetValue("Nums",out var ns)){var a=Array(ns);Check(a.Count%2==0&&a.Count<=8192,"PARENT_NUMS");int prior=-1;for(int i=0;i<a.Count;i+=2){int key=Integer(a[i]);Check(key>prior&&nums.TryAdd(key,a[i+1]),"PARENT_KEYS");prior=key;}}
   else foreach(var child in Array(d["Kids"]))NumberTree(child,depth+1);
  }
  NumberTree(tree["ParentTree"],0);Check(nums.ContainsKey(parentKey),"PARENT_PAGE_MISSING");var parents=Array(ResolveValue(nums[parentKey]));Check(parents.Count<=4096,"PARENT_ARRAY_BUDGET");
  var children=document["K"] is List<object> kids?kids:[document["K"]];var result=new HashSet<int>();var used=new HashSet<Ref>();
  foreach(var child in children)
  {
   var r=Reference(child);Check(used.Add(r),"DUPLICATE_STRUCTURE_CHILD");var p=Resolve(r);if(Type(p,"S")!="P"||Type(p,"Type")!="StructElem")continue;
   if(p.Keys.Any(k=>k is not ("Type" or "S" or "P" or "Pg" or "K")))continue;
   if(Reference(p["P"])!=documentRef||Reference(p["Pg"])!=pageRef)continue;
   var content=p["K"] is List<object> a?a:[p["K"]];if(content.Count!=1||content[0] is not int id||id<0)continue;
   Check(id<parents.Count&&parents[id] is Ref pr&&pr==r,"PARENT_MCID_MISMATCH");Check(parents.Where(v=>v is Ref rr&&rr==r).Count()==1,"DUPLICATE_PARENT_ASSOCIATION");Check(result.Add(id),"DUPLICATE_MCID");
  }
  return result;
 }
}
