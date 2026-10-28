"""Independent verification of entire combined exports, including UI saves."""
from pathlib import Path
import json,hashlib,collections,subprocess
import numpy as np
from PIL import Image
from pypdf import PdfReader
import pymupdf,pikepdf,io
from fontTools.ttLib import TTFont
import test_engine as base
R=base.ROOT;E=R/'evidence';P=E/'document-poppler';P.mkdir(exist_ok=True)
records=json.loads((E/'insertion-tests.json').read_text(encoding='utf-8'))['saved']
if (E/'document-tests.json').exists():records+=json.loads((E/'document-tests.json').read_text(encoding='utf-8'))['saved']
for p in list((E/'final-release-controls').glob('export-record-*.json'))+list((E/'selection-verified-controls').glob('export-record-*.json')):records.append(json.loads(p.read_text(encoding='utf-8')))
if (E/'process-recovery.json').exists():
 recovery=json.loads((E/'process-recovery.json').read_text(encoding='utf-8'))['second'];records.append(dict(source=recovery['source'],destination=recovery['result']['Destination'],changes=recovery['changes'],result=recovery['result']))
if (E/'position-tests.json').exists():
 for item in json.loads((E/'position-tests.json').read_text(encoding='utf-8'))['saved']:
  if 'pages' in item['verification']:
   reg=item['region'];records.append(dict(source=item['source'],destination=item['destination'],changes=[dict(Page=reg['Page'],RegionId=reg['Id'],Identity=reg['SourceIdentity'],Text=item['draft'])],result=dict(Verification=item['verification'])))
unique={r['destination']:r for r in records};records=list(unique.values());w=base.Worker();cache={}
def info(source,page):
 key=(source,page)
 if key not in cache:
  v=w.call(Command='inspect',Source=source,Page=page);assert v['Ok'],v;cache[key]=v['Data']
 return cache[key]
def fonts(reader):
 programs=set();rules=set()
 for page in reader.pages:
  used=set();selected=None
  for args,op in page.get_contents().operations if page.get_contents() else []:
   if op==b'Tf':selected=args[0]
   if op in [b'Tj',b'TJ',b"'",b'"']:
    values=args[0] if op==b'TJ' else args
    if selected is not None and any(isinstance(v,(str,bytes)) and len(v)>0 for v in values):used.add(selected)
  for name,ref in page['/Resources'].get('/Font',{}).items():
   f=ref.get_object();child=f['/DescendantFonts'][0].get_object() if '/DescendantFonts' in f else f;desc=child.get('/FontDescriptor',{});desc=desc.get_object() if hasattr(desc,'get_object') else desc
   for key in ['/FontFile','/FontFile2','/FontFile3']:
    if key in desc:programs.add(hashlib.sha256(desc[key].get_object().get_data()).hexdigest())
   rule={}
   for container,keys in [(f,['/Encoding','/ToUnicode']),(child,['/BaseFont','/Subtype','/W','/Widths','/DW','/FirstChar','/LastChar','/CIDToGIDMap'])]:
    for key in keys:
     value=container.get(key);value=value.get_object() if hasattr(value,'get_object') else value;rule[key]=hashlib.sha256(value.get_data()).hexdigest() if hasattr(value,'get_data') else str(value)
   if name in used:rules.add(json.dumps(rule,sort_keys=True))
 return programs,rules
def spaces(reader,page):
 result=collections.defaultdict(list);font=None
 for args,op in reader.pages[page].get_contents().operations:
  if op==b'Tf':font=args[0]
  if op not in [b'Tj',b'TJ'] or font is None:continue
  f=reader.pages[page]['/Resources']['/Font'][font].get_object()
  if '/DescendantFonts' in f:continue
  desc=f.get('/FontDescriptor',{});desc=desc.get_object() if hasattr(desc,'get_object') else desc
  if any(k in desc for k in ['/FontFile','/FontFile2','/FontFile3']):continue
  values=args[0] if op==b'TJ' else args
  for value in values:
   if isinstance(value,(str,bytes)):result[str(f.get('/BaseFont'))].append((bytes(value) if isinstance(value,bytes) else value.original_bytes).hex())
 return dict(result)
def chars(doc,page):
 out=[]
 for block in doc[page].get_text('rawdict')['blocks']:
  for line in block.get('lines',[]):
   for span in line['spans']:
    for c in span['chars']:out.append(dict(c,standaloneWhitespace=all(x['c']==' ' for x in span['chars'])))
 return sorted(out,key=lambda c:(round(c['origin'][1],2),c['origin'][0]))
