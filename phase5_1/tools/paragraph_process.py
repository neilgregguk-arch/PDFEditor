"""Separate WPF processes/stores prove file rediscovery independently of recovery."""
from pathlib import Path
import subprocess,time,json,hashlib,psutil
R=Path(__file__).resolve().parents[1];E=R/'evidence';out=E/('paragraph-controls-'+str(time.time_ns()));out.mkdir();runs=[]
for stage in range(1,7):
 folder=out/('stage'+str(stage));folder.mkdir();store=out/('store'+str(5 if stage==6 else stage));store.mkdir(exist_ok=True);initial=[p.name for p in store.glob('*')]
 if stage==1:source=R/'run/corpus/11-word-letter.pdf'
 elif stage<=4:source=out/('ui-generation'+str(stage-1)+'.pdf')
 else:source=Path(next(r['destination'] for r in json.loads((E/'roundtrip-tests.json').read_text())['saved'] if Path(r['destination']).name.startswith('mixed-generation1-')))
 before=hashlib.sha256(source.read_bytes()).hexdigest();p=subprocess.Popen([str(R/'run/PdfEditorPrototype.exe'),str(source),'--paragraph-stage',str(stage),'--paragraph-shared',str(out),'--recovery-store',str(store),'--audit',str(folder)]);created=psutil.Process(p.pid).create_time();p.wait(timeout=180);assert p.returncode==0,p.returncode
 result=json.loads((folder/'paragraph-control-tests.json').read_text(encoding='utf-8'));runs.append(dict(stage=stage,pid=p.pid,created=created,initialRecoveryFiles=initial,folder=str(folder),source=str(source),sourceHash=before,result=result));assert hashlib.sha256(source.read_bytes()).hexdigest()==before;print('Stage',stage,result['tests'],'checks;',result['failures'],'failures',flush=True)
 if result['failures']:break
assert len({(r['pid'],r['created']) for r in runs})==len(runs)
(E/'paragraph-controls.json').write_text(json.dumps(dict(success=len(runs)==6 and all(r['result']['failures']==0 for r in runs),tests=sum(r['result']['tests'] for r in runs),failures=sum(r['result']['failures'] for r in runs),folder=str(out),runs=runs),indent=2),encoding='utf-8')
