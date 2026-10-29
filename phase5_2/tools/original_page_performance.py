from pathlib import Path
import json,time,statistics,psutil
import test_engine as b
source=json.loads((b.EVID/'original-mixed-expectation.json').read_text(encoding='utf-8'))['source'];w=b.Worker();rows=[]
for page in range(4):
 start=time.perf_counter();v=w.call(Source=source,Page=page);assert v['Ok'],v;d=v['Data'];rows.append(dict(page=page,inspectIncludingRenderMs=(time.perf_counter()-start)*1000,lastUncachedGroupingMs=d['LastUncachedParagraphValidationMs'],regions=len(d['Regions']),groups=sum(bool(r.get('Paragraph')) for r in d['Regions'])))
proc=psutil.Process(w.p.pid);before=dict(rss=proc.memory_info().rss,handles=proc.num_handles());times=[]
for _ in range(20):
 start=time.perf_counter();v=w.call(Source=source,Page=0);assert v['Ok'];times.append((time.perf_counter()-start)*1000)
after=dict(rss=proc.memory_info().rss,handles=proc.num_handles());w.close();assert not proc.is_running();result=dict(source=source,pages=rows,repeatedPage0Inspections=20,warmMedianMs=statistics.median(times),before=before,after=after,rssDeltaBytes=after['rss']-before['rss'],handleDelta=after['handles']-before['handles'],workerExited=True,scope='Four-page mixed document. Cache observations are source-hash/page bound. No source/native pointers cached; RSS sample is not a leak diagnosis.')
(b.EVID/'original-page-performance.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print('Four-page timings',[(r['page'],round(r['inspectIncludingRenderMs'],2)) for r in rows],'handle delta',result['handleDelta'])
