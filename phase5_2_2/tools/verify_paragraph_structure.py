"""Independent marked-content and existing accessibility-structure checks."""
from pathlib import Path
import json,hashlib,collections
from pypdf import PdfReader
from pypdf.generic import IndirectObject
import pymupdf,pikepdf
R=Path(__file__).resolve().parents[1];E=R/'evidence'
records=json.loads((E/'verified-export-records.json').read_text(encoding='utf-8'));reports=[]
TAG='/PDFEditorV2_Paragraph'
def canon(value,key='',depth=0):
 assert depth<=64,'Structure graph depth'
 if isinstance(value,IndirectObject):
  if key in ['/P','/Pg','/Parent']:return {'ref':[value.idnum,value.generation]}
  value=value.get_object()
 if isinstance(value,dict):return {str(k):canon(v,str(k),depth+1) for k,v in sorted(value.items(),key=lambda p:str(p[0]))}
 if isinstance(value,(list,tuple)):return [canon(v,'',depth+1) for v in value]
 if isinstance(value,bytes):return {'bytes':value.hex()}
 if isinstance(value,(str,int,float,bool)) or value is None:return value
 return str(value)
def properties(page,value):
 if isinstance(value,str):value=page['/Resources']['/Properties'][value]
 return value.get_object() if hasattr(value,'get_object') else value
def scan(reader):
 all_ids=collections.defaultdict(set);result=[];semantics=[]
 for page_index,page in enumerate(reader.pages):
  stack=[];groups=collections.defaultdict(list);semantic=[]
  for args,op in page.get_contents().operations if page.get_contents() is not None else []:
   if op in [b'BDC',b'BMC']:
    tag=str(args[0]);props=properties(page,args[1]) if op==b'BDC' else {};item=dict(tag=tag,props=props,operators=0);stack.append(item)
    if tag!=TAG:semantic.append(dict(tag=tag,props=canon(props)))
    else:
     assert set(props)=={'/Data','/Row'};assert '/MCID' not in props and '/ActualText' not in props
     raw=props['/Data'].original_bytes;assert len(raw)<=28000;manifest=json.loads(raw);assert manifest['Version']==1;assert manifest['Page']==page_index;assert len(manifest['Id'])==32;assert len(manifest['Text'])<=512 and 1<=len(manifest['Rows'])<=8
     item.update(manifest=manifest,row=int(props['/Row']),payloadHash=hashlib.sha256(raw).hexdigest());groups[manifest['Id']].append(item);all_ids[manifest['Id']].add(page_index)
   elif op==b'EMC':assert stack;stack.pop()
   elif op in [b'Tj',b'TJ',b"'",b'"']:
    owned=[s for s in stack if s['tag']==TAG];assert len(owned)<=1
    if owned:owned[0]['operators']+=1
  assert not stack,'Unbalanced marked content'
  valid=[]
  for identity,members in groups.items():
   members.sort(key=lambda m:m['row']);manifest=members[0]['manifest'];assert [m['row'] for m in members]==list(range(len(manifest['Rows'])));assert len({m['payloadHash'] for m in members})==1;assert all(m['operators']>0 for m in members);assert ''.join(r['Text'] for r in manifest['Rows'])==manifest['Text'];assert all(len(r['Origins'])==len(r['Bounds'])==len(r['Text']) for r in manifest['Rows'])
   valid.append(dict(id=identity,manifest=manifest,payloadBytes=len(members[0]['props']['/Data'].original_bytes),members=len(members)))
  semantics.append(semantic);result.append(valid)
 assert all(len(pages)==1 for pages in all_ids.values()),'Identifier reused on different pages'
 return result,semantics
for record in records:
 a=PdfReader(record['source']);b=PdfReader(record['destination']);before,sa=scan(a);after,sb=scan(b)
 expected={region['paragraphId'] for page in record['result']['Verification']['pages'] for region in page['regions'] if region.get('paragraphId')}
 actual={group['id'] for page in after for group in page};assert expected<=actual,(record['destination'],'Expected paragraph marks were not inspected')
 assert sa==sb,(record['destination'],'Existing marked-content sequences changed')
 for pa,pb in zip(a.pages,b.pages):assert canon(pa.get('/StructParents'))==canon(pb.get('/StructParents')),(record['destination'],'Page StructParents changed')
 for key in ['/StructTreeRoot','/MarkInfo','/Lang']:
  assert canon(a.trailer['/Root'].get(key))==canon(b.trailer['/Root'].get(key)),(record['destination'],key,'Existing accessibility graph changed')
 verified=[]
 with pymupdf.open(record['destination']) as doc:
  for page,groups in enumerate(after):
   raw=[]
   for span in doc[page].get_texttrace():
    if all(c[0]==32 for c in span['chars']):continue
    raw.extend(dict(c=chr(c[0]),origin=c[2]) for c in span['chars'])
   for group in groups:
    manifest=group['manifest'];text=''
    for row in manifest['Rows']:
     available=sorted([c for c in raw if abs(c['origin'][1]-row['Baseline'])<=.01],key=lambda c:c['origin'][0]);line=''.join(c['c'] for c in available);start=line.find(row['Text']);assert start>=0,(record['destination'],'Declared row not independently extracted');chars=available[start:start+len(row['Text'])]
     assert ''.join(c['c'] for c in chars)==row['Text'];assert all(abs(c['origin'][0]-x)<=.01 for c,x in zip(chars,row['Origins']));text+=''.join(c['c'] for c in chars)
    assert text==manifest['Text'];verified.append(dict(page=page,id=group['id'],rows=group['members'],characters=len(text),payloadBytes=group['payloadBytes']))
 reports.append(dict(source=record['source'],destination=record['destination'],balancedCustomMarks=True,existingAccessibilityGraphEqual=True,existingSemanticSequencesEqual=True,groups=verified))
(E/'paragraph-structure-verification.json').write_text(json.dumps(dict(success=True,cases=reports,readers='pypdf + MuPDF + pikepdf; no production grouping code'),indent=2),encoding='utf-8');print('Independent paragraph structure:',len(reports),'PDFs;',sum(len(r['groups']) for r in reports),'group instances')
