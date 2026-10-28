from pathlib import Path
import json,time,statistics
import psutil
import test_engine as b
w=b.Worker();proc=psutil.Process(w.p.pid);cases=[]
def inspect(path,page=0):
 v=w.call(Source=str(path),Page=page);assert v['Ok'],v;return v['Data']
def change(r,text):return dict(Page=r['Page'],RegionId=r['Id'],Identity=r['SourceIdentity'],Text=text)
n=inspect(b.RUN/'document-corpus/multi-natural.pdf');rs=n['Regions'];other=inspect(n['Path'],1)
natural=[change(rs[0],'First changed working paragraph.'),change(rs[1],'Second changed working paragraph.'),change(rs[2],'Third changed working paragraph.')];across=natural+[change(other['Regions'][0],'Another page has changed text.')]
word=inspect(b.RUN/'corpus/11-word-letter.pdf');wr=word['Regions'];positioned=[change(wr[0],'Phace 3 Office letter'),change(wr[2],wr[2]['OriginalText'].replace('should','chould'))]
mixed=inspect(b.RUN/'document-corpus/mixed.pdf');mr=mixed['Regions'];mixed_changes=[change(mr[0],'Phace 3 Office letter'),change(mr[-1],'Neutral paragraph retains its original font.')]
for label,d,edits in [('two-natural',n,natural[:2]),('three-natural',n,natural),('four-two-pages',n,across),('two-Word',word,positioned),('mixed',mixed,mixed_changes)]:
 times=[]
 for i in range(5):
  t=time.perf_counter();v=w.call(Command='preview',Source=d['Path'],ExpectedHash=d['Hash'],Changes=edits);times.append((time.perf_counter()-t)*1000);assert v['Ok'] and v['Data']['Safe'],v
 cases.append(dict(name=label,changedRegions=len(edits),medianMs=statistics.median(times),times=times))
before=dict(handles=proc.num_handles(),memory=proc.memory_info()._asdict())
for i in range(24):
 v=w.call(Command='preview',Source=n['Path'],ExpectedHash=n['Hash'],Changes=across);assert v['Ok'] and v['Data']['Safe']
after=dict(handles=proc.num_handles(),memory=proc.memory_info()._asdict());assert after['handles']-before['handles']<=12
pdfs=list(b.WORK.glob('candidate-*.pdf'));pngs=list(b.WORK.glob('candidate-*.png'));assert len(pdfs)<=12 and len(pngs)<=12,(len(pdfs),len(pngs));w.close();assert not psutil.pid_exists(proc.pid)
(b.EVID/'document-performance.json').write_text(json.dumps(dict(cases=cases,repeatedPreviews=24,afterWarmup=before,after=after,handleGrowth=after['handles']-before['handles'],retainedCandidatePdfs=len(pdfs),retainedCandidatePngs=len(pngs),workerExited=True,limitations='Small local fictional corpus; IPC/analysis/save/reopen/render included. Not a large-document or physical-input latency guarantee.'),indent=2));print('Combined preview medians:',[(c['name'],round(c['medianMs'],2)) for c in cases]);print('Handle growth',after['handles']-before['handles'],'candidate files',len(pdfs),len(pngs))
