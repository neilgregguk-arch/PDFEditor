from pathlib import Path
import io,re,json,hashlib
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,DecodedStreamObject
R=Path(__file__).resolve().parents[1];O=R/'run/document-corpus';O.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('Prototype',str(R/'run/assets/PrototypeSansAscii.ttf')))
def natural(path,collision=False):
 c=canvas.Canvas(str(path),pagesize=(612,792));c.setFont('Prototype',12)
 if collision:
  c.drawString(60,692,'alpha area.');c.drawString(60,639,'.');c.drawString(60,392,'Reference area stays unchanged.')
 else:
  for y,text in [(690,'First paragraph has room for a working draft.'),(480,'Second paragraph can change independently.'),(270,'Third paragraph keeps its own original font.')]:c.drawString(60,y,text)
  c.showPage();c.setFont('Prototype',12);c.drawString(60,690,'Another page retains its own editable paragraph.');c.drawString(60,300,'Untouched reference on the second page.')
 c.save()
natural(O/'multi-natural.pdf');natural(O/'collision.pdf',True)
# Development-only mixed fixture: untouched genuine Word streams plus an
# independently generated natural text stream, without product ownership hints.
b=io.BytesIO();c=canvas.Canvas(b,pagesize=(595.32,841.92));c.setFont('Prototype',12);c.drawString(72,400,'Natural paragraph retains its original font.');c.save();extra=PdfReader(b);w=PdfWriter(clone_from=R/'run/corpus/11-word-letter.pdf');p=w.pages[0];raw=extra.pages[0].get_contents().get_data()
for name,ref in extra.pages[0]['/Resources']['/Font'].items():
 new=NameObject('/Mixed'+name[1:]);p['/Resources']['/Font'][new]=ref.clone(w);raw=re.sub(re.escape(str(name).encode())+rb'(?=\s)',str(new).encode(),raw)
st=DecodedStreamObject();st.set_data(p.get_contents().get_data()+b'\nq\n'+raw+b'\nQ\n');p[NameObject('/Contents')]=w._add_object(st)
with (O/'mixed.pdf').open('wb') as f:w.write(f)
(O/'generators.json').write_text(json.dumps(dict(generators=['ReportLab independent natural/collision pages','pypdf development fixture composition, original genuine Word page plus natural stream'],fictional=True,ownershipHints=False,sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in O.glob('*.pdf')}),indent=2))
