using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Runtime.InteropServices;
namespace PdfPrototype;

public record ParagraphOwnership(string Id,string Evidence,string PayloadHash,Box Envelope,string SemanticMarks);
public record ParagraphRow(string Text,double Baseline,double[] Origins,double[][] Bounds);
public record ParagraphManifest(int Version,string Id,int Page,double PageWidth,double PageHeight,string Text,
 string FontHash,string MappingHash,double FontSize,uint R,uint G,uint B,double X,double Baseline,
 double LineHeight,double Ascent,Box Envelope,string SemanticMarks,ParagraphRow[] Rows);

internal static partial class N
{
 const string MarkDll="pdfium.dll";
 [DllImport(MarkDll)] public static extern int FPDFPage_InsertObjectAtIndex(IntPtr page,IntPtr o,nuint index);
 [DllImport(MarkDll)] public static extern int FPDFPageObj_CountMarks(IntPtr o);
 [DllImport(MarkDll)] public static extern IntPtr FPDFPageObj_GetMark(IntPtr o,uint index);
 [DllImport(MarkDll)] public static extern IntPtr FPDFPageObj_AddMark(IntPtr o,[MarshalAs(UnmanagedType.LPUTF8Str)]string name);
 [DllImport(MarkDll)] public static extern int FPDFPageObj_AddExistingMark(IntPtr o,IntPtr mark);
 [DllImport(MarkDll)] public static extern int FPDFPageObjMark_GetName(IntPtr m,[Out]byte[]? bytes,uint size,out uint used);
 [DllImport(MarkDll)] public static extern int FPDFPageObjMark_CountParams(IntPtr m);
 [DllImport(MarkDll)] public static extern int FPDFPageObjMark_GetParamKey(IntPtr m,uint index,[Out]byte[]? bytes,uint size,out uint used);
 [DllImport(MarkDll)] public static extern int FPDFPageObjMark_GetParamValueType(IntPtr m,[MarshalAs(UnmanagedType.LPUTF8Str)]string key);
 [DllImport(MarkDll)] public static extern int FPDFPageObjMark_GetParamIntValue(IntPtr m,[MarshalAs(UnmanagedType.LPUTF8Str)]string key,out int value);
 [DllImport(MarkDll)] public static extern int FPDFPageObjMark_GetParamFloatValue(IntPtr m,[MarshalAs(UnmanagedType.LPUTF8Str)]string key,out float value);
 [DllImport(MarkDll)] public static extern int FPDFPageObjMark_GetParamBlobValue(IntPtr m,[MarshalAs(UnmanagedType.LPUTF8Str)]string key,[Out]byte[]? bytes,uint size,out uint used);
 [DllImport(MarkDll)] public static extern int FPDFPageObjMark_SetBlobParam(IntPtr d,IntPtr o,IntPtr m,[MarshalAs(UnmanagedType.LPUTF8Str)]string key,byte[] bytes,uint size);
 [DllImport(MarkDll)] public static extern int FPDFPageObjMark_SetIntParam(IntPtr d,IntPtr o,IntPtr m,[MarshalAs(UnmanagedType.LPUTF8Str)]string key,int value);
}

