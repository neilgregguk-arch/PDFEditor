"""Independent font inventory plus actual before/after worker classifications."""
from pathlib import Path
import sys,json,io,re,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent));import test_engine as t
from pypdf import PdfReader
from fontTools.ttLib import TTFont
ROOT=t.ROOT;OUT=ROOT/'evidence'
def fonts(path):
 rows=[]
 for name,ref in PdfReader(path).pages[0]['/Resources']['/Font'].items():
  f=ref.get_object();child=f['/DescendantFonts'][0].get_object() if '/DescendantFonts' in f else f;desc=child.get('/FontDescriptor',{});desc=desc.get_object() if hasattr(desc,'get_object') else desc
  row=dict(resource=name,baseFont=str(f.get('/BaseFont')),type=str(f['/Subtype']),descendantType=str(child.get('/Subtype')),encoding=str(f.get('/Encoding')),hasToUnicode='/ToUnicode' in f,taggedSubset=bool(re.match(r'^/[A-Z]{6}\+',str(f.get('/BaseFont')))),embedded=False)
  if '/FontFile2' in desc:
   raw=desc['/FontFile2'].get_data();font=TTFont(io.BytesIO(raw));cmap=font.getBestCmap() if 'cmap' in font else None
   row.update(embedded=True,fontProgramSha256=hashlib.sha256(raw).hexdigest(),fontGlyphSlots=font['maxp'].numGlyphs,unicodeCmapEntries=len(cmap or {}),hasCmapTable='cmap' in font,embeddingFsType=font['OS/2'].fsType,unitsPerEm=font['head'].unitsPerEm)
   if 'loca' in font:
    locations=font['loca'].locations;row['nonemptyGlyphs']=sum(a!=b for a,b in zip(locations,locations[1:]))
  rows.append(row)
 return rows
paths=sorted((ROOT/'run/corpus').glob('*.pdf'))+sorted((ROOT/'run/font-corpus').glob('*.pdf'));original=t.RUN;t.RUN=ROOT.parent/'phase3/run';old=t.Worker();t.RUN=original;new=t.Worker();rows=[]
for path in paths:
 a=old.call(Command='inspect',Source=str(path));b=new.call(Command='inspect',Source=str(path));assert a['Ok'] and b['Ok'],(path,a.get('Error'),b.get('Error'))
 outcomes=[dict(destination=s['destination'],draft=s['draft'],safe=True,verification=s['verification']) for doc in ['discovery-tests.json','compatibility-tests.json'] for s in json.loads((OUT/doc).read_text())['saved'] if Path(s['source'])==path]
 rows.append(dict(file=path.relative_to(ROOT/'run').as_posix(),sha256=t.WireHash(path) if hasattr(t,'WireHash') else hashlib.sha256(path.read_bytes()).hexdigest(),generator='Microsoft Word 16.0' if path.name.startswith('Word-') or path.name=='11-word-letter.pdf' else 'Microsoft PowerPoint 16.0' if path.name.startswith('PowerPoint') else 'MuPDF + subset / mapping restriction' if path.name.startswith(('09-','10-','J-')) else 'ReportLab / fontTools / mapping variants',fonts=fonts(path),phase3=[dict(state=r['Eligibility'],text=r['OriginalText'],reasons=r['Reasons']) for r in a['Data']['Regions']],phase4a=[dict(state=r['Eligibility'],text=r['OriginalText'],reasons=r['Reasons'],characters=r['Characters']) for r in b['Data']['Regions']],successfulEdits=outcomes))
old.close();new.close();(OUT/'compatibility-matrix.json').write_text(json.dumps(rows,indent=2));print('Compared',len(rows),'sources')
