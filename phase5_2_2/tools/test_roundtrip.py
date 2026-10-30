"""Fresh-worker generations and adversarial embedded declarations; fictional fixtures only."""
from pathlib import Path
import json,time,hashlib,copy
import pikepdf
import test_engine as b
E=b.EVID;D=E/'roundtrip';D.mkdir(exist_ok=True);A=E/'adversarial';A.mkdir(exist_ok=True)
rows=[];saved=[];fresh=[]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inspect(path,page=0):
 w=b.Worker()
 try:
  v=w.call(Source=str(path),Page=page);assert v['Ok'],v;fresh.append(w.p.pid);return v['Data']
 finally:w.close()
def change(r,text):return dict(Page=r['Page'],RegionId=r['Id'],Identity=r['SourceIdentity'],Text=text)
def save(d,ed,name,safe=True,dest=None):
 dest=Path(dest or D/(name+'-'+str(time.time_ns())+'.pdf'));before=digest(d['Path']);w=b.Worker()
 try:v=w.call(Command='save',Source=d['Path'],ExpectedHash=d['Hash'],Changes=ed,Destination=str(dest))
 finally:w.close()
 assert digest(d['Path'])==before,'Source bytes changed'
 if safe:
  assert v['Ok'] and v['Data']['Safe'],v;assert dest.is_file();r=dict(source=d['Path'],destination=str(dest),changes=ed,result=v['Data']);saved.append(r);return r
 assert not v['Ok'] or not v['Data']['Safe'],v;assert not dest.is_file();return v
def check(name,f):
 try:rows.append(dict(name=name,status='pass',detail=f()));print(name,'pass',flush=True)
 except Exception as e:rows.append(dict(name=name,status='fail',error=repr(e)));print(name,'FAIL',str(e)[:600],flush=True)
def group(d,text=None):return next(r for r in d['Regions'] if r.get('Paragraph') and (text is None or r['OriginalText']==text))
word=b.RUN/'corpus/11-word-letter.pdf';two=('Phase 3 letter '*9).strip();three=('Phase 3 letter '*15).strip();chains={}
def chain():
 source=word;identity=None;chain=[]
 for gen,text,count in [(1,two,2),(2,three,3),(3,'A separate letter.',1)]:
  d=inspect(source);r=d['Regions'][2] if gen==1 else group(d)
  if identity:assert r['Paragraph']['Id']==identity
  if gen>1:assert r['Eligibility']=='Editable' and r['OriginalText']==chain[-1]['changes'][0]['Text'] and r['SourceHash']==digest(source)
  out=save(d,[change(r,text)],'word-generation'+str(gen));reopened=inspect(out['destination']);g=group(reopened,text);assert g['Eligibility']=='Editable' and len(g['OriginalLines'])==count and len(g['Objects'])==count and ''.join(g['OriginalLines'])==text
  identity=g['Paragraph']['Id'];chain.append(out);source=Path(out['destination'])
 chains['word']=chain;return dict(generations=[r['destination'] for r in chain],rows=[2,3,1],stableId=identity,separateWorkers=True,noRecoveryUsed=True)
check('genuine-Word-fresh-worker-two-three-one-generations',chain)
for font in ['Arial','Calibri']:
 def test_font(font=font):
  source=b.RUN/'font-corpus'/('Word-'+font+'.pdf');outcomes=[];gid=None
  for gen,text in enumerate([('cafe calm. '*12).strip(),'calm cafe.',('calm cafe. '*12).strip()],1):
   d=inspect(source);r=d['Regions'][0] if gen==1 else group(d);out=save(d,[change(r,text)],font+'-generation'+str(gen));q=group(inspect(out['destination']),text);assert q['Eligibility']=='Editable' and q['FontHash']==r['FontHash'];assert gid is None or q['Paragraph']['Id']==gid;gid=q['Paragraph']['Id'];source=Path(out['destination']);outcomes.append(out['destination'])
  return outcomes
 check(font+'-three-editing-generations',test_font)
