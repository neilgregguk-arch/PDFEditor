"""Experimental PDFium mechanisms, separate from production eligibility/export.
Known object/font mappings in the original Word corpus are inspected with pypdf.
"""
from pathlib import Path
import sys,json,ctypes as C,hashlib,re
sys.path.insert(0,str(Path(__file__).resolve().parent))
from investigate_fonts import text,settext
import pypdfium2 as p
import pypdfium2.raw as n
import pypdfium2_raw as raw
from pypdf import PdfReader
from fontTools.ttLib import TTFont
from io import BytesIO
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence/api-lab';OUT.mkdir(exist_ok=True)
source=ROOT/'run/corpus/11-word-letter.pdf';reader=PdfReader(source);f=reader.pages[0]['/Resources']['/Font']['/F1'];child=f['/DescendantFonts'][0];program=child['/FontDescriptor']['/FontFile2'].get_data();font=TTFont(BytesIO(program));cmap=font.getBestCmap();cidmap=child['/CIDToGIDMap'].get_data();mapping={}
for block in re.findall(rb'beginbfrange(.*?)endbfrange',f['/ToUnicode'].get_data(),re.S):
 for first,last,values in re.findall(rb'<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>\s*(\[.*?\]|<[0-9a-fA-F]+>)',block,re.S):
  codes=list(range(int(first,16),int(last,16)+1));vals=re.findall(rb'<([0-9a-fA-F]+)>',values)
  if not values.startswith(b'['):vals=[f'{int(vals[0],16)+i:04x}'.encode() for i in range(len(codes))]
  for code,u in zip(codes,vals):mapping[code]=bytes.fromhex(u.decode()).decode('utf-16-be')
def codes_for(s):
 result=[]
 for char in s:
  matches=[code for code,u in mapping.items() if u==char and int.from_bytes(cidmap[code*2:code*2+2],'big')==font.getGlyphID(cmap[ord(char)])]
  assert len(matches)==1,(char,matches);result.append(matches[0])
 return result
def snapshot(page):
 tp=n.FPDFText_LoadPage(page);rows=[]
 try:
  for i in range(n.FPDFPage_CountObjects(page)):
   o=n.FPDFPage_GetObject(page,i);gs=[]
   for j in range(n.FPDFText_CountChars(tp)):
    if C.cast(n.FPDFText_GetTextObject(tp,j),C.c_void_p).value==C.cast(o,C.c_void_p).value:
     x=C.c_double();y=C.c_double();n.FPDFText_GetCharOrigin(tp,j,C.byref(x),C.byref(y));gs.append(dict(unicode=n.FPDFText_GetUnicode(tp,j),x=x.value,y=y.value))
   rows.append(dict(index=i,type=n.FPDFPageObj_GetType(o),text=text(o,tp) if n.FPDFPageObj_GetType(o)==1 else '',glyphs=gs))
  return rows
 finally:n.FPDFText_ClosePage(tp)
initial_hash=hashlib.sha256(source.read_bytes()).hexdigest();rows=[]
raw_dll=Path(raw.__file__).parent/'pdfium.dll';assert raw_dll.exists();assert hashlib.sha256(raw_dll.read_bytes()).digest()==hashlib.sha256((ROOT/'run/pdfium.dll').read_bytes()).digest()
library=C.WinDLL(str(ROOT/'run/pdfium.dll'));availability={api:bool(getattr(library,api,None)) for api in ['FPDFText_SetText','FPDFText_SetCharcodes','FPDFText_SetPositions','FPDFText_GetTextObject','FPDFFont_GetGlyphPath','FPDFFont_GetGlyphWidth']}
for mechanism in ['SetText-existing','SetCharcodes-existing','SetText-new-unmapped','SetText-original-positions','SetCharcodes-original-positions','SetCharcodes-wrong-space','SetText-equal-width-positions','SetCharcodes-equal-width-positions']:
 doc=p.PdfDocument(source);page=doc[0];before=snapshot(page);original=before[0]['text'];assert len(before[0]['glyphs'])==len(original)>0;obj=n.FPDFPage_GetObject(page,0);draft=original if 'positions' in mechanism else 'Office letter' if 'new-unmapped' not in mechanism else 'Office!'
 if 'equal-width' in mechanism:
  assert font['hmtx'][cmap[ord('s')]][0]==font['hmtx'][cmap[ord('c')]][0]
  draft=original.replace('Phase','Phace')
 codes=None;positions=None
 if mechanism.startswith('SetText'):ok=settext(obj,draft)
 else:
  codes=codes_for(draft)
  if mechanism.endswith('wrong-space'):codes=[0 if mapping[c]==' ' else c for c in codes]
  ok=n.FPDFText_SetCharcodes(obj,(C.c_uint*len(codes))(*codes),len(codes))
 if 'positions' in mechanism:
  positions=[g['x']-before[0]['glyphs'][0]['x'] for g in before[0]['glyphs'][1:]];positionsReturn=n.FPDFText_SetPositions(obj,(C.c_float*len(positions))(*positions),len(positions));assert positionsReturn==1
 else:positionsReturn=None
 page.gen_content();path=OUT/(mechanism+'.pdf');doc.save(path,flags=2);page.close();doc.close()
 reopened=p.PdfDocument(path);q=reopened[0];after=snapshot(q);q.close();reopened.close()
 neighbour_shift=0;stable=True
 for a,b in zip(before[1:],after[1:]):
  if a['text']!=b['text'] or len(a['glyphs'])!=len(b['glyphs']):stable=False;continue
  for x,y in zip(a['glyphs'],b['glyphs']):neighbour_shift=max(neighbour_shift,abs(x['x']-y['x']),abs(x['y']-y['y']));stable&=x['unicode']==y['unicode']
 replacement_match=after[0]['text']==draft
 target_shift=None
 if 'positions' in mechanism:
  target_shift=max([0]+[max(abs(a['x']-b['x']),abs(a['y']-b['y'])) for a,b in zip(before[0]['glyphs'],after[0]['glyphs'])])
 rows.append(dict(mechanism=mechanism,apiReturn=ok,positionsReturn=positionsReturn,source=str(source),destination=str(path),draft=draft,codes=codes,positions=positions,originalObjectIndex=0,reopenedObjectText=after[0]['text'],replacementExtracts=replacement_match,independentText=PdfReader(path).pages[0].extract_text(),neighbourGlyphsStable=stable,maxNeighbourGlyphShiftPt=neighbour_shift,maxOriginalTargetGlyphShiftPt=target_shift,original=before[0],after=after[0],productionApproved=False))
assert hashlib.sha256(source.read_bytes()).hexdigest()==initial_hash
(ROOT/'evidence/api-investigation.json').write_text(json.dumps(dict(pinnedDllHash=hashlib.sha256(raw_dll.read_bytes()).hexdigest(),availability=availability,wordMapping=mapping,wordCidToGid={c:int.from_bytes(cidmap[c*2:c*2+2],'big') for c in mapping},cases=rows,sourcePreserved=True),indent=2))
for r in rows:print(r['mechanism'],'API',r['apiReturn'],'text',repr(r['reopenedObjectText']),'neighbour shift',r['maxNeighbourGlyphShiftPt'],'target shift',r['maxOriginalTargetGlyphShiftPt'])
