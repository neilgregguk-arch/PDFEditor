"""Development verification only; does not import or ship PyMuPDF."""
from pathlib import Path
import hashlib,json,subprocess,time,unittest,shutil,os
from pypdf import PdfReader
from PIL import Image
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EVID=ROOT/'evidence'; EVID.mkdir(exist_ok=True)
WORK=ROOT/'test-work'/('suite-'+str(time.time_ns()));WORK.mkdir(parents=True)
RUN=ROOT/'run'; ORIGINALS=RUN/'samples'

class Worker:
    def __init__(self):
        self.p=subprocess.Popen([str(RUN/'PdfWorker.exe')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8');self.rev=0
    def call(self,**kw):
        self.rev+=1;kw.update(Revision=self.rev,Work=str(WORK))
        self.p.stdin.write(json.dumps(kw)+'\n');self.p.stdin.flush()
        line=self.p.stdout.readline()
        if not line:raise RuntimeError('Worker exited: '+self.p.stderr.read())
        result=json.loads(line);assert result['Revision']==self.rev
        return result
    def close(self):self.p.stdin.close();self.p.wait(timeout=10)

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.w=Worker();cls.hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ORIGINALS.glob('*.pdf')};cls.outputs=[]
    @classmethod
    def tearDownClass(cls):
        cls.w.close();assert cls.hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ORIGINALS.glob('*.pdf')}
    def inspect(self,name='A-Simple',source=None):
        r=self.w.call(Command='inspect',Source=str(source or ORIGINALS/(name+'.pdf')));self.assertTrue(r['Ok'],r.get('Error'));return r['Data']
    def edit(self,name,text,destination=None,command='save',**extra):
        info=self.inspect(name);source=str(ORIGINALS/(name+'.pdf'));dest=destination or WORK/(name+'-'+str(self.w.rev)+'.pdf')
        r=self.w.call(Command=command,Source=source,ExpectedHash=info['Hash'],Text=text,Destination=str(dest),**extra)
        if r['Ok'] and r['Data']['Safe'] and command=='save':
            record={'case':name,'source':source,'destination':str(dest),'draft':text,'result':r['Data']};self.outputs.append(record)
        return r
    def success(self,r):
        self.assertTrue(r['Ok'],r.get('Error'));self.assertTrue(r['Data']['Safe'],r['Data']['Diagnostic']);return r['Data']
    def test_A_actual_pdf_and_glyph_mapping(self):
        d=self.inspect();self.assertIsNotNone(d['Region']);self.assertEqual(len(d['Glyphs']),len(d['Region']['OriginalText']));self.assertEqual([g['Index'] for g in d['Glyphs']],list(range(len(d['Glyphs']))));self.assertTrue(Path(d['Image']).exists());self.assertTrue(Path(d['CleanImage']).exists())
    def test_A_successful_region_edit(self):
        r=self.success(self.edit('A-Simple','A genuinely changed paragraph.'))
        text=PdfReader(r['Destination']).pages[0].extract_text();self.assertIn('A genuinely changed paragraph.',text);self.assertNotIn('Edit this original paragraph directly on the page.',text)
        self.assertEqual(r['Verification']['outsidePixels144Dpi'],0);self.assertEqual(r['Verification']['maxNeighbourGeometryShiftPt'],0);self.assertTrue(r['Verification']['fontProgramPreserved'])
    def test_B_longer_wraps(self):
        draft=('Longer replacement text wraps into several lines without changing the protected reference. '*5).strip();r=self.success(self.edit('B-Longer',draft));lines=r['Verification']['layout']['Lines'];self.assertGreater(len(lines),3);self.assertEqual(''.join(lines),draft);self.assertIn(' '.join(draft.split()),' '.join(PdfReader(r['Destination']).pages[0].extract_text().split()))
    def test_C_unsafe_expansion_rejected(self):
        draft='All of this draft remains available. '*30;dest=WORK/'overflow-not-saved.pdf';r=self.edit('C-Restricted',draft,destination=dest);self.assertTrue(r['Ok']);self.assertFalse(r['Data']['Safe']);self.assertIn('Unsafe expansion',r['Data']['Diagnostic']);self.assertFalse(dest.exists())
    def test_C_actual_neighbour_collision_preflight(self):
        source=WORK/'collision.pdf';shutil.copyfile(ORIGINALS/'C-Restricted.pdf',source);region=json.loads((ORIGINALS/'C-Restricted.pdf.region.json').read_text());region['SafeBottom']=600;(Path(str(source)+'.region.json')).write_text(json.dumps(region));info=self.inspect(source=source)
        r=self.w.call(Command='save',Source=str(source),ExpectedHash=info['Hash'],Text='This will eventually meet the neighbour. '*15,Destination=str(WORK/'should-not-exist.pdf'));self.assertTrue(r['Ok']);self.assertFalse(r['Data']['Safe']);self.assertIn('collision',r['Data']['Diagnostic']);self.assertFalse((WORK/'should-not-exist.pdf').exists())
    def test_D_missing_glyph_rejected(self):
        r=self.edit('D-Font','Retain my snowman \u2603 draft.');self.assertTrue(r['Ok']);self.assertFalse(r['Data']['Safe']);self.assertIn('U+2603',r['Data']['Diagnostic'])
    def test_G_original_cannot_be_overwritten(self):
        src=ORIGINALS/'A-Simple.pdf';before=src.read_bytes();r=self.edit('A-Simple','Changed text.',destination=src);self.assertFalse(r['Ok']);self.assertIn('original',r['Error']);self.assertEqual(before,src.read_bytes())
    def test_G_existing_destination_unchanged(self):
        dest=WORK/'existing.pdf';dest.write_bytes(b'keep this existing file');r=self.edit('A-Simple','Changed text.',destination=dest);self.assertFalse(r['Ok']);self.assertEqual(dest.read_bytes(),b'keep this existing file')
    def test_G_locked_destination_unchanged(self):
        dest=WORK/'locked.pdf'
        with dest.open('wb') as locked:
            locked.write(b'locked destination');locked.flush();r=self.edit('A-Simple','Changed text.',destination=dest);self.assertFalse(r['Ok'])
        self.assertEqual(dest.read_bytes(),b'locked destination')
    def test_G_stale_source_hash_rejected(self):
        r=self.w.call(Command='preview',Source=str(ORIGINALS/'A-Simple.pdf'),ExpectedHash='0'*64,Text='Changed text.');self.assertFalse(r['Ok']);self.assertIn('Source changed',r['Error'])
    def test_G_append_preserves_legitimate_original_phrase_only_once(self):
        original=self.inspect()['Region']['OriginalText'];r=self.success(self.edit('A-Simple',original+' Added text wraps when necessary.'));t=PdfReader(r['Destination']).pages[0].extract_text();self.assertEqual(t.count(original),1);self.assertTrue(r['Verification']['originalTextIntentionallyRetainedInDraft']);self.assertEqual(r['Verification']['originalObjectsRemoved'],1)
    def test_G_empty_deletion_is_real(self):
        r=self.success(self.edit('A-Simple',''));text=PdfReader(r['Destination']).pages[0].extract_text();self.assertNotIn('Edit this original paragraph',text);self.assertEqual(r['Verification']['newTextObjects'],0)
    def test_G_explicit_linebreaks(self):
        r=self.success(self.edit('A-Simple','First replacement line.\n\nA second paragraph line.'));self.assertEqual(r['Verification']['layout']['Lines'],['First replacement line.','','A second paragraph line.'])
    def test_G_long_word_soft_wrap(self):
        draft='LongUnbrokenWord'*20;r=self.success(self.edit('A-Simple',draft));self.assertEqual(''.join(r['Verification']['layout']['Lines']),draft)
    def test_noop_is_not_reported_as_saved_edit(self):
        text=self.inspect()['Region']['OriginalText'];r=self.edit('A-Simple',text);self.assertTrue(r['Ok']);self.assertFalse(r['Data']['Safe']);self.assertIn('No text changes',r['Data']['Diagnostic'])
    def test_manifestless_supported_copy_is_discovered(self):
        # Phase 3 intentionally superseded this manifest requirement; frozen evidence retained.
        source=WORK/'unknown.pdf';shutil.copyfile(ORIGINALS/'A-Simple.pdf',source);d=self.inspect(source=source);self.assertIsNotNone(d['Region']);self.assertTrue(Path(d['Image']).exists());self.assertEqual(d['Region']['Eligibility'],'Editable')
    def test_tampered_manifest_view_only(self):
        source=WORK/'tampered.pdf';shutil.copyfile(ORIGINALS/'A-Simple.pdf',source);region=json.loads((ORIGINALS/'A-Simple.pdf.region.json').read_text());region['OriginalLines']=['Wrong target'];Path(str(source)+'.region.json').write_text(json.dumps(region));d=self.inspect(source=source);self.assertIsNone(d['Region']);self.assertIn('mapping mismatch',d['Diagnostic'])
    def test_cross_language_revision_roundtrip(self):
        r=self.w.call(Command='inspect',Source=str(ORIGINALS/'A-Simple.pdf'));self.assertEqual(r['Revision'],self.w.rev)

