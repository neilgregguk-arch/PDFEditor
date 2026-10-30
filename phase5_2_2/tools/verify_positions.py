"""Independent readers, every target origin and all preserved whitespace bytes."""
from pathlib import Path
import json,hashlib,collections,subprocess
import numpy as np
from PIL import Image
import pymupdf,pikepdf
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1];E=R/'evidence';P=E/'position-poppler';P.mkdir(exist_ok=True)
records=[x for x in json.loads((E/'position-tests.json').read_text())['saved'] if 'pages' not in x['verification']]
for suite in ['discovery-tests.json','compatibility-tests.json']:
 records.extend(x for x in json.loads((E/suite).read_text())['saved'] if x['region'].get('Positioned'))
ui=json.loads((E/'controls-shipping/position-control-tests.json').read_text())
for idx in [1,2]:
 result=ui['results'][idx]['metrics'];result=result['result'] if idx==1 else result
 src=R/'run/corpus/11-word-letter.pdf' if idx==1 else E/'controls-shipping/word-ui-first.pdf'
 # Same geometry rediscovered through the product, independently verified below.
 region=dict(records[0]['region']);region['OriginalText']='Phase 3 Office letter' if idx==1 else 'Phace 3 Office letter'
 records.append(dict(source=str(src),destination=result['Destination'],draft='Phace 3 Office letter' if idx==1 else 'Phace 3 Oflice letter',region=region,verification=result['Verification']))
def font_hashes(r):
 out=set()
 for p in r.pages:
  for ref in p['/Resources'].get('/Font',{}).values():
   f=ref.get_object();f=f['/DescendantFonts'][0].get_object() if '/DescendantFonts' in f else f;desc=f.get('/FontDescriptor',{});desc=desc.get_object() if hasattr(desc,'get_object') else desc
   for key in ['/FontFile','/FontFile2','/FontFile3']:
    if key in desc:out.add(hashlib.sha256(desc[key].get_object().get_data()).hexdigest())
 return out
def font_rules(reader):
 out=[]
 for ref in reader.pages[0]['/Resources']['/Font'].values():
  f=ref.get_object();child=f['/DescendantFonts'][0].get_object() if '/DescendantFonts' in f else f;row={}
  for key in ['/Encoding','/ToUnicode']:
   v=f.get(key);v=v.get_object() if hasattr(v,'get_object') else v;row[key]=hashlib.sha256(v.get_data()).hexdigest() if hasattr(v,'get_data') else str(v)
  for key in ['/BaseFont','/Subtype','/W','/Widths','/DW','/FirstChar','/LastChar','/CIDToGIDMap']:
   v=child.get(key);v=v.get_object() if hasattr(v,'get_object') else v;row[key]=hashlib.sha256(v.get_data()).hexdigest() if hasattr(v,'get_data') else str(v)
  out.append(row)
 return sorted({json.dumps(row,sort_keys=True) for row in out})
def invisible_runs(r):
 # Independent PDF stream parser; retain nonembedded-font raw bytes, not just
 # PDFium's empty standalone-space extraction. Collect per-font in content order.
 out=collections.defaultdict(list);font=None
 for args,op in r.pages[0].get_contents().operations:
  if op==b'Tf':font=args[0]
  if op not in [b'Tj',b'TJ'] or font is None:continue
  f=r.pages[0]['/Resources']['/Font'][font].get_object()
  if '/DescendantFonts' in f:continue
  desc=f.get('/FontDescriptor',{});desc=desc.get_object() if hasattr(desc,'get_object') else desc
  if any(k in desc for k in ['/FontFile','/FontFile2','/FontFile3']):continue
  vals=args[0] if op==b'TJ' else args
  for v in vals:
   if isinstance(v,(str,bytes)):out[str(f.get('/BaseFont'))].append(bytes(v) if isinstance(v,bytes) else v.original_bytes)
 return {k:[v.hex() for v in vals] for k,vals in out.items()}
def chars(path):
 d=pymupdf.open(path);out=[]
 for b in d[0].get_text('rawdict')['blocks']:
  for line in b.get('lines',[]):
   for span in line['spans']:
    for c in span['chars']:out.append(c)
 d.close();return sorted(out,key=lambda c:(round(c['origin'][1],2),c['origin'][0]))
