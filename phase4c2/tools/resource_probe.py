from pathlib import Path
import json,time,statistics
import psutil
import test_engine as b
w=b.Worker();proc=psutil.Process(w.p.pid);root=b.WORK/'resource';root.mkdir();source=b.RUN/'corpus/11-word-letter.pdf';snapshots=[];durations=[]
for i in range(32):
 path=root/f'input-{i}.pdf';path.write_bytes(source.read_bytes()+f'\n% resource probe {i}\n'.encode());start=time.perf_counter();v=w.call(Source=str(path));durations.append((time.perf_counter()-start)*1000);assert v['Ok'] and v['Data']['Region']['Positioned'];assert len(v['Data']['PageObjects'])==8
 if i in [0,7,15,31]:snapshots.append(dict(iteration=i+1,handles=proc.num_handles(),memory=proc.memory_info()._asdict()))
start_handles=snapshots[1]['handles'];end_handles=snapshots[-1]['handles'];assert end_handles-start_handles<=12
previews=[];d=v['Data'];r=d['Region']
for i in range(6):
 start=time.perf_counter();v=w.call(Command='preview',Source=d['Path'],ExpectedHash=d['Hash'],RegionId=r['Id'],Text='Phace 3 Office letter');previews.append((time.perf_counter()-start)*1000);assert v['Ok'] and v['Data']['Safe']
w.close();assert not psutil.pid_exists(proc.pid)
(b.EVID/'resource-probe.json').write_text(json.dumps(dict(inspections=32,distinctFingerprints=True,observedObjectsAlways=8,snapshots=snapshots,handlesGrowthAfterWarmup=end_handles-start_handles,processExited=True,inspectMedianMs=statistics.median(durations),previewMedianMs=statistics.median(previews),previewMs=previews,limitations='Small single-page test, no proof of leak freedom or hostile-document bounds; temp files retained as evidence'),indent=2));print('Resource probe: 32 fresh analyses, handles growth',end_handles-start_handles,'preview median',round(statistics.median(previews),2),'ms')
