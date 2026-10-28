# Phase 1 evidence index

All paths shown below are **repository-relative**. Links resolve from this handover directory. The consolidated report is self-contained; use these artifacts to independently verify implementation and measurements. Essential means required to verify the corresponding claim, rather than required to understand the report. No existing artifact was changed for this handover.

## 1. Core evidence and implementation

| Repository-relative path | Purpose | Experiment / area | Essential for verification? |
|---|---|---|---|
| [results/summary.json](../results/summary.json) | Authoritative retained run: versions, engine builds, source hashes, 16 cases, timings, integrity and raster metrics | All | Yes |
| [results/tests.json](../results/tests.json) | Machine-readable result: 14 passing tests; no errors/failures/skips | Testing | Yes, for recorded test status |
| [feasibility.py](../feasibility.py) | Actual fixture generator, three edit mechanisms, fixed-case refusals, diagnostic CLI and verification implementation | All | Yes |
| [test_feasibility.py](../test_feasibility.py) | What is asserted, expected failures, nine selected zero-outside cases and overlay control | Testing | Yes |
| [output/pdf/originals/SHA256.json](../output/pdf/originals/SHA256.json) | Six-original hash manifest | Source preservation | Yes |
| [requirements.txt](../requirements.txt) | Exact Python dependency closure | Reproduction / licensing | Yes, to reproduce environment |
| [run.ps1](../run.ps1) | Fail-fast original experiment/test/index execution sequence; writes existing outputs if run | Reproduction | Yes, to understand execution |
| [run_tests.py](../run_tests.py) | Test launcher that overwrites results/tests.json; intentionally not rerun during handover | Testing | Useful |
| [offline_check.py](../offline_check.py) | Python socket-refusal wrapper; does not sandbox native processes | Offline claim | Yes |
| [review_evidence.py](../review_evidence.py) | How contact sheets and local index were derived; no editing UI | Visual presentation | Useful |
| [test-results.log](../test-results.log) | Retained main-venv test names, status and 0.740 s duration | Testing | Yes, if auditing retained test execution |
| [clean-test-results.log](../clean-test-results.log) | Retained clean-venv 14-test result | Clean environment | Yes, for this claim |
| [clean-install.log](../clean-install.log) | Successful dependency installation into separate clean venv | Clean environment | Yes, for this claim |
| [run.log](../run.log) | Retained final experiment output, agrees with summary total 36.79 s | All | Useful; duplicates summary metrics |
| [results/cli-diagnostic-check.json](../results/cli-diagnostic-check.json) | Parseable diagnostic CLI output on integrity original | E5 | Useful |
| [results/INDEX.md](../results/INDEX.md) | Existing per-case findings and visual sheets | All | Useful navigation |
| [results/index.html](../results/index.html) | Existing static local review index; links to originals/candidates/metrics/renders | All | Useful navigation |

## 2. Original PDF corpus

These six originals are essential to the related before/after comparison. None is a customer document; all are synthetic.

| Repository-relative path | Purpose / contents | Experiment | Essential? |
|---|---|---|---|
| [output/pdf/originals/basic.pdf](../output/pdf/originals/basic.pdf) | Two pages, paragraphs, Base-14 fonts, colour, text note and untouched page | E1 | Yes |
| [output/pdf/originals/expansion.pdf](../output/pdf/originals/expansion.pdf) | One page, short sentence, fixed neighbour and paragraph reference area | E2 | Yes |
| [output/pdf/originals/complex.pdf](../output/pdf/originals/complex.pdf) | Two pages, bold/italic/monospace/subset fonts, table, images, note and link | E3 | Yes |
| [output/pdf/originals/integrity.pdf](../output/pdf/originals/integrity.pdf) | Two pages, nonempty XMP/bookmarks, note/link/images/subset font, cropped/rotated second page | E4 | Yes |
| [output/pdf/originals/mixed.pdf](../output/pdf/originals/mixed.pdf) | Page-sized raster plus visible digital caption | E5 | Yes |
| [output/pdf/originals/scanned.pdf](../output/pdf/originals/scanned.pdf) | Raster-only page with no extractable text; not an OCR test | E5 | Yes |

