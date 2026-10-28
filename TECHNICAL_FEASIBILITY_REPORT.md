# PDF Editor - Phase 1 technical feasibility

Evidence date: 27 October 2026. Target/test host: Windows 11 x64, Python 3.12.14. Scope: local experiments only. No finished application or Phase 2 implementation.

## Decision

Genuine, appearance-preserving edits are feasible for a constrained subset of digital PDF text. The experiments do **not** establish reliable editing or automatic paragraph reflow for arbitrary PDFs. A product should promise selected-text correction with explicit eligibility checks, preview and refusal, rather than Word-like editing of every document.

Direct content-operand rewriting and PDFium's existing-text-object mutation both changed saved text without a covering overlay. PyMuPDF removal/reinsertion also changed real content, but reconstructs the edited text and can alter font resources and extraction order. These mechanisms must remain distinct in the eventual user interface.

## Delivered evidence and method

Six originals and sixteen candidates are under `output/pdf/`. Thirteen candidates contain real edits; three are unchanged copies documenting refused requests. The originals' SHA256 values match before/after and the persistent `originals/SHA256.json` manifest. Existing originals are never overwritten by reruns.

The [evidence index](results/index.html) links every original, candidate, JSON result and rendering. [The evidence table](results/INDEX.md) gives a short explanation per candidate. `results/summary.json` records versions, hashes, timings, checks and measurements. `results/tests.json` records **14 automated tests passing**, including negative controls. Passing tests means the observed successes and expected failures were detected correctly; it does not mean all sixteen candidate operations succeeded.

For each real edit, the harness saves a new PDF, closes it, and reopens it. It checks the new/old text through MuPDF and PDFium extraction, and inspects parsed `Tj`/`TJ` operands to confirm removal of the original encoded word. Tests add pypdf extraction as a third semantic check and check that other words survive. A temporary white-box overlay negative control retains the old extractable text and is correctly rejected by this removal criterion.

All pages are rendered before/after through **MuPDF, PDFium and Poppler** at 144 DPI. Comparisons use each renderer against itself, an RGB maximum-channel change threshold greater than 8, and an original edit bounding box padded by approximately 3 pixels (slice endpoints include an additional terminal pixel). Controlled reflow uses the whole declared paragraph region. Diff images show blue changes inside the allowed region and red changes outside it. This measures visual isolation at one resolution; it is not a proof of identical rendering at every zoom, printer or font environment. Semantic and resource checks complement the raster test.

## Experiment 1 - Basic replacement

Input: `originals/basic.pdf`, two pages, several paragraphs, blue 12 pt Helvetica text and an existing note. Replace `blue` with `glue` in the first paragraph. These words have equal advance in this fixture.

| Candidate | Mechanism | Saved text verified | Outside pixels, MuPDF / PDFium / Poppler | Caveat |
|---|---|---|---:|---|
| `e1_operand.pdf` | Replace encoded string operand | Yes | 0 / 0 / 0 | Fixture-specific single-byte encoding |
| `e1_pdfium.pdf` | `FPDFText_SetText` on existing page text object, then regenerate content | Yes | 0 / 0 / 0 | Whole line object changed; font resource inventory reorganized |
| `e1_remove_reinsert.pdf` | Apply text-only redaction, then insert new text at captured baseline | Yes | 0 / 0 / 0 | Removal/reconstruction; adds a font resource and changes extraction ordering |

Reopened font name, font size, colour and starting baseline/position match in all three. Untouched second pages are pixel-identical. The operand route preserves the font inventory; the other routes do not preserve the exact inventory, despite visual success. Helvetica is unembedded in this fixture, so cross-machine font substitution remains a limitation inherited from the input.

The harness selects the unique word through extracted geometry, then uses either a known encoded operand or an existing PDFium object. This is not yet a general mapping from arbitrary user-selected glyphs to content operators. It does not support selections split across arbitrary operators or shared forms.

## Experiment 2 - Expansion and reflow

Input: `originals/expansion.pdf`. Replace `brief note` with `a substantially longer replacement phrase which needs several lines`.

