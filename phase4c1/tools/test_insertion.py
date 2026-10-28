from pathlib import Path
import json,time,hashlib
import test_engine as b
E=b.EVID;w=b.Worker();rows=[];saved=[]
def inspect(path,page=0):
 v=w.call(Command='inspect',Source=str(path),Page=page);assert v['Ok'],v;return v['Data']
def change(r,t):return dict(Page=r['Page'],RegionId=r['Id'],Identity=r['SourceIdentity'],Text=t)
def save(d,edits,name,safe=True,dest=None):
 dest=dest or E/(name+'-'+str(time.time_ns())+'.pdf');t=time.perf_counter();v=w.call(Command='save',Source=d['Path'],ExpectedHash=d['Hash'],Page=0,Changes=edits,Destination=str(dest));elapsed=(time.perf_counter()-t)*1000
 if safe:
  assert v['Ok'] and v['Data']['Safe'],v
  saved.append(dict(source=d['Path'],destination=str(dest),changes=edits,result=v['Data']))
 else:assert not v['Ok'] or not v['Data']['Safe'],v;assert not dest.is_file()
 return dict(ms=elapsed,response=v,destination=str(dest))
def check(name,f):
 try:rows.append(dict(name=name,status='pass',detail=f()));print(name,'pass',flush=True)
 except Exception as e:rows.append(dict(name=name,status='fail',error=repr(e)));print(name,'FAIL',str(e)[:700],flush=True)
source=b.RUN/'corpus/11-word-letter.pdf';d=inspect(source);r=d['Regions'][0];old=r['OriginalText']
variants={'A-insert-middle':'Phasse 3 Office letter','B-insert-many':'Phase 3 Office letter letter','insert-start':'Phase '+old,'insert-within-word':'Phase 3 Offiice letter','insert-between-words':'Phase 3 letter Office letter','insert-near-end':'Phase 3 Office letterr','multiple-separate-insertions':'Phasse 33 Office letterr','C-delete-character':'Phase 3 Ofice letter','D-delete-word':'Phase 3 letter','E-replace-range-different-length':'Phase 3 letter letter','delete-start':old[1:],'delete-end':old[:-1],'delete-consecutive':'Phase 3 Oice letter','K-empty-line':''}
for name,text in variants.items():check(name,lambda name=name,text=text:save(d,[change(r,text)],name))
check('new-ff-join-refused',lambda:save(d,[change(r,'Phase 3 Offfice letter')],'ff-refused',False))
check('double-space-extraction-refused',lambda:save(d,[change(r,'Phase 3  Office letter')],'double-space',False))
check('F-horizontal-overflow',lambda:save(d,[change(r,old+' letter'*70)],'overflow',False))
def obstacle():
 dd=inspect(b.RUN/'document-corpus/word-horizontal-obstacle.pdf');rr=dd['Regions'][0];assert rr['Eligibility']=='Editable',rr
 return save(dd,[change(rr,rr['OriginalText']+' letter'*6)],'horizontal-obstacle',False)
check('F-protected-graphic-horizontal-expansion',obstacle)
check('G-unsupported-glyph',lambda:save(d,[change(r,old+'\u2603')],'unsupported',False))
check('newline-never-wraps',lambda:save(d,[change(r,old+'\nletter')],'newline',False))
for font in ['Arial','Calibri']:
 fd=inspect(b.RUN/'font-corpus'/('Word-'+font+'.pdf'));fr=fd['Regions'][0]
 for name,text in [('insert','cafe calm. cafe calm. cafe'),('delete','cafe. cafe calm.'),('replace','calm calm. cafe calm.')]:check(font+'-'+name,lambda fd=fd,fr=fr,font=font,name=name,text=text:save(fd,[change(fr,text)],font+'-'+name))
check('I-unchanged-title-pairs',lambda:save(d,[change(r,'Phase 3 Office letter letter')],'preserve-pairs'))
def second():
 first=next(x for x in saved if x['changes'][0]['Text']=='Phasse 3 Office letter');dd=inspect(Path(first['destination']));rr=next(x for x in dd['Regions'] if x['OriginalText']=='Phasse 3 Office letter');assert rr['Eligibility']=='Editable',rr
 return save(dd,[change(rr,'Phasse 3 Ofice letter')],'second-generation')
check('J-reopen-and-reedit',second)
def mixed():
 dd=inspect(b.RUN/'document-corpus/mixed-multipage.pdf');dd2=inspect(Path(dd['Path']),1);rs=dd['Regions'];nr=next(x for x in dd2['Regions'] if x['Eligibility']=='Editable');ed=[change(rs[0],'Phasse 3 Office letter'),change(rs[2],rs[2]['OriginalText'].replace('should ','',1)),change(nr,'First changed working paragraph.')];return save(dd,ed,'mixed-multipage')
check('H-mixed-multi-region-pages',mixed)
def failure():
 dest=E/('denied-'+str(time.time_ns()));dest.mkdir();ed=[change(r,'Phasse 3 Office letter'),change(d['Regions'][2],d['Regions'][2]['OriginalText'].replace('should ',''))];v=save(d,ed,'failure',False,dest);assert not list(E.glob('.pdf-prototype-*.tmp'));return v
check('M-final-commit-failure-no-partial',failure)
assert hashlib.sha256(source.read_bytes()).hexdigest()==d['Hash'];w.close();(E/'insertion-tests.json').write_text(json.dumps(dict(tests=len(rows),failures=sum(x['status']=='fail' for x in rows),rows=rows,saved=saved),indent=2),encoding='utf-8')
