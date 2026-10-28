from pathlib import Path
import json,time,statistics
import psutil
import test_engine as b
w=b.Worker();proc=psutil.Process(w.p.pid)
def info(path,page=0):
 v=w.call(Source=str(path),Page=page);assert v['Ok'],v;return v['Data']
def c(r,t):return dict(Page=r['Page'],RegionId=r['Id'],Identity=r['SourceIdentity'],Text=t)
d=info(b.RUN/'corpus/11-word-letter.pdf');rs=d['Regions'];two=('Phase 3 letter '*9).strip();many=('Phase 3 letter '*20).strip();mx=info(b.RUN/'document-corpus/mixed-multipage.pdf');mp=info(Path(mx['Path']),1);cases=[]
for label,doc,edits in [('two-lines',d,[c(rs[0],two)]),('three-plus-lines',d,[c(rs[2],many)]),('long-word',d,[c(rs[0],'e'*110)]),('combined-pages',mx,[c(mx['Regions'][0],two),c(mx['Regions'][2],two),c(mp['Regions'][0],'First changed working paragraph.')])]:
 times=[];stages=[]
 for i in range(5):
  t=time.perf_counter();v=w.call(Command='preview',Source=doc['Path'],ExpectedHash=doc['Hash'],Changes=edits);times.append((time.perf_counter()-t)*1000);assert v['Ok'] and v['Data']['Safe'],v;stages.append(v['Data']['Verification']['timingsMs'])
 cases.append(dict(name=label,medianMs=statistics.median(times),timesMs=times,stages=stages))
before=dict(handles=proc.num_handles(),memory=proc.memory_info()._asdict());t=time.perf_counter()
for i in range(30):
 v=w.call(Command='preview',Source=d['Path'],ExpectedHash=d['Hash'],Changes=[c(rs[0],two if i%2==0 else 'Phasse 3 Office letter')]);assert v['Ok'] and v['Data']['Safe'],v
after=dict(handles=proc.num_handles(),memory=proc.memory_info()._asdict());pdfs=list(b.WORK.glob('candidate-*.pdf'));pngs=list(b.WORK.glob('candidate-*.png'));assert len(pdfs)<=12 and len(pngs)<=12;assert after['handles']-before['handles']<=12;w.close();assert not psutil.pid_exists(proc.pid)
recover=json.loads((b.EVID/'process-recovery.json').read_text(encoding='utf-8'));sizes=[p.stat().st_size for p in (Path(recover['folder'])/'store').glob('*.json')]
(b.EVID/'wrap-performance.json').write_text(json.dumps(dict(cases=cases,repeatedWrapUnwrap=30,before=before,after=after,handleGrowth=after['handles']-before['handles'],retainedPdfs=len(pdfs),retainedPngs=len(pngs),workerExited=True,recoveryFileBytes=sizes,scope='Small local genuine Word/development fixtures; IPC+candidate generation+reopen verification included, not physical input or large-document certification.'),indent=2),encoding='utf-8');print([(c['name'],round(c['medianMs'],2)) for c in cases]);print('handle growth',after['handles']-before['handles'],'recovery bytes',sizes)
