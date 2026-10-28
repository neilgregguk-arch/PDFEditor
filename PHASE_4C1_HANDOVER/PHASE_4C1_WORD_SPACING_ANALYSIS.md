# Phase 4C.1 Word spacing analysis

## Evidence and interpretation

`phase4c1/evidence/word-spacing-analysis.json` records fresh source hashes, producer, original content streams, TJ/Tj/Tf/Tm/Tc/Tw/Tz operands, font programs, ToUnicode data, raw encoded character codes, Unicode mappings, CID/GID observations, font advances, original glyph origins/bounds, style, transforms and protected objects. The sources are genuine Word-produced `corpus/11-word-letter.pdf`, `font-corpus/Word-Arial.pdf` and `font-corpus/Word-Calibri.pdf`. Development fixture composition does not re-author their Word text.

The existing source eligibility checks remain: complete single horizontal object, identity supported transform, opaque supported style, verified standalone embedded TrueType program and reverse character mapping, exact original reconstruction, glyph baseline/ownership and native metric compatibility. Multi-font/fragmented lines, visible whitespace interference, clipping/rotation, graphics through original text and unsupported mappings remain restricted.

Measured maximum absolute inter-glyph residuals are 0.333984 / 0.166168 / 0.683907 pt for the three letter lines; Arial sample lines 0.096001 / 0.146011 pt; Calibri lines 0.302124 / 0.302094 pt. These are `next origin - current origin - verified font advance`. They include Word/PDF spacing and width effects. They are observations, not proof of deliberate author kerning. The horizontal outer limit is approximately x=523.296 pt, inferred from the original page's conservative right margin. Protected objects can block a proposed line before that limit.

The letter source uses embedded Type0 Identity-H Arial. Its five separate nonembedded F2 whitespace objects remain independent. Code zero and code six can both decode as space in F1 while referring to different glyph identities; existing outline/width/context roundtrip checks choose safe mappings. The planner never invents raw codes or substitutes fonts. The letter font has 32 verified ASCII mappings, the Arial and Calibri samples 16 each; having a Unicode character in the original TrueType program alone is not sufficient for eligibility.

## Explicit mapping policy

For existing equal-or-narrower same-count substitutions, preserve every original glyph origin exactly as before. New replacement glyphs must fit and survive the existing extraction/outline/geometry checks; that legacy path is not reset to natural spacing.

Other edits use a bounded longest common subsequence between immutable original Unicode and current draft. Equal symbols match immediately; if deletion and insertion branches tie, skip an original symbol. Ambiguity is recorded, including alternative equal-symbol matches. This deterministic policy does not infer typing history or author intent, and repeated letters/words can align differently from the user's conceptual edit. It is stable for the same source and draft after recovery.

Mapped unchanged characters are `Surviving`. Unmatched old/new symbols between consecutive surviving anchors are paired in order as `Replaced`; extra new symbols are `Inserted`; remaining old symbols are `Deleted`. Replacement-source indices are separate from surviving indices. Classification of ambiguous replacements is descriptive only: it never grants preservation of a spacing relationship between changed characters.

## Position calculation

The first surviving or inserted draft glyph is anchored to the original line x. For each following glyph, add the preceding draft glyph's verified original-font advance. Add an original measured residual only if this glyph and its immediate predecessor map to consecutive unchanged original characters. At inserted/replaced joins and deletion seams the adjustment is zero. Accumulate in double precision; pass N-1 float offsets relative to source x to the pinned native API. Reopened origins must agree within 0.01 pt.

An unchanged source subsequence therefore keeps its internal measured distances and glyph shapes, translated as a block when edits precede it. Prefixes before an edit remain fixed. After deletion, the new join closes using the surviving preceding glyph's advance; text is not stretched to the old width. Beginning insertion shifts the original sequence to the right; beginning deletion moves the remainder to the original anchor. Unchanged adjacent pairs preserve their observed residuals even when their absolute origins shift.

Inserted glyph ink is measured through the same original PDF font in temporary native text objects. Surviving glyph bounds are translated from immutable original observations. New edited joins cannot introduce overlapping letter bounds. Overlap already evidenced inside a fully surviving original sequence is retained, rather than treating every original f/f ink overlap as a new defect. Final saved glyph ink and outlines are checked independently of the planner's logical width.

## Boundaries and known refusals

The planner checks logical extent and ink against the conservative right limit and vertical line envelope, then protected objects with a 0.5 pt pad. Combined transaction validation also checks other edited regions and final saved extents. Authorised pixel comparison covers only original and proposed extents plus the existing two-point verification padding, not the whole available blank page width. No font shrinking, moving neighbours or positioned wrapping is used.

A newly inserted third f in `Offfice` is refused because it introduces overlapping glyph bounds at a new join. Existing original `ff` relationships are preserved. A double-space insertion is refused when PDFium's saved extraction collapses the intended text. These are documented safe refusals, not certified insertions. Removing a complete line removes only that region's text object; the five separately owned F2 strings/objects in the letter fixture survive unchanged, with independent raw-byte checks.

## Independent and presentation evidence

Independent verification recomputes the alignment, reads advances from fontTools original font metrics and uses MuPDF source glyph geometry to recalculate expected surviving-pair origins. It compares each saved inserted/repositioned origin to that independent proposal, checks translated survivor bounds and retains strict neighbour geometry. pypdf checks font/mapping/width rules and protected whitespace bytes; qpdf and Poppler verify complete files and pixels.

The independent line parser initially mixed an unchanged separate F2 space into the horizontally expanded title when sorting glyphs by x. It now identifies standalone all-space spans separately; those spaces remain in the untouched-object comparison and raw-byte checks. Intended text is still checked exactly. No position or pixel threshold was changed.

Visible positioned caret/selection now use proposed geometry. Hidden native WPF caret measurements are retained separately; they are not a PDF geometry tolerance. Tests exercise four zooms at the workstation's actual 96 DPI. Other OS display scales and hardware interaction remain manual review items.