def mixed():
 d=inspect(b.RUN/'document-corpus/mixed-multipage.pdf');p=inspect(d['Path'],1);r=d['Regions'];first=save(d,[change(r[0],'Phasse 3 Office letter'),change(r[2],two),change(p['Regions'][0],'First changed working paragraph.')],'mixed-generation1')
 d=inspect(first['destination']);p=inspect(d['Path'],1);g=group(d,two);title=group(d,'Phasse 3 Office letter');out=save(d,[change(g,three),change(title,'Phace 3 Office letter'),change(p['Regions'][0],'First working paragraph.')],'mixed-generation2');assert out['result']['Verification']['changedRegions']==3;chains['mixed']=first;return out['destination']
check('reopened-group-other-Word-natural-two-pages-combined',mixed)
def empty():
 d=inspect(chains['word'][-1]['destination']);r=group(d);out=save(d,[change(r,'')],'delete-entire-paragraph');q=inspect(out['destination']);assert not any(x.get('Paragraph',{}).get('Id')==r['Paragraph']['Id'] for x in q['Regions'] if x.get('Paragraph'));assert out['result']['Verification']['pages'][0]['regions'][0]['replacementObjects']==0;return out['destination']
check('empty-edit-removes-members-without-invisible-tombstone',empty)
def collision():
 d=inspect(b.RUN/'wrap-corpus/combined-collision.pdf');a=next(r for r in d['Regions'] if r['OriginalText'].startswith('A separate'));breg=next(r for r in d['Regions'] if r['OriginalText']=='..');base=save(d,[change(a,'A separate letter.'),change(breg,'.')],'two-groups-baseline');d=inspect(base['destination']);a=group(d,'A separate letter.');breg=group(d,'.');ea=change(a,('gyp '*35).strip());eb=change(breg,('fictional letter '*12).strip());save(d,[ea],'group-A-alone');save(d,[eb],'group-B-alone');v=save(d,[ea,eb],'two-groups-collision',False);assert len(v['Data']['Regions'])==2;return v
check('two-reopened-groups-individually-safe-combined-refused',collision)
def negatives():
 d=inspect(chains['word'][0]['destination']);r=group(d);a=save(d,[change(r,r['OriginalText']+'\u2603')],'unmapped-later-generation',False);bval=save(d,[change(r,'Phase 3\nletter')],'hard-break-later-generation',False);return [a,bval]
check('unsupported-glyph-and-hard-break-later-generation-retained-refused',negatives)
def height():
 d=inspect(word);r=d['Regions'][0];out=save(d,[change(r,two)],'title-group');d=inspect(out['destination']);return save(d,[change(group(d),('Phase 3 letter '*16).strip())],'group-vertical-overflow',False)
check('reopened-group-excessive-vertical-growth-refused',height)
def denied():
 d=inspect(chains['word'][0]['destination']);r=group(d);dest=D/'destination-directory';dest.mkdir(exist_ok=True);v=save(d,[change(r,three)],'failed-save',False,dest);assert not list(D.glob('.pdf-prototype-*.tmp'));return v
check('failed-Save-As-no-partial-output',denied)
def changed():
 source=A/'changed-active-source.pdf';source.write_bytes(Path(chains['word'][0]['destination']).read_bytes());d=inspect(source);r=group(d);source.write_bytes(source.read_bytes()+b'\n% external source change\n');return save(d,[change(r,three)],'source-changed',False)
check('source-changes-after-inspection-refused',changed)

base=Path(chains['word'][0]['destination']) if 'word' in chains else None
def is_own(op):return str(op.operator)=='BDC' and str(op.operands[0])=='/PDFEditorV2_Paragraph'
def own_json(op):return json.loads(bytes(op.operands[1]['/Data']).decode())
def set_json(op,data):op.operands[1]['/Data']=pikepdf.String(json.dumps(data,separators=(',',':')).encode())
def mutate(name,callback):
 path=A/(name+'.pdf')
 with pikepdf.open(base) as pdf:
  page=pdf.pages[0];ops=list(pikepdf.parse_content_stream(page));callback(ops,pdf,page);page.Contents=pdf.make_stream(pikepdf.unparse_content_stream(ops));pdf.save(path)
 return path
