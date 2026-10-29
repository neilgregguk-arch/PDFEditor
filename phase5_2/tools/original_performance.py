"""Bounded original-discovery resource sample, not a leak diagnosis."""
from pathlib import Path
import time,json,statistics,psutil
import test_engine as b
E=b.EVID;rows=[];source=b.RUN/'original-paragraphs/Word-cafe-paragraph.pdf'
def timed(w,p,page=0):
 t=time.perf_counter();v=w.call(Source=str(p),Page=page);assert v['Ok'],v;return v['Data'],(time.perf_counter()-t)*1000
w=b.Worker();d,cold=timed(w,source);g=next(r for r in d['Regions'] if r.get('Paragraph'));assert g['Eligibility']=='Editable';proc=psutil.Process(w.p.pid);before=dict(rss=proc.memory_info().rss,handles=proc.num_handles());repeat=[]
for _ in range(20):_,ms=timed(w,source);repeat.append(ms)
after=dict(rss=proc.memory_info().rss,handles=proc.num_handles());changes=[dict(Page=0,RegionId=g['Id'],Identity=g['SourceIdentity'],Text='calm cafe. '+g['OriginalText'])];dest=E/('original-performance-'+str(time.time_ns())+'.pdf');t=time.perf_counter();v=w.call(Command='save',Source=str(source),ExpectedHash=d['Hash'],Changes=changes,Destination=str(dest));elapsed=(time.perf_counter()-t)*1000;assert v['Ok'] and v['Data']['Safe'],v;w.close();assert not proc.is_running();record=dict(source=str(source),destination=str(dest),changes=changes,result=v['Data']);(E/('export-record-original-performance-'+str(time.time_ns())+'.json')).write_text(json.dumps(record,indent=2),encoding='utf-8')
comparison=[];run=b.RUN
for phase in ['phase5_1','phase5_2']:
 b.RUN=b.ROOT.parent/phase/'run';worker=b.Worker();observed,ms=timed(worker,source);comparison.append(dict(phase=phase,coldWithRenderMs=ms,editableGroups=sum(bool(r.get('Paragraph')) and r['Eligibility']=='Editable' for r in observed['Regions']),groupingMs=observed.get('LastUncachedParagraphValidationMs')));worker.close()
b.RUN=run
result=dict(success=True,source=str(source),coldIncludingRenderMs=cold,groupingMs=d['LastUncachedParagraphValidationMs'],repeatCount=20,warmMedianIncludingRenderMs=statistics.median(repeat),before=before,after=after,rssDeltaBytes=after['rss']-before['rss'],handleDelta=after['handles']-before['handles'],workerExited=True,candidateTotalMs=elapsed,candidateStages=v['Data']['Verification']['timingsMs'],sameAuthenticSourceComparison=comparison,scope='One original two-row paragraph; 20 cached same-document inspections. RSS change is this sample only and does not establish a leak. Grouping includes raw indexed structural proof, excludes preceding font analysis. No pages reanalysed by text-only local planner.')
(E/'original-performance.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
