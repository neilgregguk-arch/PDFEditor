"""Phase 1 only: reproducible PDF fixtures, real edits, reopened evidence and raster comparisons."""
from pathlib import Path
import argparse, ctypes, hashlib, importlib.metadata, json, platform, shutil, time, io, subprocess, tempfile
import numpy as np
import pikepdf
import pymupdf as fitz
import pypdfium2 as pdfium
import pypdfium2.raw as raw
from PIL import Image, ImageDraw, ImageChops
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import reportlab

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output' / 'pdf'
ORIG = OUT / 'originals'
EDIT = OUT / 'edited'
EVID = ROOT / 'results'
PARA = 'This paragraph contains blue water beside the quiet harbour.'
LONG = 'a substantially longer replacement phrase which needs several lines'

def sha(data): return hashlib.sha256(data).hexdigest()
def json_default(value):
    if isinstance(value,(fitz.Rect,fitz.Point,fitz.Quad)): return list(value)
    if isinstance(value,bytes): return value.hex()
    raise TypeError(type(value).__name__)
def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True, default=json_default), encoding='utf-8')

def create_samples():
    ORIG.mkdir(parents=True, exist_ok=True)
    assets = ROOT / 'assets'; assets.mkdir(exist_ok=True)
    font_dir = Path(reportlab.__file__).parent / 'fonts'
    for name in ['Vera.ttf', 'bitstream-vera-license.txt']:
        src = font_dir / name
        if src.exists() and not (assets/name).exists(): shutil.copyfile(src, assets/name)
    pdfmetrics.registerFont(TTFont('VeraSubset', str(assets/'Vera.ttf')))
    im = Image.new('RGB', (300, 170), '#d9e5e8'); draw = ImageDraw.Draw(im)
    draw.rectangle((35, 40, 265, 130), fill='#264b5d'); draw.ellipse((110, 30, 190, 110), fill='#d4ac66')
    im.save(assets/'diagram.png')
    def make(name, body):
        path = ORIG/name
        if path.exists(): return # immutable fixture after first creation
        c = canvas.Canvas(str(path), pagesize=(612,792), invariant=1, pageCompression=1)
        c.setTitle('Phase 1 reproducible fixture: '+name); c.setAuthor('PDF Editor feasibility')
        c.setSubject('Offline synthetic test, no private data')
        body(c); c.save()
    def title(c, s):
        c.setFillColorRGB(.1,.2,.3); c.setFont('Helvetica-Bold',20); c.drawString(50,742,s)
        c.setFillColorRGB(0,0,0)
    def basic(c):
        title(c,'Basic text replacement')
        c.setFont('Helvetica',12); c.setFillColorRGB(.1,.25,.45)
        c.drawString(50,680,PARA)
        c.setFillColorRGB(0,0,0)
        c.drawString(50,640,'A second paragraph stays at its original coordinates.')
        c.drawString(50,620,'PDF lines have positions; paragraphs need not have semantics.')
        c.drawString(50,580,'A third paragraph verifies untouched text after saving.')
        c.textAnnotation('Keep this annotation',(500,700,520,720))
        c.showPage(); title(c,'Untouched second page'); c.setFont('Courier',12)
        c.drawString(50,680,'This entire page must remain visually identical.')
    make('basic.pdf',basic)
    def expansion(c):
        title(c,'Expansion and controlled reflow')
        c.setFont('Helvetica',12); c.drawString(50,680,'A brief note ends here.')
        c.setStrokeColorRGB(.8,.2,.2); c.rect(50,642,310,55)
        c.setFont('Helvetica-Bold',11); c.drawString(365,680,'NEIGHBOUR - DO NOT MOVE')
        c.setFont('Helvetica',12); c.drawString(50,600,'Fixed content below the allowed paragraph region.')
    make('expansion.pdf',expansion)
    def complex_body(c):
        title(c,'Complex formatting and integrity')
        for font,size,col,y,s in [
            ('Helvetica-Bold',15,(.1,.2,.6),690,'BOLD heading'),
            ('Times-Italic',13,(.65,.1,.15),655,'Italic sentence stays elegant.'),
            ('Courier',10,(.1,.4,.2),625,'Monospaced reference: AB-123'),
            ('VeraSubset',14,(.3,.1,.5),590,'Subset cafe')]:
            c.setFont(font,size); c.setFillColorRGB(*col); c.drawString(50,y,s)
        c.setFillColorRGB(0,0,0); c.setStrokeColorRGB(.2,.2,.2)
        for y in [440,480,520]: c.line(50,y,350,y)
        for x in [50,200,350]: c.line(x,440,x,520)
        c.setFont('Helvetica',12)
        for x,y,s in [(60,495,'Item'),(210,495,'Value'),(60,455,'Widget'),(210,455,'125.00')]: c.drawString(x,y,s)
        c.drawImage(str(assets/'diagram.png'),390,440,width=170,height=96)
        c.setFont('Times-Roman',11); c.drawString(50,405,'Text sits below the table and beside a positioned image.')
        c.textAnnotation('Retain this note',(530,690,550,710))
        c.linkURL('https://example.invalid/fixture',(50,380,220,395),relative=0)
        c.showPage(); title(c,'Integrity control page')
        c.drawImage(str(assets/'diagram.png'),50,500,width=300,height=170)
    make('complex.pdf',complex_body)
    # A real raster-only page, then the same kind of image with a digital caption.
    scan = Image.new('RGB',(1224,1584),'white'); sd=ImageDraw.Draw(scan)
    sd.text((100,180),'SCANNED PAGE - text exists only in pixels',fill='black',font_size=38)
    sd.text((100,260),'OCR is deliberately not run in Phase 1.',fill='black',font_size=32)
    scan.save(assets/'scan.png')
    def scanned(c): c.drawImage(str(assets/'scan.png'),0,0,width=612,height=792)
    make('scanned.pdf',scanned)
    def mixed(c):
        scanned(c); c.setFont('Helvetica',12); c.drawString(50,60,'Digital caption: blue water')
    make('mixed.pdf',mixed)
    # Nonempty XMP / bookmarks / annotations, cropped and rotated control page.
    integrity_path=ORIG/'integrity.pdf'
    if not integrity_path.exists():
        buffer=io.BytesIO(); c=canvas.Canvas(buffer,pagesize=(612,792),invariant=1)
        c.setTitle('Save integrity control'); c.setAuthor('PDF Editor feasibility')
        complex_body(c); c.save()
        with fitz.open(stream=buffer.getvalue(),filetype='pdf') as d:
            d.set_xml_metadata('<?xpacket begin=""?><x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:description>Integrity fixture XMP</dc:description></rdf:Description></rdf:RDF></x:xmpmeta><?xpacket end="w"?>')
            d.set_toc([[1,'Edited page',1],[1,'Rotated untouched control',2]])
            d[1].set_cropbox(fitz.Rect(20,20,592,772)); d[1].set_rotation(90)
            d.save(integrity_path)

