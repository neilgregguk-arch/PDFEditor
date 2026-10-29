"""Retain independently verified PDFs whose test-work/temp paths are not distributed."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[1];E=R/'evidence';D=E/'certified-exports';D.mkdir(exist_ok=True)
records=json.loads((E/'verified-export-records.json').read_text(encoding='utf-8'));mapping={}
for name in ['independent-verification','position-independent-verification']:
 records+=json.loads((E/(name+'.json')).read_text(encoding='utf-8'))['cases']
for row in records:
 for key in ['source','destination']:
  p=Path(row[key]);sha=hashlib.sha256(p.read_bytes()).hexdigest()
  try:rel=p.relative_to(R);portable='test-work' not in rel.parts
  except ValueError:portable=False
  if portable:dest=p
  else:
   dest=D/(sha+'.pdf')
   if not dest.exists():shutil.copyfile(p,dest)
   side=Path(str(p)+'.region.json')
   if side.exists():shutil.copyfile(side,Path(str(dest)+'.region.json'))
  mapping[str(p)]=dict(path=dest.relative_to(R.parent).as_posix(),sha256=sha)
(E/'portable-pdf-index.json').write_text(json.dumps(mapping,indent=2),encoding='utf-8');print('Portable PDF paths:',len(mapping),'archived outside-path PDFs:',len(list(D.glob('*.pdf'))))
