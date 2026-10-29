"""Phase 5.2 authentic originals, strict structural adversaries and fresh-worker saves."""
from pathlib import Path
import json,time,hashlib,copy,io
import pikepdf,pymupdf
from fontTools.ttLib import TTFont
import test_engine as b
E=b.EVID;D=E/('original-tests-'+str(time.time_ns()));D.mkdir();A=D/'adversaries';A.mkdir()
rows=[];saved=[];fixtures=[]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inspect(p,page=0):
 w=b.Worker()
 try:v=w.call(Source=str(p),Page=page);assert v['Ok'],v;return v['Data']
 finally:w.close()
def group(d,kind=None):return next(r for r in d['Regions'] if r.get('Paragraph') and (kind is None or r['Paragraph']['Evidence']==kind))
def change(r,text):return dict(Page=r['Page'],RegionId=r['Id'],Identity=r['SourceIdentity'],Text=text)
def save(d,changes,name,safe=True,dest=None):
 dest=Path(dest or D/(name+'-'+str(time.time_ns())+'.pdf'));old=digest(d['Path']);w=b.Worker()
 try:v=w.call(Command='save',Source=d['Path'],ExpectedHash=d['Hash'],Changes=changes,Destination=str(dest))
 finally:w.close()
 assert old==digest(d['Path'])
 if safe:
  assert v['Ok'] and v['Data']['Safe'],v;r=dict(source=d['Path'],destination=str(dest),changes=changes,result=v['Data']);saved.append(r);(D/('export-record-'+name+'-'+str(time.time_ns())+'.json')).write_text(json.dumps(r,indent=2),encoding='utf-8');return r
 assert not v['Ok'] or not v['Data']['Safe'],v;assert not dest.exists();return v

def check(name,fn):
 try:detail=fn();rows.append(dict(name=name,status='pass',detail=detail));print(name,'pass',flush=True)
 except Exception as e:rows.append(dict(name=name,status='fail',error=repr(e)));print(name,'FAIL',str(e)[:600],flush=True)
source=b.RUN/'original-paragraphs/Word-cafe-paragraph.pdf';chains=[]
def authentic():
 for name,expected in [('Word-cafe-paragraph',True),('Word-letter-paragraph',True),('Word-calm-paragraph',False),('Word-original-multiline',False),('Word-separate-paragraphs',False)]:
  p=source.with_name(name+'.pdf');d=inspect(p);gs=[r for r in d['Regions'] if r.get('Paragraph') and r['Eligibility']=='Editable'];assert bool(gs)==expected
  with pikepdf.open(p) as pdf:
   ops=list(pikepdf.parse_content_stream(pdf.pages[0]));assert not any(str(o.operands[0])=='/PDFEditorV2_Paragraph' for o in ops if str(o.operator)=='BDC');assert 'Word' in str(pdf.docinfo.get('/Producer'));assert '/Author' not in pdf.docinfo
   fonts=[]
   for name,f in pdf.pages[0].Resources.Font.items():
    c=f.DescendantFonts[0] if '/DescendantFonts' in f else f;raw=c.FontDescriptor.FontFile2.read_bytes();ff=TTFont(io.BytesIO(raw));assert all('Prototype' in n.toUnicode() for n in ff['name'].names if n.nameID in (1,6));fonts.append(dict(resource=str(name),sha256=hashlib.sha256(raw).hexdigest(),fsType=ff['OS/2'].fsType))
  if expected:
   g=gs[0];assert g['Paragraph']['Evidence']=='ExistingDocumentParagraphSingleMcid' and len(g['Objects'])==2 and len(g['Positioned']['SourceLines'])==2
   with pymupdf.open(p) as pdf:trace=[''.join(chr(c[0]) for c in span['chars']) for span in pdf[0].get_texttrace() if any(c[0]!=32 for c in span['chars'])]
   assert ''.join(trace[:2])==g['OriginalText'] and trace[:2]==g['OriginalLines'];assert g['OriginalLines'][0].endswith(' ')
  fixtures.append(dict(file=str(p),sha256=digest(p),expectedGrouped=expected,fonts=fonts,regions=[dict(id=r['Id'],objects=r['Objects'],eligibility=r['Eligibility'],reasons=r['Reasons'],observed=r['Observed']) for r in d['Regions']]))
 return fixtures