def analyze(path):
    d=fitz.open(path); pages=[]
    for p in d:
        spans=[dict(s, direction=list(line['dir'])) for b in p.get_text('dict')['blocks'] if b['type']==0 for line in b['lines'] for s in line['spans']]
        fonts=[]
        for f in p.get_fonts(full=True):
            name,ext,typ,data=d.extract_font(f[0])
            fonts.append({'resource':f[4],'basefont':f[3],'type':f[2], 'encoding':f[5], 'embedded':bool(data), 'subset':len(f[3].split('+')[0])==6 and '+' in f[3], 'program_sha256':sha(data) if data else None})
        images=[{'bbox':list(i['bbox']),'width':i['width'],'height':i['height'],'digest':i['digest'].hex()} for i in p.get_image_info(hashes=True)]
        coverage=sum(fitz.Rect(i['bbox']).get_area() for i in images)/p.rect.get_area()
        text=p.get_text(); kind='digital-text' if text.strip() else 'no-text-no-image'
        if not text.strip() and coverage>.8: kind='scan-candidate'
        elif text.strip() and coverage>.8: kind='mixed-or-OCR-candidate'
        limitations=['No inferred paragraph ownership or automatic safe reflow']
        if any(f['subset'] for f in fonts): limitations.append('Subset font: new glyph coverage must be checked; font name alone is insufficient')
        if not text.strip(): limitations.append('No extractable text: OCR or vector analysis required before text editing')
        if coverage>.8 and text.strip(): limitations.append('Large image plus text may be OCR, mixed content, or a background; heuristic only')
        pages.append({'number':p.number+1,'dimensions':list(p.rect),'mediabox':list(p.mediabox),'cropbox':list(p.cropbox),'rotation':p.rotation,'text_extractable':bool(text.strip()),'text':text,'spans':spans,'fonts':fonts,'images':images,'classification':kind,'image_coverage_sum':coverage,'limitations':limitations,'annotations':[{'type':a.type[1],'rect':list(a.rect),'info':a.info} for a in p.annots() or []], 'links':p.get_links(),'drawing_count':len(p.get_drawings())})
    result={'file':str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),'sha256':sha(path.read_bytes()),'page_count':len(d),'metadata':d.metadata,'xml_metadata':d.get_xml_metadata(),'toc':d.get_toc(),'pages':pages}
    d.close(); return result

