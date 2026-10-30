"""Critical R1 validation; bulk outputs stay ignored, compact summaries are retained."""
from pathlib import Path
import subprocess,sys,time,json,hashlib
ROOT=Path(__file__).resolve().parents[2];ap=__import__('argparse').ArgumentParser();ap.add_argument('--stage',required=True);ap.add_argument('--resume',action='store_true');args=ap.parse_args();stage=Path(args.stage).resolve();E=stage/'evidence';E.mkdir(exist_ok=True);logs=stage/'logs';logs.mkdir(exist_ok=True);rows=[]
tools=Path(__file__).parent
if args.resume and (E/'validation-progress.json').exists():
 old=json.loads((E/'validation-progress.json').read_text(encoding='utf-8'));(E/('earlier-validation-attempt-'+str(time.time_ns())+'.json')).write_text(json.dumps(old,indent=2),encoding='utf-8');rows=[x for x in old if x['exit']==0]
completed={x['suite'] for x in rows}
for name in ['test_engine','test_discovery','test_compatibility','test_position','test_insertion','test_document','test_wrap','test_roundtrip','test_original','multi_region_process','presentation_process','paragraph_process','original_process']:
 if name in completed:print('Already verified',name,flush=True);continue
 print('R1 validation',name,flush=True);t=time.monotonic()
 with (logs/(name+'.log')).open('w',encoding='utf-8') as f:q=subprocess.run([sys.executable,str(tools/'run_inherited.py'),'--stage',str(stage),'--tool',name],stdout=f,stderr=subprocess.STDOUT)
 rows.append(dict(suite=name,exit=q.returncode,seconds=round(time.monotonic()-t,2)));(E/'validation-progress.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
 if q.returncode:print('FAILED',name,flush=True);sys.exit(q.returncode)
# Full inherited control suite explicitly launches and closes the rebuilt WPF app.
folder=E/('controls-'+str(time.time_ns()));folder.mkdir();cmd=[str(stage/'run/PdfEditorPrototype.exe'),'--ui-test','--discovery-ui-test','--font-ui-test','--position-ui-test','--session-ui-test','--insertion-ui-test','--wrap-ui-test','--clipboard-probe','--paragraph-stage','0','--paragraph-shared',str(folder),'--audit',str(folder)]
print('R1 inherited WPF controls',flush=True);q=subprocess.run(cmd,timeout=600);assert q.returncode==0
controls=[]
for p in folder.glob('*tests.json'):
 d=json.loads(p.read_text(encoding='utf-8'));controls.append(dict(suite=p.name,tests=d['tests'],failures=d['failures'],failed=[r for r in d.get('results',d.get('rows',[])) if r.get('status')=='fail']))
for name in ['verify_wrap','verify_paragraph_structure']:
 print('R1 independent',name,flush=True)
 with (logs/(name+'.log')).open('w',encoding='utf-8') as f:q=subprocess.run([sys.executable,str(tools/'run_inherited.py'),'--stage',str(stage),'--tool',name],stdout=f,stderr=subprocess.STDOUT)
 assert q.returncode==0,name
def load(n):return json.loads((E/n).read_text(encoding='utf-8'))
worker=[]
for name in ['engine','discovery','compatibility','position','insertion','document','wrap','roundtrip','original']:
 d=load(name+'-tests.json');bad=sum(r.get('status') in ['fail','error'] for r in d.get('results',d.get('rows',[])));worker.append(dict(suite=name,tests=d['tests'],failures=d.get('failures',bad)))
multi=load('multi-region-release.json');presentation=load('presentation-release.json');para=load('paragraph-controls.json');original=load('original-controls.json');ind=load('wrap-independent-verification.json');structure=load('paragraph-structure-verification.json')
report=dict(stage=str(stage),workers=worker,multi=dict(tests=multi['tests'],failures=multi['failures']),presentation=dict(tests=presentation['result']['tests'],failures=presentation['result']['failures']),marked=dict(tests=para['tests'],failures=para['failures']),original=dict(tests=original['tests'],failures=original['failures']),controls=controls,independent=dict(candidates=len(ind['cases']),success=ind['success'],paragraphGroups=sum(len(c['groups']) for c in structure['cases']),structureSuccess=structure['success']),recipes=rows,cleanupExecuted=False,scope='Build/run after maintenance only. No destructive local cleanup approved or performed; post-cleanup verification remains conditional.')
(E/'R1-validation-summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2),flush=True)
assert not any(x['failures'] for x in worker)
assert all(report[k]['failures']==0 for k in ['multi','presentation','marked','original'])
assert ind['success'] and structure['success']
