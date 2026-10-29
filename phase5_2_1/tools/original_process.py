"""Fresh WPF processes for authentic original discovery and four-region recovery."""
from pathlib import Path
import subprocess,time,json,hashlib,psutil
R=Path(__file__).resolve().parents[1];E=R/'evidence';out=E/('original-controls-'+str(time.time_ns()));out.mkdir();runs=[]
for stage in range(7,12):
 folder=out/('stage'+str(stage));folder.mkdir();store=out/('store'+str(10 if stage==11 else stage));store.mkdir(exist_ok=True)
 if stage==7:source=R/'run/original-paragraphs/Word-cafe-paragraph.pdf'
 elif stage<=9:source=out/('original-ui-generation'+str(stage-7)+'.pdf')
 else:source=Path(json.loads((E/'original-mixed-expectation.json').read_text(encoding='utf-8'))['source'])
 before=hashlib.sha256(source.read_bytes()).hexdigest();p=subprocess.Popen([str(R/'run/PdfEditorPrototype.exe'),str(source),'--paragraph-stage',str(stage),'--paragraph-shared',str(out),'--recovery-store',str(store),'--audit',str(folder)]);created=psutil.Process(p.pid).create_time();p.wait(timeout=180);assert p.returncode==0,p.returncode
 result=json.loads((folder/'paragraph-control-tests.json').read_text(encoding='utf-8'));runs.append(dict(stage=stage,pid=p.pid,created=created,folder=str(folder),source=str(source),sourceHash=before,result=result));assert hashlib.sha256(source.read_bytes()).hexdigest()==before;print('Original stage',stage,result['tests'],'checks;',result['failures'],'failures',flush=True)
 if result['failures']:break
(E/'original-controls.json').write_text(json.dumps(dict(success=len(runs)==5 and all(r['result']['failures']==0 for r in runs),tests=sum(r['result']['tests'] for r in runs),failures=sum(r['result']['failures'] for r in runs),folder=str(out),runs=runs),indent=2),encoding='utf-8')