def operand_edit(src,dst,old,new,compensate=False,fix_metadata=False):
    """Deliberately restricted: known single-byte fixture strings in Tj/TJ only."""
    count=0
    with pikepdf.open(src) as d:
        for p in d.pages:
            instructions=[]
            for operands,op in pikepdf.parse_content_stream(p):
                if str(op) in ('Tj','TJ'):
                    strings=[operands[0]] if str(op)=='Tj' else list(operands[0])
                    for obj in strings:
                        if isinstance(obj,pikepdf.String) and old.encode('ascii') in bytes(obj):
                            count+=bytes(obj).count(old.encode('ascii'))
                            # Replace the operand object, not its serialized source bytes.
                            repl=pikepdf.String(bytes(obj).replace(old.encode('ascii'),new.encode('ascii')))
                            if str(op)=='Tj' and compensate:
                                prefix,suffix=bytes(obj).split(old.encode('ascii'))
                                delta=(pdfmetrics.stringWidth(new,'Helvetica-Bold',15)-pdfmetrics.stringWidth(old,'Helvetica-Bold',15))*1000/15
                                operands=[pikepdf.Array([pikepdf.String(prefix+new.encode('ascii')),delta,pikepdf.String(suffix)])]
                                op=pikepdf.Operator('TJ')
                            elif str(op)=='Tj': operands[0]=repl
                            else:
                                for j,v in enumerate(operands[0]):
                                    if v is obj or v==obj: operands[0][j]=repl
                instructions.append((operands,op))
            p.Contents=d.make_stream(pikepdf.unparse_content_stream(instructions))
        if count!=1: raise ValueError(f'Expected unique encoded occurrence, got {count}')
        d.save(dst,fix_metadata_version=fix_metadata)
    return {'method':'content-operand rewrite','encoded_occurrences':count,'advance_compensated':compensate,'fix_metadata_version':fix_metadata}

def span_at(p,rect):
    return next(s for b in p.get_text('dict')['blocks'] if b['type']==0 for l in b['lines'] for s in l['spans'] if fitz.Rect(s['bbox']).contains(rect))

def remove_reinsert(src,dst,old,new,reflow=False):
    d=fitz.open(src); p=d[0]; r=p.search_for(old)[0]; s=span_at(p,r)
    origin=(r.x0,s['origin'][1]); color=tuple(((s['color']>>v)&255)/255 for v in [16,8,0])
    p.add_redact_annot(r,fill=False); p.apply_redactions(images=0,graphics=0)
    if reflow:
        # Known fixture-owned complete paragraph area, not reconstructed arbitrary layout.
        value=p.insert_textbox(fitz.Rect(50,95,355,150),new,fontname='helv',fontsize=s['size'],color=color)
        if value<0: raise ValueError('Replacement does not fit known paragraph box')
    else: value=p.insert_text(origin,new,fontname='helv',fontsize=s['size'],color=color)
    d.save(dst,garbage=4,deflate=True); d.close()
    return {'method':'physical removal plus new text insertion','api_return':value,'automatic_reflow':False,'known_paragraph_box':reflow}

