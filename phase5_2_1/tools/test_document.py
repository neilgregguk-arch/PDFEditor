from pathlib import Path
import json,time,hashlib,statistics
import test_engine as base
R=base.ROOT;E=R/'evidence';w=base.Worker();rows=[];saved=[];times=[]
inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['corpus','document-corpus','font-corpus'] for p in (base.RUN/folder).glob('*.pdf')}
def check(name,f):
 try:rows.append(dict(name=name,status='pass',detail=f()))
 except Exception as e:rows.append(dict(name=name,status='fail',error=repr(e)))
def inspect(name,page=0):
 p=Path(name) if str(name).endswith('.pdf') else base.RUN/'document-corpus'/(name+'.pdf');v=w.call(Command='inspect',Source=str(p),Page=page);assert v['Ok'],v;return v['Data']
def change(r,text):return dict(Page=r['Page'],RegionId=r['Id'],Identity=r['SourceIdentity'],Text=text)
def transact(d,edits,label,success=True,command='save',destination=None):
 dest=destination or E/(label+'-'+str(time.time_ns())+'.pdf');start=time.perf_counter();v=w.call(Command=command,Source=d['Path'],ExpectedHash=d['Hash'],Page=0,Changes=edits,Destination=str(dest));times.append(dict(label=label,ms=(time.perf_counter()-start)*1000))
 if success:
  assert v['Ok'] and v['Data']['Safe'],v
  if command=='save':assert dest.exists();saved.append(dict(source=d['Path'],destination=str(dest),changes=edits,result=v['Data']))
 else:assert not v['Ok'] or not v['Data']['Safe'],v;assert not dest.is_file()
 return dest,v
def naturals():
 d=inspect('multi-natural');a,b,c=d['Regions'];ed=[change(a,'First changed working paragraph.'),change(b,'Second changed working paragraph.')];dest,v=transact(d,ed,'two-natural');assert v['Data']['Verification']['changedRegions']==2;return str(dest)
check('C-two-natural-single-save',naturals)
def wrapping():
 d=inspect('multi-natural');rs=d['Regions'];ed=[change(rs[0],('First changed working paragraph. '*5).strip()),change(rs[1],('Second changed working paragraph. '*4).strip())];dest,v=transact(d,ed,'two-wrapped-paragraphs');assert all(len(r['layout']['Lines'])>1 for r in v['Data']['Verification']['pages'][0]['regions']);return str(dest)
check('C-two-expanding-natural-paragraphs',wrapping)
def word():
 d=inspect(base.RUN/'corpus/11-word-letter.pdf');rs=d['Regions'];return str(transact(d,[change(rs[0],'Phace 3 Office letter'),change(rs[2],rs[2]['OriginalText'].replace('should','chould'))],'two-word')[0])
check('D-two-positioned-word-regions',word)
def mixed():
 d=inspect('mixed');p=next(r for r in d['Regions'] if r.get('Positioned'));n=next(r for r in d['Regions'] if not r.get('Positioned') and r['Eligibility']=='Editable');return str(transact(d,[change(p,'Phace 3 Office letter'),change(n,'Neutral paragraph retains its original font.')],'mixed-strategies')[0])
check('E-mixed-strategies-single-page',mixed)
def pages():
 d=inspect('multi-natural');two=inspect(d['Path'],1);return str(transact(d,[change(d['Regions'][0],'First changed working paragraph.'),change(two['Regions'][0],'Another page has changed text.')],'two-pages')[0])
check('H-different-pages',pages)
def collision():
 d=inspect('collision');a,b=d['Regions'][:2];ea=change(a,'alpha area.\nalpha area.\nalpha area.');eb=change(b,'alpha area.')
 transact(d,[ea],'collision-A-alone');transact(d,[eb],'collision-B-alone');dest,v=transact(d,[ea,eb],'collision-combined',False);assert v['Ok'] and len(v['Data']['Regions'])==2,v;return v
check('F-individually-valid-combined-collision',collision)
def invalid():
 d=inspect('multi-natural');ed=[change(d['Regions'][0],'First changed \u2603.'),change(d['Regions'][1],'Second changed working paragraph.')];return transact(d,ed,'no-partial-export',False)[1]
check('G-invalid-one-never-saves-valid-other',invalid)
def second():
 d=inspect(saved[0]['destination']);rs=d['Regions'];assert all(r['Eligibility']=='Editable' for r in rs[:2]);return str(transact(d,[change(rs[0],'First changed working paragraph again.'),change(rs[1],'Second changed working paragraph again.')],'second-generation')[0])
check('K-second-generation-combined',second)
def failed_commit():
 d=inspect('multi-natural');dest=E/('directory-'+str(time.time_ns()));dest.mkdir();before=set(E.glob('.pdf-prototype-*.tmp'));v=transact(d,[change(d['Regions'][0],'First changed working paragraph.'),change(d['Regions'][1],'Second changed working paragraph.')],'rollback',False,destination=dest)[1];assert set(E.glob('.pdf-prototype-*.tmp'))==before;return v
check('J-failed-final-move-rolls-back-stage',failed_commit)
def duplicate():
 d=inspect('multi-natural');ed=change(d['Regions'][0],'First changed working paragraph.');return transact(d,[ed,ed],'duplicate',False)[1]
check('duplicate-ownership-refused',duplicate)
def identity():
 d=inspect('multi-natural');ed=change(d['Regions'][0],'First changed working paragraph.');ed['Identity']='wrong';return transact(d,[ed],'wrong-identity',False)[1]
check('source-region-identity-refused',identity)
def stale():
 d=inspect('multi-natural');d['Hash']='wrong';return transact(d,[change(d['Regions'][0],'First changed working paragraph.')],'stale',False)[1]
check('source-hash-refused',stale)
def destinations():
 d=inspect('multi-natural');ed=[change(d['Regions'][0],'First changed working paragraph.')];
 for existing in [Path(d['Path']),Path(saved[0]['destination'])]:
  digest=hashlib.sha256(existing.read_bytes()).hexdigest();v=w.call(Command='save',Source=d['Path'],ExpectedHash=d['Hash'],Changes=ed,Destination=str(existing));assert not v['Ok'];assert hashlib.sha256(existing.read_bytes()).hexdigest()==digest
 return v
check('original-and-existing-destinations-protected',destinations)
def deletion():
 d=inspect('multi-natural');return str(transact(d,[change(d['Regions'][0],''),change(d['Regions'][1],'Second changed working paragraph.')],'delete-and-replace')[0])
check('complete-deletion-plus-other-edit',deletion)
def noops():
 d=inspect('multi-natural');return transact(d,[],'no-changes',False)[1]
check('no-change-not-reported-saved',noops)
def positioned_expansion():
 d=inspect('mixed');p=d['Regions'][0];n=d['Regions'][-1];return transact(d,[change(p,p['OriginalText']+' letter'*100),change(n,'Neutral paragraph retains its original font.')],'no-position-expansion',False)[1]
check('mixed-does-not-relax-position-boundary',positioned_expansion)
def worker_restart():
 w.close();globals()['w']=base.Worker();d=inspect('multi-natural');return str(transact(d,[change(d['Regions'][0],'First changed working paragraph.'),change(d['Regions'][1],'Second changed working paragraph.')],'after-worker-restart')[0])
check('worker-restart-source-based-identities',worker_restart)
w.close();assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in inputs.items())
(E/'document-tests.json').write_text(json.dumps(dict(tests=len(rows),failures=sum(r['status']=='fail' for r in rows),results=rows,saved=saved,times=times,sourceHashesPreserved=True),indent=2))
for r in rows:print(r['name'],r['status'],r.get('error','')[:350])
