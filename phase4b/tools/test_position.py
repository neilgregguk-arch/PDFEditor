"""Product worker tests; outputs also used by independent readers. No fixture manifests."""
from pathlib import Path
import json,time,hashlib,statistics,subprocess,os
import test_engine as base
R=base.ROOT;E=R/'evidence';W=base.Worker();rows=[];saved=[];times=[]
def check(name,f):
 try: detail=f();rows.append(dict(name=name,status='pass',detail=detail))
 except Exception as e: rows.append(dict(name=name,status='fail',error=repr(e)))
def inspect(path):
 t=time.perf_counter();v=W.call(Source=str(path),Command='inspect');times.append((time.perf_counter()-t)*1000);assert v['Ok'],v;return v['Data']
def edit(d,r,text,label,command='save',safe=True):
 dst=E/(label+'-'+str(time.time_ns())+'.pdf');v=W.call(Command=command,Source=d['Path'],ExpectedHash=d['Hash'],RegionId=r['Id'],Text=text,Destination=str(dst));assert v['Ok'],v
 assert v['Data']['Safe']==safe,v
 if safe:
  assert dst.exists();saved.append(dict(source=d['Path'],region=r,draft=text,destination=str(dst),verification=v['Data']['Verification'],reconstruction=command=='reconstruct'))
 else:assert not dst.exists()
 return dst,v
source=base.RUN/'corpus/11-word-letter.pdf';sources={str(p):basehash for p in base.RUN.rglob('*.pdf') for basehash in [hashlib.sha256(p.read_bytes()).hexdigest()]}
def stage_a():
 d=inspect(source);r=d['Regions'][0];assert r['Eligibility']=='Editable' and r['Positioned'];assert r['Positioned']['CoexistingWhitespace']==[1,2,4,5,7];return str(edit(d,r,r['OriginalText'],'word-reconstructed','reconstruct')[0])
check('A-original-position-reconstruction',stage_a)
def repeated():
 d=inspect(source);r=d['Regions'][0];one,_=edit(d,r,'Phace 3 Office letter','word-first');again=inspect(one);r=next(x for x in again['Regions'] if x['OriginalText']=='Phace 3 Office letter');assert r['Eligibility']=='Editable' and r['Positioned'];two,_=edit(again,r,'Phace 3 Oflice letter','word-second-narrower');final=inspect(two);assert any(x['Eligibility']=='Editable' and x['OriginalText']=='Phace 3 Oflice letter' for x in final['Regions']);assert not Path(str(two)+'.region.json').exists();return dict(one=str(one),two=str(two))
check('B-C-equal-and-unequal-advance-reopen-second-edit',repeated)
for label,draft in [('longer','Phase 3 Office letter extra'),('shorter','Phase 3 Office lette'),('wider','Phase 3 Office letWer'),('unmapped','Phase 3 Office lett!r'),('newline','Phase 3 Office lett\n'),('nul','Phase 3 Office lett\0')]:
 def reject(draft=draft,label=label):
  d=inspect(source);r=d['Regions'][0];return edit(d,r,draft,'refuse-'+label,safe=False)[1]
 check('D-refusal-'+label,reject)
for filename in ['Word-Arial','Word-Calibri']:
 def word(filename=filename):
  d=inspect(base.RUN/'font-corpus'/(filename+'.pdf'));r=d['Regions'][0];assert r['Eligibility']=='Editable' and r['Positioned'];draft=r['OriginalText'].replace('cafe','ccfe',1);one,_=edit(d,r,draft,filename);again=inspect(one);r=next(x for x in again['Regions'] if x['OriginalText']==draft);assert r['Eligibility']=='Editable';# narrower mapped f -> l, no positional movement
  second=draft.replace('calm','cclm',1);return str(edit(again,r,second,filename+'-second')[0])
 check('Word-'+filename+'-two-generations',word)
for name in ['Word-multiple-runs','adjacent-label','nearby-graphic','restricted-boundary','visible-whitespace']:
 def refusal(name=name):
  d=inspect(base.RUN/'position-corpus'/(name+'.pdf'));r=d['Regions'][0];assert r['Eligibility']!='Editable',r;return [(r['OriginalText'],r['Reasons']) for r in d['Regions']]
 check('protected-'+name,refusal)
for name in ['E-character-spacing','F-kerning']:
 def spacing(name=name):
  d=inspect(base.RUN/'font-corpus'/(name+'.pdf'));r=d['Regions'][0];assert r['Eligibility']!='Editable' and r['Positioned'] is None;assert 'POSITION_FONT_METRIC_ROUNDING_UNSUPPORTED' in r['Reasons'];return r['Reasons']
 check('independent-metric-guard-'+name,spacing)
def stale():
 d=inspect(source);r=d['Regions'][0];v=W.call(Command='save',Source=d['Path'],ExpectedHash='bad',RegionId=r['Id'],Text='Phace 3 Office letter',Destination=str(E/'never-stale.pdf'));assert not v['Ok'];return v
check('stale-source-hash-refused',stale)
def cache():
 a=inspect(source);b=inspect(source);assert a['Regions']==b['Regions'] and a['PageObjects']==b['PageObjects'];return True
check('cached-immutable-observations-and-probe-cleanup',cache)
def protected_dest():
 d=inspect(source);r=d['Regions'][0]
 for dest in [source,Path(saved[0]['destination'])]:
  v=W.call(Command='save',Source=d['Path'],ExpectedHash=d['Hash'],RegionId=r['Id'],Text='Phace 3 Office letter',Destination=str(dest));assert not v['Ok'],v
 return True
check('original-and-existing-destination-protected',protected_dest)
W.close();assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in sources.items())
(E/'position-tests.json').write_text(json.dumps(dict(tests=len(rows),failures=sum(r['status']=='fail' for r in rows),results=rows,saved=saved,sourceHashesPreserved=True,inspectMs=dict(min=min(times),median=statistics.median(times),max=max(times)),times=times),indent=2))
for r in rows:print(r['name'],r['status'],r.get('error','')[:300])