check('five-authentic-untouched-Word-originals-independent-text-font-provenance',authentic)
def generations():
 p=source;identity=None
 for i,text in enumerate([('calm cafe. '*10).strip(),('cafe calm. '*11).strip(),'calm cafe.'],1):
  d=inspect(p);g=group(d);before=copy.deepcopy(g['Positioned']['SourceLines']);assert i>1 or g['Paragraph']['Evidence']=='ExistingDocumentParagraphSingleMcid'
  out=save(d,[change(g,text)],'original-generation'+str(i));q=group(inspect(out['destination']));assert q['Eligibility']=='Editable' and q['OriginalText']==text and q['FontHash']==g['FontHash'] and q['Paragraph']['Evidence']=='ValidatedEmbeddedParagraphDeclaration';assert i==1 or identity==q['Paragraph']['Id'];assert before==g['Positioned']['SourceLines'];identity=q['Paragraph']['Id'];chains.append(out);p=Path(out['destination'])
 return dict(outputs=[v['destination'] for v in chains],stableOutputId=identity)
check('original-first-save-and-second-third-fresh-worker-generations',generations)
def boundary():
 d=inspect(source);g=group(d);at=len(g['OriginalLines'][0]);assert g['OriginalText'][at-1]==' '
 edits=[('insert-boundary',g['OriginalText'][:at]+'cafe '+g['OriginalText'][at:]),('delete-boundary',g['OriginalText'][:at-1]+g['OriginalText'][at:]),('replace-cross-row',g['OriginalText'][:at-5]+'calm.'+g['OriginalText'][at+5:])]
 return [save(d,[change(g,t)],n)['destination'] for n,t in edits]
check('insertion-deletion-and-replacement-across-original-row-boundary',boundary)
def second():
 d=inspect(source.with_name('Word-letter-paragraph.pdf'));g=group(d);return save(d,[change(g,g['OriginalText'].replace('safe','calm',1))],'letter-original')['destination']
check('second-authentic-paragraph-independent-export',second)
def refused():
 d=inspect(source);g=group(d)
 return [save(d,[change(g,t)],name,False) for name,t in [('unmapped',g['OriginalText']+'\u2603'),('hard-break','cafe\ncalm.'),('too-tall',('cafe calm. '*45).strip())]]
check('unsupported-hardbreak-and-overflow-whole-draft-refused',refused)
def mutate(name,fn):
 p=A/(name+'.pdf')
 with pikepdf.open(source) as pdf:fn(pdf);pdf.save(p,object_stream_mode=pikepdf.ObjectStreamMode.disable)
 d=inspect(p);assert not any(r.get('Paragraph') and r['Eligibility']=='Editable' for r in d['Regions']),[(r['Id'],r['Eligibility'],r['Reasons']) for r in d['Regions']]
 return dict(file=str(p),sha256=digest(p),classification=[dict(objects=r['Objects'],eligibility=r['Eligibility'],reasons=r['Reasons']) for r in d['Regions']])
def p0(pdf):return pdf.Root.StructTreeRoot.K[0].K[0]
def operations(pdf,fn):
 ops=list(pikepdf.parse_content_stream(pdf.pages[0]));fn(ops);pdf.pages[0].Contents=pdf.make_stream(pikepdf.unparse_content_stream(ops))
def second_tm(ops,fn):
 found=0
 for i,o in enumerate(ops):
  if str(o.operator)=='Tm':
   found+=1
   if found==2:ops[i]=pikepdf.ContentStreamInstruction(fn(list(o.operands)),o.operator);return
 raise AssertionError('second Tm missing')
