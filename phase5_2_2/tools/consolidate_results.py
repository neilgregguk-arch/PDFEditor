"""Index exact final suites without treating known failures as passing."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];E=R/'evidence'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
ui=[]
for p in sorted((E/'controls-shipping').glob('*tests.json')):
 d=load(p);ui.append(dict(file=p.relative_to(E).as_posix(),tests=d['tests'],failures=d['failures'],failed=[r for r in d.get('results',d.get('rows',[])) if r.get('status')=='fail']))
workers=[]
for name in ['engine','discovery','compatibility','position','insertion','document','wrap','roundtrip','original']:
 d=load(E/(name+'-tests.json'));rows=d.get('results',d.get('rows',[]));bad=[v for v in rows if v.get('status')=='fail'];workers.append(dict(suite=name,tests=d['tests'],failures=d.get('failures',len(bad)),success=d.get('success',not bad)))
historical=[]
for p in sorted(E.glob('phase*-regression.json')):
 d=load(p);historical.append(dict(file=p.relative_to(E).as_posix(),tests=d['tests'],success=d['success'],failed=[r for r in d['results'] if r.get('status')=='fail']))
report=dict(inheritedWpf=dict(tests=sum(d['tests'] for d in ui),failures=sum(d['failures'] for d in ui),suites=ui),workers=workers,models=load(E/'model/model-tests.json'),multi=load(E/'multi-region-release.json'),presentation=load(E/'presentation-release.json'),paragraph=load(E/'paragraph-controls.json'),original=load(E/'original-controls.json'),historical=historical,clipboardProbe=load(E/'controls-shipping/clipboard-probe.json'))
(E/'consolidated-test-results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('Final inherited WPF:',report['inheritedWpf']['tests'],'checks;',report['inheritedWpf']['failures'],'failures')
for row in workers:print(row['suite'],row['tests'],row['failures'],row['success'])
