from pathlib import Path
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,DecodedStreamObject
import re,json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'run/wrap-corpus';O.mkdir(exist_ok=True);src=R/'run/corpus/11-word-letter.pdf'
cmap=PdfReader(src).pages[0]['/Resources']['/Font']['/F1']['/ToUnicode'].get_object().get_data().decode('latin1');a={}
for line in cmap.splitlines():
 m=re.match(r'^<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*(\[.*\]|<[0-9A-Fa-f]+>)$',line.strip())
 if not m:continue
 first,last=int(m[1],16),int(m[2],16);values=re.findall(r'<([0-9A-Fa-f]+)>',m[3]);values=[int(v,16) for v in values]
 for i,c in enumerate(range(first,last+1)):a[c]=chr(values[i] if m[3].startswith('[') else values[0]+i)
encode=lambda text:''.join(f'{next(k for k,v in a.items() if v==c):04x}' for c in text)

def fixture(name,extra):
 w=PdfWriter(clone_from=src);p=w.pages[0];s=DecodedStreamObject();s.set_data(p.get_contents().get_data()+b'\nq\n'+extra.encode()+b'\nQ\n');p[NameObject('/Contents')]=w._add_object(s)
 with (O/(name+'.pdf')).open('wb') as f:w.write(f)
fixture('graphic-below','0 0 0 rg 72 725.92 200 12 re f')
fixture('paragraph-below',f'BT /F1 12 Tf 1 0 0 1 72.024 735.92 Tm <{encode("letter")}> Tj ET')
period=encode('.')
fixture('combined-collision',f'BT /F1 12 Tf 1 0 0 1 72.024 627.37 Tm [<{period}> -20 <{period}>] TJ ET')
w=PdfWriter();w.append(PdfReader(src));w.append(PdfReader(R/'run/font-corpus/Word-Arial.pdf'))
with (O/'two-Word-pages.pdf').open('wb') as f:w.write(f)
(R/'evidence/wrap-corpus.json').write_text(json.dumps(dict(description='Untouched genuine Word content and existing font resources, plus independently appended protected graphic/text or tiny positioned line; no ownership hints.',hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in O.glob('*.pdf')}),indent=2),encoding='utf-8')
