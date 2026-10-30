"""Run unchanged inherited test logic with output roots redirected into R1 staging."""
from pathlib import Path
import argparse,sys,types,hashlib,json
ap=argparse.ArgumentParser();ap.add_argument('--stage',required=True);ap.add_argument('--tool',required=True);args=ap.parse_args()
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/'phase5_2_2/tools';stage=Path(args.stage).resolve()
assert stage.is_relative_to(ROOT/'.local-generated') and (stage/'run/PdfWorker.exe').is_file()
sys.path.insert(0,str(SRC));(stage/'evidence').mkdir(exist_ok=True)
rewrites=[]
def redirected(path):
 text=path.read_text(encoding='utf-8');old='Path(__file__).resolve().parents[1]'
 if old in text:text=text.replace(old,f'Path({str(stage)!r})');rewrites.append(dict(file=path.name,change='Output/test root only'))
 for old,new in [("ROOT.parent/'phase3/run'",f"Path({str(ROOT/'phase3/run')!r})"),("b.ROOT.parent/'phase4c2/evidence/final-controls-approved/wrap-many-ui.pdf'",f"Path({str(ROOT/'phase4c2/evidence/final-controls-approved/wrap-many-ui.pdf')!r})")]:
  if old in text:text=text.replace(old,new);rewrites.append(dict(file=path.name,change='Read-only historical reference path'))
 return text
if args.tool!='test_engine':
 p=SRC/'test_engine.py';engine=types.ModuleType('test_engine');engine.__file__=str(p);sys.modules['test_engine']=engine;exec(compile(redirected(p),str(p),'exec'),engine.__dict__)
p=SRC/(args.tool+'.py');assert p.is_file() and p.parent==SRC
(stage/'evidence'/('recipe-'+args.tool+'.json')).write_text(json.dumps(dict(source=str(p.relative_to(ROOT)),sourceSha256=hashlib.sha256(p.read_bytes()).hexdigest(),rewrites=rewrites+([dict(file=p.name,change='Output/test root only')] if 'Path(__file__).resolve().parents[1]' in p.read_text(encoding='utf-8') else []),note='Only path bindings change in memory; historical source and application logic are not edited.'),indent=2),encoding='utf-8')
sys.argv=[str(p)]
exec(compile(redirected(p),str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
