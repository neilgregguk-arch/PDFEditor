"""Read-only source investigation; temporary PDFium probes remain in memory."""
from pathlib import Path
import json,ctypes as C,hashlib,io
from pypdf import PdfReader
from fontTools.ttLib import TTFont
import pypdfium2 as pdfium
import pypdfium2.raw as n
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence';OUT.mkdir(exist_ok=True)
def text(o,tp):
 size=n.FPDFTextObj_GetText(o,tp,None,0);buf=C.create_string_buffer(size);n.FPDFTextObj_GetText(o,tp,C.cast(buf,C.POINTER(C.c_ushort)),size);return buf.raw.decode('utf-16-le').rstrip('\0')
def settext(o,s):
 buf=C.create_string_buffer(s.encode('utf-16-le')+b'\0\0');return n.FPDFText_SetText(o,C.cast(buf,C.POINTER(C.c_ushort)))
def probe(d,p,f,s,size,code=None):
 o=n.FPDFPageObj_CreateTextObj(d,f,size);ok=settext(o,s) if code is None else n.FPDFText_SetCharcodes(o,(C.c_uint*len(code))(*code),len(code));n.FPDFPageObj_Transform(o,1,0,0,1,20,36);n.FPDFPage_InsertObject(p,o);tp=n.FPDFText_LoadPage(p)
 try:
  chars=[]
  for i in range(n.FPDFText_CountChars(tp)):
   if C.cast(n.FPDFText_GetTextObject(tp,i),C.c_void_p).value==C.cast(o,C.c_void_p).value:
    x=C.c_double();y=C.c_double();n.FPDFText_GetCharOrigin(tp,i,C.byref(x),C.byref(y));chars.append(dict(unicode=n.FPDFText_GetUnicode(tp,i),x=x.value,y=y.value))
  return dict(apiReturn=ok,text=text(o,tp),chars=chars)
 finally:n.FPDFText_ClosePage(tp);assert n.FPDFPage_RemoveObject(p,o);n.FPDFPageObj_Destroy(o)
def inspect(path):
 reader=PdfReader(path);resources=[]
 for name,ref in reader.pages[0]['/Resources']['/Font'].items():
  f=ref.get_object();child=f['/DescendantFonts'][0].get_object() if '/DescendantFonts' in f else f;desc=child.get('/FontDescriptor',{});desc=desc.get_object() if hasattr(desc,'get_object') else desc
  row=dict(resource=name,subtype=str(f['/Subtype']),baseFont=str(f.get('/BaseFont')),encoding=str(f.get('/Encoding')),toUnicode=f['/ToUnicode'].get_data().decode('latin1') if '/ToUnicode' in f else None,widths=str(child.get('/W',child.get('/Widths'))),cidToGid=str(child.get('/CIDToGIDMap')))
  if '/FontFile2' in desc:
   raw=desc['/FontFile2'].get_data();font=TTFont(io.BytesIO(raw));row.update(programSha256=hashlib.sha256(raw).hexdigest(),glyphCount=font['maxp'].numGlyphs,cmap={str(c):dict(name=g,gid=font.getGlyphID(g),advance=font['hmtx'][g][0]) for c,g in ((font.getBestCmap() or {}) if 'cmap' in font else {}).items()},unitsPerEm=font['head'].unitsPerEm,embeddingFsType=font['OS/2'].fsType)
  resources.append(row)
 doc=pdfium.PdfDocument(path);page=doc[0];tp=n.FPDFText_LoadPage(page);objects=[]
 try:
  for i in range(n.FPDFPage_CountObjects(page)):
   o=n.FPDFPage_GetObject(page,i)
   if n.FPDFPageObj_GetType(o)!=1:continue
   f=n.FPDFTextObj_GetFont(o);size=C.c_float();n.FPDFTextObj_GetFontSize(o,C.byref(size));m=n.FS_MATRIX();n.FPDFPageObj_GetMatrix(o,C.byref(m));s=text(o,tp)
   original=[]
   for j in range(n.FPDFText_CountChars(tp)):
    if C.cast(n.FPDFText_GetTextObject(tp,j),C.c_void_p).value==C.cast(o,C.c_void_p).value:
     x=C.c_double();y=C.c_double();n.FPDFText_GetCharOrigin(tp,j,C.byref(x),C.byref(y));original.append(dict(unicode=n.FPDFText_GetUnicode(tp,j),x=x.value,y=y.value))
   rows={c:probe(doc,page,f,c,size.value) for c in ' ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!?.'} if s.strip() else {}
   objects.append(dict(index=i,text=s,size=size.value,matrix={k:getattr(m,k) for k in 'abcdef'},glyphs=original,probes=rows))
 finally:n.FPDFText_ClosePage(tp);page.close();doc.close()
 return dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),fonts=resources,objects=objects,content=reader.pages[0].get_contents().get_data().decode('latin1'))
if __name__=='__main__':
 rows=[]
 for name in ['11-word-letter','10-mupdf-subset']:
  row=inspect(ROOT/'run/corpus'/(name+'.pdf'));rows.append(row)
  for o in row['objects']:
   if o['text'].strip():print(name,o['index'],repr(o['text']), 'mapped', ''.join(c for c,r in o['probes'].items() if r['text']==c))
 (OUT/'font-investigation.json').write_text(json.dumps(rows,indent=2))
