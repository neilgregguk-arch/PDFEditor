"""Targeted development sources: ReportLab + fontTools, then parsed mapping variants.
No runtime dependency and no mutation of earlier phases. Only fictional documents.
"""
from pathlib import Path
import json,hashlib
from fontTools import subset
from fontTools.ttLib import TTFont as Font
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pikepdf
import pymupdf
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'phase5_2/run/font-corpus';OUT.mkdir(parents=True,exist_ok=True)
WORK=ROOT/'phase5_2/test-work/font-generation';WORK.mkdir(parents=True,exist_ok=True)
records=[]
def generate(name,original,fontfile,characters,spacing=0,fragment=False):
 font=Font(fontfile);font.recalcTimestamp=False;options=subset.Options();options.recalc_timestamp=False;options.notdef_glyph=True;options.notdef_outline=True;options.recommended_glyphs=False
 ss=subset.Subsetter(options=options);ss.populate(text=characters);ss.subset(font)
 if Path(fontfile).name=='Vera.ttf':
  for entry in font['name'].names:
   if entry.nameID in [1,2,3,4,6,16,17]:
    value={1:'Compatibility Sans',2:'Regular',3:'CompatibilitySans-Subset',4:'Compatibility Sans',6:'CompatibilitySans-Subset',16:'Compatibility Sans',17:'Regular'}[entry.nameID]
    entry.string=value.encode(entry.getEncoding(),errors='replace')
 # Standalone intermediates are local test inputs, never part of the distribution.
 path=WORK/(name+'.ttf');font.save(path);pdfmetrics.registerFont(TTFont(name,str(path)))
 target=OUT/(name+'.pdf');c=canvas.Canvas(str(target),pagesize=(612,792),invariant=1);c.setTitle(name);c.setAuthor('PDF Editor V2 fictional compatibility corpus');c.setFillColorRGB(.14,.22,.28);c.setFont(name,12)
 if fragment:c.drawString(60,642,'cafe');c.drawString(150,642,'calm')
 elif spacing:
  t=c.beginText(60,642);t.setFont(name,12);t.setCharSpace(spacing);t.textOut(original);c.drawText(t)
 else:c.drawString(60,642,original)
 c.setFont('Helvetica',10);c.setFillColorRGB(.4,.4,.4);c.drawString(60,400,'Protected reference block - keep its position.');c.save()
 records.append(dict(file=target.name,generator='ReportLab + fontTools subset',original=original,subsetCharacters=characters,expected='structural refusal' if spacing or fragment else 'proposed-character eligibility'))
 return target
vera=ROOT/'assets/Vera.ttf';bold=Path('C:/Windows/Fonts/arialbd.ttf')
basic=generate('A-subset-existing','cafe calm.',vera,'cafe lm.')
generate('B-original-only','cafe',vera,'cafe')
generate('C-subset-bold','Bold calm.',bold,'Bold cam.')
generate('D-fragmented','cafe calm',vera,'cafe lm.',fragment=True)
generate('E-character-spacing','cafe calm.',vera,'cafe lm.',spacing=.2)
generate('F-kerning','cafe calm.',vera,'cafe lm.')
# Add genuine TJ adjustments while preserving text/glyph programs.
with pikepdf.open(OUT/'F-kerning.pdf',allow_overwriting_input=True) as pdf:
 page=pdf.pages[0];instructions=pikepdf.parse_content_stream(page);new=[]
 for operands,op in instructions:
  if str(op)=='Tj' and bytes(operands[0])==b'cafe calm.':new.append(([pikepdf.Array([pikepdf.String('ca'),20,pikepdf.String('fe calm.')])],pikepdf.Operator('TJ')))
  else:new.append((operands,op))
 page.Contents=pdf.make_stream(pikepdf.unparse_content_stream(new));pdf.save(OUT/'F-kerning.pdf')
for name,mode in [('G-duplicate-unicode','duplicate'),('H-wrong-unicode','wrong'),('I-missing-unicode','missing')]:
 with pikepdf.open(basic) as pdf:
  f=next(v for v in pdf.pages[0].Resources.Font.values() if '/ToUnicode' in v)
  cmap=f.ToUnicode.read_bytes()
  # ReportLab ASCII readable subsets declare direct 00..7F mappings. Rewrite one
  # mapping to deliberately create duplicate/incorrect Unicode, without changing glyphs.
  if mode=='duplicate':cmap=cmap.replace(b'<62> <0062>',b'<62> <0063>')
  elif mode=='wrong':cmap=cmap.replace(b'<63> <0063>',b'<63> <0061>')
  else:cmap=cmap.replace(b'<63> <0063>',b'<63> <0000>')
  assert cmap!=f.ToUnicode.read_bytes(),name
  f.ToUnicode=pdf.make_stream(cmap);pdf.save(OUT/(name+'.pdf'));records.append(dict(file=name+'.pdf',generator='ReportLab + pikepdf adversarial ToUnicode',expected='verified glyph reuse or explicit mapping refusal',variant=mode))
# A valid, Word-like condition: font subset retains one unused glyph, but the PDF
# ToUnicode map describes only actual document characters. The font program is
# unchanged by this mapping restriction. It is not an editing sidecar.
program=Font(vera);program.recalcTimestamp=False;opts=subset.Options();opts.recalc_timestamp=False;ss=subset.Subsetter(options=opts);ss.populate(text='cafe lm.Z');ss.subset(program)
for entry in program['name'].names:
 if entry.nameID in [1,3,4,6,16]:entry.string=('Compatibility Sans' if entry.nameID in [1,4,16] else 'CompatibilitySans-Subset').encode(entry.getEncoding(),errors='replace')
font_path=WORK/'partial-encoding.ttf';program.save(font_path);doc=pymupdf.open();page=doc.new_page(width=612,height=792);page.insert_font(fontname='Original',fontfile=str(font_path));page.insert_text((60,150),'cafe calm.',fontname='Original',fontsize=12,color=(.14,.22,.28));page.insert_text((60,392),'Protected reference block - keep its position.',fontsize=10)
temp=WORK/'partial-before-map.pdf';doc.save(temp);doc.close();encoding=program.getBestCmap()
with pikepdf.open(temp) as pdf:
 f=next(v for v in pdf.pages[0].Resources.Font.values() if '/ToUnicode' in v)
 entries='\n'.join(f'<{program.getGlyphID(encoding[ord(c)]):04x}> <{ord(c):04x}>' for c in sorted(set('cafe calm.')))
 cmap=f'/CIDInit /ProcSet findresource begin\n12 dict begin\nbegincmap\n/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def\n/CMapName /Compatibility-UCS def\n/CMapType 2 def\n1 begincodespacerange\n<0000> <ffff>\nendcodespacerange\n{len(set("cafe calm."))} beginbfchar\n{entries}\nendbfchar\nendcmap\nCMapName currentdict /CMap defineresource pop\nend\nend'
 f.ToUnicode=pdf.make_stream(cmap.encode());pdf.save(OUT/'J-partial-encoding.pdf')
records.append(dict(file='J-partial-encoding.pdf',generator='MuPDF + fontTools subset; ToUnicode restricted to used glyphs',original='cafe calm.',expected='newly eligible existing glyphs; retained but unmapped Z refused'))
import shutil
shutil.copyfile(ROOT/'assets/bitstream-vera-license.txt',OUT/'FONT-LICENSE.txt')
for row in records:row['sha256']=hashlib.sha256((OUT/row['file']).read_bytes()).hexdigest()
(OUT/'corpus.json').write_text(json.dumps(records,indent=2));print('Created',len(records),'targeted sources')