| Candidate | Observed result | Outside pixels, MuPDF / PDFium / Poppler |
|---|---|---:|
| `e2_overflow.pdf` | Genuine replacement, one line, no automatic wrapping; visibly collides with fixed neighbouring text | 5356 / 5829 / 5350 |
| `e2_controlled_reflow.pdf` | Remove the complete known paragraph and lay out its replacement in a declared 305 x 55 pt box; two lines fit at 12 pt | 0 / 0 / 0 |
| `e2_rejected_expansion.pdf` | Width comparison rejects the change within the original phrase width; byte-identical candidate | 0 / 0 / 0 |

The naive edit saves cleanly and contains the new phrase: API success, syntax validity and text extraction do not detect the collision. The diff does. Existing following content does not move to accommodate the phrase.

Controlled reflow succeeds because the experiment owns the entire paragraph, knows its font and layout rectangle, and has space inside that rectangle. It changes the paragraph's original positioning within that box intentionally. It does **not** infer a paragraph from an arbitrary PDF or move subsequent tables/images/pages. Reliable bounded reflow is realistic for app-created blocks, known templates or explicitly reconstructed regions. General document reflow needs layout reconstruction, font shaping, ownership and collision policies; original authoring intent may be absent. The underlying format often positions individual characters and table cells rather than storing editable paragraphs. [pypdf's extraction discussion](https://pypdf.readthedocs.io/en/stable/user/extract-text.html) describes this semantic ambiguity.

## Experiment 3 - Complex formatting

Input: `originals/complex.pdf`, two pages, Helvetica-Bold 15 pt blue, Times-Italic 13 pt red, Courier 10 pt green, embedded/subset Bitstream Vera 14 pt purple, a ruled table, positioned raster images, note and link.

| Candidate | Result | Outside pixels, MuPDF / PDFium / Poppler |
|---|---|---:|
| `e3_bold.pdf` | `BOLD` -> `GOLD` retains style and start position, but wider glyph advance shifts `heading` | 1204 / 1474 / 1222 |
| `e3_bold_compensated.pdf` | A `TJ` spacing adjustment compensates the known advance difference; following word stays fixed | 0 / 0 / 0 |
| `e3_italic.pdf` | `elegant` -> `refined` retains Times-Italic, colour, size and anchor; a small difference outside the original region remains in PDFium | 0 / 1 / 0 |
| `e3_table.pdf` | `125.00` -> `175.00`; equal-width digits, table rules/cells/image unaffected | 0 / 0 / 0 |
| `e3_subset.pdf` | `cafe` -> `face`, reusing existing encoded ASCII glyphs and identical embedded font program | 0 / 0 / 0 |
| `e3_rejected_glyph.pdf` | Requested U+2603 snowman absent from every embedded subset cmap; refused | 0 / 0 / 0 |

The bold compensation is deliberately limited to the known 15 pt Helvetica-Bold fixture, using ReportLab metrics. It reduces the gap after the wider word to preserve the following word's position. It is not a general font-metric/kerning solution, and enough expansion would cause collision even with compensation. The uncorrected case is retained to demonstrate this failure.

The italic result is not claimed to have perfect isolation. Its period/final advance and raster boundary need tighter glyph geometry checks; a single outside pixel is still recorded, not rounded away. The embedded subset success establishes reuse of available glyphs only. Adding a missing glyph may need the original full font, permission to embed it, a new font resource, a valid encoding and appropriate shaping. A matching font name does not guarantee these.

## Experiment 4 - Save integrity

Input: `originals/integrity.pdf`, a dedicated two-page fixture with nonempty XMP, document information, two bookmarks, a text annotation, a link, images, an embedded subset font, and a cropped/90-degree-rotated untouched second page. Change the table value.

`e4_integrity.pdf` preserves page count; MediaBox/CropBox/render dimensions and rotation; image placement and decoded-image digests; font names and embedded-program hashes; annotation properties/rectangles; link targets/rectangles; document information; exact extracted XMP string; and bookmark titles/destinations. Both pages have zero outside-region changes in all three renderers; the entire second page is pixel-identical.

`e4_default_metadata.pdf` uses pikepdf's default `fix_metadata_version=True`. It preserves the visual document and other measured properties but rewrites the XMP serialization. We record exact-XMP preservation as **false**. The successful candidate uses `fix_metadata_version=False`, which preserves this fixture's packet. The default result shows a configuration-sensitive metadata change, not proof that user metadata was lost.

All modified outputs reopen through multiple libraries, with no qpdf syntax warnings. Resource identity checks use embedded font program hashes and decoded image hashes, not xref numbers or whole-file byte identity. Saving legitimately renumbers objects and rewrites/compresses streams. Font inventory differences in the PDFium and PyMuPDF cases are reported rather than hidden.

This does not certify forms, tagged accessibility structures, signatures, encryption, portfolios, embedded files, PDF/A, ICC colour fidelity, transparency, shared Form XObjects or incremental revisions. None is adequately covered by this small corpus. Editing may invalidate signatures; production eligibility must detect and handle signed files explicitly.

## Experiment 5 - Diagnostic capability

`feasibility.py analyze INPUT --output OUTPUT.json` reports per-page extracted text; spans, bounding boxes, directions, baselines, font names/sizes/colours; font resource names, type/encoding, embedded/subset status and embedded-program hashes; image boxes/dimensions/digests; page dimensions/boxes/rotation; annotations, links, metadata and limitations.

- `basic.pdf`, `complex.pdf`, `expansion.pdf` and `integrity.pdf` classify as digital-text pages.
- `scanned.pdf` has a page-sized raster and no extractable text: `scan-candidate`. Its refused candidate remains byte-identical.
- `mixed.pdf` has a page-sized raster plus a digital caption: `mixed-or-OCR-candidate`. `e5_mixed_edit.pdf` genuinely changes the caption with zero outside pixels in all renderers and the original image digest/location preserved.

These are page-level heuristics, not forensic provenance classification. The image-area ratio sums rectangles rather than computing a union and may exceed one. Large backgrounds can resemble scans; OCR text can be invisible over pixels; text can be outlines or have unusable mappings. Document-level categorization requires combining page results. OCR recognition/editing was not implemented. Changing an OCR text layer would not change the visible scanned letters.

## Reliability, performance and limits

The complete measured run takes tens of seconds including disk I/O, three renderers and PNG/diff generation; the exact delivered timing and per-operation milliseconds are in `results/summary.json`. Individual edit/save operations took tens of milliseconds on these fixtures. They are single-run observations on tiny local fixtures, not a fair engine benchmark: engines, font inventories, workloads and cache states differ. Cold launch, memory use, very large pages, many-page files and hostile-input timeouts are unmeasured.

The exact requirements file also installed successfully into a second clean venv without inherited system packages, and all 14 tests passed there (`clean-install.log`, `clean-test-results.log`). An additional complete run with Python socket connection APIs replaced by refusal functions passed (`offline_check.py`). This supports no-network Python execution for the exercised paths; it is not an operating-system network sandbox or a clean-VM installer test. Poppler 26.07.0 was supplied by the local tool runtime.

Fundamental constraints include missing authoring semantics, incomplete font subsets, arbitrary encodings, separately positioned glyphs, and no unique correct way to redistribute expanded text. Implementation work can improve glyph-to-operator mapping, spacing, shaping, collision detection and save policy, but cannot recover information absent from a file with certainty. Tagged PDFs may provide structure, but do not universally restore authoring layout.

This corpus is deliberately synthetic and small. It demonstrates mechanisms and failure modes, not a real-world success percentage. Safe isolated edits were observed; general reliability remains unproven. The next milestone should broaden adversarial and independently produced documents before any user-facing promise is enlarged.

## What we can realistically promise

Offer offline correction of eligible existing digital text, preserving appearance when the replacement fits and required glyphs/resources are available, with verified preview and Save As. Explain when an operation reconstructs a region or uses a replacement font. Refuse unsupported encodings, missing glyphs or unsafe geometry. Offer bounded paragraph reconstruction only where ownership and layout are explicit. Do not promise arbitrary reflow, scan-text replacement, perfect font recovery, signature retention or universal lossless saves.

See [PDF_ENGINE_COMPARISON.md](PDF_ENGINE_COMPARISON.md) for licensing and maintained-engine research, [ARCHITECTURE_RECOMMENDATION.md](ARCHITECTURE_RECOMMENDATION.md) for the proposed stack, and [PHASE_2_PROPOSAL.md](PHASE_2_PROPOSAL.md) for the next review gate. Phase 1 stops here.
