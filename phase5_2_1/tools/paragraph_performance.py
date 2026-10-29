"""Rediscovery, validation, generations and 32-group local resource measurements."""
from pathlib import Path
import json,time,statistics,hashlib,psutil
import pikepdf
import test_engine as b
E=b.EVID;D=E/'performance';D.mkdir(exist_ok=True);records=[]
def changes(d,text):return [dict(Page=0,RegionId=r['Id'],Identity=r['SourceIdentity'],Text=text) for r in d['Regions'] if r['Eligibility']=='Editable']
def info(w,path):
 start=time.perf_counter();v=w.call(Source=str(path));elapsed=(time.perf_counter()-start)*1000;assert v['Ok'],v;return v['Data'],elapsed
def save(w,d,ed,name):
 dest=D/(name+'-'+str(time.time_ns())+'.pdf');start=time.perf_counter();v=w.call(Command='save',Source=d['Path'],ExpectedHash=d['Hash'],Changes=ed,Destination=str(dest));ms=(time.perf_counter()-start)*1000;assert v['Ok'] and v['Data']['Safe'],v;r=dict(source=d['Path'],destination=str(dest),changes=ed,result=v['Data']);records.append(r);return dest,ms,v['Data']['Verification']['timingsMs']
source=b.RUN/'corpus/11-word-letter.pdf';fixture=D/('32-positioned-lines-'+str(time.time_ns())+'.pdf')
with pikepdf.open(source) as original,pikepdf.Pdf.new() as pdf:
 page=pdf.add_blank_page(page_size=(595.32,3400));page.Resources=pdf.copy_foreign(original.make_indirect(original.pages[0].Resources));first=next(op for op in pikepdf.parse_content_stream(original.pages[0]) if str(op.operator)=='TJ');text=pikepdf.unparse_content_stream([first]);parts=[]
 for i in range(32):parts.append(('q BT /F1 12 Tf 0 g 1 0 0 1 72.024 '+str(3400-83.3-i*100)+' Tm\n').encode()+text+b'\nET Q\n')
 page.Contents=pdf.make_stream(b''.join(parts));pdf.save(fixture)
w=b.Worker();d,first_ms=info(w,fixture);assert len(d['Regions'])==32 and all(r['Eligibility']=='Editable' and r.get('Positioned') for r in d['Regions']);baseline_hash=hashlib.sha256(fixture.read_bytes()).hexdigest()
dest,save_ms,stages=save(w,d,changes(d,('Phase 3 letter '*9).strip()),'32-groups-generation1');w.close()
w=b.Worker();d,rediscovery_ms=info(w,dest);assert sum(bool(r.get('Paragraph')) and r['Eligibility']=='Editable' for r in d['Regions'])==32
group_validation_ms=d['LastUncachedParagraphValidationMs'];process=psutil.Process(w.p.pid);before=dict(handles=process.num_handles(),rss=process.memory_info().rss);warm=[]
for i in range(20):_,ms=info(w,dest);warm.append(ms)
after=dict(handles=process.num_handles(),rss=process.memory_info().rss);second,second_ms,second_stages=save(w,d,changes(d,'A separate letter.'),'32-groups-generation2');w.close();assert not process.is_running()
# Same input PDF, two engine versions; cold analysis versus cached requests.
small=Path(json.loads((E/'roundtrip-tests.json').read_text())['saved'][0]['destination']);comparison=[];run=b.RUN
for phase in ['phase4c2','phase5_2_1']:
 b.RUN=b.ROOT.parent/phase/'run';worker=b.Worker();observed,cold=info(worker,small);values=[info(worker,small)[1] for _ in range(8)];comparison.append(dict(engine=phase,coldMs=cold,warmMedianMs=statistics.median(values),regions=len(observed['Regions']),groups=sum(bool(r.get('Paragraph')) for r in observed['Regions']),lastUncachedParagraphValidationMs=observed.get('LastUncachedParagraphValidationMs')));worker.close()
b.RUN=run
assert hashlib.sha256(fixture.read_bytes()).hexdigest()==baseline_hash
(E/'paragraph-performance-records.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
result=dict(success=True,fixture=dict(source=str(fixture),sourceSha256=baseline_hash,provenance='Development-only 32-line page using existing fictional Word title TJ and original F1 font resource; new untagged page, not claimed to be an untouched Word export',groups=32,pageSize=[595.32,3400]),initialUnmarkedInspectionMs=first_ms,firstSaveMs=save_ms,firstSaveStages=stages,markedColdRediscoveryMs=rediscovery_ms,groupValidationMs=group_validation_ms,warmRediscoveryMedianMs=statistics.median(warm),secondSaveMs=second_ms,secondSaveStages=second_stages,repeatedInspections=20,before=before,after=after,handleGrowth=after['handles']-before['handles'],rssGrowth=after['rss']-before['rss'],workerExited=True,sameFileEngineComparison=comparison,scope='Small local synthetic/genuine-derived fixtures; warm time includes page render. LastUncachedParagraphValidationMs excludes earlier font analysis; bounded document mark index may be cached.')
(E/'paragraph-performance.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print('32 groups: cold',round(rediscovery_ms,2),'ms; validation',round(group_validation_ms,2),'ms; generations',round(save_ms,2),round(second_ms,2),'ms; handle growth',result['handleGrowth'])