def rejected(name,callback):
 p=mutate(name,callback);d=inspect(p);assert not any(r.get('Paragraph') and r['Eligibility']=='Editable' for r in d['Regions']),(name,d['Regions']);assert d['Region'] is None or d['Region'].get('Paragraph') is None;return dict(source=str(p),classified=[dict(id=r['Id'],eligibility=r['Eligibility'],reasons=r['Reasons']) for r in d['Regions']])
def data_change(fn,all_rows=True):
 def callback(ops,pdf,page):
  for op in ops:
   if is_own(op):
    data=own_json(op);fn(data);set_json(op,data)
    if not all_rows:break
 return callback
adversaries={
 'identifier-path-string':data_change(lambda m:m.update(Id='../not-a-group')),
 'identifier-noncanonical-case':data_change(lambda m:m.update(Id=m['Id'].upper())),
 'wrong-page':data_change(lambda m:m.update(Page=1)),
 'unknown-version':data_change(lambda m:m.update(Version=999)),
 'unknown-property':data_change(lambda m:m.update(Execute='file:///not-followed')),
 'null-member-array':data_change(lambda m:m.update(Rows=None)),
 'too-many-members':data_change(lambda m:m.update(Rows=m['Rows']*5)),
 'wrong-logical-text':data_change(lambda m:m.update(Text=m['Text']+'x')),
 'envelope-outside-page':data_change(lambda m:m['Envelope'].update(Width=100000)),
 'font-hash-changed':data_change(lambda m:m.update(FontHash='0'*64)),
 'mapping-hash-changed':data_change(lambda m:m.update(MappingHash='0'*64)),
 'conflicting-member-payload':data_change(lambda m:m.update(Text=m['Text'].replace('Phase','Phace',1)),False),
 'conflicting-identifiers':data_change(lambda m:m.update(Id='1'*32),False),
}
def payload(ops,pdf,page):
 op=next(x for x in ops if is_own(x));op.operands[1]['/Data']=pikepdf.String(b'x'*30000)
adversaries['oversize-payload']=payload
def broken(ops,pdf,page):next(x for x in ops if is_own(x)).operands[1]['/Data']=pikepdf.String(b'{broken')
adversaries['broken-json']=broken
def duplicate_key(ops,pdf,page):
 op=next(x for x in ops if is_own(x));raw=bytes(op.operands[1]['/Data']);op.operands[1]['/Data']=pikepdf.String(b'{"Version":1,'+raw[1:])
adversaries['duplicate-json-key']=duplicate_key
def fractional(ops,pdf,page):next(x for x in ops if is_own(x)).operands[1]['/Row']=1.5
adversaries['fractional-member-index']=fractional
def missing(ops,pdf,page):
 start=next(i for i,x in enumerate(ops) if is_own(x));end=next(i for i in range(start+1,len(ops)) if str(ops[i].operator)=='EMC');del ops[start:end+1]
adversaries['missing-member']=missing
def duplicate(ops,pdf,page):
 start=next(i for i,x in enumerate(ops) if is_own(x));end=next(i for i in range(start+1,len(ops)) if str(ops[i].operator)=='EMC');ops[end+1:end+1]=ops[start:end+1]
adversaries['duplicate-member']=duplicate

def reordered(ops,pdf,page):
 indices=[i for i,op in enumerate(ops) if is_own(op)];blocks=[]
 for mark in indices[:2]:
  start=mark;end=next(i for i in range(mark+1,len(ops)) if str(ops[i].operator)=='EMC');blocks.append((start,end))
 (a,b),(c,d)=blocks;assert a<=b<c<=d
 ops[:]=ops[:a]+ops[c:d+1]+ops[b+1:c]+ops[a:b+1]+ops[d+1:]
