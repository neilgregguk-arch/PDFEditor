"""Development corpus: independent ReportLab and MuPDF generators. No runtime dependency."""
from pathlib import Path
import json, hashlib
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pymupdf
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'phase3/run/corpus';OUT.mkdir(parents=True,exist_ok=True)
regular=ROOT/'assets/Vera.ttf';bold=Path('C:/Windows/Fonts/arialbd.ttf')
pdfmetrics.registerFont(TTFont('CorpusRegular',str(regular)))
pdfmetrics.registerFont(TTFont('CorpusBold',str(bold)))
records=[]
def make(name,draw,expected):
    path=OUT/(name+'.pdf');c=canvas.Canvas(str(path),pagesize=(612,792),invariant=1)
    c.setTitle('Phase 3 fictional test corpus - '+name);c.setAuthor('PDF Editor V2 test corpus')
    def line(text,x,y,size=12,font='CorpusRegular',color=(.14,.22,.28)):
        c.setFont(font,size);c.setFillColorRGB(*color);c.drawString(x,792-y,text)
    draw(c,line);c.save();records.append(dict(file=path.name,generator='ReportLab',expected=expected))
def letter(c,line):
    line('Northbank Research',60,65,22,'CorpusBold')
    line('Dear reader,',60,125)
    line('This ordinary digital letter contains an embedded font and plain Latin text.',60,165)
    line('The next visual line belongs to the same paragraph and keeps stable leading.',60,183)
    line('A separate paragraph remains a separate region after a clear vertical gap.',60,240)
    line('Kind regards,',60,315)
make('01-letter',letter,'editable paragraphs; heading and salutation separate')
def report(c,line):
    line('Quarterly field report',60,65,20,'CorpusBold')
    for i,t in enumerate(['A single column report demonstrates ordinary text with stable line spacing.', 'The paragraph continues with sufficient width to justify a conservative join.', 'Its final line remains part of the same region.']):line(t,60,130+18*i)
    line('A blue note uses a separate colour and smaller size.',60,245,10,color=(.1,.3,.8))
    line('Bold summary has its own original font.',60,300,14,'CorpusBold')
    c.showPage();line('Untouched second page with independent content.',60,90)
make('02-report',report,'regular, bold, coloured regions; untouched second page')
make('03-adjacent',lambda c,l:(l('Account label',60,130),l('Value to the right',315,130),l('An isolated body sentence remains identifiable.',60,230)),'same-baseline labels limited; isolated text editable')
def columns(c,l):
    for i in range(5):l('Left column line '+str(i+1),60,130+18*i);l('Right column line '+str(i+1),325,130+18*i)
make('04-two-columns',columns,'limited; no cross-column joins')
def table(c,l):
    for y in [110,140,170,200]:c.line(60,792-y,520,792-y)
    for x in [60,280,520]:c.line(x,592,x,682)
    for i in range(3):l('Row '+str(i+1),70,130+30*i);l('Amount '+str(i+1),300,130+30*i)
make('05-table',table,'limited; no table cell reconstruction')
make('06-ambiguous',lambda c,l:(l('Short sentence.',60,130),l('Another unrelated short line.',60,148)),'limited short-line boundary; do not merge')
def rotated(c,l):
    c.saveState();c.translate(130,500);c.rotate(18);c.setFont('CorpusRegular',12);c.drawString(0,0,'Rotated text is not supported.');c.restoreState()
make('07-rotated',rotated,'view only transform')
def base14(c,l):c.setFont('Helvetica',12);c.drawString(60,650,'A nonembedded standard font is visible but cannot be substituted.')
make('08-nonembedded',base14,'view only font not embedded')
def image(c,l):
    l('An image overlaps this existing text region.',60,130)
    c.drawImage(str(ROOT/'assets/diagram.png'),60,620,width=280,height=60)
make('12-image-overlap',image,'limited intersecting image; no automatic image movement')
def shuffled(c,l):
    l('The final visual line belongs to this paragraph.',60,166)
    l('A geometrically ordered paragraph can survive reversed object extraction order.',60,130)
    l('Its second line has the same font and sufficient width for conservative grouping.',60,148)
make('13-shuffled-order',shuffled,'editable paragraph grouped geometrically despite reversed object order')
def annotation(c,l):
    l('This page has an annotation and remains conservatively view only.',60,130)
    c.linkURL('https://example.invalid', (60,650,400,675),relative=0)
make('14-annotation',annotation,'view only page annotation')
def spacing(c,l):
    t=c.beginText(60,650);t.setFont('CorpusRegular',12);t.setCharSpace(1);t.textOut('Explicit letter spacing requires a different layout model.');c.drawText(t)
make('15-letter-spacing',spacing,'view only nonnatural glyph spacing')
for name,full in [('09-mupdf-letter',True),('10-mupdf-subset',False)]:
    d=pymupdf.open();p=d.new_page(width=612,height=792);p.insert_font(fontname='Original',fontfile=str(regular))
    p.insert_text((60,100),'Independent generator letter',fontname='Original',fontsize=18,color=(.12,.22,.3))
    p.insert_text((60,160),'This paragraph was generated independently from the editing engine.',fontname='Original',fontsize=12)
    p.insert_text((60,240),'A second region remains unchanged during the first edit.',fontname='Original',fontsize=12)
    if not full:d.subset_fonts()
    d.save(OUT/(name+'.pdf'));d.close();records.append(dict(file=name+'.pdf',generator='MuPDF',expected='embedded horizontal text; missing subset glyphs blocked when unavailable'))
if (OUT/'11-word-letter.pdf').exists():records.append(dict(file='11-word-letter.pdf',generator='Microsoft Word 16.0',expected='view only subset mapping and object-space restrictions'))
records.sort(key=lambda r:r['file'])
for row in records:row['sha256']=hashlib.sha256((OUT/row['file']).read_bytes()).hexdigest()
(OUT/'corpus.json').write_text(json.dumps(records,indent=2))
print(json.dumps(records,indent=2))