def select_line(glyphs,text,x,baseline):
 if not text:return []
 indices=[i for i,c in enumerate(glyphs) if abs(c['origin'][1]-baseline)<.03 and not c.get('standaloneWhitespace')];line=''.join(glyphs[i]['c'] for i in indices);starts=[];start=0
 while True:
  pos=line.find(text,start)
  if pos<0:break
  starts.append(pos);start=pos+1
 if not starts and text!=text.rstrip():return select_line(glyphs,text.rstrip(),x,baseline)
 if not starts:raise AssertionError(('Independent line missing',text,line))
 pos=min(starts,key=lambda p:abs(glyphs[indices[p]]['origin'][0]-x));return indices[pos:pos+len(text)]
def render(path,prefix,page,dpi):
 subprocess.run(['pdftoppm','-f',str(page+1),'-l',str(page+1),'-singlefile','-r',str(dpi),'-png',str(path),str(prefix)],capture_output=True,check=True)
 return np.asarray(Image.open(str(prefix)+'.png').convert('RGB'),dtype=np.int16)
rows=[]
for number,record in enumerate(records):
 source=Path(record['source']);dest=Path(record['destination']);ra=PdfReader(source);rb=PdfReader(dest);da=pymupdf.open(source);db=pymupdf.open(dest);verification=record['result']['Verification'];assert hashlib.sha256(source.read_bytes()).hexdigest()==verification['sourceHash'];assert hashlib.sha256(dest.read_bytes()).hexdigest()==verification['candidateHash'];assert verification['changedRegions']==len(record['changes']);assert len(ra.pages)==len(rb.pages);assert [list(p.mediabox) for p in ra.pages]==[list(p.mediabox) for p in rb.pages];assert dict(ra.metadata or {})==dict(rb.metadata or {});assert fonts(ra)==fonts(rb)
 with pikepdf.open(dest) as pdf:assert not pdf.check_pdf_syntax()
 page_reports=[]
 for page in range(len(ra.pages)):
  assert spaces(ra,page)==spaces(rb,page),(dest,page,'unembedded whitespace bytes changed')
  edits=[c for c in record['changes'] if c['Page']==page];plan=next((p for p in verification['pages'] if p['page']==page),None);a,b=chars(da,page),chars(db,page);owned_a=set();owned_b=set();positioned_shift=0;replacement_checks=[]
  for edit in edits:
   region=next(r for r in info(str(source),page)['Regions'] if r['Id']==edit['RegionId']);assert region['SourceIdentity']==edit['Identity'];p=next(r for r in plan['regions'] if r['sourceIdentity']==edit['Identity']);before_indices=[];after_indices=[]
   for i,line in enumerate(region['OriginalLines']):before_indices+=select_line(a,line,region['X'],region['Baseline']+i*region['LineHeight'])
   for i,line in enumerate(p['layout']['Lines']):after_indices+=select_line(b,line,region['X'],region['Baseline']+i*region['LineHeight'])
   assert not owned_a.intersection(before_indices) and not owned_b.intersection(after_indices);owned_a.update(before_indices);owned_b.update(after_indices)
   assert ' '.join(edit['Text'].split()) in ' '.join(rb.pages[page].extract_text().split())
   if region.get('Positioned'):
    text=edit['Text'];assert len(after_indices)==len(text)
    model=p['layout']['Positioned'];mapping=model['OriginalIndices'];original=region['OriginalText'];assert len(mapping)==len(text)
    # Independent alignment and advances from preserved font program, not proposed origins.
    ft=TTFont(region['FontFile']);cmap=ft.getBestCmap();units=ft['head'].unitsPerEm
    advance=lambda c:ft['hmtx'].metrics[cmap[ord(c)]][0]/units*region['FontSize']
    fixed=len(text)==len(original) and all(x==y or advance(y)<=advance(x)+.001 for x,y in zip(original,text))
    if fixed:expected_map=[i if text[i]==original[i] else -1 for i in range(len(text))]
    else:
     dp=[[0]*(len(text)+1) for _ in range(len(original)+1)]
     for i in range(len(original)-1,-1,-1):
      for j in range(len(text)-1,-1,-1):dp[i][j]=1+dp[i+1][j+1] if original[i]==text[j] else max(dp[i+1][j],dp[i][j+1])
     expected_map=[-1]*len(text);i=j=0
     while i<len(original) and j<len(text):
      if original[i]==text[j]:expected_map[j]=i;i+=1;j+=1
      elif dp[i+1][j]>=dp[i][j+1]:i+=1
      else:j+=1
    assert mapping==expected_map,(dest,'alignment mismatch')
    xs=[]
    for i,idx in enumerate(after_indices):
     ca=b[idx];m=mapping[i]
     if fixed:x=a[before_indices[i]]['origin'][0]
     elif i==0:x=region['X']
     elif mapping[i-1]>=0 and m==mapping[i-1]+1:x=xs[-1]+a[before_indices[m]]['origin'][0]-a[before_indices[m-1]]['origin'][0]
     else:x=xs[-1]+advance(text[i-1])
     xs.append(x);delta=max(abs(ca['origin'][0]-x),abs(ca['origin'][1]-region['Baseline']));positioned_shift=max(positioned_shift,delta);assert delta<=.01,(dest,'proposed glyph origin',i,delta);assert ca['c']==text[i]
     assert abs(model['Origins'][i]-x)<=.01,(dest,'independent proposal mismatch')
     if m>=0 and text[i]!=' ':
      original_char=a[before_indices[m]];dx=x-original_char['origin'][0];expected_box=[original_char['bbox'][0]+dx,original_char['bbox'][1],original_char['bbox'][2]+dx,original_char['bbox'][3]];assert max(abs(v-z) for v,z in zip(ca['bbox'],expected_box))<=.01,(dest,'surviving glyph box')
    ft.close()
   else:
    for line_index,line in enumerate(p['layout']['Lines']):
     indices=select_line(b,line,region['X'],region['Baseline']+line_index*region['LineHeight']);x=region['X']
     for j,idx in enumerate(indices):
      c=b[idx];assert c['c']==line[j];assert abs(c['origin'][1]-(region['Baseline']+line_index*region['LineHeight']))<=.15;assert abs(c['origin'][0]-x)<=1
      if j:assert abs(c['origin'][0]-b[indices[j-1]]['origin'][0]-region['Advances'][ord(line[j-1])-32])<=.05
      x+=region['Advances'][ord(line[j])-32]
   replacement_checks.append(dict(key=p['key'],strategy=p['strategy'],text=edit['Text'],independentVisibleGlyphs=len(after_indices)))
  untouched_a=[c for i,c in enumerate(a) if i not in owned_a];untouched_b=[c for i,c in enumerate(b) if i not in owned_b];assert len(untouched_a)==len(untouched_b),(dest,page,'untouched glyph count',len(untouched_a),len(untouched_b));max_shift=0
  for ca,cb in zip(untouched_a,untouched_b):
   assert ca['c']==cb['c'],(dest,page,ca,cb);shift=max(abs(x-y) for x,y in zip(tuple(ca['origin'])+tuple(ca['bbox']),tuple(cb['origin'])+tuple(cb['bbox'])));max_shift=max(max_shift,shift);assert shift<=.01,(dest,page,'untouched glyph shift',shift)
  comparisons=[]
  for dpi in [72,144]:
   before=render(source,P/f'{number}-p{page}-before-{dpi}',page,dpi);after=render(dest,P/f'{number}-p{page}-after-{dpi}',page,dpi);assert before.shape==after.shape;changed=np.max(abs(before-after),axis=2)>8;yy,xx=np.indices(changed.shape);scale=dpi/72;inside=np.zeros(changed.shape,dtype=bool)
   for box in ([] if plan is None else [r['allowed'] for r in plan['regions']]):inside|=(xx/scale>=box['X'])&(xx/scale<=box['Right'])&(yy/scale>=box['Y'])&(yy/scale<=box['Bottom'])
   outside=int(np.sum(changed&~inside));assert outside==0,(dest,page,dpi,outside);comparisons.append(dict(dpi=dpi,changedPixels=int(changed.sum()),outsidePixels=outside))
  page_reports.append(dict(page=page,replacements=replacement_checks,unmodifiedGlyphs=len(untouched_a),maxUntouchedGlyphShiftPt=max_shift,maxPositionedTargetOriginShiftPt=positioned_shift,whitespaceBytes=spaces(rb,page),comparisons=comparisons))
 da.close();db.close();rows.append(dict(source=str(source),destination=str(dest),allChangesVerified=True,originalFontsAndMappingRulesPreserved=True,pages=page_reports));print('Verified',dest.name,flush=True)
w.close();(E/'document-independent-verification.json').write_text(json.dumps(dict(success=True,readers='MuPDF + pypdf + Poppler 72/144 DPI + qpdf via pikepdf',cases=rows),indent=2));print('Independent combined exports:',len(rows))