def render(path,prefix,dpi):
 subprocess.run(['pdftoppm','-f','1','-singlefile','-r',str(dpi),'-png',str(path),str(prefix)],capture_output=True,check=True)
 return np.asarray(Image.open(str(prefix)+'.png').convert('RGB'),dtype=np.int16)
rows=[]
for i,v in enumerate(records):
 a=Path(v['source']);b=Path(v['destination']);ra=PdfReader(a);rb=PdfReader(b);r=v['region'];assert len(ra.pages)==len(rb.pages);assert [list(p.mediabox) for p in ra.pages]==[list(p.mediabox) for p in rb.pages];assert dict(ra.metadata or {})==dict(rb.metadata or {});assert font_hashes(ra)==font_hashes(rb)
 assert font_rules(ra)==font_rules(rb),(a,'font rules changed')
 assert invisible_runs(ra)==invisible_runs(rb),(a,b,invisible_runs(ra),invisible_runs(rb))
 with pikepdf.open(b) as d:assert not d.check_pdf_syntax()
 assert v['draft'] in rb.pages[0].extract_text()
 ca,cb=chars(a),chars(b);assert len(ca)==len(cb),(a,len(ca),len(cb));max_origin=0;max_unchanged_bounds=0;target=[]
 line_indices=[i for i,c in enumerate(ca) if abs(c['origin'][1]-r['Baseline'])<.02];line_text=''.join(ca[i]['c'] for i in line_indices);start=line_text.find(r['OriginalText']);assert start>=0,(a,line_text,r['OriginalText']);target_indices=set(line_indices[start:start+len(r['OriginalText'])])
 for glyph_index,(x,y) in enumerate(zip(ca,cb)):
  shift=max(abs(xx-yy) for xx,yy in zip(x['origin'],y['origin']));max_origin=max(max_origin,shift);assert shift<=.01,(a,x,y)
  if glyph_index in target_indices:target.append(y['c'])
  else:assert x['c']==y['c'],(x,y)
  if x['c']==y['c']:
   delta=max(abs(xx-yy) for xx,yy in zip(x['bbox'],y['bbox']));max_unchanged_bounds=max(max_unchanged_bounds,delta);assert delta<=.01
 assert ''.join(target)==v['draft'],(a,target,v['draft'])
 comparisons=[]
 for dpi in [72,144]:
  before=render(a,P/f'{i}-before-{dpi}',dpi);after=render(b,P/f'{i}-after-{dpi}',dpi);assert before.shape==after.shape;changed=np.max(abs(before-after),axis=2)>8;yy,xx=np.indices(changed.shape);s=dpi/72;box=r['ObservedBounds'];mask=(xx/s>=box['X']-2)&(xx/s<=box['Right']+2)&(yy/s>=box['Y']-2)&(yy/s<=box['Bottom']+2);outside=int(np.sum(changed&~mask));assert outside==0,(b,dpi,outside)
  if v.get('reconstruction'):assert not changed.any(),('Original reconstruction differs',dpi)
  comparisons.append(dict(dpi=dpi,changedPixels=int(changed.sum()),outsidePixels=outside))
 rows.append(dict(source=str(a),destination=str(b),fontProgramsEqual=True,fontEncodingWidthsAndMappingsEqual=True,fontResourceAliasesBefore=len(ra.pages[0]['/Resources']['/Font']),fontResourceAliasesAfter=len(rb.pages[0]['/Resources']['/Font']),metadataEqual=True,whitespaceRawBytesPreserved=invisible_runs(rb),independentGlyphs=len(ca),maxAllGlyphOriginShiftPt=max_origin,maxUnchangedGlyphBoxShiftPt=max_unchanged_bounds,targetExactlyExtracted=True,comparisons=comparisons,sourceSha256=hashlib.sha256(a.read_bytes()).hexdigest()))
(E/'position-independent-verification.json').write_text(json.dumps(dict(success=True,readers='MuPDF, pypdf, Poppler, qpdf via pikepdf',cases=rows),indent=2));print('Position verification passed:',len(rows),'PDFs, 72/144 DPI; all glyph origins and retained whitespace bytes')
