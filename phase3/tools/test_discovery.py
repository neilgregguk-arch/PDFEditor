from pathlib import Path
import sys,json,time,unittest,hashlib,subprocess,shutil
sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_engine as base
from pypdf import PdfReader
ROOT=base.ROOT;OUT=ROOT/'evidence';CORPUS=base.RUN/'corpus'
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.w=base.Worker();cls.sources={str(p):basehash(p) for p in CORPUS.glob('*.pdf')};cls.saved=[];cls.observations=[]
 @classmethod
 def tearDownClass(cls):
  cls.w.close();assert cls.sources=={p:basehash(Path(p)) for p in cls.sources}
 def inspect(self,name,page=0,**kw):
  p=Path(name) if str(name).endswith('.pdf') else CORPUS/(name+'.pdf');start=time.perf_counter();r=self.w.call(Command='inspect',Source=str(p),Page=page,**kw);self.assertTrue(r['Ok'],r.get('Error'));d=r['Data'];self.observations.append(dict(source=str(p),page=page,ms=(time.perf_counter()-start)*1000,regions=d['Regions']));return d
 def region(self,d,prefix):return next(r for r in d['Regions'] if r['OriginalText'].startswith(prefix))
 def save(self,d,r,text,label):
  dest=OUT/(label+'.pdf')
  # Test-owned files only; fresh evidence destination on each execution.
  if dest.exists():dest=OUT/(label+'-'+str(time.time_ns())+'.pdf')
  result=self.w.call(Command='save',Source=d['Path'],ExpectedHash=d['Hash'],Page=d['Page'],RegionId=r['Id'],Text=text,Destination=str(dest));self.assertTrue(result['Ok'],result.get('Error'));v=result['Data'];self.assertTrue(v['Safe'],v['Diagnostic']);self.assertEqual(v['Verification']['outsidePixels144Dpi'],0);self.assertLessEqual(v['Verification']['maxNeighbourGeometryShiftPt'],.01);self.assertTrue(v['Verification']['fontProgramPreserved']);self.saved.append(dict(source=d['Path'],region=r,draft=text,destination=str(dest),verification=v['Verification']));return dest
 def test_01_letter_grouping(self):
  d=self.inspect('01-letter');r=self.region(d,'This ordinary');self.assertEqual(r['Eligibility'],'Editable');self.assertEqual(len(r['Objects']),2);self.assertEqual(len(d['Regions']),5);self.assertNotEqual(d['Regions'][0]['FontHash'],r['FontHash']);self.assertTrue(r['Glyphs']);self.assertTrue(r['Observed']);self.assertTrue(r['Inferred']);self.assertTrue(d['PageObjects'])
 def test_02_report_multiline_and_page_two(self):
  d=self.inspect('02-report');r=self.region(d,'A single');self.assertEqual(len(r['Objects']),3);self.assertEqual(d['PageCount'],2);self.assertEqual(self.inspect('02-report',page=1)['Page'],1);self.save(d,r,'A revised report preserves its neighbours and untouched second page.','report-edited')
 def test_03_regular_original_font_save(self):
  d=self.inspect('01-letter');self.save(d,self.region(d,'This ordinary'),'A revised letter uses the actual embedded font without replacement.','letter-edited')
 def test_04_bold_original_font_save(self):
  d=self.inspect('02-report');r=self.region(d,'Bold summary');self.assertTrue(any('weight:Bold' in x for x in r['Observed']));self.save(d,r,'Bold revised summary retains its original font.','bold-edited')
 def test_05_colour_and_size_save(self):
  d=self.inspect('02-report');r=self.region(d,'A blue note');self.assertEqual(r['FontSize'],10);self.assertGreater(r['B'],r['R']);self.save(d,r,'A revised blue note retains its colour and size.','colour-edited')
 def test_06_independent_generator_save(self):
  d=self.inspect('09-mupdf-letter');self.save(d,self.region(d,'This paragraph'),'An independent PDF now contains a genuine replacement.','mupdf-edited')
 def test_07_second_generation_same_paragraph(self):
  d=self.inspect('01-letter');first=('First generation edit survives. '+('This extended sentence wraps into a discovered paragraph. '*3)).rstrip()
  one=self.save(d,self.region(d,'This ordinary'),first,'generation-one');self.assertFalse(Path(str(one)+'.region.json').exists());again=self.inspect(one);r=self.region(again,'First generation');self.assertEqual(r['Eligibility'],'Editable');second=first+' Second generation edit also survives.';two=self.save(again,r,second,'generation-two');text=' '.join(PdfReader(two).pages[0].extract_text().split());self.assertIn('First generation edit survives.',text);self.assertIn('Second generation edit also survives.',text);self.assertNotIn('This ordinary digital letter',text);final=self.inspect(two);self.assertEqual(self.region(final,'First generation')['Eligibility'],'Editable')
 def test_08_adjacent_labels_not_joined(self):
  d=self.inspect('03-adjacent');self.assertEqual(len(d['Regions']),3);self.assertTrue(all(r['Eligibility']!='Editable' for r in d['Regions'][:2]));self.assertEqual(d['Regions'][2]['Eligibility'],'Editable')
 def test_09_columns_not_joined(self):
  d=self.inspect('04-two-columns');self.assertEqual(len(d['Regions']),10);self.assertTrue(all(r['Eligibility']!='Editable' and len(r['Objects'])==1 for r in d['Regions']))
 def test_10_table_refused(self):
  d=self.inspect('05-table');self.assertTrue(all(r['Eligibility']!='Editable' for r in d['Regions']));self.assertTrue(any(o['Type']==2 for o in d['PageObjects']))
 def test_11_ambiguous_short_lines_limited(self):
  d=self.inspect('06-ambiguous');self.assertEqual(len(d['Regions']),2);self.assertTrue(all(r['Eligibility']=='Limited' for r in d['Regions']));self.assertTrue(all('AMBIGUOUS_SHORT_LINE_PARAGRAPH_BOUNDARY' in r['Reasons'] for r in d['Regions']))
 def test_12_transform_refused(self):self.assertIn('UNSUPPORTED_TRANSFORM',self.inspect('07-rotated')['Regions'][0]['Reasons'])
 def test_13_font_substitution_refused(self):self.assertIn('FONT_NOT_EMBEDDED',self.inspect('08-nonembedded')['Regions'][0]['Reasons'])
 def test_14_subset_and_word_restrictions_explicit(self):
  for name in ['10-mupdf-subset','11-word-letter']:
   d=self.inspect(name);self.assertTrue(d['Regions']);self.assertTrue(all(r['Eligibility']!='Editable' and r['Reasons'] for r in d['Regions']))
 def test_15_overflow_no_destination(self):
  d=self.inspect('01-letter');r=self.region(d,'This ordinary');dest=base.WORK/'unsafe.pdf';a=self.w.call(Command='save',Source=d['Path'],ExpectedHash=d['Hash'],RegionId=r['Id'],Text='Retain the full unsafe draft. '*200,Destination=str(dest));self.assertTrue(a['Ok']);self.assertFalse(a['Data']['Safe']);self.assertFalse(dest.exists())
 def test_16_missing_glyph_no_destination(self):
  d=self.inspect('01-letter');r=self.region(d,'This ordinary');a=self.w.call(Command='preview',Source=d['Path'],ExpectedHash=d['Hash'],RegionId=r['Id'],Text='Keep my snowman \u2603.');self.assertTrue(a['Ok']);self.assertFalse(a['Data']['Safe']);self.assertIn('U+2603',a['Data']['Diagnostic'])
 def test_17_unsupported_or_unknown_region_cannot_commit(self):
  for name,id in [('06-ambiguous','p0-o0'),('01-letter','invented')]:
   d=self.inspect(name);a=self.w.call(Command='preview',Source=d['Path'],ExpectedHash=d['Hash'],RegionId=id,Text='Must not save.');self.assertFalse(a['Ok'])
 def test_18_cache_and_fingerprint(self):
  first=self.inspect('01-letter');again=self.inspect('01-letter');self.assertEqual(first['Hash'],again['Hash']);self.assertEqual(first['Regions'],again['Regions']);self.assertIn(first['Hash'][:16],first['Image'])
 def test_19_images_are_observed_and_block_overlap(self):
  d=self.inspect('12-image-overlap');self.assertTrue(any(o['Type']==3 for o in d['PageObjects']));self.assertTrue(all(r['Eligibility']!='Editable' for r in d['Regions']))
 def test_20_visual_order_beats_object_order(self):
  d=self.inspect('13-shuffled-order');self.assertEqual(len(d['Regions']),1);r=d['Regions'][0];self.assertEqual(r['Eligibility'],'Editable');self.assertEqual(r['Objects'],[1,2,0]);self.assertTrue(r['OriginalText'].startswith('A geometrically'));self.save(d,r,'A changed geometrically grouped paragraph survives export.','shuffled-edited')
 def test_21_annotations_block_commit(self):
  d=self.inspect('14-annotation');self.assertTrue(all(r['Eligibility']=='View Only' for r in d['Regions']));self.assertTrue(any('ANNOTATION' in reason for r in d['Regions'] for reason in r['Reasons']))
 def test_22_explicit_character_spacing_blocked(self):
  d=self.inspect('15-letter-spacing');self.assertIn('NON_NATURAL_GLYPH_SPACING',d['Regions'][0]['Reasons'])
def basehash(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 with (OUT/'discovery-tests.log').open('w') as log:r=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=base.RecordedResult).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 (OUT/'discovery-tests.json').write_text(json.dumps(dict(tests=r.testsRun,success=r.wasSuccessful(),results=r.rows,sources=Tests.sources,saved=Tests.saved,observations=Tests.observations),indent=2));print('tests',r.testsRun,'failures',len(r.failures),'errors',len(r.errors));print((OUT/'discovery-tests.log').read_text()[-5000:]);raise SystemExit(not r.wasSuccessful())