adversaries['externally-reordered-member-sequence']=reordered

def text_modified(ops,pdf,page):
 start=next(i for i,x in enumerate(ops) if is_own(x))
 for op in ops[start+1:]:
  if str(op.operator)=='Tj':op.operands[0]=pikepdf.String(bytes(op.operands[0])[2:]);return
  if str(op.operator)=='TJ':
   for i,x in enumerate(op.operands[0]):
    if isinstance(x,pikepdf.String) and len(bytes(x))>=2:op.operands[0][i]=pikepdf.String(bytes(x)[2:]);return
 raise AssertionError('No text operator')
adversaries['external-member-text-change']=text_modified
def moved(ops,pdf,page):
 start=next(i for i,x in enumerate(ops) if is_own(x));index=next(i for i in range(start+1,len(ops)) if str(ops[i].operator)=='Tm');op=ops[index];args=list(op.operands);args[4]=float(args[4])+4;ops[index]=pikepdf.ContentStreamInstruction(args,op.operator)
adversaries['external-member-position-change']=moved
def protected_space(ops,pdf,page):
 # Separate F2 space object in the row gap, never declared as a group member.
 ops.extend(pikepdf.parse_content_stream(pdf.make_stream(b'BT /F2 12 Tf 1 0 0 1 80 650 Tm ( ) Tj ET')))
adversaries['protected-whitespace-between-rows']=protected_space
for name,callback in adversaries.items():check(name,lambda name=name,callback=callback:rejected(name,callback))
def external_roundtrip():
 p=mutate('external-pikepdf-preserve',lambda ops,pdf,page:None);d=inspect(p);r=group(d);assert r['Eligibility']=='Editable' and r['OriginalText']==two;return save(d,[change(r,three)],'external-preserved-generation')['destination']
check('external-tool-save-retaining-valid-declaration-supported',external_roundtrip)

def cross_page_conflict():
 def callback(ops,pdf,page):
  pdf.pages.append(page);second=pdf.pages[1];other=list(pikepdf.parse_content_stream(second))
  for op in other:
   if is_own(op):
    value=own_json(op);value['Page']=1;set_json(op,value)
  second.Contents=pdf.make_stream(pikepdf.unparse_content_stream(other))
 p=mutate('duplicate-identifier-across-pages',callback);results=[inspect(p,page) for page in [0,1]]
 assert all(not any(r.get('Paragraph') and r['Eligibility']=='Editable' for r in d['Regions']) for d in results)
 return dict(source=str(p),pages=2)
check('duplicate-identifier-across-pages-refused',cross_page_conflict)
def semantic_change(ops,pdf,page):
 own=next(i for i,x in enumerate(ops) if is_own(x));prior=next(x for x in reversed(ops[:own]) if str(x.operator)=='BDC' and str(x.operands[0])=='/Span');prior.operands[1]['/ActualText']=pikepdf.String('external semantics')
check('existing-accessibility-semantics-modified-refused',lambda:rejected('semantic-change',semantic_change))

def unmarked():
 # Prior exported C2 rows have no embedded ownership; retain conservative individual-line rules.
 path=b.ROOT.parent/'phase4c2/evidence/final-controls-approved/wrap-many-ui.pdf';d=inspect(path);assert not any(r.get('Paragraph') for r in d['Regions']);return [(r['OriginalText'][:25],r['Eligibility']) for r in d['Regions']]
check('unmarked-nearby-matching-lines-never-promoted-to-editor-group',unmarked)
(E/'roundtrip-tests.json').write_text(json.dumps(dict(tests=len(rows),failures=sum(x['status']=='fail' for x in rows),rows=rows,saved=saved,workerPids=fresh,scope='new native worker per inspect/save; no in-memory session or recovery snapshot'),indent=2),encoding='utf-8')
print('Roundtrip:',len(rows),'checks;',sum(x['status']=='fail' for x in rows),'failures;',len(saved),'saved outputs')
