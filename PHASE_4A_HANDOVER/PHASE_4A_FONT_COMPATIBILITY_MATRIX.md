# Phase 4A font compatibility matrix

28 October 2026. Actual classifications were queried from the frozen Phase 3 binary and final Phase 4A binary for the same source bytes. Counts refer to candidate text regions on page one; whitespace-only objects are not counted as regions. The full program hashes, font inventory, cmap coverage, embedding flags, reasons and saved filenames are in `phase4a/evidence/compatibility-matrix.json`.

Only automatically discovered Editable regions can activate. A structurally supported region still needs draft glyph/layout checks and the full export verifier. No font substitution or extension is used.

## Source corpus

| PDF | Generator | Main font class / embedding | Encoding | Phase 3 | Phase 4A | Demonstrated edits or restrictions |
|---|---|---|---|---|---|---|
| corpus/01-letter.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | Editable 5 | Editable 5 | Verified original-font save: 2 recorded case(s) |
| corpus/02-report.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | Editable 4 | Editable 4 | Verified original-font save: 3 recorded case(s) |
| corpus/03-adjacent.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | Editable 1, View Only 2 | Editable 1, View Only 2 | Restrictions retained: AMBIGUOUS_COLUMNS_LABELS_OR_FRAGMENTED_LINE, COMPLETE_OBJECT_OWNERSHIP, CONSERVATIVE_SPACE_AVAILABLE, INCOMPLETE_GLYPH_OWNERSHIP, INITIAL_OBJECT_RECONSTRUCTION_DIFFERS, NATURAL_HORIZONTAL_GLYPH_GEOMETRY, ORIGINAL_CHARACTER_OUTLINES_WIDTHS_AND_ENCODING_VERIFIED, OWNED_SPACE_INTERSECTS_NEIGHBOUR, PAGE_BOUNDARY_OR_METRICS |
| corpus/04-two-columns.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | View Only 10 | View Only 10 | Restrictions retained: AMBIGUOUS_COLUMNS_LABELS_OR_FRAGMENTED_LINE, INCOMPLETE_GLYPH_OWNERSHIP, INITIAL_OBJECT_RECONSTRUCTION_DIFFERS, INSUFFICIENT_VERTICAL_SPACE, OWNED_SPACE_INTERSECTS_NEIGHBOUR, PAGE_BOUNDARY_OR_METRICS |
| corpus/05-table.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | View Only 6 | View Only 6 | Restrictions retained: AMBIGUOUS_COLUMNS_LABELS_OR_FRAGMENTED_LINE, INCOMPLETE_GLYPH_OWNERSHIP, INITIAL_OBJECT_RECONSTRUCTION_DIFFERS, INSUFFICIENT_VERTICAL_SPACE, OWNED_SPACE_INTERSECTS_NEIGHBOUR, PAGE_BOUNDARY_OR_METRICS |
| corpus/06-ambiguous.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | Limited 2 | Limited 2 | Restrictions retained: AMBIGUOUS_SHORT_LINE_PARAGRAPH_BOUNDARY, INSUFFICIENT_VERTICAL_SPACE |
| corpus/07-rotated.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | View Only 1 | View Only 1 | Restrictions retained: NON_NATURAL_GLYPH_SPACING, UNSUPPORTED_TRANSFORM |
| corpus/08-nonembedded.pdf | ReportLab / fontTools / mapping variants | Not embedded; /Type1 | simple; no ToUnicode | View Only 1 | View Only 1 | Restrictions retained: FONT_NOT_EMBEDDED |
| corpus/09-mupdf-letter.pdf | MuPDF + subset / mapping restriction | /Type0; embedded; embedding | Identity-H + ToUnicode | Editable 3 | Editable 3 | Verified original-font save: 1 recorded case(s) |
| corpus/10-mupdf-subset.pdf | MuPDF + subset / mapping restriction | /Type0; embedded; subset tag | Identity-H + ToUnicode; no font cmap | View Only 3 | View Only 3 | Subset has no usable font Unicode cmap; remains view-only |
| corpus/11-word-letter.pdf | Microsoft Word 16.0 | /TrueType, /Type0; embedded; subset tag | Identity-H + ToUnicode, simple; no ToUnicode | View Only 3 | View Only 3 | Font coverage assessed separately; spacing/reconstruction/whitespace ownership still blocks activation |
| corpus/12-image-overlap.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | Limited 1 | Limited 1 | Restrictions retained: GRAPHIC_IMAGE_OR_TABLE_INTERSECTION, OWNED_SPACE_INTERSECTS_NEIGHBOUR |
| corpus/13-shuffled-order.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | Editable 1 | Editable 1 | Verified original-font save: 1 recorded case(s) |
| corpus/14-annotation.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | View Only 1 | View Only 1 | Restrictions retained: DOCUMENT_OR_PAGE_SIGNATURE_ENCRYPTION_ROTATION_ANNOTATION_OR_FORM |
| corpus/15-letter-spacing.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | View Only 1 | View Only 1 | Restrictions retained: INITIAL_OBJECT_RECONSTRUCTION_DIFFERS, NON_NATURAL_GLYPH_SPACING |
| font-corpus/A-subset-existing.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | Editable 1, View Only 1 | Editable 1, View Only 1 | Existing glyph reordering and longer text save; Z unavailable |
| font-corpus/B-original-only.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | Editable 1, View Only 1 | Editable 1, View Only 1 | Repetition/reordering of original letters saves; no space coverage |
| font-corpus/C-subset-bold.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | Editable 1, View Only 1 | Editable 1, View Only 1 | Original bold glyphs save |
| font-corpus/D-fragmented.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | Limited 1, View Only 2 | Limited 1, View Only 2 | Fragments/labels remain unmerged |
| font-corpus/E-character-spacing.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | View Only 2 | View Only 2 | Explicit spacing refused |
| font-corpus/F-kerning.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | View Only 2 | View Only 2 | Kerning refused |
| font-corpus/G-duplicate-unicode.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | Editable 1, View Only 1 | Editable 1, View Only 1 | Verified selected mapping saves despite unused alias |
| font-corpus/H-wrong-unicode.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | View Only 2 | View Only 2 | Wrong mapping/reconstruction refused |
| font-corpus/I-missing-unicode.pdf | ReportLab / fontTools / mapping variants | /TrueType; embedded; subset tag | simple + ToUnicode | View Only 2 | View Only 2 | Missing mapping/reconstruction refused |
| font-corpus/J-partial-encoding.pdf | MuPDF + subset / mapping restriction | /Type0; embedded; physical subset provenance | Identity-H + ToUnicode | View Only 2 | Editable 1, View Only 1 | NEW: existing mapped glyphs save/reopen/re-edit; retained Z blocked |
| font-corpus/PowerPoint-Arial-subset.pdf | Microsoft PowerPoint 16.0 | /TrueType; embedded; subset tag | simple; no ToUnicode | View Only 2 | View Only 2 | Office spacing/background intersection refused |
| font-corpus/Word-Arial.pdf | Microsoft Word 16.0 | /TrueType, /Type0; embedded; subset tag | Identity-H + ToUnicode, simple; no ToUnicode | View Only 2 | View Only 2 | Font coverage assessed separately; spacing/reconstruction/whitespace ownership still blocks activation |
| font-corpus/Word-Calibri.pdf | Microsoft Word 16.0 | /TrueType, /Type0; embedded; subset tag | Identity-H + ToUnicode, simple; no ToUnicode | View Only 2 | View Only 2 | Font coverage assessed separately; spacing/reconstruction/whitespace ownership still blocks activation |
| font-corpus/Word-Consolas.pdf | Microsoft Word 16.0 | /TrueType, /Type0; embedded; subset tag | Identity-H + ToUnicode, simple; no ToUnicode | View Only 2 | Limited 2 | Font coverage assessed separately; spacing/reconstruction/whitespace ownership still blocks activation |

