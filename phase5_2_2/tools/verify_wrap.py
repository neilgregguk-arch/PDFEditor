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
records=json.loads((E/'wrap-tests.json').read_text(encoding='utf-8'))['saved']
if (E/'paragraph-performance-records.json').exists():records+=json.loads((E/'paragraph-performance-records.json').read_text(encoding='utf-8'))
if (E/'roundtrip-tests.json').exists():records+=json.loads((E/'roundtrip-tests.json').read_text(encoding='utf-8'))['saved']
if (E/'development-generations.json').exists():records+=[r for r in json.loads((E/'development-generations.json').read_text()) if r.get('result',{}).get('Safe')]
for file in ['insertion-tests.json','document-tests.json','original-tests.json']:
 if (E/file).exists():records+=json.loads((E/file).read_text(encoding='utf-8'))['saved']
for p in E.rglob('export-record-*.json'):
 if not any((part.startswith('frozen') or part.startswith('basic-retry-phase5_1')) for part in p.relative_to(E).parts):records.append(json.loads(p.read_text(encoding='utf-8')))
for p in E.glob('probe-wrap-*.json'):records.append(json.loads(p.read_text(encoding='utf-8')))
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
  for args,op in page.get_contents().operations if page.get_contents() is not None else []:
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
 # Text drawing traces retain separate F2 whitespace runs even when rawdict
 # merges their spans after preserved content order is restored. No characters
 # are trimmed or normalized: standalone source spaces remain in untouched checks.
 out=[]
 for span in doc[page].get_texttrace():
  standalone=all(c[0]==32 for c in span['chars'])
  for code,gid,origin,bounds in span['chars']:out.append(dict(c=chr(code),glyphId=gid,origin=origin,bbox=bounds,standaloneWhitespace=standalone))
 return sorted(out,key=lambda c:(round(c['origin'][1],2),c['origin'][0]))