def extra_space(pdf):
 def f(ops):
  idx=next(i for i,o in enumerate(ops) if str(o.operator)=='Tm');show=next(i for i in range(idx,len(ops)) if str(ops[i].operator)=='TJ');ops[show+1:show+1]=[pikepdf.ContentStreamInstruction([pikepdf.Name('/F2'),12],pikepdf.Operator('Tf')),pikepdf.ContentStreamInstruction([pikepdf.Array([pikepdf.String(' ')])],pikepdf.Operator('TJ')),pikepdf.ContentStreamInstruction([pikepdf.Name('/F1'),12],pikepdf.Operator('Tf'))]
 operations(pdf,f)
def separator(pdf):
 def f(ops):
  for i,o in enumerate(ops):
   if str(o.operator)=='TJ':
    args=list(o.operands[0]);j=max(i for i,v in enumerate(args) if isinstance(v,pikepdf.String));raw=bytes(args[j]);args[j]=pikepdf.String(raw[:-2]);ops[i]=pikepdf.ContentStreamInstruction([pikepdf.Array(args)],o.operator);return
 operations(pdf,f)
def paint_conflict(pdf):
 old=pdf.pages[0].Contents.read_bytes();pdf.pages[0].Contents=pdf.make_stream(old+b'\nq 0 0 0 rg 80 740 60 30 re f Q\n')
def separate_scope(pdf):
 def f(ops):
  t=[i for i,o in enumerate(ops) if str(o.operator)=='Tm'][1];ops[t:t]=[pikepdf.ContentStreamInstruction([],pikepdf.Operator('EMC')),pikepdf.ContentStreamInstruction([pikepdf.Name('/Span'),pikepdf.Dictionary(MCID=0,Lang=pikepdf.String('en'))],pikepdf.Operator('BDC'))]
 operations(pdf,f)
def clipped(pdf):
 old=pdf.pages[0].Contents.read_bytes();pdf.pages[0].Contents=pdf.make_stream(b'q 70 720 300 100 re W n\n'+old+b'\nQ')
def mixed_style(pdf):
 def f(ops):
  found=0
  for i,o in enumerate(ops):
   if str(o.operator)=='Tf':
    found+=1
    if found==2:ops[i]=pikepdf.ContentStreamInstruction([o.operands[0],14],o.operator);return
 operations(pdf,f)
def compressed_only(pdf):
 # This variant is saved separately below to exercise the intentional narrow parser boundary.
 pass
neg=[('clipped-original',clipped),('mixed-font-size',mixed_style),('header-role',lambda p:setattr(p0(p),'S',pikepdf.Name('/Header'))),('wrong-structure-backlink',lambda p:setattr(p0(p),'P',p.Root.StructTreeRoot)),('duplicate-structure-child',lambda p:p.Root.StructTreeRoot.K[0].K.append(p0(p))),('missing-structure',lambda p:p.Root.__delitem__('/StructTreeRoot')),('heading-role',lambda p:setattr(p0(p),'S',pikepdf.Name('/H1'))),('table-cell-role',lambda p:setattr(p0(p),'S',pikepdf.Name('/TD'))),('list-role',lambda p:setattr(p0(p),'S',pikepdf.Name('/L'))),('footer-role',lambda p:setattr(p0(p),'S',pikepdf.Name('/Footer'))),('changed-K',lambda p:setattr(p0(p),'K',pikepdf.Array([99]))),('changed-page-parent-key',lambda p:setattr(p.pages[0].obj,'StructParents',9)),('duplicate-parent-association',lambda p:p.Root.StructTreeRoot.ParentTree.Nums[1].__setitem__(1,p0(p))),('swapped-parent-index',lambda p:(p.Root.StructTreeRoot.ParentTree.Nums[1].__setitem__(0,p.Root.StructTreeRoot.K[0].K[1]),p.Root.StructTreeRoot.ParentTree.Nums[1].__setitem__(1,p0(p)))),('actual-text-semantics',lambda p:setattr(p0(p),'ActualText',pikepdf.String('different'))),('column-or-label-value',lambda p:operations(p,lambda ops:second_tm(ops,lambda a:a[:4]+[a[4]+150,a[5]]))),('reading-order-reversed',lambda p:operations(p,lambda ops:second_tm(ops,lambda a:a[:5]+[a[5]+40]))),('rotated-row',lambda p:operations(p,lambda ops:second_tm(ops,lambda a:[0,1,-1,0]+a[4:]))),('interleaved-whitespace',extra_space),('ambiguous-separator',separator),('near-protected-graphic',paint_conflict),('duplicate-native-MCID-scope',separate_scope)]
for name,fn in neg:check('negative-'+name,lambda name=name,fn=fn:mutate(name,fn))
def unsupported_xref():
 p=A/'xref-stream-only.pdf'
 with pikepdf.open(source) as pdf:pdf.save(p,object_stream_mode=pikepdf.ObjectStreamMode.generate)
 d=inspect(p);assert not any(r.get('Paragraph') and r['Eligibility']=='Editable' for r in d['Regions']);return str(p)