## Verified product output cases

The following 19 exports pass the complete product verifier and independent pypdf/MuPDF/Poppler/qpdf checks. Equal-width means equal total advance in the tested original font, not a general word substitution rule. Each file uses the original program. Independent outside-region pixels are zero at 72/144 DPI and neighbouring glyph displacement is zero in these cases.

| Output case | Source | Modification / generation |
|---|---|---|
| report-edited-1793181429707332400.pdf | 02-report.pdf | existing glyph replacement/reuse; verified |
| letter-edited-1793181429855438500.pdf | 01-letter.pdf | existing glyph replacement/reuse; verified |
| bold-edited-1793181429977492600.pdf | 02-report.pdf | existing glyph replacement/reuse; verified |
| colour-edited-1793181430095502600.pdf | 02-report.pdf | existing glyph replacement/reuse; verified |
| mupdf-edited-1793181430316246600.pdf | 09-mupdf-letter.pdf | existing glyph replacement/reuse; verified |
| generation-one-1793181430429992400.pdf | 01-letter.pdf | longer existing glyphs / wrapping; verified |
| generation-two-1793181430672694500.pdf | generation-one-1793181430429992400.pdf | second generation; verified |
| shuffled-edited-1793181432005447100.pdf | 13-shuffled-order.pdf | existing glyph replacement/reuse; verified |
| subset-equal-width-1793181433045314700.pdf | A-subset-existing.pdf | existing glyph replacement/reuse; verified |
| subset-longer-1793181433179984400.pdf | A-subset-existing.pdf | longer existing glyphs / wrapping; verified |
| original-only-reuse-1793181433360739000.pdf | B-original-only.pdf | existing glyph replacement/reuse; verified |
| subset-bold-1793181433571508400.pdf | C-subset-bold.pdf | existing glyph replacement/reuse; verified |
| duplicate-mapping-safe-1793181433981917700.pdf | G-duplicate-unicode.pdf | existing glyph replacement/reuse; verified |
| subset-gen-one-1793181434620507200.pdf | A-subset-existing.pdf | existing glyph replacement/reuse; verified |
| subset-gen-two-1793181434808367600.pdf | subset-gen-one-1793181434620507200.pdf | second generation; verified |
| probe-object-count-1793181435051697900.pdf | A-subset-existing.pdf | existing glyph replacement/reuse; verified |
| new-partial-encoding-edit-1793181435336335100.pdf | J-partial-encoding.pdf | existing glyph replacement/reuse; verified |
| new-partial-gen-one-1793181435470506000.pdf | J-partial-encoding.pdf | existing glyph replacement/reuse; verified |
| new-partial-gen-two-1793181435633823900.pdf | new-partial-gen-one-1793181435470506000.pdf | second generation; verified |

