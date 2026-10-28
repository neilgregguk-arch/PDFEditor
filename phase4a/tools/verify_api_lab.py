from pathlib import Path
import sys,json,subprocess
import numpy as np
from PIL import Image
from pypdf import PdfReader
import hashlib
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
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'evidence';RENDERS=OUT/'api-lab/renders';RENDERS.mkdir(exist_ok=True)
lab=json.loads((OUT/'api-investigation.json').read_text());rows=[]
def render(path,label,dpi):
 prefix=RENDERS/(label+'-'+str(dpi));subprocess.run(['pdftoppm','-f','1','-singlefile','-r',str(dpi),'-png',str(path),str(prefix)],check=True,capture_output=True);return np.asarray(Image.open(str(prefix)+'.png').convert('RGB'),dtype=np.int16)
source=Path(lab['cases'][0]['source']);a=PdfReader(source)
for case in lab['cases']:
 dest=Path(case['destination']);b=PdfReader(dest);assert font_hashes(a)==font_hashes(b);assert dict(a.metadata)==dict(b.metadata);metrics=[]
 for dpi in [72,144]:
  before=render(source,'source',dpi);after=render(dest,case['mechanism'],dpi);changed=np.max(np.abs(before-after),axis=2)>8;yy,xx=np.indices(changed.shape);scale=dpi/72
  owned=(xx/scale>=70)&(xx/scale<=540)&(yy/scale>=68)&(yy/scale<=90);outside=int(np.sum(changed&~owned));assert outside==0
  if case['mechanism'] in ['SetText-original-positions','SetCharcodes-original-positions']:assert not np.any(changed)
  if 'equal-width' in case['mechanism']:assert np.any(changed)
  correct=render(Path(lab['cases'][1]['destination']),'correct-existing',dpi)
  delta_from_correct=int(np.sum(np.max(np.abs(after-correct),axis=2)>8))
  if case['mechanism']=='SetCharcodes-wrong-space':assert delta_from_correct>0
  if case['mechanism']=='SetText-existing':assert delta_from_correct==0
  metrics.append(dict(dpi=dpi,changed=int(np.sum(changed)),outside=outside,differingPixelsVsCorrectExisting=delta_from_correct))
 rows.append(dict(mechanism=case['mechanism'],fontProgramsPreserved=True,metadataEqual=True,reopenedText=case['reopenedObjectText'],expectedTextMatches=case['replacementExtracts'],maxNeighbourGlyphShiftPt=case['maxNeighbourGlyphShiftPt'],maxTargetOriginShiftPt=case['maxOriginalTargetGlyphShiftPt'],comparisons=metrics,productionApproved=False))
(OUT/'api-independent-verification.json').write_text(json.dumps(dict(cases=rows,scope='experimental known-object mapping; not production-approved eligibility'),indent=2));print('Verified',len(rows),'API experiments, including negative controls')