check('unsupported-xref-stream-only-fails-closed',unsupported_xref)
# Derived mixed document; authentic positive acceptance above uses byte-original export only.
mixed=D/'mixed-original-marked-natural-other-page.pdf'
def build_mixed():
 global mixed
 with pikepdf.open(source) as pdf,pikepdf.open(source) as marked,pikepdf.open(b.RUN/'document-corpus/mixed-multipage.pdf') as natural:
  pdf.pages.extend(marked.pages);pdf.pages.append(natural.pages[1]);pdf.pages.append(natural.pages[1]);root=pdf.Root.StructTreeRoot;doc=root.K[0];children=list(doc.K);parents=list(root.ParentTree.Nums)
  pdf.pages[1].obj.StructParents=1
  arr=[]
  for old in marked.Root.StructTreeRoot.K[0].K:
   elem=pdf.make_indirect(pikepdf.Dictionary(Type=pikepdf.Name('/StructElem'),S=old.S,P=doc,Pg=pdf.pages[1].obj,K=old.K));children.append(elem);arr.append(elem)
  doc.K=pikepdf.Array(children);root.ParentTree.Nums=pikepdf.Array(parents+[1,pikepdf.Array(arr)]);root.ParentTreeNextKey=2;pdf.save(mixed,object_stream_mode=pikepdf.ObjectStreamMode.disable)
 # Establish a real page-1 declaration through the verified editor, after combining.
 raw=inspect(mixed,1);original=group(raw);staged=save(raw,[change(original,'calm cafe. '+original['OriginalText'])],'mixed-establish-page1-marker');mixed=Path(staged['destination'])
 d=inspect(mixed);g=group(d,'ExistingDocumentParagraphSingleMcid');m=group(inspect(mixed,1),'ValidatedEmbeddedParagraphDeclaration');n=inspect(mixed,2)['Regions'][0];o=inspect(mixed,3)['Regions'][0]
 edits=[change(g,'calm cafe. '+g['OriginalText']),change(m,'cafe calm.'),change(n,'First changed working paragraph.'),change(o,'First working paragraph.')];out=save(d,edits,'mixed-four-regions');assert out['result']['Verification']['changedRegions']==4
 (E/'original-mixed-expectation.json').write_text(json.dumps(dict(source=str(mixed),changes=edits),indent=2),encoding='utf-8');return out['destination']
check('mixed-original-marked-natural-and-other-page-atomic-save',build_mixed)
def no_subset():
 d=inspect(mixed);g=group(d);n=inspect(mixed,2)['Regions'][0];return save(d,[change(g,'cafe\ncalm'),change(n,'First working paragraph.')],'no-subset',False)
check('mixed-invalid-region-blocks-entire-export',no_subset)
def guards():
 p=D/'guard-source.pdf';p.write_bytes(source.read_bytes());d=inspect(p);g=group(d);p.write_bytes(p.read_bytes()+b'\n% external change\n');v=save(d,[change(g,'cafe calm.')],'changed-source',False);assert not v['Ok'];return v
check('new-original-source-hash-guard',guards)
(E/'original-tests.json').write_text(json.dumps(dict(tests=len(rows),failures=sum(r['status']!='pass' for r in rows),rows=rows,saved=saved,fixtures=fixtures),indent=2),encoding='utf-8')
print('TOTAL',len(rows),'FAIL',sum(r['status']!='pass' for r in rows),flush=True)
