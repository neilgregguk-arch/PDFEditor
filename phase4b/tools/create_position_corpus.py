from pathlib import Path
import io
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader,PdfWriter
from pypdf.generic import DecodedStreamObject,NameObject
r=Path(__file__).resolve().parents[1];out=r/'run/position-corpus';out.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('Compatibility',str(r/'run/assets/PrototypeSansAscii.ttf')))
for name,kind in [('visible-whitespace','visible'),('adjacent-label','label'),('nearby-graphic','graphic'),('restricted-boundary','boundary')]:
 b=io.BytesIO();c=canvas.Canvas(b,pagesize=(612,792));t=c.beginText(60,650);t.setFont('Compatibility',12);t.setCharSpace(.2);t.textLine('cafe calm.');c.drawText(t)
 if kind=='label':c.drawString(180,650,'nearby label')
 if kind=='graphic':c.rect(90,645,8,12,fill=1)
 if kind=='visible':c.setFont('Compatibility',12);c.drawString(110,650,'X')
 c.save();w=PdfWriter(clone_from=PdfReader(b))
 if kind=='boundary':w.pages[0].mediabox.upper_right=(110,792)
 if kind=='visible':
  f=next(x.get_object() for x in w.pages[0]['/Resources']['/Font'].values() if '/ToUnicode' in x.get_object());cm=f['/ToUnicode'].get_data();assert b'<58> <0058>' in cm;cm=cm.replace(b'<58> <0058>',b'<58> <0020>');st=DecodedStreamObject();st.set_data(cm);f[NameObject('/ToUnicode')]=w._add_object(st)
 with (out/(name+'.pdf')).open('wb') as f:w.write(f)