## 3. Candidate PDFs and per-case machine evidence

Every candidate listed is essential to independently verify that case. **Unsafe and unchanged-refusal candidates are evidence, not successful user-ready edits.** Each JSON file is essential for the recorded metrics. Candidate IDs map directly to section C of the consolidated report.

| Case / experiment | Candidate PDF (repository-relative) | Metrics JSON (repository-relative) | Purpose / outcome | Essential? |
|---|---|---|---|---|
| e1_operand / E1 | [output/pdf/edited/e1_operand.pdf](../output/pdf/edited/e1_operand.pdf) | [results/e1_operand.json](../results/e1_operand.json) | Direct encoded operand change; isolated appearance preserved | Yes |
| e1_pdfium / E1 | [output/pdf/edited/e1_pdfium.pdf](../output/pdf/edited/e1_pdfium.pdf) | [results/e1_pdfium.json](../results/e1_pdfium.json) | Existing PDFium line object changed; font inventory regenerated | Yes |
| e1_remove_reinsert / E1 | [output/pdf/edited/e1_remove_reinsert.pdf](../output/pdf/edited/e1_remove_reinsert.pdf) | [results/e1_remove_reinsert.json](../results/e1_remove_reinsert.json) | Physical removal/reinsertion; added font resource and reading-order change | Yes |
| e2_overflow / E2 | [output/pdf/edited/e2_overflow.pdf](../output/pdf/edited/e2_overflow.pdf) | [results/e2_overflow.json](../results/e2_overflow.json) | Deliberately unsafe expansion; real saved text overlaps neighbour | Yes |
| e2_controlled_reflow / E2 | [output/pdf/edited/e2_controlled_reflow.pdf](../output/pdf/edited/e2_controlled_reflow.pdf) | [results/e2_controlled_reflow.json](../results/e2_controlled_reflow.json) | Whole known sentence reconstructed into owned box; two lines | Yes |
| e3_bold / E3 | [output/pdf/edited/e3_bold.pdf](../output/pdf/edited/e3_bold.pdf) | [results/e3_bold.json](../results/e3_bold.json) | Unequal word advance moves following heading by about 0.840 pt | Yes |
| e3_bold_compensated / E3 | [output/pdf/edited/e3_bold_compensated.pdf](../output/pdf/edited/e3_bold_compensated.pdf) | [results/e3_bold_compensated.json](../results/e3_bold_compensated.json) | Known-font TJ spacing compensation protects following heading | Yes |
| e3_italic / E3 | [output/pdf/edited/e3_italic.pdf](../output/pdf/edited/e3_italic.pdf) | [results/e3_italic.json](../results/e3_italic.json) | Italic correction; period moves about -1.443 pt; one outside pixel in PDFium | Yes |
| e3_table / E3 | [output/pdf/edited/e3_table.pdf](../output/pdf/edited/e3_table.pdf) | [results/e3_table.json](../results/e3_table.json) | Equal-width numeric cell edit with nearby content preserved | Yes |
| e3_subset / E3 | [output/pdf/edited/e3_subset.pdf](../output/pdf/edited/e3_subset.pdf) | [results/e3_subset.json](../results/e3_subset.json) | Existing encoded glyph reuse in identical embedded subset program | Yes |
| e4_integrity / E4 | [output/pdf/edited/e4_integrity.pdf](../output/pdf/edited/e4_integrity.pdf) | [results/e4_integrity.json](../results/e4_integrity.json) | Configured save preserves all nine measured integrity properties | Yes |
| e4_default_metadata / E4 | [output/pdf/edited/e4_default_metadata.pdf](../output/pdf/edited/e4_default_metadata.pdf) | [results/e4_default_metadata.json](../results/e4_default_metadata.json) | Default save changes exact XMP serialization, with visual success | Yes |
| e5_mixed_edit / E5 | [output/pdf/edited/e5_mixed_edit.pdf](../output/pdf/edited/e5_mixed_edit.pdf) | [results/e5_mixed_edit.json](../results/e5_mixed_edit.json) | Digital caption changed; raster remains unchanged | Yes |
| e2_rejected_expansion / E2 | [output/pdf/edited/e2_rejected_expansion.pdf](../output/pdf/edited/e2_rejected_expansion.pdf) | [results/e2_rejected_expansion.json](../results/e2_rejected_expansion.json) | Unchanged scripted refusal; records 50.028 vs 362.148 pt widths | Yes |
| e3_rejected_glyph / E3 | [output/pdf/edited/e3_rejected_glyph.pdf](../output/pdf/edited/e3_rejected_glyph.pdf) | [results/e3_rejected_glyph.json](../results/e3_rejected_glyph.json) | Unchanged scripted refusal; U+2603 absent from embedded cmap | Yes |
| e5_scan_no_edit / E5 | [output/pdf/edited/e5_scan_no_edit.pdf](../output/pdf/edited/e5_scan_no_edit.pdf) | [results/e5_scan_no_edit.json](../results/e5_scan_no_edit.json) | Raster-only classification; unchanged scripted non-edit | Yes |

