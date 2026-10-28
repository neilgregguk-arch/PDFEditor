# Phase 4A analysis of the original Word PDF

28 October 2026. Source: the unchanged `phase3/run/corpus/11-word-letter.pdf`, copied into Phase 4A's corpus. It was genuinely exported by Microsoft Word 16.0. This analysis separates font-program, encoding, positioning and ownership restrictions.

## Structure

The document has one A4 page, approximately 595.32 x 841.92 pt. PDFium observes eight top-level text objects. The three visible lines are complete objects 0, 3 and 6, all regular Arial 12 pt with identity horizontal matrices. Their baselines are approximately 83.30, 131.30 and 179.18 pt. Despite multiple strings/numeric adjustments in each TJ array, these visible lines are **not fragmented into separate word objects** in PDFium.

Objects 1, 4 and 7 are separately styled trailing spaces at x approximately 180.53, 484.20 and 366.31 on those baselines. Objects 2 and 5 are spaces on intervening blank-paragraph baselines. The F2 font used by these whitespace objects is not embedded. Their boundaries participate in ownership/collision checks even though the candidate-region list omits whitespace-only text.

The content also contains Word MCID/language marked content and full-page clipping operators. This phase does not establish tagged-PDF preservation or recover Word paragraphs from that structure.

## Font programs and mappings

F1 is `/BCDEEE+ArialMT`, a Type0 font with Identity-H encoding, a CIDFontType2 descendant, embedded TrueType program, explicit widths, CIDToGIDMap stream and ToUnicode CMap. Its `maxp` table retains 4,651 glyph slots; this does **not** mean 4,651 usable characters survive subsetting. Many outlines are empty. The font has a usable cmap with only a limited set of Unicode entries. Its OS/2 embedding flag is 8; this is a recorded flag, not a general legal permission determination.

The PDF's ToUnicode map covers character codes 0 through 32, with 32 distinct Unicode values because codes 0 and 6 both map to U+0020. Their glyph identities differ: code 0 selects GID 0 (`.notdef`) and width 750; code 6 selects GID 3 (the genuine space) and width 278. A Unicode extraction match alone cannot establish that the selected space code is visually correct.

Phase 4A verifies 32 ASCII characters through the current PDF reverse mapping, outline and width. Another 13 ASCII characters have usable embedded cmap entries but fail the existing PDF encoding round trip. Fifty ASCII characters lack usable subset cmap coverage. This distinguishes a retained glyph that is not PDF-encodable from a character unavailable through the embedded subset's cmap.

The original visible text uses verified characters. The broad font blocker is therefore removed for those original characters. No encoding or font program was extended to achieve that result.

## Why Phase 3 rejected it

Phase 3 constructs one alphabet string from the font's available ASCII cmap entries. Unmapped retained characters cause that whole probe to fail, leaving every advance unavailable. It then reports `ORIGINAL_FONT_MAPPING_UNAVAILABLE` and may derive `NON_NATURAL_GLYPH_SPACING` from unavailable advances. That second result was not, by itself, an independent measurement of the Word line's real spacing.

Phase 4A assesses each character separately and can compute the actual initial text metrics. With valid initial character advances, the Word file still has independent restrictions below. Removing the broad probe alone does not make it Editable.

## Independent remaining blockers

| Blocker | Measured evidence | Consequence |
|---|---|---|
| Explicit TJ spacing | Maximum local differences from the embedded font's natural advances are approximately **0.3340 pt**, **0.1662 pt** and **0.6839 pt** for objects 0, 3 and 6. Cumulative differences reach about 0.2408, 0.2772 and 0.8020 pt. | The unchanged 0.05 pt local spacing rule fails. The current natural inline model cannot reproduce these initial positions. |
| Original reconstruction | A fresh natural text object with the same Unicode, font, size, colour and transform does not exactly reproduce the original object's bitmap. | `INITIAL_OBJECT_RECONSTRUCTION_DIFFERS`; activation remains blocked even if extraction succeeds. |
| Ownership/space | Conservative inferred region widths include independently owned trailing F2 whitespace objects on the same baseline. | `OWNED_SPACE_INTERSECTS_NEIGHBOUR`; ownership is not silently expanded to absorb another-font objects. |
| Unsupported proposed characters | Thirteen retained ASCII glyphs are not verified through the existing PDF encoding; other characters lack subset cmap coverage. | Those characters remain individually blocked. A cmap entry is not treated as an encoding guarantee. |

The final visible regions remain **View Only**. Their machine reasons are recorded separately in the compatibility matrix. No geometry threshold, collision rule, whitespace exclusion or mixed-style ownership rule was weakened to promote them.

## What the pinned PDFium APIs can do

The API lab uses known object indices and mappings independently inspected with pypdf/fontTools. It is deliberately separate from product eligibility.

| Mechanism | Actual result after save/reopen |
|---|---|
| `SetText` with existing characters | `Office letter` extracts correctly with the original font and stable unrelated glyphs. Natural positioning replaces the targeted object's original TJ spacing. |
| `SetCharcodes` with verified existing codes | Same intended replacement and render as the existing-character SetText case. No arbitrary code guessing is needed in the lab because the actual ToUnicode and CIDToGIDMap were inspected. |
| `SetText` with an unmapped `!` | API returns success, but reopened object text is `Office ` rather than `Office!`. The product's character/whole-text checks reject this case. |
| Correct text plus `SetPositions` | Real nonempty position arrays return success, survive save/reopen and restore original glyph positions. The unchanged-title experiments render identically to the original page in Poppler at 72 and 144 DPI. |
| Equal-width edit plus explicit positions | `Phase` -> `Phace` changes a genuine existing glyph while preserving the positions of other glyphs. Original font programs and document info metadata remain; changes stay inside the title row. This is a known-object experiment, not an activated product feature. |
| Wrong space code 0 | Reopened Unicode still says `Office letter`, but the glyph is wrong. Compared with the correct-code render, **235 pixels at 72 DPI** and **730 at 144 DPI** differ. All changes remain inside the edit area, showing why isolation and extraction alone are insufficient. |

The lab originally compared ctypes pointer wrappers rather than native addresses, producing empty ownership lists and vacuous zero-shift results. That driver was corrected, nonempty ownership/position assertions were added, and the lab was rerun. The earlier JSON is retained as `api-investigation-initial-pointer-driver.json` and must not be used as final evidence. This did not affect the C# production code, which uses native IntPtr equality, or the independent MuPDF geometry checks.

## Words, lines and paragraphs

A known equal-width character/word edit is technically possible with original mappings and explicit positions, as the lab shows. A known complete line can be rewritten using existing glyphs, but preserving arbitrary original kerning through the natural WPF editor is not demonstrated. General paragraph editing is also restricted by ownership of separate whitespace objects and by the absence of a supported mixed-format/explicit-position interactive model.

Next investigation should consider a font-aware, glyph-positioned single-region model and documented ownership of invisible space fragments, with independent glyph/render checks. Raw SetCharcodes should require an inspected, unambiguous selected glyph mapping; it should not be used to bypass failed Unicode probes. Font extension is not needed for the demonstrated existing-glyph cases and is not implemented. These are recommendations for review, not Phase 4B work already begun.

Evidence: `font-investigation.json`, `word-spacing-analysis.json`, `compatibility-matrix.json`, `api-investigation.json` and `api-independent-verification.json` under `phase4a/evidence/` contain the precise programs, mappings, positions and saved outputs.
