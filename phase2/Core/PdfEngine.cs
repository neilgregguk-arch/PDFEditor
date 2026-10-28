using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Windows.Media;
using System.Windows.Media.Imaging;
namespace PdfPrototype;

public sealed class PdfEngine
{
    public PdfEngine(){N.FPDF_InitLibrary();}
    sealed class Doc : IDisposable
    {
        public IntPtr Handle;
        public Doc(string path){Handle=N.FPDF_LoadDocument(path,IntPtr.Zero);if(Handle==IntPtr.Zero)throw new IOException("PDF cannot be opened (encrypted, invalid or unavailable).");}
        public void Dispose()=>N.FPDF_CloseDocument(Handle);
    }
    sealed class Page : IDisposable
    {
        public IntPtr Handle;
        public Page(IntPtr d,int index){Handle=N.FPDF_LoadPage(d,index);if(Handle==IntPtr.Zero)throw new IOException("Page cannot be loaded.");}
        public void Dispose()=>N.FPDF_ClosePage(Handle);
    }
    public static string Hash(byte[] bytes)=>Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
    static Box Bounds(IntPtr o,double h){N.Check(N.FPDFPageObj_GetBounds(o,out float l,out float b,out float r,out float t),"object bounds");return new(l,h-t,r-l,t-b);}
    static IntPtr[] Objects(IntPtr p)=>Enumerable.Range(0,N.FPDFPage_CountObjects(p)).Select(i=>N.FPDFPage_GetObject(p,i)).ToArray();
    static string[] ObjectTexts(IntPtr p)
    {
        IntPtr t=N.FPDFText_LoadPage(p);
        try{return Objects(p).Where(o=>N.FPDFPageObj_GetType(o)==1).Select(o=>N.Text(o,t)).ToArray();}
        finally{N.FPDFText_ClosePage(t);}
    }
    static Region? Owned(string source,IntPtr d,IntPtr page,int pageIndex,out string diagnostic)
    {
        diagnostic="View only: no verified paragraph ownership. This prototype edits the supplied controlled PDFs and their hash-bound region files.";
        string manifest=source+".region.json";
        if(!File.Exists(manifest))return null;
        try
        {
            var r=Wire.Read<Region>(File.ReadAllText(manifest));
            if(r.SourceHash!=Wire.Hash(source))throw new InvalidDataException("The PDF differs from its ownership manifest.");
            if(r.Page!=pageIndex){diagnostic="View only: this page has no owned paragraph.";return null;}
            if(r.Objects.Length==0||r.Objects.Length!=r.OriginalLines.Length||r.Advances.Length!=95)throw new InvalidDataException("Invalid region mapping.");
            if(r.Width<=0||r.X<0||r.X+r.Width>N.FPDF_GetPageWidth(page)||r.Top<0||r.SafeBottom>N.FPDF_GetPageHeight(page)-20)throw new InvalidDataException("Invalid region boundaries.");
            IntPtr tp=N.FPDFText_LoadPage(page);
            try
            {
                for(int i=0;i<r.Objects.Length;i++)
                {
                    if(r.Objects[i]<0||r.Objects[i]>=N.FPDFPage_CountObjects(page))throw new InvalidDataException("Missing paragraph object.");
                    var o=N.FPDFPage_GetObject(page,r.Objects[i]);
                    if(N.FPDFPageObj_GetType(o)!=1||N.Text(o,tp)!=r.OriginalLines[i])throw new InvalidDataException("Paragraph text mapping mismatch.");
                    N.Check(N.FPDFPageObj_GetMatrix(o,out var m),"matrix");
                    if(Math.Abs(m.A-1)>.0001||Math.Abs(m.D-1)>.0001||Math.Abs(m.B)>.0001||Math.Abs(m.C)>.0001||Math.Abs(m.E-r.X)>.01||Math.Abs(m.F-(N.FPDF_GetPageHeight(page)-r.Baseline-i*r.LineHeight))>.01)throw new InvalidDataException("Only verified horizontal original text matrices are editable.");
                    N.Check(N.FPDFTextObj_GetFontSize(o,out float size),"font size");N.Check(N.FPDFPageObj_GetFillColor(o,out uint red,out uint g,out uint b,out uint a),"fill");
                    if(Math.Abs(size-r.FontSize)>.001||red!=r.R||g!=r.G||b!=r.B||a!=255)throw new InvalidDataException("Unsupported original text style.");
                    if(Hash(N.FontData(N.FPDFTextObj_GetFont(o)))!=r.FontHash)throw new InvalidDataException("Embedded font does not match the owned region.");
                }
            }
            finally{N.FPDFText_ClosePage(tp);}
            string fontFile=Path.Combine(AppContext.BaseDirectory,"assets",Path.GetFileName(r.FontFile));
            if(!File.Exists(fontFile)||Wire.Hash(fontFile)!=r.FontHash)throw new InvalidDataException("Matching original font is unavailable; no substitution allowed.");
            var face=new GlyphTypeface(new Uri(fontFile));
            for(int c=32;c<=126;c++)
            {
                if(!face.CharacterToGlyphMap.TryGetValue(c,out var glyph)||Math.Abs(face.AdvanceWidths[glyph]*r.FontSize-r.Advances[c-32])>.001)throw new InvalidDataException("Font advance mapping mismatch.");
            }
            diagnostic="Supported: owned horizontal Latin paragraph, original embedded Prototype Sans font. Region reconstruction on save.";
            return r;
        }
        catch(Exception e){diagnostic="View only: "+e.Message;return null;}
    }
    public DocumentInfo Inspect(EditRequest req)
    {
        string source=Path.GetFullPath(req.Source); using var d=new Doc(source);
        int count=N.FPDF_GetPageCount(d.Handle),index=Math.Clamp(req.Page,0,count-1);
        using var p=new Page(d.Handle,index);double w=N.FPDF_GetPageWidth(p.Handle),h=N.FPDF_GetPageHeight(p.Handle);
        Directory.CreateDirectory(req.Work);string imageKey=Wire.Hash(source)[..16];string normal=Path.Combine(req.Work,$"page-{imageKey}-{index}.png");Render(p.Handle,normal,2);
        var region=Owned(source,d.Handle,p.Handle,index,out string diagnostic);var glyphs=new List<Glyph>();string? clean=null;
        if(region!=null)
        {
            var pointers=region.Objects.Select(i=>N.FPDFPage_GetObject(p.Handle,i)).ToArray();
            var counts=new int[pointers.Length];var tp=N.FPDFText_LoadPage(p.Handle);
            try
            {
                for(int i=0;i<N.FPDFText_CountChars(tp);i++)
                {
                    int row=Array.IndexOf(pointers,N.FPDFText_GetTextObject(tp,i));if(row<0)continue;
                    var code=N.FPDFText_GetUnicode(tp,i);if(code<32||code>126)continue;
                    int within=counts[row]++;if(within>=region.OriginalLines[row].Length||region.OriginalLines[row][within]!=(char)code)throw new InvalidDataException("Ambiguous original glyph mapping; editing disabled.");
                    N.Check(N.FPDFText_GetCharBox(tp,i,out double l,out double right,out double bottom,out double top),"glyph box");
                    N.Check(N.FPDFText_GetCharOrigin(tp,i,out double x,out double y),"glyph origin");
                    int logical=region.OriginalLines.Take(row).Sum(s=>s.Length+1)+within;
                    glyphs.Add(new(logical,((char)code).ToString(),new(l,h-top,right-l,top-bottom),x,h-y,region.Objects[row]));
                }
            }
            finally{N.FPDFText_ClosePage(tp);}
            if(counts.Where((n,i)=>n!=region.OriginalLines[i].Length).Any())throw new InvalidDataException("Incomplete original glyph mapping.");
            foreach(var o in pointers){N.Check(N.FPDFPage_RemoveObject(p.Handle,o),"remove display text");N.FPDFPageObj_Destroy(o);}
            clean=Path.Combine(req.Work,$"clean-{imageKey}-{index}.png");Render(p.Handle,clean,2);
        }
        return new(source,Wire.Hash(source),count,index,w,h,normal,clean,region,glyphs.ToArray(),diagnostic);
    }
    static byte[] Pixels(IntPtr p,double scale,out int width,out int height)
    {
        width=(int)Math.Ceiling(N.FPDF_GetPageWidth(p)*scale);height=(int)Math.Ceiling(N.FPDF_GetPageHeight(p)*scale);
        if((long)width*height>40_000_000)throw new InvalidOperationException("Page exceeds prototype render limit.");
        var b=N.FPDFBitmap_Create(width,height,1);if(b==IntPtr.Zero)throw new IOException("Bitmap allocation failed.");
        try{N.FPDFBitmap_FillRect(b,0,0,width,height,0xffffffff);N.FPDF_RenderPageBitmap(b,p,0,0,width,height,0,1);byte[] data=new byte[width*height*4];int stride=N.FPDFBitmap_GetStride(b);for(int y=0;y<height;y++)Marshal.Copy(N.FPDFBitmap_GetBuffer(b)+y*stride,data,y*width*4,width*4);return data;}
        finally{N.FPDFBitmap_Destroy(b);}
    }
    static void Render(IntPtr p,string path,double scale)
    {
        byte[] bytes=Pixels(p,scale,out int w,out int h);var image=BitmapSource.Create(w,h,72*scale,72*scale,PixelFormats.Bgra32,null,bytes,w*4);image.Freeze();
        var png=new PngBitmapEncoder();png.Frames.Add(BitmapFrame.Create(image));using var output=File.Create(path);png.Save(output);
    }
    static void Save(IntPtr document,string path)
    {
        using var file=new FileStream(path,FileMode.CreateNew,FileAccess.Write,FileShare.None);
        Exception? error=null;
        N.WriteBlock callback=(self,data,size)=>{try{byte[] b=new byte[size];Marshal.Copy(data,b,0,(int)size);file.Write(b);return 1;}catch(Exception e){error=e;return 0;}};
        var writer=new N.FileWriter{Version=1,Write=callback};N.Check(N.FPDF_SaveAsCopy(document,ref writer,2),"save");GC.KeepAlive(callback);if(error!=null)throw error;file.Flush(true);
    }
    sealed record ObjectState(int Type,string Text,Box Bounds,string Font,float Size,string Color);
    static ObjectState[] Snapshot(IntPtr page,HashSet<int>? exclude=null)
    {
        var t=N.FPDFText_LoadPage(page);double h=N.FPDF_GetPageHeight(page);
        try{return Objects(page).Select((o,i)=>(o,i)).Where(v=>exclude==null||!exclude.Contains(v.i)).Select(v=>
        {
            int type=N.FPDFPageObj_GetType(v.o);string text=type==1?N.Text(v.o,t):"",font="",color="";float size=0;
            if(type==1){font=Hash(N.FontData(N.FPDFTextObj_GetFont(v.o)));N.FPDFTextObj_GetFontSize(v.o,out size);N.FPDFPageObj_GetFillColor(v.o,out var r,out var g,out var b,out var a);color=$"{r},{g},{b},{a}";}
            return new ObjectState(type,text,Bounds(v.o,h),font,size,color);
        }).ToArray();}finally{N.FPDFText_ClosePage(t);}
    }
    public EditResult Edit(EditRequest req)
    {
        string source=Path.GetFullPath(req.Source);
        if(Wire.Hash(source)!=req.ExpectedHash)throw new InvalidOperationException("Source changed on disk. Draft retained; reopen the source deliberately before exporting.");
        using var d=new Doc(source);using var p=new Page(d.Handle,req.Page);
        var region=Owned(source,d.Handle,p.Handle,req.Page,out string issue)??throw new InvalidOperationException(issue);
        var layout=ParagraphLayout.Plan(region,req.Text);
        if(!layout.Safe)return new(req.Revision,false,layout.Diagnostic,null,null);
        var oldObjects=region.Objects.Select(i=>N.FPDFPage_GetObject(p.Handle,i)).ToArray();var exclude=region.Objects.ToHashSet();
        var neighbours=Snapshot(p.Handle,exclude);
        foreach(var box in layout.LineBoxes)
            if(neighbours.Any(o=>box.Intersects(o.Bounds,.5)))return new(req.Revision,false,"Potential collision with a neighbouring PDF object. Draft retained; nothing saved.",null,null);
        if(req.Text==region.OriginalText)return new(req.Revision,false,"No text changes to export. Original document and draft retained.",null,null);
        double h=N.FPDF_GetPageHeight(p.Handle);var font=N.FPDFTextObj_GetFont(oldObjects[0]);
        var added=new List<IntPtr>();
        // Create new runs using the existing embedded font BEFORE releasing original text objects.
        for(int i=0;i<layout.Lines.Length;i++)
        {
            if(layout.Lines[i].Length==0)continue;
            var o=N.FPDFPageObj_CreateTextObj(d.Handle,font,(float)region.FontSize);if(o==IntPtr.Zero)throw new IOException("Cannot create original-font text object.");
            N.Check(N.FPDFText_SetText(o,Encoding.Unicode.GetBytes(layout.Lines[i]+"\0")),"set region line");N.Check(N.FPDFPageObj_SetFillColor(o,region.R,region.G,region.B,255),"style");
            N.FPDFPageObj_Transform(o,1,0,0,1,region.X,h-region.Baseline-i*region.LineHeight);N.FPDFPage_InsertObject(p.Handle,o);added.Add(o);
        }
        foreach(var o in oldObjects){N.Check(N.FPDFPage_RemoveObject(p.Handle,o),"remove original content");N.FPDFPageObj_Destroy(o);}
        N.Check(N.FPDFPage_GenerateContent(p.Handle),"generate content");
        Directory.CreateDirectory(req.Work);string token=Guid.NewGuid().ToString("N"),candidate=Path.Combine(req.Work,"candidate-"+token+".pdf"),png=Path.Combine(req.Work,"candidate-"+token+".png");
        Save(d.Handle,candidate);
        object verification;
        using(var reopened=new Doc(candidate))using(var q=new Page(reopened.Handle,req.Page))using(var original=new Doc(source))using(var op=new Page(original.Handle,req.Page))
        {
            var objects=Objects(q.Handle);int count=neighbours.Length;
            if(objects.Length!=count+added.Count)throw new IOException("Saved content count differs; original removal not established.");
            var observed=Snapshot(q.Handle);var preserved=observed.Take(count).ToArray();
            if(preserved.Length!=neighbours.Length)throw new IOException("Neighbour count changed.");
            double maxShift=0;
            for(int i=0;i<count;i++)
            {
                var a=neighbours[i];var b=preserved[i];
                double delta=new[]{Math.Abs(a.Bounds.X-b.Bounds.X),Math.Abs(a.Bounds.Y-b.Bounds.Y),Math.Abs(a.Bounds.Width-b.Bounds.Width),Math.Abs(a.Bounds.Height-b.Bounds.Height)}.Max();maxShift=Math.Max(maxShift,delta);
                if(a.Type!=b.Type||a.Text!=b.Text||a.Font!=b.Font||a.Color!=b.Color||Math.Abs(a.Size-b.Size)>.001||delta>.01)throw new IOException("Neighbour text, font, colour or geometry changed. Draft retained.");
            }
            var newRuns=observed.Skip(count).ToArray();var expected=layout.Lines.Where(line=>line.Length>0).ToArray();
            if(!newRuns.Select(o=>o.Text).SequenceEqual(expected))throw new IOException("Saved replacement text differs from draft layout.");
            if(newRuns.Any(o=>o.Font!=region.FontHash||Math.Abs(o.Size-region.FontSize)>.001||o.Color!=$"{region.R},{region.G},{region.B},255"))throw new IOException("Saved original-font/style verification failed.");
            bool oldAbsent=!string.Join("\n",ObjectTexts(q.Handle)).Contains(region.OriginalText,StringComparison.Ordinal);
            bool intentional=req.Text.Contains(region.OriginalText,StringComparison.Ordinal);
            if(!oldAbsent&&!intentional)throw new IOException("Original targeted text remains unexpectedly extractable.");
            if(N.FPDF_GetPageCount(original.Handle)!=N.FPDF_GetPageCount(reopened.Handle))throw new IOException("Page count changed.");
            int otherPageDifferences=0;
            for(int j=0;j<N.FPDF_GetPageCount(original.Handle);j++)
            {
                using var a=new Page(original.Handle,j);using var b=new Page(reopened.Handle,j);
                if(N.FPDF_GetPageWidth(a.Handle)!=N.FPDF_GetPageWidth(b.Handle)||N.FPDF_GetPageHeight(a.Handle)!=N.FPDF_GetPageHeight(b.Handle)||N.FPDFPage_GetAnnotCount(a.Handle)!=N.FPDFPage_GetAnnotCount(b.Handle))throw new IOException("Page dimensions or annotation count changed.");
                if(j!=req.Page&&!Pixels(a.Handle,1,out _,out _).SequenceEqual(Pixels(b.Handle,1,out _,out _)))otherPageDifferences++;
            }
            if(otherPageDifferences!=0)throw new IOException("Untouched page rendering changed.");
            foreach(string tag in new[]{"Title","Author","Subject","Keywords","Creator","Producer","CreationDate","ModDate"})if(N.Meta(original.Handle,tag)!=N.Meta(reopened.Handle,tag))throw new IOException("Metadata changed: "+tag);
            byte[] before=Pixels(op.Handle,2,out int width,out int height),after=Pixels(q.Handle,2,out _,out _);int outside=0,changed=0;
            double bottom=Math.Max(region.Top+layout.Height,region.Top+region.OriginalLines.Length*region.LineHeight)+2;
            var allowed=new Box(region.X-2,region.Top-2,region.Width+4,bottom-region.Top+2);
            for(int y=0;y<height;y++)for(int x=0;x<width;x++)
            {int offset=(y*width+x)*4;int delta=Math.Max(Math.Abs(before[offset]-after[offset]),Math.Max(Math.Abs(before[offset+1]-after[offset+1]),Math.Abs(before[offset+2]-after[offset+2])));if(delta>8){changed++;if(!allowed.Contains(x/2.0,y/2.0))outside++;}}
            if(outside>0)throw new IOException($"Visual verification found {outside} changed pixels outside owned edit area.");
            Render(q.Handle,png,2);
            verification=new { method="owned-region original-font reconstruction; original text objects removed",sourceHash=req.ExpectedHash,candidateHash=Wire.Hash(candidate),revision=req.Revision,originalObjectsRemoved=oldObjects.Length,newTextObjects=added.Count,replacementLinesMatch=true,originalFullTextAbsent=oldAbsent,originalTextIntentionallyRetainedInDraft=intentional,fontProgramPreserved=true,maxNeighbourGeometryShiftPt=maxShift,changedPixels144Dpi=changed,outsidePixels144Dpi=outside,untouchedPageDifferences=otherPageDifferences,metadataPreserved=true,layout };
        }
        string? destination=null;
        if(req.Command=="save")
        {
            destination=Path.GetFullPath(req.Destination);
            if(string.Equals(destination,source,StringComparison.OrdinalIgnoreCase))throw new IOException("The original PDF cannot be overwritten.");
            if(File.Exists(destination))throw new IOException("Destination already exists. Choose a new filename; no file was overwritten.");
            string directory=Path.GetDirectoryName(destination)!;Directory.CreateDirectory(directory);
            string staged=Path.Combine(directory,".pdf-prototype-"+token+".tmp");
            try{File.Copy(candidate,staged,false);if(Wire.Hash(staged)!=Wire.Hash(candidate))throw new IOException("Staged file checksum differs.");if(Wire.Hash(source)!=req.ExpectedHash)throw new IOException("Source changed during save; candidate not committed.");File.Move(staged,destination,false);}
            finally{if(File.Exists(staged))File.Delete(staged);}
            File.WriteAllText(Path.Combine(req.Work,"verification-"+token+".json"),Wire.Write(verification));
        }
        return new(req.Revision,true,req.Command=="save"?"Verified PDF saved. Source preserved.":"Candidate reopened and verified. Draft remains editable.",png,verification,destination);
    }
    public static void GenerateSamples(string folder)
    {
        Directory.CreateDirectory(folder);string asset=Path.Combine(AppContext.BaseDirectory,"assets","PrototypeSansAscii.ttf");byte[] data=File.ReadAllBytes(asset);var face=new GlyphTypeface(new Uri(asset));
        foreach(string name in new[]{"A-Simple","B-Longer","C-Restricted","D-Font"})
        {
            string path=Path.Combine(folder,name+".pdf");if(File.Exists(path))continue;
            var d=N.FPDF_CreateNewDocument();var p=N.FPDFPage_New(d,0,612,792);var f=N.FPDFText_LoadFont(d,data,(uint)data.Length,2,1);if(f==IntPtr.Zero)throw new IOException("Cannot embed fixture font.");
            var r=new Region{Name=name,Objects=[2],OriginalLines=[name.StartsWith("B")?"A brief original sentence.":name.StartsWith("D")?"Original font supports plain Latin text.":"Edit this original paragraph directly on the page."],Baseline=150,Ascent=face.Baseline*12,SafeBottom=name.StartsWith("C")?190:620,FontHash=Hash(data),Advances=Enumerable.Range(32,95).Select(c=>face.AdvanceWidths[face.CharacterToGlyphMap[c]]*12).ToArray()};
            void Text(string text,double x,double baseline,double size,uint red,uint g,uint b)
            {var o=N.FPDFPageObj_CreateTextObj(d,f,(float)size);N.Check(N.FPDFText_SetText(o,Encoding.Unicode.GetBytes(text+"\0")),"fixture text");N.FPDFPageObj_SetFillColor(o,red,g,b,255);N.FPDFPageObj_Transform(o,1,0,0,1,x,792-baseline);N.FPDFPage_InsertObject(p,o);}
            Text("PDF / IN PLACE",60,64,22,24,44,61);
            Text(name+"  -  click the paragraph below to edit",60,96,10,90,100,110);
            Text(r.OriginalLines[0],r.X,r.Baseline,r.FontSize,r.R,r.G,r.B);
            Text(name.StartsWith("C")?"PROTECTED NEIGHBOUR - never move this block":"Untouched reference block - never move this block",60,name.StartsWith("C")?210:660,11,85,94,105);
            Text("Offline prototype / original embedded font / source remains unchanged",60,744,9,100,110,120);
            N.Check(N.FPDFPage_GenerateContent(p),"fixture content");Save(d,path);N.FPDF_ClosePage(p);N.FPDFFont_Close(f);N.FPDF_CloseDocument(d);
            r.SourceHash=Wire.Hash(path);File.WriteAllText(path+".region.json",Wire.Write(r));
        }
    }
}