def select_line(glyphs,text,x,baseline):
 if not text:return []
 indices=[i for i,c in enumerate(glyphs) if abs(c['origin'][1]-baseline)<.03 and not c.get('standaloneWhitespace')];line=''.join(glyphs[i]['c'] for i in indices);starts=[];start=0
 while True:
  pos=line.find(text,start)
  if pos<0:break
  starts.append(pos);start=pos+1
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
   observed_region=next(r for r in info(str(source),page)['Regions'] if r['Id']==edit['RegionId']);region=observed_region
   if 'sourceRegion' in record:
    # Early development records predate the switch from quantized claimed
    # offsets to exact observed offsets in source fingerprints. Bind their
    # captured observations to the actual file, never by opaque ID alone.
    region=dict(record['sourceRegion']);assert region['SourceIdentity']==edit['Identity']
    for key in ['SourceHash','Page','Id','Objects','OriginalText','OriginalLines','FontHash','FontSize','R','G','B','X','Baseline','Width','SafeBottom','LineHeight','Ascent']:assert region[key]==observed_region[key],(dest,'captured source observation differs',key)
    assert len(region['Glyphs'])==len(observed_region['Glyphs'])
    for ga,gb in zip(region['Glyphs'],observed_region['Glyphs']):
     assert ga['Text']==gb['Text'] and abs(ga['OriginX']-gb['OriginX'])<=.01 and abs(ga['Baseline']-gb['Baseline'])<=.01
     assert max(abs(ga['Bounds'][k]-gb['Bounds'][k]) for k in ['X','Y','Width','Height'])<=.01
    region['FontFile']=observed_region['FontFile']
   else:assert region['SourceIdentity']==edit['Identity'],(dest,'current source identity differs')
   p=next(r for r in plan['regions'] if r['sourceIdentity']==edit['Identity']);before_indices=[];after_indices=[]
   for i,line in enumerate(region['OriginalLines']):before_indices+=select_line(a,line,region['X'],region['Positioned']['SourceLines'][i]['Baseline'] if region.get('Paragraph') else region['Baseline']+i*region['LineHeight'])
   for i,line in enumerate(p['layout']['Lines']):after_indices+=select_line(b,line,region['X'],p['layout']['Positioned']['Lines'][i]['Baseline'] if p['layout'].get('Positioned') else region['Baseline']+i*region['LineHeight'])
   assert not owned_a.intersection(before_indices) and not owned_b.intersection(after_indices);owned_a.update(before_indices);owned_b.update(after_indices)
   assert ('\n'.join(p['layout']['Lines']) if not region.get('Positioned') and '\n' in edit['Text'] else ''.join(p['layout']['Lines']))==edit['Text'],(dest,'logical text changed by wrapping')
   if region.get('Positioned'):
    text=edit['Text'];assert len(after_indices)==len(text)
    model=p['layout']['Positioned'];mapping=model['OriginalIndices'];original=region['OriginalText'];assert len(mapping)==len(text)
    # Independent alignment and advances from preserved font program, not proposed origins.
    ft=TTFont(region['FontFile']);cmap=ft.getBestCmap();units=ft['head'].unitsPerEm
    advance=lambda c:ft['hmtx'].metrics[cmap[ord(c)]][0]/units*region['FontSize']
    fixed=len(text)==len(original) and all(x==y or advance(y)<=advance(x)+.001 for x,y in zip(original,text))
    flattened=[region['X']]
    for i in range(1,len(original)):
     prev=a[before_indices[i-1]];cur=a[before_indices[i]];flattened.append(flattened[-1]+(cur['origin'][0]-prev['origin'][0] if abs(cur['origin'][1]-prev['origin'][1])<.01 else advance(original[i-1])))
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
    from fontTools.pens.boundsPen import BoundsPen
    glyphset=ft.getGlyphSet();boxes=[]
    for compat in region['Characters']:
     if compat['Advance']<0 or compat['Unicode']==32:continue
     pen=BoundsPen(glyphset);glyphset[cmap[compat['Unicode']]].draw(pen)
     if pen.bounds:boxes.append(pen.bounds)
    inkheight=(max(bb[3] for bb in boxes)-min(bb[1] for bb in boxes))*region['FontSize']/units
    leading=max(2*region['FontSize'],inkheight+3);xs=[]
    for row,line in enumerate(model['Lines']):
     baseline=region['Baseline']+row*leading;assert abs(line['Baseline']-baseline)<=.01
     indices=select_line(b,line['Text'],region['X'],baseline)
     for j,idx in enumerate(indices):
      i=line['Start']+j;ca=b[idx];m=mapping[i]
      if j==0:x=region['X']
      elif row==0 and fixed:x=flattened[i]
      elif row==0 and mapping[i-1]>=0 and m==mapping[i-1]+1:x=xs[-1]+flattened[m]-flattened[m-1]
      else:x=xs[-1]+advance(text[i-1])
      xs.append(x);delta=max(abs(ca['origin'][0]-x),abs(ca['origin'][1]-baseline));positioned_shift=max(positioned_shift,delta);assert delta<=.01,(dest,'proposed glyph origin',i,delta);assert ca['c']==text[i];assert ca['glyphId']==ft.getGlyphID(cmap[ord(text[i])]),(dest,'independent glyph identity');assert abs(model['Origins'][i]-x)<=.01
      if m>=0 and text[i]!=' ':
       original_char=a[before_indices[m]];dx=x-original_char['origin'][0];dy=baseline-original_char['origin'][1];expected_box=[original_char['bbox'][0]+dx,original_char['bbox'][1]+dy,original_char['bbox'][2]+dx,original_char['bbox'][3]+dy];assert max(abs(v-z) for v,z in zip(ca['bbox'],expected_box))<=.01,(dest,'surviving glyph box')
    assert ''.join(b[idx]['c'] for idx in after_indices)==text,(dest,'exact logical text independent extraction')
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
   assert ca['c']==cb['c'] and ca['glyphId']==cb['glyphId'],(dest,page,ca,cb);shift=max(abs(x-y) for x,y in zip(tuple(ca['origin'])+tuple(ca['bbox']),tuple(cb['origin'])+tuple(cb['bbox'])));max_shift=max(max_shift,shift);assert shift<=.01,(dest,page,'untouched glyph shift',shift)
  comparisons=[]
  for dpi in [72,144]:
   before=render(source,P/f'{number}-p{page}-before-{dpi}',page,dpi);after=render(dest,P/f'{number}-p{page}-after-{dpi}',page,dpi);assert before.shape==after.shape;changed=np.max(abs(before-after),axis=2)>8;yy,xx=np.indices(changed.shape);scale=dpi/72;inside=np.zeros(changed.shape,dtype=bool)
   for box in ([] if plan is None else [r['allowed'] for r in plan['regions']]):inside|=(xx/scale>=box['X'])&(xx/scale<=box['Right'])&(yy/scale>=box['Y'])&(yy/scale<=box['Bottom'])
   outside=int(np.sum(changed&~inside));assert outside==0,(dest,page,dpi,outside);comparisons.append(dict(dpi=dpi,changedPixels=int(changed.sum()),outsidePixels=outside))
  page_reports.append(dict(page=page,replacements=replacement_checks,unmodifiedGlyphs=len(untouched_a),maxUntouchedGlyphShiftPt=max_shift,maxPositionedTargetOriginShiftPt=positioned_shift,whitespaceBytes=spaces(rb,page),comparisons=comparisons))
 da.close();db.close();rows.append(dict(source=str(source),destination=str(dest),allChangesVerified=True,originalFontsAndMappingRulesPreserved=True,pages=page_reports));print('Verified',dest.name,flush=True)
(E/'verified-export-records.json').write_text(json.dumps(records,indent=2),encoding='utf-8');w.close();(E/'wrap-independent-verification.json').write_text(json.dumps(dict(success=True,readers='MuPDF + pypdf + Poppler 72/144 DPI + qpdf via pikepdf',cases=rows),indent=2));print('Independent combined exports:',len(rows))
