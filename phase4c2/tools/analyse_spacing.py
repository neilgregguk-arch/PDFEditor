from pathlib import Path
import json,hashlib,io,re
from pypdf import PdfReader
from fontTools.ttLib import TTFont
import test_engine as b
E=b.EVID;w=b.Worker();rows=[]
for name in ['corpus/11-word-letter.pdf','font-corpus/Word-Arial.pdf','font-corpus/Word-Calibri.pdf']:
 p=b.RUN/name;v=w.call(Command='inspect',Source=str(p));assert v['Ok'],v;d=v['Data'];print(name,[(r['OriginalText'],r['Eligibility'],r.get('Positioned') is not None) for r in d['Regions']]);reader=PdfReader(p);raw=reader.pages[0].get_contents().get_data().decode('latin1');arrays=[{'operator':op.decode(),'args':str(args)} for args,op in reader.pages[0].get_contents().operations if op in [b'TJ',b'Tj',b'Tf',b'Tm',b'Tc',b'Tw',b'Tz']];lines=[]
 for r in d['Regions']:
  if not r.get('Positioned'):continue
  gs=r['Glyphs'];res=[gs[i+1]['OriginX']-g['OriginX']-r['Advances'][ord(g['Text'])-32] for i,g in enumerate(gs[:-1])];lines.append(dict(region=r,adjustmentsPt=res,maxAbsoluteAdjustmentPt=max(map(abs,res)),interpretation='Measured PDF displacement residuals, not proven author-intended kerning.'))
  font_evidence={}
 for key,ref in reader.pages[0]['/Resources']['/Font'].items():
  f=ref.get_object();child=f['/DescendantFonts'][0].get_object() if '/DescendantFonts' in f else f;desc=child.get('/FontDescriptor',{});desc=desc.get_object() if hasattr(desc,'get_object') else desc;program=next((desc[k].get_object().get_data() for k in ['/FontFile2','/FontFile','/FontFile3'] if k in desc),None);unicode=f.get('/ToUnicode');unicode=unicode.get_object().get_data().decode('latin1') if unicode else '';mapping={}
  for block in re.findall(r'beginbfchar(.*?)endbfchar',unicode,re.S):
   for code,value in re.findall(r'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>',block):mapping[int(code,16)]=bytes.fromhex(value).decode('utf-16-be')
  for block in re.findall(r'beginbfrange(.*?)endbfrange',unicode,re.S):
   for first,last,value in re.findall(r'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>',block):
    for code in range(int(first,16),int(last,16)+1):mapping[code]=chr(int(value,16)+code-int(first,16))
  cid=child.get('/CIDToGIDMap');cidbytes=cid.get_object().get_data() if hasattr(cid,'get_object') and hasattr(cid.get_object(),'get_data') else None
  ft=TTFont(io.BytesIO(program)) if program else None
  font_evidence[str(key)]=dict(baseFont=str(f.get('/BaseFont')),subtype=str(f.get('/Subtype')),encoding=str(f.get('/Encoding')),fontProgramSha256=hashlib.sha256(program).hexdigest() if program else None,toUnicode=unicode,unicodeByCode=mapping,cidToGidSha256=hashlib.sha256(cidbytes).hexdigest() if cidbytes else str(cid),widths=str(child.get('/W',child.get('/Widths'))))
  encoded=[];current=None
  for args,op in reader.pages[0].get_contents().operations:
   if op==b'Tf':current=str(args[0])
   if current!=str(key) or op not in [b'TJ',b'Tj']:continue
   vals=args[0] if op==b'TJ' else args
   for value in vals:
    if not isinstance(value,(str,bytes)):continue
    raw=value if isinstance(value,bytes) else value.original_bytes
    width=2 if '/DescendantFonts' in f else 1
    for off in range(0,len(raw),width):
     code=int.from_bytes(raw[off:off+width],'big');gid=int.from_bytes(cidbytes[code*2:code*2+2],'big') if cidbytes else code;glyph=ft.getGlyphOrder()[gid] if ft and gid<len(ft.getGlyphOrder()) else None
     encoded.append(dict(code=code,rawHex=raw[off:off+width].hex(),unicode=mapping.get(code),gid=gid,glyph=glyph,fontAdvanceUnits=ft['hmtx'].metrics[glyph][0] if glyph else None))
  font_evidence[str(key)]['encodedGlyphs']=encoded
  if ft:ft.close()
 rows.append(dict(fontEvidence=font_evidence,file=str(p),hash=hashlib.sha256(p.read_bytes()).hexdigest(),producer=reader.metadata.producer,rawContent=reader.pages[0].get_contents().get_data().decode("latin1"),operators=arrays,lines=lines));
(E/'word-spacing-analysis.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');w.close()