def pdfium_edit(src,dst):
    d=pdfium.PdfDocument(src); p=d[0]; tp=p.get_textpage(); changed=0
    for obj in p.get_objects():
        if obj.type != raw.FPDF_PAGEOBJ_TEXT: continue
        n=raw.FPDFTextObj_GetText(obj,tp,None,0)
        buf=ctypes.create_string_buffer(n)
        raw.FPDFTextObj_GetText(obj,tp,ctypes.cast(buf,ctypes.POINTER(ctypes.c_ushort)),n)
        text=buf.raw.decode('utf-16-le').rstrip('\0')
        if 'blue' in text:
            encoded=ctypes.create_string_buffer((text.replace('blue','glue')+'\0').encode('utf-16-le'))
            if not raw.FPDFText_SetText(obj,ctypes.cast(encoded,ctypes.POINTER(ctypes.c_ushort))): raise RuntimeError('PDFium rejected text')
            changed+=1
    if changed!=1: raise ValueError(f'Expected one PDFium text object: {changed}')
    p.gen_content(); d.save(dst); d.close()
    return {'method':'PDFium existing text object FPDFText_SetText','objects_changed':changed}

def render(path,engine,index):
    if engine=='poppler':
        with tempfile.TemporaryDirectory(prefix='pdf-phase1-') as folder:
            prefix=Path(folder)/'page'
            subprocess.run(['pdftoppm','-r','144','-f',str(index+1),'-l',str(index+1),'-singlefile','-png',str(path),str(prefix)],check=True,capture_output=True)
            with Image.open(prefix.with_suffix('.png')) as im: return im.convert('RGB').copy()
    if engine=='mupdf':
        with fitz.open(path) as d:
            pix=d[index].get_pixmap(matrix=fitz.Matrix(2,2),alpha=False)
            return Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    d=pdfium.PdfDocument(path); p=d[index]; bitmap=p.render(scale=2,draw_annots=True)
    im=bitmap.to_pil().convert('RGB').copy(); bitmap.close(); p.close(); d.close(); return im

def compare(src,dst,regions,name):
    before,after=analyze(src),analyze(dst); diffs={}
    for engine in ['mupdf','pdfium']+(['poppler'] if shutil.which('pdftoppm') else []):
        metrics=[]
        for i in range(before['page_count']):
            a=render(src,engine,i); b=render(dst,engine,i)
            folder=EVID/'renders'/name/engine; folder.mkdir(parents=True,exist_ok=True)
            a.save(folder/f'p{i+1}-before.png'); b.save(folder/f'p{i+1}-after.png')
            delta=np.abs(np.array(a).astype(int)-np.array(b).astype(int)).max(axis=2)
            mask=np.zeros(delta.shape,dtype=bool)
            for r in regions if i==0 else []:
                x0,y0,x1,y1=r; mask[max(0,int(y0*2)-3):int(y1*2)+4,max(0,int(x0*2)-3):int(x1*2)+4]=True
            changed=delta>8
            vis=np.full((*delta.shape,3),255,dtype=np.uint8); vis[changed & mask]=[30,120,210]; vis[changed & ~mask]=[230,35,60]
            Image.fromarray(vis).save(folder/f'p{i+1}-diff.png')
            metrics.append({'page':i+1,'changed_pixels':int(changed.sum()),'outside_edit_pixels':int((changed & ~mask).sum()),'max_channel_delta':int(delta.max())})
        diffs[engine]=metrics
    def image_sigs(d): return [[(im['bbox'],im['digest']) for im in p['images']] for p in d['pages']]
    def font_sigs(d): return [[(f['basefont'],f['program_sha256']) for f in p['fonts']] for p in d['pages']]
    checks={'page_count':before['page_count']==after['page_count'], 'dimensions':[(p['dimensions'],p['mediabox'],p['cropbox'],p['rotation']) for p in before['pages']]==[(p['dimensions'],p['mediabox'],p['cropbox'],p['rotation']) for p in after['pages']], 'images':image_sigs(before)==image_sigs(after),'fonts_exact_inventory':font_sigs(before)==font_sigs(after),'annotations': [p['annotations'] for p in before['pages']]==[p['annotations'] for p in after['pages']],'metadata':before['metadata']==after['metadata'],'xml_metadata':before['xml_metadata']==after['xml_metadata'],'toc':before['toc']==after['toc'],'links':[[{k:v for k,v in l.items() if k!='xref'} for l in p['links']] for p in before['pages']]==[[{k:v for k,v in l.items() if k!='xref'} for l in p['links']] for p in after['pages']]}
    return before,after,{'integrity':checks,'visual':diffs}