## 4. Diagnostic pairs and original diagnostics

The following **32 diagnostic files** are essential to verify the hashes, extracted text, span boxes/style, font programs, image locations, page boxes, annotations, links, metadata and bookmarks for each case. In every row the purpose is before/after resource and geometry comparison; the associated experiment is the case prefix.

| Case | Before (repository-relative) | After (repository-relative) | Essential? |
|---|---|---|---|
| e1_operand | [results/diagnostics/e1_operand-before.json](../results/diagnostics/e1_operand-before.json) | [results/diagnostics/e1_operand-after.json](../results/diagnostics/e1_operand-after.json) | Yes |
| e1_pdfium | [results/diagnostics/e1_pdfium-before.json](../results/diagnostics/e1_pdfium-before.json) | [results/diagnostics/e1_pdfium-after.json](../results/diagnostics/e1_pdfium-after.json) | Yes |
| e1_remove_reinsert | [results/diagnostics/e1_remove_reinsert-before.json](../results/diagnostics/e1_remove_reinsert-before.json) | [results/diagnostics/e1_remove_reinsert-after.json](../results/diagnostics/e1_remove_reinsert-after.json) | Yes |
| e2_overflow | [results/diagnostics/e2_overflow-before.json](../results/diagnostics/e2_overflow-before.json) | [results/diagnostics/e2_overflow-after.json](../results/diagnostics/e2_overflow-after.json) | Yes |
| e2_controlled_reflow | [results/diagnostics/e2_controlled_reflow-before.json](../results/diagnostics/e2_controlled_reflow-before.json) | [results/diagnostics/e2_controlled_reflow-after.json](../results/diagnostics/e2_controlled_reflow-after.json) | Yes |
| e3_bold | [results/diagnostics/e3_bold-before.json](../results/diagnostics/e3_bold-before.json) | [results/diagnostics/e3_bold-after.json](../results/diagnostics/e3_bold-after.json) | Yes |
| e3_bold_compensated | [results/diagnostics/e3_bold_compensated-before.json](../results/diagnostics/e3_bold_compensated-before.json) | [results/diagnostics/e3_bold_compensated-after.json](../results/diagnostics/e3_bold_compensated-after.json) | Yes |
| e3_italic | [results/diagnostics/e3_italic-before.json](../results/diagnostics/e3_italic-before.json) | [results/diagnostics/e3_italic-after.json](../results/diagnostics/e3_italic-after.json) | Yes |
| e3_table | [results/diagnostics/e3_table-before.json](../results/diagnostics/e3_table-before.json) | [results/diagnostics/e3_table-after.json](../results/diagnostics/e3_table-after.json) | Yes |
| e3_subset | [results/diagnostics/e3_subset-before.json](../results/diagnostics/e3_subset-before.json) | [results/diagnostics/e3_subset-after.json](../results/diagnostics/e3_subset-after.json) | Yes |
| e4_integrity | [results/diagnostics/e4_integrity-before.json](../results/diagnostics/e4_integrity-before.json) | [results/diagnostics/e4_integrity-after.json](../results/diagnostics/e4_integrity-after.json) | Yes |
| e4_default_metadata | [results/diagnostics/e4_default_metadata-before.json](../results/diagnostics/e4_default_metadata-before.json) | [results/diagnostics/e4_default_metadata-after.json](../results/diagnostics/e4_default_metadata-after.json) | Yes |
| e5_mixed_edit | [results/diagnostics/e5_mixed_edit-before.json](../results/diagnostics/e5_mixed_edit-before.json) | [results/diagnostics/e5_mixed_edit-after.json](../results/diagnostics/e5_mixed_edit-after.json) | Yes |
| e2_rejected_expansion | [results/diagnostics/e2_rejected_expansion-before.json](../results/diagnostics/e2_rejected_expansion-before.json) | [results/diagnostics/e2_rejected_expansion-after.json](../results/diagnostics/e2_rejected_expansion-after.json) | Yes |
| e3_rejected_glyph | [results/diagnostics/e3_rejected_glyph-before.json](../results/diagnostics/e3_rejected_glyph-before.json) | [results/diagnostics/e3_rejected_glyph-after.json](../results/diagnostics/e3_rejected_glyph-after.json) | Yes |
| e5_scan_no_edit | [results/diagnostics/e5_scan_no_edit-before.json](../results/diagnostics/e5_scan_no_edit-before.json) | [results/diagnostics/e5_scan_no_edit-after.json](../results/diagnostics/e5_scan_no_edit-after.json) | Yes |