class RecordedResult(unittest.TextTestResult):
    def __init__(self,*args,**kw):super().__init__(*args,**kw);self.rows=[]
    def startTest(self,test):self.started=time.perf_counter();super().startTest(test)
    def addSuccess(self,test):self.rows.append({'test':test.id(),'status':'pass','ms':round((time.perf_counter()-self.started)*1000,2)});super().addSuccess(test)
    def addFailure(self,test,err):self.rows.append({'test':test.id(),'status':'fail','error':str(err[1])});super().addFailure(test,err)
    def addError(self,test,err):self.rows.append({'test':test.id(),'status':'error','error':str(err[1])});super().addError(test,err)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests);result=unittest.TextTestRunner(verbosity=2,resultclass=RecordedResult).run(suite)
    (EVID/'engine-tests.json').write_text(json.dumps({'scope':'worker/backend, not GUI input','tests':result.testsRun,'passed':result.wasSuccessful(),'results':result.rows,'work':str(WORK),'source_hashes':Tests.hashes,'saved_outputs':Tests.outputs},indent=2))
    folder=EVID/'pdf';folder.mkdir(exist_ok=True)
    for sample in ORIGINALS.glob('*'):shutil.copyfile(sample,folder/sample.name)
    for name in ['A-Simple','B-Longer']:
        outputs=[r for r in Tests.outputs if r['case']==name and (r['case']!='A-Simple' or r['draft']=='A genuinely changed paragraph.')]
        if outputs:shutil.copyfile(outputs[0]['destination'],folder/(name+'-edited.pdf'))
    raise SystemExit(0 if result.wasSuccessful() else 1)
