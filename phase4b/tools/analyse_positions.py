from pathlib import Path
import json,re,hashlib
from pypdf import PdfReader
from fontTools.ttLib import TTFont
from io import BytesIO
R=Path(__file__).resolve().parents[1];E=R/'evidence';source=R/'run/corpus/11-word-letter.pdf';reader=PdfReader(source);page=reader.pages[0];font=page['/Resources']['/Font']['/F1'];child=font['/DescendantFonts'][0];program=child['/FontDescriptor']['/FontFile2'].get_data();tt=TTFont(BytesIO(program));cid=child['/CIDToGIDMap'].get_data();mapping={}
for block in re.findall(rb'beginbfrange(.*?)endbfrange',font['/ToUnicode'].get_data(),re.S):
 for first,last,values in re.findall(rb'<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>\s*(\[.*?\]|<[0-9a-fA-F]+>)',block,re.S):
  codes=list(range(int(first,16),int(last,16)+1));vals=re.findall(rb'<([0-9a-fA-F]+)>',values)
  if not values.startswith(b'['):vals=[f'{int(vals[0],16)+i:04x}'.encode() for i in range(len(codes))]
  for code,u in zip(codes,vals):mapping[code]=bytes.fromhex(u.decode()).decode('utf-16-be')
runs=[];selected=None
for args,op in page.get_contents().operations:
 if op==b'Tf':selected=str(args[0])
 if op not in [b'TJ',b'Tj']:continue
 vals=args[0] if op==b'TJ' else args;raw=b''.join(v if isinstance(v,bytes) else v.original_bytes for v in vals if isinstance(v,(str,bytes)))
 codes=[int.from_bytes(raw[i:i+2],'big') for i in range(0,len(raw),2)] if selected=='/F1' else list(raw)
 runs.append(dict(fontResource=selected,rawHex=raw.hex(),codes=codes,tjAdjustments=[float(v) for v in vals if not isinstance(v,(str,bytes))]))
matrix=json.loads((E/'position-matrix.json').read_text());observed=next(x for x in matrix['cases'] if x['name'].replace('\\','/')=='corpus/11-word-letter.pdf')['phase4a1'];lab=json.loads((E/'font-investigation.json').read_text())[0];objects=[]
for i,run in enumerate(runs):
 o=next(x for x in lab['objects'] if x['index']==i);region=next((x for x in observed if x['Objects']==[i]),None);chars=[]
 if region:
  assert len(run['codes'])==len(region['Glyphs'])
  for code,g in zip(run['codes'],region['Glyphs']):
   u=mapping[code];gid=int.from_bytes(cid[code*2:code*2+2],'big');name=tt.getGlyphName(gid);assert u==g['Text'];chars.append(dict(logicalOffset=g['Index'],unicode=u,pdfCharacterCode=code,glyphId=gid,naturalAdvancePt=tt['hmtx'][name][0]/tt['head'].unitsPerEm*o['size'],originalOriginX=g['OriginX'],baselineTopDown=g['Baseline'],originalBoundingBox=g['Bounds']))
 objects.append(dict(index=i,raw=run,extractedByPDFium=o['text'],matrix=o['matrix'],size=o['size'],characters=chars,classification='Complete visible text object' if chars else 'Separately retained, raw U+0020 code, zero extent, no painted contribution at 144 DPI; semantic role unknown'))
(E/'word-position-analysis.json').write_text(json.dumps(dict(source=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),fontProgramSha256=hashlib.sha256(program).hexdigest(),objects=objects,regions=observed,originalContent=page.get_contents().get_data().decode('latin1'),observed='Raw codes/TJ arrays from pypdf; cmap/GIDs/metrics from fontTools; positions/bounds from pinned PDFium',inferred='Paragraph meaning, blank-line role and tagged reading-order relationships remain unproven; no ownership of other-font spaces is assumed'),indent=2))
print('Recorded',len(objects),'objects and',sum(len(o['characters']) for o in objects),'visible glyphs')