## Interpretation and limits

J is the actual product compatibility gain: a standard Type0/Identity-H pattern with a physically subsetted TrueType program, usable Unicode cmap and a PDF ToUnicode map limited to used characters. Its retained but unmapped Z defeats the Phase 3 batch probe; Phase 4A permits the original mapped set without inventing a Z encoding. This is a targeted reproducible fixture modelled on the independently observed Word condition, not a claim that the original Word file is now editable.

A/B/C were already supported by Phase 3 and are explicitly not counted as newly compatible documents. G has multiple PDF codes mapping to one Unicode value; the selected reverse mapping is accepted only after outline/width/round-trip and original-object checks. H/I remain refused. Word and PowerPoint are actual Office exports, not simulated Office labels.

The source generator records describe physical subsetting; a six-letter BaseFont tag is reported separately and is not the sole evidence of a subset. Sparse cmap coverage can indicate unavailable or unmapped characters; it does not by itself prove which otherwise unencoded outlines remain. The MuPDF no-cmap case is classified distinctly from an ordinary sparse cmap.

All API-lab outputs are excluded from the product-output table. Their known-code Word experiments and deliberately unsafe negative controls are detailed in the Word analysis and test report. Forms/signatures/encryption, arbitrary Unicode/CFF/collections, mixed-style paragraphs and whole-document reflow are not certified.