The six additional original-only diagnostics are useful baseline/scan-classification references (duplicated information is not required in a compact evidence transfer):

- [results/diagnostics/basic-original.json](../results/diagnostics/basic-original.json) - E1, original text/resources and classification; useful, not additional essential evidence beyond the pairs.
- [results/diagnostics/expansion-original.json](../results/diagnostics/expansion-original.json) - E2, original text/resources and classification; useful, not additional essential evidence beyond the pairs.
- [results/diagnostics/complex-original.json](../results/diagnostics/complex-original.json) - E3, original text/resources and classification; useful, not additional essential evidence beyond the pairs.
- [results/diagnostics/integrity-original.json](../results/diagnostics/integrity-original.json) - E4, original text/resources and classification; useful, not additional essential evidence beyond the pairs.
- [results/diagnostics/mixed-original.json](../results/diagnostics/mixed-original.json) - E5, original text/resources and classification; useful, not additional essential evidence beyond the pairs.
- [results/diagnostics/scanned-original.json](../results/diagnostics/scanned-original.json) - E5, original text/resources and classification; useful, not additional essential evidence beyond the pairs.

## 5. Render evidence

All 243 files in the following family exist. The placeholders are a directory-family notation, not literal filenames:

`results/renders/<case-id>/<renderer>/p<page>-<before|after|diff>.png`

- `<case-id>` is any of the 16 IDs in section 3.
- `<renderer>` is `mupdf`, `pdfium` or `poppler`.
- `<page>` is 1, plus 2 where the source is `basic.pdf`, `complex.pdf` or `integrity.pdf`.
- Purpose: original/candidate page render and thresholded diff. Associated experiment: the case prefix. **Before/after files are essential** to recalculate visual metrics; diff files are derived visual aids.
- The 81 before/after pairs were read and their thresholded metrics reconciled during consolidation, without rerendering or rewriting files.
- A zero diff outside a padded mask does not establish stable neighbour geometry; inspect spans/glyphs as well.