public sealed partial class PdfEngine
{
 const string ParagraphTag="PDFEditorV2_Paragraph";
 const int MaxMarkBytes=28000,MaxPageMarkBytes=8_388_608;
 static readonly JsonSerializerOptions MarkJson=new(){MaxDepth=16,UnmappedMemberHandling=JsonUnmappedMemberHandling.Disallow};
 readonly Dictionary<string,HashSet<string>> conflictingParagraphIds=new();
 HashSet<string> ConflictingParagraphIds(IntPtr doc,IntPtr currentPage,int currentIndex,string fingerprint)
 {
  if(conflictingParagraphIds.TryGetValue(fingerprint,out var cached))return cached;
  int pages=N.FPDF_GetPageCount(doc),objectsSeen=0,bytesSeen=0;Require(pages<=256,"Paragraph document index page budget.");
  var locations=new Dictionary<string,HashSet<int>>(StringComparer.Ordinal);
  for(int index=0;index<pages;index++)
  {
   Page? loaded=index==currentIndex?null:new Page(doc,index);IntPtr page=loaded?.Handle??currentPage;
   try
   {
    var objects=Objects(page);objectsSeen+=objects.Length;Require(objectsSeen<=65536,"Paragraph document index object budget.");
    foreach(var o in objects)
    {
     int count=N.FPDFPageObj_CountMarks(o);Require(count>=0&&count<=16,"Paragraph document mark budget.");
     for(uint k=0;k<count;k++)
     {
      var mark=N.FPDFPageObj_GetMark(o,k);if(MarkName(mark)!=ParagraphTag)continue;
      try
      {
       var blob=MarkBlob(mark,"Data");bytesSeen+=blob.Length;Require(bytesSeen<=MaxPageMarkBytes,"Paragraph document metadata budget.");
       using var json=JsonDocument.Parse(blob,new JsonDocumentOptions{MaxDepth=16});
       if(json.RootElement.ValueKind!=JsonValueKind.Object||!json.RootElement.TryGetProperty("Id",out var value)||value.ValueKind!=JsonValueKind.String)continue;
       string? id=value.GetString();if(id==null||!Guid.TryParseExact(id,"N",out var guid))continue;id=guid.ToString("N");
       if(!locations.TryGetValue(id,out var found))locations[id]=found=[];found.Add(index);
      }
      catch(Exception ex) when(ex is JsonException or InvalidOperationException){/* Invalid declaration is quarantined by its page's full validator. */}
     }
    }
   }
   finally{loaded?.Dispose();}
  }
  var result=locations.Where(p=>p.Value.Count>1).Select(p=>p.Key).ToHashSet(StringComparer.Ordinal);
  if(conflictingParagraphIds.Count>=4)conflictingParagraphIds.Clear();conflictingParagraphIds[fingerprint]=result;return result;
 }
 static string MarkName(IntPtr m)
 {
  N.Check(N.FPDFPageObjMark_GetName(m,null,0,out uint n),"mark name length");
  if(n>256||n%2!=0)throw new InvalidDataException("Mark name exceeds limit.");
  byte[] b=new byte[n];N.Check(N.FPDFPageObjMark_GetName(m,b,n,out _),"mark name");return Encoding.Unicode.GetString(b).TrimEnd('\0');
 }
 static string[] MarkKeys(IntPtr m)
 {
  int count=N.FPDFPageObjMark_CountParams(m);if(count<0||count>16)throw new InvalidDataException("Mark parameter limit.");var keys=new List<string>();
  for(uint i=0;i<count;i++)
  {
   N.Check(N.FPDFPageObjMark_GetParamKey(m,i,null,0,out uint n),"mark key length");if(n>256||n%2!=0)throw new InvalidDataException("Mark key limit.");byte[] b=new byte[n];
   N.Check(N.FPDFPageObjMark_GetParamKey(m,i,b,n,out _),"mark key");string key=Encoding.Unicode.GetString(b).TrimEnd('\0');if(key.Any(c=>c<32||c>126))throw new InvalidDataException("Mark key range.");keys.Add(key);
  }
  return keys.Order(StringComparer.Ordinal).ToArray();
 }
 static byte[] MarkBlob(IntPtr mark,string key,int max=MaxMarkBytes)
 {
  N.Check(N.FPDFPageObjMark_GetParamBlobValue(mark,key,null,0,out uint n),"mark blob length");if(n>max)throw new InvalidDataException("Mark payload limit.");
  byte[] bytes=new byte[n];N.Check(N.FPDFPageObjMark_GetParamBlobValue(mark,key,bytes,n,out uint used),"mark blob");if(used!=n)throw new InvalidDataException("Mark payload changed.");return bytes;
 }
 static string MarkSignature(IntPtr o,bool semanticsOnly=false)
 {
  int count=N.FPDFPageObj_CountMarks(o);if(count<0||count>16)throw new InvalidDataException("Content mark count limit.");var marks=new List<object>();
  for(uint i=0;i<count;i++)
  {
   var m=N.FPDFPageObj_GetMark(o,i);string name=MarkName(m);if(semanticsOnly&&name==ParagraphTag)continue;
   var values=new List<object>();foreach(string key in MarkKeys(m))
   {
    int type=N.FPDFPageObjMark_GetParamValueType(m,key);
    if(semanticsOnly&&(name!="Span"||key is not ("MCID" or "Lang")))throw new InvalidDataException("Existing marked-content semantics cannot safely be transferred.");
    if(type==2){N.Check(N.FPDFPageObjMark_GetParamFloatValue(m,key,out float value),"mark number");if(!float.IsFinite(value))throw new InvalidDataException("Nonfinite mark value.");values.Add(new{key,type,value});}
    else if(type==3){values.Add(new{key,type,blob=Convert.ToBase64String(MarkBlob(m,key))});}
    else throw new InvalidDataException("Unsupported marked-content property type.");
   }
   if(semanticsOnly&&name!="Span")throw new InvalidDataException("Unsupported existing semantic tag.");marks.Add(new{name,values});
  }
  return Wire.Write(marks);
 }
 static IntPtr[] SemanticHandles(IntPtr o)
 {
  var result=new List<IntPtr>();for(uint i=0;i<N.FPDFPageObj_CountMarks(o);i++){var mark=N.FPDFPageObj_GetMark(o,i);if(MarkName(mark)!=ParagraphTag)result.Add(mark);}return result.ToArray();
 }
 static void CopySemanticMarks(IntPtr source,IntPtr dest)
 {
  _=MarkSignature(source,true);for(uint i=0;i<N.FPDFPageObj_CountMarks(source);i++){var mark=N.FPDFPageObj_GetMark(source,i);if(MarkName(mark)!=ParagraphTag)N.Check(N.FPDFPageObj_AddExistingMark(dest,mark),"preserve existing content mark");}
 }
 static string MappingHash(Region r)=>Hash(Encoding.UTF8.GetBytes(Wire.Write(r.Characters)));
 static ParagraphManifest NewManifest(Region r,Layout layout,string text,IntPtr page,string semantics,ObjectState[] actual)
 {
  var p=layout.Positioned!;
  return new(1,r.Paragraph?.Evidence=="ValidatedEmbeddedParagraphDeclaration"?r.Paragraph.Id:Guid.NewGuid().ToString("N"),r.Page,N.FPDF_GetPageWidth(page),N.FPDF_GetPageHeight(page),text,r.FontHash,MappingHash(r),r.FontSize,r.R,r.G,r.B,r.X,r.Baseline,r.LineHeight,r.Ascent,
   new(r.X,r.Top,r.Positioned!.SafeRight-r.X,r.SafeBottom-r.Top),semantics,p.Lines.Select((l,i)=>new ParagraphRow(l.Text,l.Baseline,l.Origins.Select(v=>Math.Round(v,3)).ToArray(),actual[i].Glyphs.Select(g=>new[]{g.Bounds.X,g.Bounds.Y,g.Bounds.Width,g.Bounds.Height}.Select(v=>Math.Round(v,3)).ToArray()).ToArray())).ToArray());
 }
 static void WriteParagraphMark(IntPtr doc,IntPtr o,byte[] payload,int row)
 {
  if(payload.Length>MaxMarkBytes)throw new InvalidDataException("Paragraph payload exceeds limit.");var mark=N.FPDFPageObj_AddMark(o,ParagraphTag);if(mark==IntPtr.Zero)throw new IOException("Cannot add paragraph identification.");
  N.Check(N.FPDFPageObjMark_SetBlobParam(doc,o,mark,"Data",payload,(uint)payload.Length),"paragraph payload");N.Check(N.FPDFPageObjMark_SetIntParam(doc,o,mark,"Row",row),"paragraph row");
 }
 sealed record MarkClaim(int Index,int Row,string Payload,ParagraphManifest Manifest);
 static bool Close(double a,double b,double tolerance=.01)=>double.IsFinite(a)&&double.IsFinite(b)&&Math.Abs(a-b)<=tolerance;
 static void Require(bool condition,string message){if(!condition)throw new InvalidDataException(message);}
 static void ValidateManifest(ParagraphManifest m,int page,double w,double h)
 {
  Require(m.Version==1&&m.Id!=null&&m.Id.Length==32&&Guid.TryParseExact(m.Id,"N",out var id)&&id.ToString("N")==m.Id,"Paragraph schema/identifier.");
  Require(m.Page==page&&Close(m.PageWidth,w)&&Close(m.PageHeight,h),"Paragraph page binding.");
  Require(m.Text!=null&&m.Text.Length is >0 and <=512&&m.Text.All(c=>c>=32&&c<=126),"Paragraph character/length limit.");
  Require(m.FontHash is {Length:64}&&m.MappingHash is {Length:64}&&m.FontHash.All(Uri.IsHexDigit)&&m.MappingHash.All(Uri.IsHexDigit),"Paragraph font identity.");
  Require(m.Rows is {Length:>0 and <=8}&&m.Rows.All(l=>l!=null&&l.Text is {Length:>0}&&l.Origins!=null&&l.Bounds!=null&&l.Origins.Length==l.Text.Length&&l.Bounds.Length==l.Text.Length)&&string.Concat(m.Rows.Select(l=>l.Text))==m.Text,"Paragraph member/text sequence.");
  Require(m.SemanticMarks!=null&&m.SemanticMarks.Length<=4096&&m.FontSize>=6&&m.FontSize<=48&&m.R<=255&&m.G<=255&&m.B<=255&&Close(m.LineHeight,m.FontSize*1.5)&&m.Ascent>0&&m.Ascent<=m.FontSize*2,"Paragraph style.");
  Require(m.Envelope!=null&&Close(m.Envelope.X,m.X)&&Close(m.Envelope.Y,m.Baseline-m.Ascent)&&m.X>=0&&m.Envelope.Y>=0&&m.Envelope.Width>0&&double.IsFinite(m.Envelope.Width)&&double.IsFinite(m.Envelope.Height)&&m.Envelope.Height>0&&m.Envelope.Right<=w-Math.Max(20,m.X)+.01&&m.Envelope.Bottom<=h-20+.01,"Paragraph boundary claim.");
  foreach(var row in m.Rows)Require(double.IsFinite(row.Baseline)&&row.Origins.All(double.IsFinite)&&row.Bounds.All(b=>b is {Length:4}&&b.All(double.IsFinite)&&b[2]>=0&&b[3]>=0),"Paragraph finite geometry.");
 }
 List<Region> ReadParagraphGroups(IntPtr doc,IntPtr page,int pageIndex,IntPtr[] objects,List<Region> candidates,string fingerprint)
 {
  if(objects.Length>4096){foreach(var r in candidates)Limit(r,"EDITOR_PARAGRAPH_PAGE_OBJECT_BUDGET");return candidates;}
  var claims=new List<MarkClaim>();int bytes=0;var marked=new HashSet<int>();
  for(int i=0;i<objects.Length;i++)
  {
   try
   {
    int count=N.FPDFPageObj_CountMarks(objects[i]);Require(count>=0&&count<=16,"Mark count limit.");var own=new List<IntPtr>();
    for(uint k=0;k<count;k++){var mark=N.FPDFPageObj_GetMark(objects[i],k);if(MarkName(mark)==ParagraphTag)own.Add(mark);}
    if(own.Count==0)continue;marked.Add(i);Require(own.Count==1,"Duplicate paragraph marks.");var m=own[0];Require(MarkKeys(m).SequenceEqual(new[]{"Data","Row"}),"Paragraph parameter keys.");
    var blob=MarkBlob(m,"Data");bytes+=blob.Length;Require(bytes<=MaxPageMarkBytes,"Page metadata budget.");
    string payload=new UTF8Encoding(false,true).GetString(blob);var manifest=JsonSerializer.Deserialize<ParagraphManifest>(payload,MarkJson)??throw new InvalidDataException("Missing paragraph data.");
    // Duplicate JSON keys are not resolved by last-value-wins.
    using(var json=JsonDocument.Parse(payload,new JsonDocumentOptions{MaxDepth=16}))RejectDuplicateKeys(json.RootElement);
    ValidateManifest(manifest,pageIndex,N.FPDF_GetPageWidth(page),N.FPDF_GetPageHeight(page));
    int row=-1;Require(N.FPDFPageObjMark_GetParamValueType(m,"Row")==2&&N.FPDFPageObjMark_GetParamIntValue(m,"Row",out row)!=0,"Paragraph member index.");
    N.FPDFPageObjMark_GetParamFloatValue(m,"Row",out float exact);Require(exact==row&&row>=0&&row<manifest.Rows.Length,"Paragraph integer member index.");claims.Add(new(i,row,payload,manifest));
   }
   catch(Exception ex) when(ex is InvalidDataException or JsonException or InvalidOperationException or DecoderFallbackException or NullReferenceException)
   {marked.Add(i);foreach(var r in candidates.Where(r=>r.Objects.Contains(i))){Limit(r,"EDITOR_PARAGRAPH_INVALID_METADATA");r.Observed=r.Observed.Append("paragraph-diagnostic:"+ex.Message).ToArray();}}
  }
  if(bytes>MaxPageMarkBytes||claims.Count>1024||claims.Select(c=>c.Manifest.Id).Distinct().Count()>128)
  {foreach(var r in candidates.Where(r=>r.Objects.Any(marked.Contains)))Limit(r,"EDITOR_PARAGRAPH_PAGE_BUDGET");return candidates;}
  var result=new List<Region>();var accepted=new HashSet<int>();
  HashSet<string> conflicting=[];
  if(claims.Count>0)try{conflicting=ConflictingParagraphIds(doc,page,pageIndex,fingerprint);}
  catch(InvalidDataException){foreach(var r in candidates.Where(r=>r.Objects.Any(marked.Contains)))Limit(r,"EDITOR_PARAGRAPH_DOCUMENT_INDEX_BUDGET");return candidates;}
  foreach(var set in claims.GroupBy(c=>c.Manifest.Id))
  {
   try
   {
    var ordered=set.OrderBy(c=>c.Row).ToArray();var m=ordered[0].Manifest;
    Require(!conflicting.Contains(m.Id),"Paragraph identifier conflicts across pages.");
    Require(ordered.Length==m.Rows.Length&&ordered.Select(c=>c.Row).SequenceEqual(Enumerable.Range(0,m.Rows.Length))&&ordered.All(c=>c.Payload==ordered[0].Payload),"Missing, duplicate or conflicting paragraph members.");
    Require(ordered.Select(c=>c.Index).SequenceEqual(ordered.Select(c=>c.Index).Order()),"Paragraph member paint/reading sequence changed.");
    var members=ordered.Select(c=>candidates.SingleOrDefault(r=>r.Objects.Length==1&&r.Objects[0]==c.Index)??throw new InvalidDataException("Member is not a complete text object.")).ToArray();
    Require(members.All(r=>r.Reasons.All(reason=>reason is "NON_NATURAL_GLYPH_SPACING" or "INITIAL_OBJECT_RECONSTRUCTION_DIFFERS")),"Member structural/font guard failed.");
    var first=members[0];var f=N.FPDFTextObj_GetFont(objects[ordered[0].Index]);var ink=first.Positioned?.InkOffsets??new Box?[95];
    for(int c=32;c<=126;c++)if(c!=32&&first.Advances[c-32]>=0&&ink[c-32]==null)ink[c-32]=MeasureGlyphInk(doc,page,f,(char)c,first.FontSize);
    double inkHeight=ink.Where(b=>b!=null).Max(b=>b!.Bottom)-ink.Where(b=>b!=null).Min(b=>b!.Y),leading=Math.Max(2*m.FontSize,inkHeight+3);
    var glyphs=new List<Glyph>();var lines=new List<PositionedLine>();int start=0;
    for(int i=0;i<members.Length;i++)
    {
     var r=members[i];var row=m.Rows[i];var o=objects[ordered[i].Index];N.FPDFPageObj_GetMatrix(o,out var matrix);
     Require(r.OriginalText==row.Text&&r.FontHash==m.FontHash&&MappingHash(r)==m.MappingHash&&Close(r.FontSize,m.FontSize,.001)&&r.R==m.R&&r.G==m.G&&r.B==m.B&&Close(r.Ascent,m.Ascent)&&Close(r.X,m.X)&&Close(r.Baseline,m.Baseline+i*leading)&&Close(row.Baseline,r.Baseline),"Paragraph text/font/style/baseline mismatch.");
     Require(MarkSignature(o,true)==m.SemanticMarks&&SemanticHandles(o).SequenceEqual(SemanticHandles(objects[ordered[0].Index]))&&r.Glyphs.Length==row.Text.Length&&row.Text.All(c=>r.Advances[c-32]>=0),"Paragraph semantic marks or character mapping changed.");
     var relative=r.Glyphs.Skip(1).Select(g=>(float)(g.OriginX-r.X)).ToArray();Require(OriginalReconstructionMatches(doc,page,o,row.Text,matrix,m.R,m.G,m.B,relative),"Paragraph exact row reconstruction failed.");
     for(int j=0;j<r.Glyphs.Length;j++)
     {
      var g=r.Glyphs[j];Require(g.Text==row.Text[j].ToString()&&Close(g.OriginX,row.Origins[j])&&Close(g.Baseline,row.Baseline)&&BoxShift(g.Bounds,new(row.Bounds[j][0],row.Bounds[j][1],row.Bounds[j][2],row.Bounds[j][3]))<=.01, $"Paragraph claimed glyph geometry differs at row {i}, character {j} ({(int)row.Text[j]}): X={g.OriginX-row.Origins[j]}, Y={g.Baseline-row.Baseline}, box={BoxShift(g.Bounds,new(row.Bounds[j][0],row.Bounds[j][1],row.Bounds[j][2],row.Bounds[j][3]))}.");
      Require(j==0?Close(g.OriginX,m.X):g.OriginX>r.Glyphs[j-1].OriginX,"Paragraph row origin ordering.");
      Require(N.FPDFFont_GetGlyphWidth(N.FPDFTextObj_GetFont(o),row.Text[j],(float)m.FontSize,out float advance)!=0&&Close(advance,r.Advances[row.Text[j]-32]),"Paragraph font metric mismatch.");
      glyphs.Add(g with{Index=start+j});
     }
     lines.Add(new(start,row.Text,r.Baseline,r.Glyphs.Select(g=>g.OriginX).ToArray(),relative,r.Glyphs.Select(g=>g.Bounds).ToArray()));start+=row.Text.Length;
    }
    var bounds=members.Select(r=>r.ObservedBounds!).ToArray();double left=bounds.Min(b=>b.X),top=bounds.Min(b=>b.Y),right=bounds.Max(b=>b.Right),bottom=bounds.Max(b=>b.Bottom);
    var group=first with{Id=$"p{pageIndex}-g{m.Id}",Name="Verified editor paragraph",Objects=ordered.Select(c=>c.Index).ToArray(),OriginalLines=m.Rows.Select(l=>l.Text).ToArray(),LogicalText=m.Text,Glyphs=glyphs.ToArray(),ObservedBounds=new(left,top,right-left,bottom-top),Width=m.Envelope.Width,SafeBottom=m.Envelope.Bottom,Eligibility="Editable",Reasons=[],Paragraph=new(m.Id,"ValidatedEmbeddedParagraphDeclaration",Hash(Encoding.UTF8.GetBytes(ordered[0].Payload)),m.Envelope,m.SemanticMarks),Observed=first.Observed.Append("EDITOR_PARAGRAPH_MEMBERS_TEXT_FONT_GEOMETRY_VERIFIED").ToArray(),Inferred=["Editor-generated membership validated against actual page content; not inferred from proximity."]};
    group.Positioned=new(glyphs.ToArray(),lines[0].RelativePositions,"ValidatedEditorParagraph","Actual original-font mappings, row bitmaps and claimed glyph geometry verified.",[]){SafeRight=m.Envelope.Right,InkOffsets=ink,CoexistingWhitespace=ObserveNonPaintingSpaces(page),SourceLines=lines.ToArray()};
    Require(PositionLayout.SourceLayout(group).LineBoxes.All(b=>b.X>=m.Envelope.X-.01&&b.Right<=m.Envelope.Right+.01&&b.Bottom<=m.Envelope.Bottom+.01),"Paragraph source leaves envelope.");
    result.Add(group);foreach(var c in ordered)accepted.Add(c.Index);
   }
   catch(Exception ex) when(ex is InvalidDataException or InvalidOperationException or NullReferenceException)
   {foreach(var c in set)foreach(var r in candidates.Where(r=>r.Objects.Contains(c.Index))){Limit(r,"EDITOR_PARAGRAPH_INCONSISTENT_MEMBERS");r.Observed=r.Observed.Append("paragraph-diagnostic:"+ex.Message).ToArray();}}
  }
  // Marked members never fall back to proximity-based paragraph inference.
  foreach(var r in candidates.Where(r=>r.Objects.Any(marked.Contains)&&!r.Objects.Any(accepted.Contains)))Limit(r,"EDITOR_PARAGRAPH_GROUP_REJECTED");
  candidates.RemoveAll(r=>r.Objects.Any(accepted.Contains));candidates.AddRange(result);return candidates;
 }
 static void RejectDuplicateKeys(JsonElement value)
 {
  if(value.ValueKind==JsonValueKind.Object){var names=new HashSet<string>(StringComparer.Ordinal);foreach(var p in value.EnumerateObject()){Require(names.Add(p.Name),"Duplicate paragraph JSON key.");RejectDuplicateKeys(p.Value);}}
  else if(value.ValueKind==JsonValueKind.Array)foreach(var item in value.EnumerateArray())RejectDuplicateKeys(item);
 }
}
