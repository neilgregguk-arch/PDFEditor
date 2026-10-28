"""Independent Poppler renders / pypdf run geometry and font-program checks."""
from pathlib import Path
import json,subprocess,hashlib,xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
from pypdf import PdfReader
root=Path(__file__).resolve().parents[1];evid=root/'evidence';folder=evid/'independent';folder.mkdir(exist_ok=True)
rows=[]
def fonts(path):
    result=[]
    for resource in PdfReader(path).pages[0]['/Resources']['/Font'].values():
        font=resource.get_object()
        for entry in font.get('/DescendantFonts',[font]):
            descriptor=entry.get_object().get('/FontDescriptor')
            if descriptor:
                descriptor=descriptor.get_object()
                for key in ['/FontFile','/FontFile2','/FontFile3']:
                    if key in descriptor:result.append(hashlib.sha256(descriptor[key].get_object().get_data()).hexdigest())
    return sorted(set(result))
def runs(path):
    page=PdfReader(path).pages[0];result=[];height=float(page.mediabox.height)
    def visit(text,cm,tm,font,size):
        if text.strip():
            x=tm[4]*cm[0]+tm[5]*cm[2]+cm[4];y=height-(tm[4]*cm[1]+tm[5]*cm[3]+cm[5])
            result.append((text.strip(),round(x,3),round(y,3),round(size,3),font.get('/BaseFont') if font else None))
    page.extract_text(visitor_text=visit);return result
for name in ['A-Simple','B-Longer']:
    a=evid/'pdf'/(name+'.pdf');b=evid/'pdf'/(name+'-edited.pdf');r=json.loads(Path(str(a)+'.region.json').read_text())
    # Use authoritative saved layout, not an inferred paragraph.
    suite=json.loads((evid/'engine-tests.json').read_text());record=next(v for v in suite['saved_outputs'] if v['case']==name and (name!='A-Simple' or v['draft']=='A genuinely changed paragraph.'))
    layout=record['result']['Verification']['layout'];top=r['Baseline']-r['Ascent'];bottom=top+max(len(r['OriginalLines']),len(layout['Lines']))*r['LineHeight']
    metrics=[]
    for dpi in [72,144]:
        images=[]
        for label,path in [('before',a),('after',b)]:
            prefix=folder/f'{name}-{dpi}-{label}';subprocess.run(['pdftoppm','-r',str(dpi),'-singlefile','-png',str(path),str(prefix)],check=True,capture_output=True);images.append(np.asarray(Image.open(prefix.with_suffix('.png')).convert('RGB')).astype(int))
        delta=np.abs(images[0]-images[1]).max(axis=2);mask=np.zeros(delta.shape,dtype=bool);scale=dpi/72
        mask[max(0,int((top-2)*scale)):int((bottom+2)*scale)+1,max(0,int((r['X']-2)*scale)):int((r['X']+r['Width']+2)*scale)+1]=True
        outside=int(((delta>8)&~mask).sum());assert outside==0,(name,dpi,outside)
        metrics.append({'dpi':dpi,'outside_pixels':outside,'changed_pixels':int((delta>8).sum())})
    def outside(w):return not (r['X']-2<=w[1]<=r['X']+r['Width']+2 and top-2<=w[2]<=bottom+2)
    wa=sorted(w for w in runs(a) if outside(w));wb=sorted(w for w in runs(b) if outside(w));assert wa==wb,(name,wa,wb)
    fa,fb=fonts(a),fonts(b);assert fa==fb and r['FontHash'] in fa
    rows.append({'case':name,'renders':metrics,'pypdf_neighbour_run_origins_style_unchanged':True,'neighbour_run_count':len(wa),'embedded_font_program_sha256':fa,'pypdf_font_programs_match':True})
(evid/'independent-verification.json').write_text(json.dumps({'renderer':'Poppler 26.07.0','extractor':'pypdf 6.10.0','scope':'two representative saved PDFs, two resolutions; run baselines/style, not all glyph geometry','results':rows},indent=2));print(json.dumps(rows,indent=2))
