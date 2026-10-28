from pathlib import Path
import json,time,hashlib
import test_engine as b
w=b.Worker();rows=[];saved=[];E=b.EVID
inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ['corpus','font-corpus','wrap-corpus','document-corpus'] for p in (b.RUN/folder).glob('*.pdf')}
def info(source,page=0):
 v=w.call(Source=str(source),Page=page);assert v['Ok'],v;return v['Data']
def change(r,t):return dict(Page=r['Page'],RegionId=r['Id'],Identity=r['SourceIdentity'],Text=t)
def save(d,ed,name,safe=True):
 dest=E/(name+'-'+str(time.time_ns())+'.pdf');v=w.call(Command='save',Source=d['Path'],ExpectedHash=d['Hash'],Changes=ed,Destination=str(dest));
 if safe:
  assert v['Ok'] and v['Data']['Safe'],v;assert dest.exists();record=dict(source=d['Path'],destination=str(dest),changes=ed,result=v['Data']);saved.append(record);return record
 assert not v['Ok'] or not v['Data']['Safe'],v;assert not dest.exists();return v
 def_unused=0
def check(name,f):
 try:rows.append(dict(name=name,status='pass',detail=f()));print(name,'pass',flush=True)
 except Exception as ex:rows.append(dict(name=name,status='fail',error=repr(ex)));print(name,'FAIL',str(ex)[:400],flush=True)
word=info(b.RUN/'corpus/11-word-letter.pdf');title=word['Regions'][0];third=word['Regions'][2];two=('Phase 3 letter '*9).strip();multi=('Phase 3 letter '*20).strip()
check('A-genuine-Word-title-two-lines',lambda:save(word,[change(title,two)],'word-two'))
check('B-genuine-Word-third-line-three-plus',lambda:save(word,[change(third,multi)],'word-multiline'))
check('long-word-character-fallback',lambda:save(word,[change(title,'e'*110)],'long-word'))
for font in ['Arial','Calibri']:
 d=info(b.RUN/'font-corpus'/('Word-'+font+'.pdf'));r=d['Regions'][0]
 check(font+'-two-line-wrap',lambda d=d,r=r,font=font:save(d,[change(r,('cafe calm. '*12).strip())],font+'-wrap'))
check('punctuation-at-wrap',lambda:save(word,[change(third,('letter. letter. '*12).strip())],'punctuation'))
check('descenders-safe-baseline-spacing',lambda:save(word,[change(third,('paragraph paragraph. '*10).strip())],'descenders'))
check('hard-break-retained-refused',lambda:save(word,[change(title,'Phase 3\nletter')],'hard-break',False))
check('adjacent-spaces-extraction-restriction',lambda:save(word,[change(title,('Phase 3  letter '*8).strip())],'multiple-spaces',False))
check('vertical-overflow-protected-Word-paragraph',lambda:save(word,[change(title,('Phase 3 letter '*16).strip())],'vertical',False))
for name in ['graphic-below','paragraph-below']:
 d=info(b.RUN/'wrap-corpus'/(name+'.pdf'));r=d['Regions'][0];check(name+'-source-eligible-wrap-refused',lambda d=d,r=r,name=name:(r['Eligibility']=='Editable' or (_ for _ in []).throw(AssertionError(r)),save(d,[change(r,two)],name,False)))
def collision():
 d=info(b.RUN/'wrap-corpus/combined-collision.pdf');a=next(r for r in d['Regions'] if r['OriginalText'].startswith('A separate'));r=next(r for r in d['Regions'] if r['OriginalText']=='..');assert a['Eligibility']==r['Eligibility']=='Editable',(a['Reasons'],r['Reasons']);ea=change(a,('gyp '*35).strip());eb=change(r,('fictional letter '*12).strip());sa=save(d,[ea],'collision-wrap-A');sb=save(d,[eb],'collision-wrap-B');assert len(sa['result']['Verification']['pages'][0]['regions'][0]['layout']['Lines'])>=2 and len(sb['result']['Verification']['pages'][0]['regions'][0]['layout']['Lines'])>=2;pa=sa['result']['Verification']['pages'][0]['regions'][0]['layout']['Positioned'];pb=sb['result']['Verification']['pages'][0]['regions'][0]['layout']['Positioned'];overlaps=[(x,y) for x in pa['InkBounds'] for y in pb['InkBounds'] if x['Width']>0 and y['Width']>0 and x['X']<y['Right'] and x['Right']>y['X'] and x['Y']<y['Bottom'] and x['Bottom']>y['Y']];assert overlaps,'Fixture has no actual proposed ink overlap';v=save(d,[ea,eb],'collision-combined',False);assert len(v['Data']['Regions'])==2;return dict(individuallyValid=True,actualProposedInkOverlap=overlaps,result=v)
check('two-independent-wrapped-edits-collide',collision)
def mixed():
 d=info(b.RUN/'document-corpus/mixed-multipage.pdf');p=info(Path(d['Path']),1);return save(d,[change(d['Regions'][0],two),change(d['Regions'][2],two),change(p['Regions'][0],'First changed working paragraph.')],'mixed-pages')
check('mixed-wrapped-unwrapped-two-pages',mixed)
def again():
 rec=next(r for r in saved if Path(r['destination']).name.startswith('word-two-'));d=info(Path(rec['destination']));p=rec['result']['Verification']['pages'][0]['regions'][0]['layout']['Lines'][0];r=next(r for r in d['Regions'] if r['OriginalText']==p);assert r['Eligibility']=='Editable',r;out=save(d,[change(r,p.replace('Phase','Phace',1))],'rediscovered-first-line');return dict(limitation='No unjustified paragraph grouping. Eligible first emitted line re-edited as its own region; remaining emitted lines stay protected.',regions=[dict(text=r['OriginalText'],eligibility=r['Eligibility'],reasons=r['Reasons']) for r in d['Regions']],output=out['destination'])
check('reopen-safe-line-rediscovery-second-generation',again)
def two_pages():
 d=info(b.RUN/'wrap-corpus/two-Word-pages.pdf');p=info(Path(d['Path']),1);return save(d,[change(d['Regions'][0],two),change(p['Regions'][0],('cafe calm. '*12).strip())],'two-wrapped-pages')
check('wrapped-edits-on-two-genuine-Word-pages',two_pages)
def protect():
 before=hashlib.sha256(Path(word['Path']).read_bytes()).hexdigest();v=w.call(Command='save',Source=word['Path'],ExpectedHash=word['Hash'],Changes=[change(title,two)],Destination=word['Path']);assert not v['Ok'];assert hashlib.sha256(Path(word['Path']).read_bytes()).hexdigest()==before;return v
check('wrapped-export-original-protected',protect)
check('unsupported-one-blocks-all',lambda:save(word,[change(title,two+'\u2603'),change(third,'A separate letter.')],'unsupported-all',False))
check('single-glyph-positioned-run',lambda:save(word,[change(title,'e')],'single-glyph'))
check('single-glyph-last-wrapped-line',lambda:save(word,[change(title,'e'*68)],'single-tail'))
check('single-line-C1-unchanged',lambda:save(word,[change(title,'Phasse 3 Office letter')],'single-line'))
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in inputs.items());w.close();(E/'wrap-tests.json').write_text(json.dumps(dict(tests=len(rows),failures=sum(r['status']=='fail' for r in rows),rows=rows,saved=saved,sourceHashes=inputs),indent=2),encoding='utf-8')