Representative exact paths for important findings:

| Repository-relative path | Purpose / experiment | Essential? |
|---|---|---|
| [results/renders/e1_pdfium/pdfium/p1-before.png](../results/renders/e1_pdfium/pdfium/p1-before.png) | e1_pdfium: PDFium page-one before | Yes, for visual comparison |
| [results/renders/e1_pdfium/pdfium/p1-after.png](../results/renders/e1_pdfium/pdfium/p1-after.png) | e1_pdfium: PDFium page-one after | Yes, for visual comparison |
| [results/renders/e1_pdfium/pdfium/p1-diff.png](../results/renders/e1_pdfium/pdfium/p1-diff.png) | e1_pdfium: PDFium page-one diff | Derived aid |
| [results/renders/e2_overflow/pdfium/p1-before.png](../results/renders/e2_overflow/pdfium/p1-before.png) | e2_overflow: PDFium page-one before | Yes, for visual comparison |
| [results/renders/e2_overflow/pdfium/p1-after.png](../results/renders/e2_overflow/pdfium/p1-after.png) | e2_overflow: PDFium page-one after | Yes, for visual comparison |
| [results/renders/e2_overflow/pdfium/p1-diff.png](../results/renders/e2_overflow/pdfium/p1-diff.png) | e2_overflow: PDFium page-one diff | Derived aid |
| [results/renders/e2_controlled_reflow/pdfium/p1-before.png](../results/renders/e2_controlled_reflow/pdfium/p1-before.png) | e2_controlled_reflow: PDFium page-one before | Yes, for visual comparison |
| [results/renders/e2_controlled_reflow/pdfium/p1-after.png](../results/renders/e2_controlled_reflow/pdfium/p1-after.png) | e2_controlled_reflow: PDFium page-one after | Yes, for visual comparison |
| [results/renders/e2_controlled_reflow/pdfium/p1-diff.png](../results/renders/e2_controlled_reflow/pdfium/p1-diff.png) | e2_controlled_reflow: PDFium page-one diff | Derived aid |
| [results/renders/e3_bold/pdfium/p1-before.png](../results/renders/e3_bold/pdfium/p1-before.png) | e3_bold: PDFium page-one before | Yes, for visual comparison |
| [results/renders/e3_bold/pdfium/p1-after.png](../results/renders/e3_bold/pdfium/p1-after.png) | e3_bold: PDFium page-one after | Yes, for visual comparison |
| [results/renders/e3_bold/pdfium/p1-diff.png](../results/renders/e3_bold/pdfium/p1-diff.png) | e3_bold: PDFium page-one diff | Derived aid |
| [results/renders/e3_bold_compensated/pdfium/p1-before.png](../results/renders/e3_bold_compensated/pdfium/p1-before.png) | e3_bold_compensated: PDFium page-one before | Yes, for visual comparison |
| [results/renders/e3_bold_compensated/pdfium/p1-after.png](../results/renders/e3_bold_compensated/pdfium/p1-after.png) | e3_bold_compensated: PDFium page-one after | Yes, for visual comparison |
| [results/renders/e3_bold_compensated/pdfium/p1-diff.png](../results/renders/e3_bold_compensated/pdfium/p1-diff.png) | e3_bold_compensated: PDFium page-one diff | Derived aid |
| [results/renders/e3_italic/pdfium/p1-before.png](../results/renders/e3_italic/pdfium/p1-before.png) | e3_italic: PDFium page-one before | Yes, for visual comparison |
| [results/renders/e3_italic/pdfium/p1-after.png](../results/renders/e3_italic/pdfium/p1-after.png) | e3_italic: PDFium page-one after | Yes, for visual comparison |
| [results/renders/e3_italic/pdfium/p1-diff.png](../results/renders/e3_italic/pdfium/p1-diff.png) | e3_italic: PDFium page-one diff | Derived aid |
| [results/renders/e4_integrity/pdfium/p1-before.png](../results/renders/e4_integrity/pdfium/p1-before.png) | e4_integrity: PDFium page-one before | Yes, for visual comparison |
| [results/renders/e4_integrity/pdfium/p1-after.png](../results/renders/e4_integrity/pdfium/p1-after.png) | e4_integrity: PDFium page-one after | Yes, for visual comparison |
| [results/renders/e4_integrity/pdfium/p1-diff.png](../results/renders/e4_integrity/pdfium/p1-diff.png) | e4_integrity: PDFium page-one diff | Derived aid |

