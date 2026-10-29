using System.Runtime.InteropServices;
using System.Text;
namespace PdfPrototype;
internal static partial class N
{
 [DllImport("pdfium.dll")] public static extern IntPtr FPDF_StructTree_GetForPage(IntPtr page);
 [DllImport("pdfium.dll")] public static extern void FPDF_StructTree_Close(IntPtr tree);
 [DllImport("pdfium.dll")] public static extern int FPDF_StructTree_CountChildren(IntPtr tree);
 [DllImport("pdfium.dll")] public static extern IntPtr FPDF_StructTree_GetChildAtIndex(IntPtr tree,int index);
 [DllImport("pdfium.dll")] public static extern int FPDF_StructElement_CountChildren(IntPtr element);
 [DllImport("pdfium.dll")] public static extern IntPtr FPDF_StructElement_GetChildAtIndex(IntPtr element,int index);
 [DllImport("pdfium.dll")] public static extern int FPDF_StructElement_GetChildMarkedContentID(IntPtr element,int index);
 [DllImport("pdfium.dll")] public static extern uint FPDF_StructElement_GetType(IntPtr element,[Out]byte[]? buffer,uint size);
 [DllImport("pdfium.dll")] public static extern uint FPDF_StructElement_GetActualText(IntPtr element,[Out]byte[]? buffer,uint size);
 [DllImport("pdfium.dll")] public static extern int FPDF_StructElement_GetAttributeCount(IntPtr element);
}
public sealed partial class PdfEngine
{
 static string StructureType(IntPtr e)
 {
  uint n=N.FPDF_StructElement_GetType(e,null,0);Require(n is >0 and <=256&&n%2==0,"Original structure type limit.");
  var bytes=new byte[n];N.FPDF_StructElement_GetType(e,bytes,n);return Encoding.Unicode.GetString(bytes).TrimEnd('\0');
 }
 // This deliberately accepts only Document -> P -> one page-scoped MCID.
 // PDFium loads the page tree through StructParents/ParentTree, not proximity.
 static HashSet<int> OriginalParagraphMcids(IntPtr page)
 {
  var tree=N.FPDF_StructTree_GetForPage(page);if(tree==IntPtr.Zero)return [];
  try
  {
   var ids=new HashSet<int>();var duplicate=new HashSet<int>();int nodes=0;
   int roots=N.FPDF_StructTree_CountChildren(tree);Require(roots==1,"Original paragraph requires one Document root.");
   var root=N.FPDF_StructTree_GetChildAtIndex(tree,0);Require(root!=IntPtr.Zero&&StructureType(root)=="Document","Original Document scope unsupported.");
   int count=N.FPDF_StructElement_CountChildren(root);Require(count>=0&&count<=4096,"Original structure budget.");
   for(int i=0;i<count;i++)
   {
    var e=N.FPDF_StructElement_GetChildAtIndex(root,i);if(e==IntPtr.Zero)continue;
    Require(++nodes<=4096,"Original structure node budget.");
    if(StructureType(e)!="P"||N.FPDF_StructElement_CountChildren(e)!=1||N.FPDF_StructElement_GetChildAtIndex(e,0)!=IntPtr.Zero||N.FPDF_StructElement_GetActualText(e,null,0)>0||N.FPDF_StructElement_GetAttributeCount(e)>0)continue;
    int id=N.FPDF_StructElement_GetChildMarkedContentID(e,0);if(id<0)continue;if(!ids.Add(id))duplicate.Add(id);
   }
   ids.ExceptWith(duplicate);return ids;
  }
  finally{N.FPDF_StructTree_Close(tree);}
 }
 static int OriginalMcid(IntPtr o)
 {
  var marks=SemanticHandles(o);if(marks.Length!=1||MarkName(marks[0])!="Span")return -1;
  if(N.FPDFPageObjMark_GetParamIntValue(marks[0],"MCID",out int id)==0||id<0)return -1;
  N.FPDFPageObjMark_GetParamFloatValue(marks[0],"MCID",out float exact);return exact==id?id:-1;
 }
 readonly Dictionary<string,(HashSet<int> Ids,string Diagnostic)> originalParagraphScopes=[];
 List<Region> ReadOriginalParagraphs(IntPtr doc,IntPtr page,int pageIndex,IntPtr[] objects,List<Region> candidates,string fingerprint,string source)
 {
  if(objects.Length>4096)return candidates;
  var claimed=new HashSet<int>();var result=new List<Region>();
  var sets=candidates.Where(r=>r.Paragraph==null&&r.Objects.Length==1).GroupBy(r=>OriginalMcid(objects[r.Objects[0]])).Where(g=>g.Key>=0&&g.Count()>1).Take(129).ToArray();
  if(sets.Length==0)return candidates;
  string key=fingerprint+":"+pageIndex;
  if(!originalParagraphScopes.TryGetValue(key,out var scope))
  {
   var supported=new HashSet<int>();string diagnostic="";
   try{supported=OriginalParagraphMcids(page);supported.IntersectWith(new OriginalStructureProof(source).Mcids(pageIndex));}
   catch(Exception ex) when(ex is InvalidDataException or KeyNotFoundException or FormatException or OverflowException or ArgumentException or IOException){supported=[];diagnostic=ex.Message;}
   scope=(supported,diagnostic);if(originalParagraphScopes.Count>=8)originalParagraphScopes.Clear();originalParagraphScopes[key]=scope;
  }
  string structureDiagnostic=scope.Diagnostic;var spaces=ObserveNonPaintingSpaces(page).ToHashSet();
  if(sets.Length>128){foreach(var s in sets)foreach(var r in s)Limit(r,"ORIGINAL_PARAGRAPH_GROUP_BUDGET");return candidates;}
  foreach(var set in sets)
  {
   var members=set.OrderBy(r=>r.Objects[0]).ToArray();
   try
   {
    Require(scope.Ids.Contains(set.Key),"ORIGINAL_PARAGRAPH_STRUCTURAL_SCOPE_UNPROVEN");
    Require(members.Length is >=2 and <=8&&members.All(r=>r.Eligibility=="Editable"&&r.Positioned!=null&&r.Reasons.Length==0),"ORIGINAL_PARAGRAPH_MEMBER_GUARD");
    var first=members[0];string semantics=MarkSignature(objects[first.Objects[0]],true);var handles=SemanticHandles(objects[first.Objects[0]]);
    Require(members.All(r=>r.FontHash==first.FontHash&&MappingHash(r)==MappingHash(first)&&Close(r.FontSize,first.FontSize,.001)&&r.R==first.R&&r.G==first.G&&r.B==first.B&&Close(r.X,first.X)&&MarkSignature(objects[r.Objects[0]],true)==semantics&&SemanticHandles(objects[r.Objects[0]]).SequenceEqual(handles)),"ORIGINAL_PARAGRAPH_STYLE_OR_SCOPE_MISMATCH");
    // A second occurrence of the numeric MCID in a different native scope is a conflict.
    var indices=members.Select(r=>r.Objects[0]).ToArray();
    for(int i=0;i<objects.Length;i++)if(OriginalMcid(objects[i])==set.Key&&!indices.Contains(i))
     Require(spaces.Contains(i)&&i>indices[^1]&&SemanticHandles(objects[i]).SequenceEqual(handles),"ORIGINAL_PARAGRAPH_EXTRA_SCOPE_CONTENT");
    Require(indices.SequenceEqual(Enumerable.Range(indices[0],indices.Length)),"ORIGINAL_PARAGRAPH_INTERLEAVED_PAINT_ORDER");
    string text=string.Concat(members.Select(r=>r.OriginalText));Require(text.Length<=512,"ORIGINAL_PARAGRAPH_TEXT_BUDGET");
    Require(members.Take(members.Length-1).All(r=>r.OriginalText.EndsWith(' ')&&!r.OriginalText.EndsWith("  "))&&members.All(r=>!r.OriginalText.StartsWith(' ')),"ORIGINAL_PARAGRAPH_SEPARATOR_AMBIGUOUS");
    double gap=members[1].Baseline-first.Baseline;Require(gap>=first.FontSize&&gap<=first.FontSize*2,"ORIGINAL_PARAGRAPH_LEADING_UNSUPPORTED");
    Require(members.Skip(1).Select((r,i)=>Math.Abs(r.Baseline-members[i].Baseline-gap)).All(d=>d<=.15),"ORIGINAL_PARAGRAPH_READING_ORDER_OR_LEADING");
    double w=N.FPDF_GetPageWidth(page),h=N.FPDF_GetPageHeight(page),right=w-Math.Max(20,first.X);
    Require(members.Take(members.Length-1).All(r=>r.ObservedBounds!.Width>=(right-first.X)*.5),"ORIGINAL_PARAGRAPH_SHORT_ROW_BOUNDARY");
    var lines=new List<PositionedLine>();var glyphs=new List<Glyph>();int start=0;
    foreach(var r in members)
    {
     var gs=r.Glyphs;Require(gs.Length==r.OriginalText.Length,"ORIGINAL_PARAGRAPH_GLYPH_OWNERSHIP");
     var relative=gs.Skip(1).Select(g=>(float)(g.OriginX-r.X)).ToArray();
     lines.Add(new(start,r.OriginalText,r.Baseline,gs.Select(g=>g.OriginX).ToArray(),relative,gs.Select(g=>g.Bounds).ToArray()));glyphs.AddRange(gs.Select((g,j)=>g with{Index=start+j}));start+=gs.Length;
    }
    var boxes=members.Select(r=>r.ObservedBounds!).ToArray();double x=boxes.Min(b=>b.X),y=boxes.Min(b=>b.Y),bott=boxes.Max(b=>b.Bottom);
    var envelope=new Box(first.X,first.Top,right-first.X,h-20-first.Top);string proof=$"Document/P/MCID:{set.Key};members:{string.Join(',',indices)};semantics:{semantics}";
    string hash=Hash(Encoding.UTF8.GetBytes(proof));
    var group=first with{Id=$"p{pageIndex}-original-{set.Key}",Name="Verified source paragraph",Objects=indices,OriginalLines=members.Select(r=>r.OriginalText).ToArray(),LogicalText=text,Glyphs=glyphs.ToArray(),ObservedBounds=new(x,y,boxes.Max(b=>b.Right)-x,bott-y),Width=envelope.Width,Paragraph=new(hash[..32],"ExistingDocumentParagraphSingleMcid",hash,envelope,semantics),Observed=members.SelectMany(r=>r.Observed).Append(proof).Append("ORIGINAL_PARAGRAPH_EXPLICIT_SOURCE_SPACES").ToArray(),Inferred=["Source P scope establishes structural membership. Uniform horizontal rows support bounded reflow. Authoring intent outside this supported scope is unknown."]};
    group.Positioned=first.Positioned! with{OriginalGlyphs=glyphs.ToArray(),RelativePositions=lines[0].RelativePositions,SourceLines=lines.ToArray(),SafeRight=right,CoexistingWhitespace=spaces.ToArray(),Strategy="ExistingStructuredParagraph"};
    result.Add(group);foreach(int i in indices)Require(claimed.Add(i),"ORIGINAL_PARAGRAPH_OWNERSHIP_CONFLICT");
   }
   catch(InvalidDataException ex){foreach(var r in members){Limit(r,ex.Message);r.Observed=r.Observed.Append("original-paragraph-diagnostic:"+ex.Message+";"+structureDiagnostic).ToArray();}}
  }
  candidates.RemoveAll(r=>r.Objects.Any(claimed.Contains));candidates.AddRange(result);return candidates;
 }
}
