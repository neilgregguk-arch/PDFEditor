"""Independent development extraction, structure, geometry and Poppler checks."""
from pathlib import Path
import json,hashlib,subprocess,collections
from pypdf import PdfReader
from PIL import Image
import numpy as np
import pikepdf
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence';RENDERS=OUT/'poppler';RENDERS.mkdir(exist_ok=True)
def font_hashes(reader):
 result=set()
 for page in reader.pages:
  for ref in page.get('/Resources',{}).get('/Font',{}).values():
   f=ref.get_object()
   if '/DescendantFonts' in f:f=f['/DescendantFonts'][0].get_object()
   descriptor=f.get('/FontDescriptor',{});descriptor=descriptor.get_object() if hasattr(descriptor,'get_object') else descriptor
   for tag in ['/FontFile','/FontFile2','/FontFile3']:
    if tag in descriptor:result.add(hashlib.sha256(descriptor[tag].get_object().get_data()).hexdigest())
 return result
def runs(page):
 result=[]
 def visit(text,cm,tm,font,size):
  for line in text.splitlines():
   if line:result.append((line,round(tm[4]*cm[0]+tm[5]*cm[2]+cm[4],3),round(tm[4]*cm[1]+tm[5]*cm[3]+cm[5],3),round(size,3)))
 page.extract_text(visitor_text=visit);return result
def render(path,prefix,dpi):
 subprocess.run(['pdftoppm','-f','1','-singlefile','-r',str(dpi),'-png',str(path),str(prefix)],check=True,capture_output=True)
 return np.asarray(Image.open(str(prefix)+'.png').convert('RGB'),dtype=np.int16)
rows=[]
records=json.loads((OUT/'discovery-tests.json').read_text())['saved']
for i,record in enumerate(records):
 source=Path(record['source']);dest=Path(record['destination']);region=record['region'];a=PdfReader(source);b=PdfReader(dest)
 assert len(a.pages)==len(b.pages)
 assert [list(p.mediabox) for p in a.pages]==[list(p.mediabox) for p in b.pages]
 assert dict(a.metadata or {})==dict(b.metadata or {})
 assert font_hashes(a)==font_hashes(b)
 with pikepdf.open(dest) as pdf:assert not pdf.check_pdf_syntax()
 text=' '.join(b.pages[0].extract_text().split());assert ' '.join(record['draft'].split()) in text
 old_lines={line.strip() for line in region['OriginalLines']}
 before=[r for r in runs(a.pages[0]) if r[0].strip() not in old_lines];after=runs(b.pages[0])
 # Each untouched original run must retain text, position and size independently.
 counts=collections.Counter(after)
 for run in before:assert counts[run]>0,('Neighbour run changed',run);counts[run]-=1
 comparisons=[]
 for dpi in [72,144]:
  x=render(source,RENDERS/f'{i}-before-{dpi}',dpi);y=render(dest,RENDERS/f'{i}-after-{dpi}',dpi);assert x.shape==y.shape
  changed=np.max(np.abs(x-y),axis=2)>8;scale=dpi/72
  layout=record['verification']['layout'];top=region['Baseline']-region['Ascent'];bottom=max(top+layout['Height'],top+len(region['OriginalLines'])*region['LineHeight'])+2
  yy,xx=np.indices(changed.shape);inside=(xx/scale>=region['X']-2)&(xx/scale<=region['X']+region['Width']+2)&(yy/scale>=top-2)&(yy/scale<=bottom)
  outside=int(np.sum(changed&~inside));assert outside==0,(dest.name,dpi,outside)
  comparisons.append(dict(dpi=dpi,changed=int(np.sum(changed)),outside=outside))
 rows.append(dict(source=str(source),destination=str(dest),syntaxWarnings=[],fontProgramsEqual=True,untouchedRuns=len(before),metadataEqual=True,replacementExtracted=True,comparisons=comparisons))
(OUT/'independent-verification.json').write_text(json.dumps(dict(success=True,engine='Poppler + pypdf + qpdf via pikepdf (development only)',cases=rows),indent=2));print('Independent checks passed:',len(rows),'PDFs at 72 and 144 DPI')
