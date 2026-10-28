# Phase 4A.1 Word editing analysis

28 October 2026. Primary source: `phase3/run/corpus/11-word-letter.pdf`, unchanged; copied into `phase4a1/run/corpus/`. Producer is Microsoft Word 16.0. Source SHA256 is `d6201ddefe84b6476804cdc022360313998c465d250207fae02cd6ede01f872f`.

## Observations

One A4 page, approximately 595.32 × 841.92 pt. Eight top-level text objects. Visible objects 0, 3 and 6 contain complete lines, not one object per TJ fragment. Baselines are approximately 83.30, 131.30 and 179.18 pt. Identity horizontal transforms, regular Arial 12 pt, opaque fill. The source content includes Word marked content, language/MCID information and full-page clipping operators. Page-level clip context is not assumed to establish semantic ownership.

`phase4a1/evidence/word-position-analysis.json` contains all 154 visible characters: logical offset, original PDF code, Unicode, font GID, program advance, explicit origin, baseline and bounding box, together with all eight object matrices, raw strings, TJ adjustments, original content and protected object observations. Codes/TJ arrays come from pypdf; font cmaps, GIDs and advances from fontTools; geometry from pinned PDFium. Font resource/CIDToGID/ToUnicode data and probes are also retained in `font-investigation.json`. Object references are source-local indices, bound to the source hash, not persistent identities across rewritten files. Rediscovery after save is fresh.

The F1 `/BCDEEE+ArialMT` font is embedded Type0 Identity-H/CIDFontType2 TrueType. Codes 0 and 6 both extract as space, but code 0 is GID 0/notdef while code 6 is GID 3/space. Source visible spaces use the correct code. Existing outline/advance/Unicode proofs select the correct reverse mapping; raw-code guessing is not introduced. Many retained program glyphs still cannot be encoded by the PDF; these remain refused.

Natural reconstruction fails: original TJ adjustments produce measured local advance differences up to approximately 0.3340, 0.1662 and 0.6839 pt on the three lines. These are actual source positions, not new semantic paragraph constraints. Explicit N-1 offsets restore the original object bitmap and produce identical full-page independent renders for the tested title reconstruction.

## Separately retained whitespace

Objects 1, 4 and 7 are raw code 0x20 in F2 `/BCDFEE+ArialMT`, separately owned trailing spaces near x=180.53, 484.20 and 366.31. Objects 2 and 5 are corresponding spaces at intervening baselines 107.30/155.30. F2 is not embedded. PDFium returns empty standalone extraction and zero extent for these objects; MuPDF/pypdf expose their spaces. Their trailing/blank-paragraph roles are plausible **inferences**, not established semantic ownership.

The title's trailing object lies inside its bounding-box vicinity; ignoring whitespace generically would be unsafe. Instead, activation measures zero painted contribution at 144 DPI and retains these separate objects. It does not delete, move, absorb, normalize or recreate them as title spaces. Candidate checks preserve their original count, bounds and style, and independent stream parsing preserves all five F2 0x20 strings. The independent checks also compare encoding, CIDToGIDMap, ToUnicode, widths and font program sets. Visible whitespace or nonzero geometry is not granted this exception. Accessibility/tag-tree equivalence is not certified; retaining bytes/geometry is stronger than dropping spaces but is not a full semantic validation.

## Implemented stages

| Stage | Actual result |
|---|---|
| A: original reconstruction | Same source mapping and recorded offsets; all original glyph origins retained; Poppler full-page pixels identical at 72/144 DPI. |
| B: equal advance | Actual WPF selection/editor/history/ExportTo changes `Phase` to `Phace`; s and c have equal Arial advance. Other origins/bounds remain fixed. |
| C: narrower advance | Reopen first output and change `Office` to `Oflice`; the second f becomes l, approximately 0.668 pt narrower. Fixed surrounding origins, no overlap, correct extraction, same font and independent verification. Separate Arial/Calibri samples have two verified narrower-substitution generations. |
| C: excessive narrowing | `cafe calm.` -> `cafe call.` creates a large gap; PDFium inserts a space before the period in extraction. Exact extraction rejects it; WPF retains the full draft/recovery. |
| D: longer text | Insertions, deletions and newlines are allowed in the draft but refused for export. No general reflow or surrounding movement is implemented. |

A synthetic kerning fixture initially passed PDFium but shifted a space 0.012009 pt in MuPDF. It is development negative evidence (`development/independent-kerning-negative.json`), not a release capability. Additional font-metric gating now restricts that fixture and related ReportLab character-spacing examples. No tolerance was raised.

Word Arial and Calibri first lines activate and pass two-generation exports (`cafe calm. cafe calm.` -> `ccfe calm. cafe calm.` -> `ccfe cclm. cafe calm.`). Reference lines can activate but were not independently edited here. Word Consolas remains limited: its already-natural line hits the existing ownership check; coexistence was not extended to the natural model. The new genuine Word multiple-run document remains ambiguous on its mixed-font first line; no run merging or mixed-style editing is added. PowerPoint remains restricted by graphics/ownership. See the per-document matrix for counts and evidence.

Repeated saves may add another resource **alias** pointing to the same existing font dictionary (observed object 5 under FXF2 and FXF3). Independent checks distinguish aliases from new font programs or mappings. Alias accumulation is retained as an open issue, not described as font extension or byte-identical resource dictionaries.