def run():
    start=time.perf_counter(); create_samples(); EDIT.mkdir(parents=True,exist_ok=True)
    hashes={p.name:sha(p.read_bytes()) for p in ORIG.glob('*.pdf')}; results=[]
    manifest=ORIG/'SHA256.json'
    if manifest.exists() and any(hashes.get(k)!=v for k,v in json.loads(manifest.read_text()).items()): raise ValueError('Original fixture manifest mismatch; originals must not be overwritten')
    if not manifest.exists(): dump(manifest,hashes)
    elif json.loads(manifest.read_text())!=hashes: dump(manifest,hashes)
    jobs=[
        ('e1_operand','basic.pdf','blue','glue','operand'),
        ('e1_pdfium','basic.pdf','blue','glue','pdfium'),
        ('e1_remove_reinsert','basic.pdf','blue','glue','redact'),
        ('e2_overflow','expansion.pdf','brief note',LONG,'operand'),
        ('e2_controlled_reflow','expansion.pdf','A brief note ends here.','A '+LONG+' ends here.','reflow'),
        ('e3_bold','complex.pdf','BOLD','GOLD','operand'),
        ('e3_bold_compensated','complex.pdf','BOLD','GOLD','compensate'),
        ('e3_italic','complex.pdf','elegant','refined','operand'),
        ('e3_table','complex.pdf','125.00','175.00','operand'),
        ('e3_subset','complex.pdf','cafe','face','operand'),
        ('e4_integrity','integrity.pdf','125.00','175.00','operand'),
        ('e4_default_metadata','integrity.pdf','125.00','175.00','default_metadata'),
        ('e5_mixed_edit','mixed.pdf','blue','glue','operand'),
    ]
    for name,file,old,new,method in jobs:
        src=ORIG/file; dst=EDIT/(name+'.pdf')
        with fitz.open(src) as d: regions=[list(r) for r in d[0].search_for(old)]
        if method=='reflow': regions=[[49,94,356,151]]
        begin=time.perf_counter()
        if method in ('operand','compensate','default_metadata'): info=operand_edit(src,dst,old,new,method=='compensate',method=='default_metadata')
        elif method=='pdfium': info=pdfium_edit(src,dst)
        else: info=remove_reinsert(src,dst,old,new,method=='reflow')
        edit_ms=(time.perf_counter()-begin)*1000
        before,after,evidence=compare(src,dst,regions,name)
        with pikepdf.open(dst) as q:
            syntax=q.check_pdf_syntax()
            strings=[bytes(s) for p in q.pages for operands,op in pikepdf.parse_content_stream(p) if str(op) in ('Tj','TJ') for s in ([operands[0]] if str(op)=='Tj' else operands[0]) if isinstance(s,pikepdf.String)]
        independent=pdfium.PdfDocument(dst); pdfium_text='\n'.join(independent[i].get_textpage().get_text_range() for i in range(len(independent))); independent.close()
        text='\n'.join(p['text'] for p in after['pages'])
        # Wrapped text normalizes whitespace for verification.
        norm=lambda s:' '.join(s.split())
        verification={'old_absent_mupdf':old not in text,'new_present_mupdf':norm(new) in norm(text),'old_absent_pdfium':old not in pdfium_text,'new_present_pdfium':norm(new) in norm(pdfium_text),'old_absent_text_operands':not any(old.encode('ascii') in s for s in strings),'syntax_warnings':syntax}
        if method!='reflow':
            with fitz.open(src) as a, fitz.open(dst) as b:
                oldr=a[0].search_for(old)[0]; newrs=b[0].search_for(new)
                os=span_at(a[0],oldr); ns=span_at(b[0],newrs[0])
                verification['style']={'font_before':os['font'],'font_after':ns['font'],'size_before':os['size'],'size_after':ns['size'],'color_before':os['color'],'color_after':ns['color'],'origin_before':[oldr.x0,os['origin'][1]],'origin_after':[newrs[0].x0,ns['origin'][1]]}
        row={'id':name,'source':file,'output':str(dst.relative_to(ROOT)),'old':old,'new':new,'regions':regions,'edit_save_ms':round(edit_ms,3),**info,**evidence,'verification':verification}
        dump(EVID/'diagnostics'/(name+'-before.json'),before); dump(EVID/'diagnostics'/(name+'-after.json'),after)
        dump(EVID/(name+'.json'),row); results.append(row)
    # Explicit refused operations still produce an unchanged candidate and evidence.
    for name,file,reason in [('e2_rejected_expansion','expansion.pdf','Long replacement exceeds original phrase width; no paragraph ownership known'),('e3_rejected_glyph','complex.pdf','U+2603 is absent from embedded subset cmap; no silent fallback'),('e5_scan_no_edit','scanned.pdf','No extractable text; scan pixels are not native PDF text')]:
        src=ORIG/file; dst=EDIT/(name+'.pdf'); shutil.copyfile(src,dst)
        if name=='e3_rejected_glyph':
            from fontTools.ttLib import TTFont as FT
            import io
            with fitz.open(src) as d:
                f=next(f for f in d[0].get_fonts() if '+' in f[3]); data=d.extract_font(f[0])[3]
            font=FT(io.BytesIO(data)); assert all(0x2603 not in t.cmap for t in font['cmap'].tables)
        rejection_evidence={}
        if name=='e2_rejected_expansion':
            oldw=pdfmetrics.stringWidth('brief note','Helvetica',12); neww=pdfmetrics.stringWidth(LONG,'Helvetica',12)
            assert neww>oldw
            rejection_evidence={'original_width_pt':oldw,'replacement_width_pt':neww,'fits_original_width':neww<=oldw}
        elif name=='e3_rejected_glyph': rejection_evidence={'requested_codepoint':'U+2603','present_in_any_embedded_cmap':False}
        else: rejection_evidence={'text_extractable':analyze(src)['pages'][0]['text_extractable']}
        before,after,evidence=compare(src,dst,[],name)
        row={'id':name,'source':file,'output':str(dst.relative_to(ROOT)),'status':'refused','reason':reason,'evidence':rejection_evidence,'byte_identical':src.read_bytes()==dst.read_bytes(),**evidence}
        dump(EVID/'diagnostics'/(name+'-before.json'),before); dump(EVID/'diagnostics'/(name+'-after.json'),after); dump(EVID/(name+'.json'),row); results.append(row)
    for p in ORIG.glob('*.pdf'): dump(EVID/'diagnostics'/(p.stem+'-original.json'),analyze(p))
    current={p.name:sha(p.read_bytes()) for p in ORIG.glob('*.pdf')}
    poppler_version=subprocess.run(['pdftoppm','-v'],capture_output=True,text=True).stderr.splitlines()[0] if shutil.which('pdftoppm') else None
    summary={'platform':platform.platform(),'python':platform.python_version(),'harness_sha256':sha(Path(__file__).read_bytes()),'versions':{m:importlib.metadata.version(m) for m in ['pymupdf','pikepdf','pypdfium2','reportlab','Pillow','numpy','pypdf','fonttools']},'pdfium_build':str(pdfium.PDFIUM_INFO),'qpdf_version':pikepdf.__libqpdf_version__,'poppler_version':poppler_version,'render_scale':2,'diff_threshold':8,'mask_padding_pixels':3,'original_hashes_before':hashes,'original_hashes_after':current,'originals_unchanged':hashes==current,'experiments':results,'total_seconds':round(time.perf_counter()-start,2)}
    dump(EVID/'summary.json',summary)
    print(json.dumps({'originals_unchanged':summary['originals_unchanged'],'experiments':len(results),'total_seconds':summary['total_seconds'],'results':[{k:r[k] for k in ['id','integrity','visual'] } for r in results]},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('command',choices=['run','analyze']); parser.add_argument('pdf',nargs='?'); parser.add_argument('--output')
    a=parser.parse_args()
    if a.command=='run': run()
    else:
        if not a.pdf: parser.error('analyze requires a PDF path')
        result=analyze(Path(a.pdf).resolve())
        if a.output: dump(Path(a.output),result)
        else: print(json.dumps(result,indent=2,default=json_default))
