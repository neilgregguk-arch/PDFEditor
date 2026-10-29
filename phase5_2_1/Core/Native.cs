using System.Runtime.InteropServices;
using System.Text;
namespace PdfPrototype;
internal static partial class N
{
 const string D="pdfium.dll";
 [DllImport(D)] public static extern int FPDFText_SetCharcodes(IntPtr o,uint[] charcodes,nuint count);
 [DllImport(D)] public static extern int FPDFText_SetPositions(IntPtr o,float[] positions,nuint count);
 [DllImport(D)] public static extern int FPDFFont_GetGlyphWidth(IntPtr f,uint unicode,float size,out float width);
 [DllImport(D)] public static extern IntPtr FPDFFont_GetGlyphPath(IntPtr f,uint unicode,float size);
 [DllImport(D)] public static extern int FPDFGlyphPath_CountGlyphSegments(IntPtr path);
 [DllImport(D)] public static extern IntPtr FPDFGlyphPath_GetGlyphPathSegment(IntPtr path,int i);
 [DllImport(D)] public static extern int FPDFPathSegment_GetPoint(IntPtr segment,out float x,out float y);
 [DllImport(D)] public static extern int FPDFPathSegment_GetType(IntPtr segment);
 [DllImport(D)] public static extern int FPDFPathSegment_GetClose(IntPtr segment);
 [DllImport(D)] public static extern IntPtr FPDFTextObj_GetRenderedBitmap(IntPtr d,IntPtr p,IntPtr o,float scale);
 [DllImport(D)] public static extern int FPDFBitmap_GetWidth(IntPtr b);
 [DllImport(D)] public static extern int FPDFBitmap_GetHeight(IntPtr b);
 [DllImport(D)] public static extern int FPDFFont_GetIsEmbedded(IntPtr f);
 [DllImport(D)] public static extern int FPDFTextObj_GetTextRenderMode(IntPtr o);
 [DllImport(D)] public static extern int FPDFPageObj_HasTransparency(IntPtr o);
 [DllImport(D)] public static extern IntPtr FPDFPageObj_GetClipPath(IntPtr o);
 [DllImport(D)] public static extern int FPDFClipPath_CountPaths(IntPtr c);
 [DllImport(D)] public static extern int FPDFPage_GetRotation(IntPtr p);
 [DllImport(D)] public static extern int FPDF_GetSignatureCount(IntPtr d);
 [DllImport(D)] public static extern int FPDF_GetFormType(IntPtr d);
 [DllImport(D)] public static extern int FPDF_GetSecurityHandlerRevision(IntPtr d);
 [DllImport(D)] public static extern void FPDF_InitLibrary();
 [DllImport(D)] public static extern IntPtr FPDF_LoadDocument([MarshalAs(UnmanagedType.LPUTF8Str)]string path,IntPtr password);
 [DllImport(D)] public static extern void FPDF_CloseDocument(IntPtr d);
 [DllImport(D)] public static extern IntPtr FPDF_CreateNewDocument();
 [DllImport(D)] public static extern int FPDF_GetPageCount(IntPtr d);
 [DllImport(D)] public static extern IntPtr FPDF_LoadPage(IntPtr d,int index);
 [DllImport(D)] public static extern void FPDF_ClosePage(IntPtr p);
 [DllImport(D)] public static extern double FPDF_GetPageWidth(IntPtr p);
 [DllImport(D)] public static extern double FPDF_GetPageHeight(IntPtr p);
 [DllImport(D)] public static extern IntPtr FPDFPage_New(IntPtr d,int index,double w,double h);
 [DllImport(D)] public static extern int FPDFPage_CountObjects(IntPtr p);
 [DllImport(D)] public static extern IntPtr FPDFPage_GetObject(IntPtr p,int index);
 [DllImport(D)] public static extern int FPDFPageObj_GetType(IntPtr o);
 [DllImport(D)] public static extern int FPDFPageObj_GetBounds(IntPtr o,out float l,out float b,out float r,out float t);
 [DllImport(D)] public static extern void FPDFPageObj_Transform(IntPtr o,double a,double b,double c,double d,double e,double f);
 [DllImport(D)] public static extern int FPDFPageObj_GetMatrix(IntPtr o,out Matrix m);
 [StructLayout(LayoutKind.Sequential)] public struct Matrix {public float A,B,C,D,E,F;}
 [DllImport(D)] public static extern int FPDFPage_RemoveObject(IntPtr p,IntPtr o);
 [DllImport(D)] public static extern void FPDFPageObj_Destroy(IntPtr o);
 [DllImport(D)] public static extern void FPDFPage_InsertObject(IntPtr p,IntPtr o);
 [DllImport(D)] public static extern int FPDFPage_GenerateContent(IntPtr p);
 [DllImport(D)] public static extern IntPtr FPDFText_LoadPage(IntPtr p);
 [DllImport(D)] public static extern void FPDFText_ClosePage(IntPtr t);
 [DllImport(D)] public static extern uint FPDFTextObj_GetText(IntPtr o,IntPtr text,[Out]byte[]? buffer,uint length);
 [DllImport(D)] public static extern int FPDFText_CountChars(IntPtr t);
 [DllImport(D)] public static extern uint FPDFText_GetUnicode(IntPtr t,int i);
 [DllImport(D)] public static extern IntPtr FPDFText_GetTextObject(IntPtr t,int i);
 [DllImport(D)] public static extern int FPDFText_GetCharBox(IntPtr t,int i,out double l,out double r,out double b,out double top);
 [DllImport(D)] public static extern int FPDFText_GetCharOrigin(IntPtr t,int i,out double x,out double y);
 [DllImport(D)] public static extern IntPtr FPDFTextObj_GetFont(IntPtr o);
 [DllImport(D)] public static extern int FPDFTextObj_GetFontSize(IntPtr o,out float size);
 [DllImport(D)] public static extern int FPDFPageObj_GetFillColor(IntPtr o,out uint r,out uint g,out uint b,out uint a);
 [DllImport(D)] public static extern int FPDFPageObj_SetFillColor(IntPtr o,uint r,uint g,uint b,uint a);
 [DllImport(D)] public static extern IntPtr FPDFText_LoadFont(IntPtr d,byte[] bytes,uint size,int type,int cid);
 [DllImport(D)] public static extern void FPDFFont_Close(IntPtr font);
 [DllImport(D)] public static extern IntPtr FPDFPageObj_CreateTextObj(IntPtr d,IntPtr font,float size);
 [DllImport(D)] public static extern int FPDFText_SetText(IntPtr o,byte[] text);
 [DllImport(D)] public static extern int FPDFFont_GetFontData(IntPtr f,[Out]byte[]? bytes,nuint size,out nuint used);
 [DllImport(D)] public static extern int FPDFFont_GetAscent(IntPtr f,float size,out float ascent);
 [DllImport(D)] public static extern IntPtr FPDFBitmap_Create(int w,int h,int alpha);
 [DllImport(D)] public static extern void FPDFBitmap_FillRect(IntPtr bmp,int x,int y,int w,int h,uint color);
 [DllImport(D)] public static extern void FPDF_RenderPageBitmap(IntPtr bmp,IntPtr p,int x,int y,int w,int h,int rotation,int flags);
 [DllImport(D)] public static extern IntPtr FPDFBitmap_GetBuffer(IntPtr bmp);
 [DllImport(D)] public static extern int FPDFBitmap_GetStride(IntPtr bmp);
 [DllImport(D)] public static extern void FPDFBitmap_Destroy(IntPtr bmp);
 [DllImport(D)] public static extern int FPDFPage_GetAnnotCount(IntPtr p);
 [DllImport(D)] public static extern uint FPDF_GetMetaText(IntPtr d,[MarshalAs(UnmanagedType.LPUTF8Str)]string tag,[Out]byte[]? buf,uint size);
 [DllImport(D)] public static extern int FPDF_SaveAsCopy(IntPtr d,ref FileWriter writer,uint flags);
 [UnmanagedFunctionPointer(CallingConvention.Cdecl)] public delegate int WriteBlock(IntPtr self,IntPtr data,uint size);
 [StructLayout(LayoutKind.Sequential)] public struct FileWriter {public int Version; public WriteBlock Write;}
 public static string Text(IntPtr o,IntPtr tp){uint n=FPDFTextObj_GetText(o,tp,null,0);byte[] b=new byte[n];FPDFTextObj_GetText(o,tp,b,n);return Encoding.Unicode.GetString(b).TrimEnd('\0');}
 public static byte[] FontData(IntPtr font){Check(FPDFFont_GetFontData(font,null,0,out nuint n),"font length");byte[] b=new byte[(int)n];Check(FPDFFont_GetFontData(font,b,n,out _),"font data");return b;}
 public static void Check(int ok,string name){if(ok==0)throw new InvalidOperationException("PDFium failed: "+name);}
 public static string Meta(IntPtr d,string tag){uint n=FPDF_GetMetaText(d,tag,null,0);byte[] b=new byte[n];FPDF_GetMetaText(d,tag,b,n);return Encoding.Unicode.GetString(b).TrimEnd('\0');}
}
