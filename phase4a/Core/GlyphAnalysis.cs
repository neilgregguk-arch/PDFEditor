using System.Runtime.InteropServices;
using System.Text;
using System.Windows.Media;
namespace PdfPrototype;

public sealed partial class PdfEngine
{
    sealed class FontAnalysisScope:IDisposable
    {
        // Native handles never escape this page's analysis. The existing fingerprint/page
        // cache stores only the resulting immutable character observations, capped at 8 pages.
        readonly IntPtr referenceDocument=N.FPDF_CreateNewDocument();
        readonly Dictionary<string,(GlyphTypeface Face,IntPtr Font)> programs=new();
        readonly Dictionary<IntPtr,(string Hash,string File,GlyphTypeface Face,CharacterCompatibility[] Characters)> mappings=new();
        public (string Hash,string File,GlyphTypeface Face,CharacterCompatibility[] Characters) Analyse(IntPtr document,IntPtr page,IntPtr font,string work)
        {
            if(mappings.TryGetValue(font,out var known))return known;
            if(N.FPDFFont_GetIsEmbedded(font)!=1)throw new InvalidDataException("FONT_NOT_EMBEDDED");
            byte[] data=N.FontData(font);
            if(data.Length<12||!((data[0]==0&&data[1]==1&&data[2]==0&&data[3]==0)||Encoding.ASCII.GetString(data,0,4)=="true"))throw new InvalidDataException("UNSUPPORTED_FONT_PROGRAM: only standalone TrueType programs are verified.");
            string hash=Hash(data),folder=Path.Combine(work,"fonts",hash);Directory.CreateDirectory(folder);string file=Path.Combine(folder,"original.ttf");
            if(!File.Exists(file))File.WriteAllBytes(file,data);
            if(!programs.TryGetValue(hash,out var program))
            {
                var face=new GlyphTypeface(new Uri(file));
                var reference=N.FPDFText_LoadFont(referenceDocument,data,(uint)data.Length,2,0);
                if(reference==IntPtr.Zero)throw new InvalidDataException("FONT_REFERENCE_UNAVAILABLE");
                programs[hash]=program=(face,reference);
            }
            var rows=new List<CharacterCompatibility>();
            bool usableCmap=program.Face.CharacterToGlyphMap.Any(pair=>pair.Value!=0);
            foreach(int c in Enumerable.Range(32,95))
            {
                if(!program.Face.CharacterToGlyphMap.TryGetValue(c,out var gid)||gid==0)
                {rows.Add(new(c,usableCmap?"AbsentFromEmbeddedSubset":"UnicodeMappingMissing",usableCmap?"GLYPH_ABSENT_FROM_FONT_CMAP":"FONT_UNICODE_CMAP_UNAVAILABLE",null,-1));continue;}
                double advance=program.Face.AdvanceWidths[gid];
                // Path comparison uses the same original program loaded in a scratch document.
                // It neither changes the source font nor adds a font to the candidate PDF.
                bool shape=SameGlyphPath(font,program.Font,(uint)c);
                bool width=N.FPDFFont_GetGlyphWidth(font,(uint)c,1000,out float actualWidth)!=0&&Math.Abs(actualWidth-advance*1000)<2;
                bool roundtrip=c==' '||ProbeCharacter(document,page,font,(char)c);
                string state=!roundtrip?"FontPresentEncodingUnavailable":!shape||!width?"MappingGlyphMismatchOrAmbiguous":"ExistingMappingVerified";
                string reason=!roundtrip?"PDF_ENCODING_ROUNDTRIP_FAILED":!shape?"PDF_GLYPH_DIFFERS_FROM_EMBEDDED_CMAP":!width?"PDF_GLYPH_WIDTH_DIFFERS_FROM_FONT":"UNICODE_OUTLINE_AND_WIDTH_VERIFIED";
                rows.Add(new(c,state,reason,gid,state=="ExistingMappingVerified"?advance:-1));
            }
            var space=rows[0];var anchor=rows.FirstOrDefault(c=>c.Unicode!=32&&c.State=="ExistingMappingVerified");
            if(space.State=="ExistingMappingVerified"&&(anchor==null||!ProbeContent(document,page,font,$"{(char)anchor.Unicode} {(char)anchor.Unicode}")))rows[0]=space with{State="FontPresentEncodingUnavailable",Reason="SPACE_CONTEXT_ROUNDTRIP_FAILED",Advance=-1};
            known=(hash,file,program.Face,rows.ToArray());mappings[font]=known;return known;
        }
        public void Dispose(){foreach(var p in programs.Values)N.FPDFFont_Close(p.Font);N.FPDF_CloseDocument(referenceDocument);}
    }
    static bool ProbeCharacter(IntPtr document,IntPtr page,IntPtr font,char c)
        =>ProbeContent(document,page,font,new string(c,3));
    static bool ProbeContent(IntPtr document,IntPtr page,IntPtr font,string expected)
    {
        var o=N.FPDFPageObj_CreateTextObj(document,font,12);if(o==IntPtr.Zero)return false;bool inserted=false;
        try
        {
            // Repeated characters expose extraction collapse; spaces use a verified anchor.
            if(N.FPDFText_SetText(o,Encoding.Unicode.GetBytes(expected+"\0"))==0)return false;
            N.FPDFPageObj_Transform(o,1,0,0,1,20,36);N.FPDFPage_InsertObject(page,o);inserted=true;
            var text=N.FPDFText_LoadPage(page);
            try{return N.Text(o,text)==expected;}
            finally{N.FPDFText_ClosePage(text);}
        }
        finally{if(inserted)N.Check(N.FPDFPage_RemoveObject(page,o),"remove character probe");N.FPDFPageObj_Destroy(o);}
    }
    static bool SameGlyphPath(IntPtr actual,IntPtr reference,uint unicode)
    {
        var a=N.FPDFFont_GetGlyphPath(actual,unicode,1000);var b=N.FPDFFont_GetGlyphPath(reference,unicode,1000);
        int ca=a==IntPtr.Zero?0:N.FPDFGlyphPath_CountGlyphSegments(a),cb=b==IntPtr.Zero?0:N.FPDFGlyphPath_CountGlyphSegments(b);
        if(ca!=cb||ca<0||(unicode!=' '&&ca==0))return false;
        for(int i=0;i<ca;i++)
        {
            var x=N.FPDFGlyphPath_GetGlyphPathSegment(a,i);var y=N.FPDFGlyphPath_GetGlyphPathSegment(b,i);
            if(N.FPDFPathSegment_GetType(x)!=N.FPDFPathSegment_GetType(y)||N.FPDFPathSegment_GetClose(x)!=N.FPDFPathSegment_GetClose(y))return false;
            if(N.FPDFPathSegment_GetPoint(x,out var ax,out var ay)==0||N.FPDFPathSegment_GetPoint(y,out var bx,out var by)==0||Math.Abs(ax-bx)>.000001||Math.Abs(ay-by)>.000001)return false;
        }
        return true;
    }
    static bool OriginalReconstructionMatches(IntPtr document,IntPtr page,IntPtr original,string text,N.Matrix matrix,uint red,uint green,uint blue)
    {
        N.FPDFTextObj_GetFontSize(original,out float size);var o=N.FPDFPageObj_CreateTextObj(document,N.FPDFTextObj_GetFont(original),size);if(o==IntPtr.Zero)return false;
        try
        {
            if(N.FPDFText_SetText(o,Encoding.Unicode.GetBytes(text+"\0"))==0)return false;
            N.FPDFPageObj_SetFillColor(o,red,green,blue,255);N.FPDFPageObj_Transform(o,matrix.A,matrix.B,matrix.C,matrix.D,matrix.E,matrix.F);
            var a=N.FPDFTextObj_GetRenderedBitmap(document,page,original,2);var b=N.FPDFTextObj_GetRenderedBitmap(document,page,o,2);
            try
            {
                if(a==IntPtr.Zero||b==IntPtr.Zero)return false;
                if(N.FPDFBitmap_GetWidth(a)!=N.FPDFBitmap_GetWidth(b)||N.FPDFBitmap_GetHeight(a)!=N.FPDFBitmap_GetHeight(b)||N.FPDFBitmap_GetStride(a)!=N.FPDFBitmap_GetStride(b))return false;
                int count=checked(N.FPDFBitmap_GetStride(a)*N.FPDFBitmap_GetHeight(a));if(count>16_000_000)return false;
                byte[] aa=new byte[count],bb=new byte[count];Marshal.Copy(N.FPDFBitmap_GetBuffer(a),aa,0,count);Marshal.Copy(N.FPDFBitmap_GetBuffer(b),bb,0,count);return aa.SequenceEqual(bb);
            }
            finally{if(a!=IntPtr.Zero)N.FPDFBitmap_Destroy(a);if(b!=IntPtr.Zero)N.FPDFBitmap_Destroy(b);}
        }
        finally{N.FPDFPageObj_Destroy(o);}
    }
}
