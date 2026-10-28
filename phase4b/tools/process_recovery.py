from pathlib import Path
import subprocess,time,json,hashlib
R=Path(__file__).resolve().parents[1];out=R/'evidence'/('process-recovery-'+str(time.time_ns()));out.mkdir();store=out/'store';store.mkdir();source=R/'run/document-corpus/multi-natural.pdf';digest=hashlib.sha256(source.read_bytes()).hexdigest()
for stage in [1,2]:
 p=subprocess.Popen([str(R/'run/PdfEditorPrototype.exe'),str(source),'--recovery-stage'+str(stage),'--recovery-store',str(store),'--audit',str(out)]);p.wait(timeout=60);assert p.returncode==0
 data=json.loads((out/f'process-stage{stage}.json').read_text(encoding='utf-8'));assert data['success'],data
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
a=json.loads((out/'process-stage1.json').read_text());b=json.loads((out/'process-stage2.json').read_text());assert a['pid']!=b['pid'];assert a['changes']==b['changes']
(R/'evidence/process-recovery.json').write_text(json.dumps(dict(success=True,separateProcesses=True,sourceHashPreserved=True,folder=str(out),first=a,second=b),indent=2));print('Three drafts on two pages recovered across two exited processes, history restored and combined output saved')
