using System.Text;
namespace PdfPrototype;
public sealed partial class PdfEngine
{
 sealed record Target(Region Region,RegionChange Change,Layout Layout,IntPtr Font)
 { public List<IntPtr> Added {get;}=[];public int[] SavedIndices {get;set;}=[];public byte[]? ParagraphPayload {get;set;} public string Semantics {get;set;}=""; }
 sealed class TransactionPage : IDisposable
 {
  public required Page Page;public required int Index;public required Target[] Targets;
  public required IntPtr[] OriginalObjects;public required HashSet<int> Excluded;
  public int[] PreservedIndices=[];
  public required ObjectState[] Neighbours;public required int[] ProtectedIndices;
  public void Dispose()=>Page.Dispose();
 }
 static Box Allowed(Target t)
 {
  var r=t.Region;double bottom=Math.Max(r.Top+t.Layout.Height,r.Top+(r.Paragraph==null?r.OriginalLines.Length*r.LineHeight:PositionLayout.SourceLayout(r).Height))+2;
  double right=r.Positioned==null?r.X+r.Width:Math.Max(r.ObservedBounds!.Right,t.Layout.LineBoxes.Select(b=>b.Right).DefaultIfEmpty(r.X).Max());
  return new(r.X-2,r.Top-2,right-r.X+4,bottom-r.Top+2);
 }
 public static RegionValidation[] CombinedCollisions((Region Region,Layout Layout)[] plans)
 {
  var result=new List<RegionValidation>();
  for(int i=0;i<plans.Length;i++)for(int j=i+1;j<plans.Length;j++)
   if(plans[i].Region.Page==plans[j].Region.Page&&plans[i].Layout.LineBoxes.Any(a=>plans[j].Layout.LineBoxes.Any(b=>a.Intersects(b,.5))))
    foreach(var k in new[]{i,j})result.Add(new(DocumentSession.Key(plans[k].Region.Page,plans[k].Region.Id),"Blocked","These two changed text areas overlap. Both drafts have been kept."));
  return result.Distinct().ToArray();
 }
 EditResult EditDocument(EditRequest req)
 {
  long transactionStart=System.Diagnostics.Stopwatch.GetTimestamp();
  string source=Path.GetFullPath(req.Source);if(Wire.Hash(source)!=req.ExpectedHash)throw new IOException("Source changed on disk. All drafts retained; reopen deliberately.");
  var changes=req.Changes!;
  if(changes.Length==0)return new(req.Revision,false,"No changed text areas to export.",null,null);
  if(changes.Length>128)throw new IOException("This version validates at most 128 changed text areas per export. All drafts retained.");
  if(changes.Select(c=>DocumentSession.Key(c.Page,c.RegionId)).Distinct().Count()!=changes.Length)throw new IOException("Duplicate source region reference.");
  Directory.CreateDirectory(req.Work);using var d=new Doc(source);var pages=new List<TransactionPage>();var failures=new List<RegionValidation>();
  try
  {
   // Resolve every identity/pointer from the same original document before
   // inserting/removing anything. Never rediscover an intermediate candidate.
   foreach(var group in changes.GroupBy(c=>c.Page).OrderBy(g=>g.Key))
   {
    if(group.Key<0||group.Key>=N.FPDF_GetPageCount(d.Handle))throw new IOException("Invalid source page reference.");
    var page=new Page(d.Handle,group.Key);bool owned=false;
    try
    {
     Region[] regions;
     if(File.Exists(source+".region.json")){var r=Owned(source,d.Handle,page.Handle,group.Key,out _);regions=r==null?[]:[r];}
     else regions=Discover(d.Handle,page.Handle,group.Key,req.ExpectedHash,req.Work,source);
     var targets=new List<Target>();var excluded=new HashSet<int>();var objects=Objects(page.Handle);
     foreach(var change in group)
     {
      string key=DocumentSession.Key(change.Page,change.RegionId);
      var r=regions.SingleOrDefault(r=>r.Id==change.RegionId&&r.Eligibility=="Editable");
      if(r==null||DocumentSession.Identity(r)!=change.Identity)throw new IOException("A changed text area no longer matches its original source identity. All drafts retained.");
      if(r.Objects.Any(i=>!excluded.Add(i)))throw new IOException("Changed areas share original content ownership.");
      if(r.Positioned!=null&&Wire.Hash(Path.Combine(AppContext.BaseDirectory,"pdfium.dll"))!=PositionBinaryHash)throw new IOException("Position editing requires the verified native binary.");
      var layout=ParagraphLayout.Plan(r,change.Text);
      if(change.Text==r.OriginalText)throw new IOException("An unchanged region was submitted as a modification.");
      if(!layout.Safe)failures.Add(new(key,"Blocked",layout.Diagnostic));
      string semantic=MarkSignature(objects[r.Objects[0]],true);
      if(r.Objects.Any(i=>MarkSignature(objects[i],true)!=semantic||!SemanticHandles(objects[i]).SequenceEqual(SemanticHandles(objects[r.Objects[0]]))))throw new IOException("This region spans different existing accessibility marks; editing is restricted.");
      targets.Add(new(r,change,layout,N.FPDFTextObj_GetFont(objects[r.Objects[0]])){Semantics=semantic});
     }
     var state=new TransactionPage{Page=page,Index=group.Key,Targets=targets.ToArray(),OriginalObjects=objects,Excluded=excluded,Neighbours=Snapshot(page.Handle,excluded),ProtectedIndices=Enumerable.Range(0,objects.Length).Where(i=>!excluded.Contains(i)).ToArray()};pages.Add(state);owned=true;
    }
    finally{if(!owned)page.Dispose();}
   }
   if(failures.Count>0)return new(req.Revision,false,$"{failures.Count} changed text area(s) need attention. All drafts kept; nothing saved.",null,null){Regions=failures.ToArray()};
   failures.AddRange(CombinedCollisions(pages.SelectMany(p=>p.Targets).Select(t=>(t.Region,t.Layout)).ToArray()));
   foreach(var p in pages)foreach(var t in p.Targets)
   {
    var protectedObjects=p.Neighbours.Where((o,k)=>!(t.Region.Positioned?.CoexistingWhitespace.Contains(p.ProtectedIndices[k])??false));
    if(t.Layout.LineBoxes.Any(box=>protectedObjects.Any(o=>box.Intersects(o.Bounds,.5))))failures.Add(new(DocumentSession.Key(t.Region.Page,t.Region.Id),"Blocked","A changed text area reaches protected content. All drafts have been kept."));
   }
   if(failures.Count>0)return new(req.Revision,false,"Changed areas conflict with each other or protected content. All drafts kept; nothing saved.",null,null){Regions=failures.Distinct().ToArray()};
   double planningMs=System.Diagnostics.Stopwatch.GetElapsedTime(transactionStart).TotalMilliseconds;long candidateStart=System.Diagnostics.Stopwatch.GetTimestamp();
   foreach(var p in pages)
   {
    double h=N.FPDF_GetPageHeight(p.Page.Handle);
    foreach(var t in p.Targets)
    {
     var r=t.Region;
     for(int i=0;i<t.Layout.Lines.Length;i++)
     {
      string text=t.Layout.Lines[i];if(text.Length==0)continue;
      var o=N.FPDFPageObj_CreateTextObj(d.Handle,t.Font,(float)r.FontSize);if(o==IntPtr.Zero)throw new IOException("Cannot create original-font text.");bool inserted=false;
      try
      {
       N.Check(N.FPDFText_SetText(o,Encoding.Unicode.GetBytes(text+"\0")),"combined text");
       if(r.Positioned!=null&&t.Layout.Positioned!.Lines[i].RelativePositions.Length>0)N.Check(N.FPDFText_SetPositions(o,t.Layout.Positioned!.Lines[i].RelativePositions,(nuint)t.Layout.Positioned.Lines[i].RelativePositions.Length),"combined positions");
       CopySemanticMarks(p.OriginalObjects[r.Objects[0]],o);
       N.Check(N.FPDFPageObj_SetFillColor(o,r.R,r.G,r.B,255),"combined style");N.FPDFPageObj_Transform(o,1,0,0,1,r.X,h-(t.Layout.Positioned?.Lines[i].Baseline??(r.Baseline+i*r.LineHeight)));int anchor=Array.IndexOf(Objects(p.Page.Handle),p.OriginalObjects[r.Objects[0]]);if(anchor<0)throw new IOException("Original insertion anchor missing.");
       // The API takes ownership even on failure. Insert before the still-live
       // source object so the new run adopts its content stream and tag scope.
       inserted=true;N.Check(N.FPDFPage_InsertObjectAtIndex(p.Page.Handle,o,(nuint)anchor),"insert replacement at source position");t.Added.Add(o);
      }
      finally{if(!inserted)N.FPDFPageObj_Destroy(o);}
     }
    }
    foreach(int index in p.Excluded){var o=p.OriginalObjects[index];N.Check(N.FPDFPage_RemoveObject(p.Page.Handle,o),"combined original removal");N.FPDFPageObj_Destroy(o);}
    // Verify the source-relative order without detaching unrelated objects.
    // Existing shared MCID sequences remain at the same source position.
    var ordered=new List<IntPtr>();
    for(int k=0;k<p.OriginalObjects.Length;k++)
    {
     var target=p.Targets.SingleOrDefault(t=>t.Region.Objects[0]==k);
     if(target!=null){target.SavedIndices=Enumerable.Range(ordered.Count,target.Added.Count).ToArray();ordered.AddRange(target.Added);}
     if(!p.Excluded.Contains(k))ordered.Add(p.OriginalObjects[k]);
    }
    p.PreservedIndices=ordered.Select((o,k)=>(o,k)).Where(v=>!p.Targets.Any(t=>t.Added.Contains(v.o))).Select(v=>v.k).ToArray();
    if(!Objects(p.Page.Handle).SequenceEqual(ordered))throw new IOException("Replacement object order differs from original source sequence.");
    var actual=Snapshot(p.Page.Handle);
    foreach(var t in p.Targets.Where(t=>t.Region.Positioned!=null&&t.Change.Text.Length is >0 and <=PositionLayout.MaxCharacters))
    {
     t.ParagraphPayload=System.Text.Json.JsonSerializer.SerializeToUtf8Bytes(NewManifest(t.Region,t.Layout,t.Change.Text,p.Page.Handle,t.Semantics,t.SavedIndices.Select(i=>actual[i]).ToArray()),MarkJson);
     for(int i=0;i<t.Added.Count;i++)WriteParagraphMark(d.Handle,t.Added[i],t.ParagraphPayload,i);
    }
    N.Check(N.FPDFPage_GenerateContent(p.Page.Handle),"combined content generation");
   }
   string token=Guid.NewGuid().ToString("N"),candidate=Path.Combine(req.Work,"candidate-"+token+".pdf");Save(d.Handle,candidate); // one candidate, one save
   double candidateGenerationMs=System.Diagnostics.Stopwatch.GetElapsedTime(candidateStart).TotalMilliseconds;long verifyStart=System.Diagnostics.Stopwatch.GetTimestamp();
   var reports=new List<object>();var images=new Dictionary<int,string>();
   using(var reopened=new Doc(candidate))using(var original=new Doc(source))
   {
    if(N.FPDF_GetPageCount(original.Handle)!=N.FPDF_GetPageCount(reopened.Handle))throw new IOException("Combined page count changed.");
    foreach(string tag in new[]{"Title","Author","Subject","Keywords","Creator","Producer","CreationDate","ModDate"})if(N.Meta(original.Handle,tag)!=N.Meta(reopened.Handle,tag))throw new IOException("Combined metadata changed.");
    for(int index=0;index<N.FPDF_GetPageCount(original.Handle);index++)
    {
     using var before=new Page(original.Handle,index);using var after=new Page(reopened.Handle,index);
     if(N.FPDF_GetPageWidth(before.Handle)!=N.FPDF_GetPageWidth(after.Handle)||N.FPDF_GetPageHeight(before.Handle)!=N.FPDF_GetPageHeight(after.Handle)||N.FPDFPage_GetAnnotCount(before.Handle)!=N.FPDFPage_GetAnnotCount(after.Handle))throw new IOException("Combined page dimensions or annotation count changed.");
     var p=pages.SingleOrDefault(p=>p.Index==index);
     if(p==null){if(!Pixels(before.Handle,1,out _,out _).SequenceEqual(Pixels(after.Handle,1,out _,out _)))throw new IOException("Unmodified page changed.");continue;}
     var observed=Snapshot(after.Handle);var pointers=Objects(after.Handle);
     if(observed.Length!=p.Neighbours.Length+p.Targets.Sum(t=>t.Added.Count))throw new IOException("Combined original removal/object count failed.");
     double neighbourShift=VerifyPreserved(p.Neighbours,p.PreservedIndices.Select(i=>observed[i]).ToArray());
     var renderedTargets=new Dictionary<Target,ObjectState[]>();
     foreach(var t in p.Targets)
     {
      var runs=t.SavedIndices.Select(i=>observed[i]).ToArray();renderedTargets[t]=runs;
      VerifyTarget(reopened.Handle,after.Handle,pointers,t,runs,p);
     }
     if(p.Targets.Any(t=>t.ParagraphPayload!=null))
     {
      var rediscovered=Discover(reopened.Handle,after.Handle,index,Wire.Hash(candidate),req.Work,candidate);
      foreach(var t in p.Targets.Where(t=>t.ParagraphPayload!=null))
      {
       var manifest=System.Text.Json.JsonSerializer.Deserialize<ParagraphManifest>(t.ParagraphPayload!,MarkJson)!;
       var grouped=rediscovered.SingleOrDefault(r=>r.Paragraph?.Id==manifest.Id&&r.Eligibility=="Editable");
       if(grouped==null||grouped.OriginalText!=t.Change.Text||!grouped.Objects.SequenceEqual(t.SavedIndices))throw new IOException("Candidate paragraph identification did not survive independent source rediscovery.");
      }
     }
     // Check actual saved ink, not only the proposed layout rectangles.
     foreach(var t in p.Targets)
     {
      var others=p.Targets.Where(x=>x!=t).SelectMany(x=>renderedTargets[x]).Select(x=>x.Bounds);
      var protectedBoxes=p.Neighbours.Where((o,k)=>!(t.Region.Positioned?.CoexistingWhitespace.Contains(p.ProtectedIndices[k])??false)).Select(o=>o.Bounds);
      foreach(var run in renderedTargets[t])if(others.Concat(protectedBoxes).Any(box=>run.Bounds.Intersects(box,.5)))throw new IOException("Saved changed areas or protected content overlap. All drafts retained.");
     }
     byte[] a=Pixels(before.Handle,2,out int width,out int height),b=Pixels(after.Handle,2,out _,out _);int outside=0,changed=0;var allowed=p.Targets.Select(Allowed).ToArray();
     for(int y=0;y<height;y++)for(int x=0;x<width;x++){int offset=(y*width+x)*4;int delta=Math.Max(Math.Abs(a[offset]-b[offset]),Math.Max(Math.Abs(a[offset+1]-b[offset+1]),Math.Abs(a[offset+2]-b[offset+2])));if(delta>8){changed++;if(!allowed.Any(box=>box.Contains(x/2.0,y/2.0)))outside++;}}
     if(outside!=0)throw new IOException("Combined rendering changed pixels outside all authorised areas.");
     if(index==req.Page){string png=Path.Combine(req.Work,$"candidate-{token}-p{index}.png");Render(after.Handle,png,2);images[index]=png;}
     reports.Add(new{page=index,regions=p.Targets.Select(t=>new{key=DocumentSession.Key(t.Region.Page,t.Region.Id),sourceIdentity=t.Change.Identity,t.Change.Text,strategy=t.Region.Positioned==null?"Natural":"Positioned",layout=t.Layout,allowed=Allowed(t),originalObjects=t.Region.Objects,replacementObjects=t.Added.Count,replacementIndices=t.SavedIndices,paragraphId=t.ParagraphPayload==null?null:System.Text.Json.JsonSerializer.Deserialize<ParagraphManifest>(t.ParagraphPayload,MarkJson)!.Id}),maxNeighbourGeometryAndGlyphShiftPt=neighbourShift,outsidePixels144Dpi=outside,changedPixels144Dpi=changed});
    }
   }
   if(Wire.Hash(source)!=req.ExpectedHash)throw new IOException("Source changed during transaction. No output committed.");
   var verification=new{method="single source-bound multi-region transaction",sourceHash=req.ExpectedHash,candidateHash=Wire.Hash(candidate),revision=req.Revision,changedRegions=changes.Length,originalObjectsRemoved=pages.Sum(p=>p.Excluded.Count),singleCandidateSave=true,timingsMs=new{planning=planningMs,candidateGeneration=candidateGenerationMs,reopenVerification=System.Diagnostics.Stopwatch.GetElapsedTime(verifyStart).TotalMilliseconds},allModificationsVerified=true,fontProgramsAndOutlinesVerified=true,pages=reports};
   string? destination=null;
   if(req.Command=="save")
   {
    destination=Path.GetFullPath(req.Destination);if(string.Equals(destination,source,StringComparison.OrdinalIgnoreCase)||File.Exists(destination))throw new IOException("Original and existing destinations are protected. Choose a new filename.");
    string dir=Path.GetDirectoryName(destination)!;Directory.CreateDirectory(dir);string stage=Path.Combine(dir,".pdf-prototype-"+token+".tmp");
    try{File.Copy(candidate,stage,false);if(Wire.Hash(stage)!=Wire.Hash(candidate)||Wire.Hash(source)!=req.ExpectedHash)throw new IOException("Staged checksum/source verification failed.");File.Move(stage,destination,false);}
    finally{if(File.Exists(stage))File.Delete(stage);}
   }
   TrimCandidates(req.Work,token);
   return new(req.Revision,true,destination==null?"All changed text areas verified together. Drafts retained.":"All changed text areas saved together. Source and working drafts retained.",images.GetValueOrDefault(req.Page),verification,destination){Regions=changes.Select(c=>new RegionValidation(DocumentSession.Key(c.Page,c.RegionId),"Verified","Combined candidate verified.")).ToArray(),ProposedTextEligibility="Supported"};
  }
  finally{foreach(var p in pages)p.Dispose();}
 }
 static void TrimCandidates(string work,string current)
 {
  // Only this worker's candidate prefix in the caller-owned work directory.
  try
  {
   foreach(string pattern in new[]{"candidate-*.pdf","candidate-*.png"})foreach(var f in new DirectoryInfo(work).GetFiles(pattern).OrderByDescending(f=>f.LastWriteTimeUtc).Skip(12))
    if(!f.Name.Contains(current,StringComparison.Ordinal))try{f.Delete();}catch(IOException){}catch(UnauthorizedAccessException){}
  }
  catch(IOException){}catch(UnauthorizedAccessException){}
 }
 static double VerifyPreserved(ObjectState[] before,ObjectState[] after)
 {
  if(before.Length!=after.Length)throw new IOException("Preserved object count changed.");double max=0;
  for(int i=0;i<before.Length;i++)
  {
   var a=before[i];var b=after[i];double shift=BoxShift(a.Bounds,b.Bounds);max=Math.Max(max,shift);
   if(a.Type!=b.Type||a.Text!=b.Text||a.Font!=b.Font||a.Color!=b.Color||a.Marks!=b.Marks||Math.Abs(a.Size-b.Size)>.001||shift>.01||a.Glyphs.Length!=b.Glyphs.Length)throw new IOException($"Untouched object changed at {i}: [{a.Text}] / [{b.Text}]; marks={a.Marks==b.Marks}, geometry={shift}, font={a.Font==b.Font}.");
   for(int j=0;j<a.Glyphs.Length;j++){var x=a.Glyphs[j];var y=b.Glyphs[j];double delta=Math.Max(Math.Max(Math.Abs(x.X-y.X),Math.Abs(x.Y-y.Y)),BoxShift(x.Bounds,y.Bounds));max=Math.Max(max,delta);if(x.Unicode!=y.Unicode||delta>.01)throw new IOException("Untouched glyph changed in combined candidate.");}
  }
  return max;
 }
 static double BoxShift(Box a,Box b)=>new[]{Math.Abs(a.X-b.X),Math.Abs(a.Y-b.Y),Math.Abs(a.Width-b.Width),Math.Abs(a.Height-b.Height)}.Max();
 static void VerifyTarget(IntPtr doc,IntPtr page,IntPtr[] pointers,Target t,ObjectState[] runs,TransactionPage context)
 {
  var r=t.Region;var lines=t.Layout.Lines.Select((text,row)=>(text,row)).Where(x=>x.text.Length>0).ToArray();
  if(!runs.Select(x=>x.Text).SequenceEqual(lines.Select(x=>x.text)))throw new IOException("One of the saved changes differs from its complete draft.");
  for(int i=0;i<runs.Length;i++)
  {
   var run=runs[i];var o=pointers[t.SavedIndices[i]];var f=N.FPDFTextObj_GetFont(o);N.Check(N.FPDFPageObj_GetMatrix(o,out var m),"saved combined matrix");
   if(run.Font!=r.FontHash||Math.Abs(run.Size-r.FontSize)>.001||run.Color!=$"{r.R},{r.G},{r.B},255"||!OriginalReconstructionMatches(doc,page,o,run.Text,m,r.R,r.G,r.B,t.Layout.Positioned?.Lines[lines[i].row].RelativePositions))throw new IOException("Combined original-font/style/reconstruction check failed.");
   foreach(char c in run.Text.Distinct())if(!SameGlyphPath(f,t.Font,c))throw new IOException("Combined replacement glyph outline changed.");
   if(run.Glyphs.Length!=run.Text.Length)throw new IOException("Combined replacement glyph ownership differs.");
   double x=r.X;
   for(int j=0;j<run.Glyphs.Length;j++)
   {
    var g=run.Glyphs[j];double expected=t.Layout.Positioned?.Lines[lines[i].row].Origins[j]??x;double error=Math.Abs(g.X-expected);double local=j==0?g.X-r.X:g.X-run.Glyphs[j-1].X-r.Advances[run.Text[j-1]-32];
    if(g.Unicode!=run.Text[j]||Math.Abs(g.Y-(t.Layout.Positioned?.Lines[lines[i].row].Baseline??(r.Baseline+lines[i].row*r.LineHeight)))>(r.Positioned!=null?.01:.15))throw new IOException("Combined Unicode/baseline check failed.");
    if(r.Positioned!=null)
    {
     if(error>.01)throw new IOException("Combined explicit origin shifted.");
     var plan=t.Layout.Positioned!;var predicted=plan.Lines[lines[i].row].InkBounds[j];
     if(run.Text[j]!=' '&&BoxShift(g.Bounds,predicted)>.01)throw new IOException("Proposed positioned glyph ink differs from saved glyph.");
     if(run.Glyphs.Where((other,k)=>k!=j&&run.Text[k]!=' '&&run.Text[j]!=' '&&!(lines[i].row==0&&PositionLayout.SourceSequence(r,plan.OriginalIndices,j,k))).Any(other=>g.Bounds.Intersects(other.Bounds)))throw new IOException("Positioned edited join overlaps another letter.");
    }
    else if(error>1||Math.Abs(local)>.05)throw new IOException("Combined natural glyph advances changed.");
    x+=r.Advances[run.Text[j]-32];
   }
   var allowed=Allowed(t);if(!allowed.Contains(run.Bounds.X,run.Bounds.Y)||!allowed.Contains(run.Bounds.Right,run.Bounds.Bottom))throw new IOException("Saved ink leaves its authorised area.");
  }
 }
}