Review-sheet overviews are useful but downsampled and cropped; they are not substitutes for full renders:

- [results/e1-review.png](../results/e1-review.png) - E1, before/after/diff overview; useful, not essential.
- [results/e2-review.png](../results/e2-review.png) - E2, before/after/diff overview; useful, not essential.
- [results/e3-review.png](../results/e3-review.png) - E3, before/after/diff overview; useful, not essential.
- [results/e4-review.png](../results/e4-review.png) - E4, before/after/diff overview; useful, not essential.
- [results/e5-review.png](../results/e5-review.png) - E5, before/after/diff overview; useful, not essential.

## 6. Reports and fixture assets

| Repository-relative path | Purpose | Area | Essential? |
|---|---|---|---|
| [TECHNICAL_FEASIBILITY_REPORT.md](../TECHNICAL_FEASIBILITY_REPORT.md) | Original Phase 1 findings; some qualifications refined by the handover | All | Useful historical interpretation |
| [PDF_ENGINE_COMPARISON.md](../PDF_ENGINE_COMPARISON.md) | Original technology, maintenance, source-link and distribution research | Technology/licensing | Yes, to audit research provenance |
| [ARCHITECTURE_RECOMMENDATION.md](../ARCHITECTURE_RECOMMENDATION.md) | Original native-shell/worker recommendation; not an implemented architecture | Architecture | Useful |
| [PHASE_2_PROPOSAL.md](../PHASE_2_PROPOSAL.md) | Original CLI/engine-first milestone; handover now prioritizes a tightly scoped inline-editing proof | Planning | Useful; proposal only |
| [README.md](../README.md) | Original reproduction and artifact navigation instructions | Reproduction | Useful |
| [assets/Vera.ttf](../assets/Vera.ttf) | Supplied full font used to generate embedded subset fixtures | E3/E4 | Yes, to recreate subset fixtures |
| [assets/bitstream-vera-license.txt](../assets/bitstream-vera-license.txt) | License for the supplied fixture font | Font distribution | Yes |
| [assets/diagram.png](../assets/diagram.png) | Synthetic diagram image used by complex/integrity samples | E3/E4 | Yes, to recreate fixtures |
| [assets/scan.png](../assets/scan.png) | Synthetic raster-only text image | E5 | Yes, to recreate scan/mixed fixtures |

## 7. Preservation, verification boundaries and package decision

- The handover creates only `PHASE_1_HANDOVER/PHASE_1_CONSOLIDATED_REPORT.md` and this index. Existing source, tests, PDFs, results and logs are retained byte-for-byte.
- Dependencies (`.venv/`, `.venv-clean/`), `__pycache__/` and `.gitignore` are not substantive experimental proof and need not be transferred for review. `.gitignore` was inventoried but is not an important technical conclusion source.
- The retained run log and tests contain final results; no complete intermediate development-error chronology is available.
- No existing test runner was executed during consolidation because it writes artifacts. Read-only PDF, JSON, saved-raster and hash checks were used instead.
- **No `PHASE_1_EVIDENCE.zip` was created.** The consolidated report includes the important measured results and qualifications, with this index locating originals for deeper checks. An archive would duplicate existing material without filling a communication gap.
- The interactive editing architecture and next milestone are proposals. No direct input/caret/undo/collision/worker feature was added.
