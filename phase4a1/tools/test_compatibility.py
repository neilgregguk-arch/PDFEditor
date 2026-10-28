from pathlib import Path
import sys,json,time,unittest,hashlib,collections
sys.path.insert(0,str(Path(__file__).resolve().parent))
import test_engine as base
from pypdf import PdfReader
ROOT=base.ROOT;OUT=ROOT/'evidence';CORPUS=base.RUN/'font-corpus'
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.w=base.Worker();cls.sources={str(p):digest(p) for p in CORPUS.glob('*.pdf')};cls.saved=[];cls.calls=[]
 @classmethod
 def tearDownClass(cls):cls.w.close();assert all(digest(Path(p))==h for p,h in cls.sources.items())
 def inspect(self,name,source=None):
  start=time.perf_counter();r=self.w.call(Command='inspect',Source=str(source or CORPUS/(name+'.pdf')));self.assertTrue(r['Ok'],r.get('Error'));d=r['Data'];self.calls.append(dict(command='inspect',source=d['Path'],ms=(time.perf_counter()-start)*1000,regions=d['Regions']));return d
 def region(self,d):return d['Regions'][0]
 def edit(self,d,draft,label,save=True):
  dest=OUT/(label+'-'+str(time.time_ns())+'.pdf');start=time.perf_counter();r=self.w.call(Command='save' if save else 'preview',Source=d['Path'],ExpectedHash=d['Hash'],RegionId=self.region(d)['Id'],Text=draft,Destination=str(dest));self.calls.append(dict(command='save' if save else 'preview',ms=(time.perf_counter()-start)*1000));return r,dest
 def success(self,d,draft,label):
  r,dest=self.edit(d,draft,label);self.assertTrue(r['Ok'],r.get('Error'));v=r['Data'];self.assertTrue(v['Safe'],v['Diagnostic']);self.assertEqual(v['ProposedTextEligibility'],'Supported');self.assertEqual(v['ExportEligibility'],'Verified');self.assertEqual(v['Verification']['outsidePixels144Dpi'],0);self.assertLessEqual(v['Verification']['maxNeighbourGlyphShiftPt'],.01);self.assertTrue(v['Verification']['replacementGlyphsVerified']);self.assertIn(' '.join(draft.split()),' '.join(PdfReader(dest).pages[0].extract_text().split()));self.saved.append(dict(source=d['Path'],region=self.region(d),draft=draft,destination=str(dest),verification=v['Verification']));return dest
 def test_A_new_subset_activates_without_alphabet_coverage(self):
  d=self.inspect('A-subset-existing');r=self.region(d);self.assertEqual(r['StructuralEligibility'],'Editable');self.assertEqual(r['ProposedTextEligibility'],'DependsOnDraft');self.assertLess(sum(c['State']=='ExistingMappingVerified' for c in r['Characters']),20);self.assertTrue(r['Glyphs'])
 def test_B_equal_width_existing_glyph_reordering(self):
  d=self.inspect('A-subset-existing');self.success(d,'face calm.','subset-equal-width')
 def test_C_longer_existing_glyphs_wrap(self):
  d=self.inspect('A-subset-existing');dest=self.success(d,('calm cafe. '*12).strip(),'subset-longer');self.assertGreater(len(self.saved[-1]['verification']['layout']['Lines']),1)
 def test_D_only_original_chars_reused(self):
  d=self.inspect('B-original-only');self.success(d,'facefaceface','original-only-reuse')
 def test_E_unavailable_glyph_rejected(self):
  d=self.inspect('A-subset-existing');r,dest=self.edit(d,'cafe Z','must-not-save');self.assertTrue(r['Ok']);v=r['Data'];self.assertFalse(v['Safe']);self.assertEqual(v['ProposedTextEligibility'],'Unsupported');self.assertEqual(v['ExportEligibility'],'Blocked');self.assertEqual(v['GlyphIssues'][0]['Unicode'],ord('Z'));self.assertFalse(dest.exists());self.assertIn('Your changes have been kept',v['Diagnostic'])
 def test_F_bold_subset_reused(self):
  d=self.inspect('C-subset-bold');self.success(d,'calm Bold.','subset-bold')
 def test_G_fragments_not_promoted(self):
  d=self.inspect('D-fragmented');self.assertTrue(all(r['Eligibility']!='Editable' for r in d['Regions'][:2]))
 def test_H_character_spacing_refused(self):self.assertIn('POSITION_FONT_METRIC_ROUNDING_UNSUPPORTED',self.region(self.inspect('E-character-spacing'))['Reasons'])
 def test_I_kerning_refused(self):self.assertIn('POSITION_FONT_METRIC_ROUNDING_UNSUPPORTED',self.region(self.inspect('F-kerning'))['Reasons'])
 def test_J_duplicate_unicode_safe_selected_mapping(self):
  d=self.inspect('G-duplicate-unicode');self.success(d,'face calm.','duplicate-mapping-safe')
 def test_K_wrong_unicode_not_promoted(self):
  d=self.inspect('H-wrong-unicode');self.assertNotEqual(self.region(d)['Eligibility'],'Editable');self.assertIn('INITIAL_OBJECT_RECONSTRUCTION_DIFFERS',self.region(d)['Reasons'])
 def test_L_missing_unicode_not_promoted(self):
  d=self.inspect('I-missing-unicode');self.assertNotEqual(self.region(d)['Eligibility'],'Editable');self.assertIn('INITIAL_OBJECT_RECONSTRUCTION_DIFFERS',self.region(d)['Reasons'])
 def test_M_word_positions_and_separate_spaces(self):
  d=self.inspect(None,source=base.RUN/'corpus/11-word-letter.pdf');r=self.region(d);self.assertEqual(r['Eligibility'],'Editable');self.assertEqual(r['Positioned']['CoexistingWhitespace'],[1,2,4,5,7]);self.success(d,'Phace 3 Office letter','word-compatibility-edit')
 def test_N_word_fonts_assessed_individually(self):
  for name in ['Word-Arial','Word-Calibri']:
   d=self.inspect(name);self.assertTrue(d['Regions']);self.assertTrue(all(r['Eligibility']=='Editable' and r['Positioned'] for r in d['Regions']))
  d=self.inspect('Word-Consolas');self.assertTrue(all(r['Eligibility']!='Editable' and r['Reasons'] for r in d['Regions']))
 def test_O_second_generation_subset_edit(self):
  d=self.inspect('A-subset-existing');one=self.success(d,'face calm.','subset-gen-one');again=self.inspect(None,source=one);self.assertEqual(self.region(again)['Eligibility'],'Editable');two=self.success(again,'face calm. cafe.','subset-gen-two');final=self.inspect(None,source=two);self.assertEqual(self.region(final)['Eligibility'],'Editable')
 def test_P_probes_removed_and_cache_stable(self):
  d=self.inspect('A-subset-existing');again=self.inspect('A-subset-existing');self.assertEqual(d['PageObjects'],again['PageObjects']);self.assertEqual(d['Regions'],again['Regions']);dest=self.success(d,'face calm.','probe-object-count');self.assertEqual(len(PdfReader(d['Path']).pages[0]['/Resources']['/Font']),len(PdfReader(dest).pages[0]['/Resources']['/Font']))
 def test_Q_unsafe_growth_not_weakened(self):
  d=self.inspect('A-subset-existing');r,dest=self.edit(d,'cafe calm. '*300,'overflow');self.assertTrue(r['Ok']);self.assertFalse(r['Data']['Safe']);self.assertFalse(dest.exists())
 def test_R_no_cmap_is_distinct_from_missing_subset_character(self):
  d=self.inspect(None,source=base.RUN/'corpus/10-mupdf-subset.pdf');self.assertTrue(any(c['State']=='UnicodeMappingMissing' for c in self.region(d)['Characters']))
 def test_S_new_partial_encoding_scenario(self):
  d=self.inspect('J-partial-encoding');self.assertEqual(self.region(d)['Eligibility'],'Editable');self.assertEqual(next(c for c in self.region(d)['Characters'] if c['Unicode']==90)['State'],'FontPresentEncodingUnavailable');self.success(d,'face calm.','new-partial-encoding-edit')
 def test_T_unmapped_existing_font_glyph_refused(self):
  d=self.inspect('J-partial-encoding');r,dest=self.edit(d,'cafe Z','unmapped-glyph');self.assertTrue(r['Ok']);self.assertFalse(r['Data']['Safe']);self.assertEqual(r['Data']['GlyphIssues'][0]['State'],'FontPresentEncodingUnavailable');self.assertFalse(dest.exists())
 def test_U_partial_encoding_second_generation(self):
  d=self.inspect('J-partial-encoding');one=self.success(d,'face calm.','new-partial-gen-one');again=self.inspect(None,source=one);self.assertEqual(self.region(again)['Eligibility'],'Editable');self.success(again,'face calm. cafe.','new-partial-gen-two')
 def test_V_frozen_phase3_refuses_new_scenario(self):
  previous=base.RUN
  try:
   base.RUN=ROOT.parent/'phase3/run';old=base.Worker();r=old.call(Command='inspect',Source=str(CORPUS/'J-partial-encoding.pdf'));old.close();self.assertTrue(r['Ok']);self.assertIsNone(r['Data']['Region']);self.assertIn('ORIGINAL_FONT_MAPPING_UNAVAILABLE',r['Data']['Regions'][0]['Reasons'])
  finally:base.RUN=previous
 def test_W_powerpoint_conservative_refusal(self):
  d=self.inspect('PowerPoint-Arial-subset');self.assertTrue(all(r['Eligibility']!='Editable' for r in d['Regions']));self.assertTrue(any('GRAPHIC_IMAGE_OR_TABLE_INTERSECTION' in r['Reasons'] for r in d['Regions']))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 with (OUT/'compatibility-tests.log').open('w') as log:r=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=base.RecordedResult).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 (OUT/'compatibility-tests.json').write_text(json.dumps(dict(tests=r.testsRun,success=r.wasSuccessful(),results=r.rows,sources=Tests.sources,saved=Tests.saved,calls=Tests.calls),indent=2));print((OUT/'compatibility-tests.log').read_text()[-5000:]);raise SystemExit(not r.wasSuccessful())
