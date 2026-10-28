"""Tests inspect saved outputs and negative controls, rather than API return codes."""
import json, tempfile, unittest
from pathlib import Path
from collections import Counter
import pymupdf as fitz
import pikepdf
from pypdf import PdfReader
import feasibility as f

class SavedEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary=json.loads((f.EVID/'summary.json').read_text())
        if cls.summary['harness_sha256']!=f.sha(Path(f.__file__).read_bytes()): raise ValueError('Evidence is stale: rerun the current harness')
        cls.rows={r['id']:r for r in cls.summary['experiments']}

    def test_originals_match_persistent_manifest(self):
        manifest=json.loads((f.ORIG/'SHA256.json').read_text())
        self.assertTrue(self.summary['originals_unchanged'])
        self.assertEqual(manifest,{p.name:f.sha(p.read_bytes()) for p in f.ORIG.glob('*.pdf')})

    def test_reopen_semantics_and_no_old_operands(self):
        for name,r in self.rows.items():
            if r.get('status')=='refused': continue
            with self.subTest(name=name):
                for key,value in r['verification'].items():
                    if key.startswith(('old_','new_')): self.assertTrue(value,key)
                self.assertEqual(r['verification']['syntax_warnings'],[])
                text=' '.join(' '.join(p.extract_text().split()) for p in PdfReader(f.ROOT/r['output']).pages)
                self.assertNotIn(r['old'],text)
                self.assertIn(' '.join(r['new'].split()),text)

    def test_core_save_integrity(self):
        for r in self.rows.values():
            with self.subTest(name=r['id']):
                for key in ['page_count','dimensions','images','annotations','metadata','xml_metadata','toc','links']:
                    if r['id']=='e4_default_metadata' and key=='xml_metadata':
                        self.assertFalse(r['integrity'][key]); continue
                    self.assertTrue(r['integrity'][key],key)

    def test_untouched_second_pages_are_pixel_identical(self):
        for r in self.rows.values():
            for engine,pages in r['visual'].items():
                for p in pages[1:]: self.assertEqual(p['changed_pixels'],0,(r['id'],engine))

    def test_safe_cases_have_no_outside_changes(self):
        for name in ['e1_operand','e1_pdfium','e1_remove_reinsert','e2_controlled_reflow','e3_bold_compensated','e3_table','e3_subset','e4_integrity','e5_mixed_edit']:
            for engine,pages in self.rows[name]['visual'].items():
                self.assertEqual(sum(p['outside_edit_pixels'] for p in pages),0,(name,engine))

    def test_known_overflow_and_advance_regressions_are_detected(self):
        for name in ['e2_overflow','e3_bold']:
            for engine,pages in self.rows[name]['visual'].items():
                self.assertGreater(pages[0]['outside_edit_pixels'],0,(name,engine))

    def test_font_size_color_and_anchor_preservation(self):
        for r in self.rows.values():
            if 'verification' not in r or 'style' not in r['verification']: continue
            s=r['verification']['style']
            with self.subTest(name=r['id']):
                for prop in ['font','size','color','origin']:
                    self.assertEqual(s[prop+'_before'],s[prop+'_after'],prop)

    def test_original_font_programs_preserved_by_operand_edits(self):
        for r in self.rows.values():
            if r.get('method')=='content-operand rewrite': self.assertTrue(r['integrity']['fonts_exact_inventory'],r['id'])

    def test_nonempty_integrity_features(self):
        a=json.loads((f.EVID/'diagnostics/e4_integrity-before.json').read_text())
        self.assertTrue(a['xml_metadata']); self.assertEqual(len(a['toc']),2)
        self.assertTrue(a['pages'][0]['annotations']); self.assertTrue(a['pages'][0]['links'])
        self.assertTrue(a['pages'][0]['images']); self.assertEqual(a['pages'][1]['rotation'],90)
        self.assertTrue(any(font['embedded'] for font in a['pages'][0]['fonts']))

    def test_refusals_are_byte_identical(self):
        rows=[r for r in self.rows.values() if r.get('status')=='refused']
        self.assertEqual(len(rows),3)
        for r in rows:
            self.assertEqual((f.ORIG/r['source']).read_bytes(),(f.ROOT/r['output']).read_bytes())
            self.assertTrue(r['evidence'])

    def test_reflow_is_multiline_and_inside_owned_box(self):
        with fitz.open(f.ROOT/self.rows['e2_controlled_reflow']['output']) as d:
            box=fitz.Rect(50,95,355,150)
            lines=[l for b in d[0].get_text('dict')['blocks'] if b['type']==0 for l in b['lines'] if box.intersects(fitz.Rect(l['bbox']))]
            self.assertGreaterEqual(len(lines),2)
            for l in lines: self.assertTrue(box.contains(fitz.Rect(l['bbox'])))
            neighbor=d[0].search_for('NEIGHBOUR - DO NOT MOVE')[0]
        with fitz.open(f.ORIG/'expansion.pdf') as d: self.assertEqual(neighbor,d[0].search_for('NEIGHBOUR - DO NOT MOVE')[0])

    def test_scan_and_mixed_are_heuristics(self):
        scan=f.analyze(f.ORIG/'scanned.pdf')['pages'][0]
        mixed=f.analyze(f.ORIG/'mixed.pdf')['pages'][0]
        self.assertEqual(scan['classification'],'scan-candidate')
        self.assertEqual(mixed['classification'],'mixed-or-OCR-candidate')
        self.assertFalse(scan['text_extractable']); self.assertTrue(mixed['text_extractable'])

    def test_overlay_cannot_pass_semantic_removal_check(self):
        # Deliberately deceptive visual technique, only a temporary negative control.
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'overlay.pdf'
            with fitz.open(f.ORIG/'basic.pdf') as d:
                p=d[0]; r=p.search_for('blue')[0]
                p.draw_rect(r,color=None,fill=(1,1,1)); p.insert_text((r.x0,112),'glue',fontsize=12)
                d.save(path)
            with fitz.open(path) as d:
                text=d[0].get_text()
                self.assertIn('blue',text); self.assertIn('glue',text)

    def test_untargeted_words_preserved(self):
        for r in self.rows.values():
            if r.get('status')=='refused': continue
            before=f.analyze(f.ORIG/r['source']); after=f.analyze(f.ROOT/r['output'])
            a=' '.join(p['text'] for p in before['pages']); b=' '.join(p['text'] for p in after['pages'])
            expected=Counter(a.replace(r['old'],r['new']).split())
            self.assertEqual(expected,Counter(b.split()),r['id'])

if __name__=='__main__': unittest.main(verbosity=2)
