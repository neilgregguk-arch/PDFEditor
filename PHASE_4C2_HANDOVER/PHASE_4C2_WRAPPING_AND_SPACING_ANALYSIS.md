# Phase 4C.2 wrapping and spacing analysis

## Logical text and word breaks

Concatenating positioned plan row texts reproduces the exact draft. A separator at a soft break stays in the preceding text run. Leading, trailing and adjacent spaces are not trimmed or normalised. The greedy planner fits verified advances and measured ink, prefers the last fitting space and falls back to a character boundary for an uninterrupted word. A glyph too wide for the available area blocks export. Typed newlines are hard breaks: positioned export remains refused, and the draft/recovery retain the newline. Existing natural paragraph hard-break behaviour is retained.

## Conservative ownership

The left edge is the original anchor. The right edge uses the previously established safe limit, reduced by protected content ahead of the original line. The bottom uses source SafeBottom and nearby protected objects below the original baseline, with existing separation. Eight rows impose a further cap. This is a conservative editing envelope, not ownership of arbitrary empty page space. Neighbours never move.

Original source observations, indices, font probes and identity remain immutable. The position path's existing exception covers independently verified nonpainting, zero-extent coexisting whitespace only; these objects remain untouched in the PDF. Natural ownership rules are not broadened. Combined edited envelopes are checked together. The collision fixture proves actual proposed descender/ascender ink overlap, beyond merely overlapping envelopes.

## Glyph positioning

The C1 equal-length/equal-or-narrower substitution path keeps fixed origins. Other edits use bounded deterministic longest-common-subsequence alignment, without claiming the user's intended correspondence. Surviving adjacent source pairs can retain their observed residual on row one. Insertions and changed joins use verified original-font advances.

Each later row starts at the original X and advances naturally using the original font. No source residual crosses a new row boundary or is transplanted into later rows. Surviving glyph ink translates with the proposed X/baseline; it is not resized. New joins must satisfy ink checks. Only an original surviving sequence on row one retains the existing overlap exception. New rows have no blanket exception.

Each PDF run uses its own row-relative offsets. A one-character run has zero offsets and uses only its transform. Calling the native SetPositions API with count zero caused a real development export failure; the unnecessary call is now omitted. Tests cover a single-character draft and a 68-character uninterrupted word that emits rows of 67 and one characters.

## Baselines and leading

The first baseline stays original. Step is `max(2 * originalFontSize, verifiedInkHeight + 3 pt)`, spanning the measured supported glyph ink. Demonstrated 12 pt Word fonts use 24 pt leading. This is an intentionally generous inference for legibility and conservative line rediscovery, not recovered Word paragraph formatting. Saved baselines must match within 0.01 pt; fontTools independently derives font bounds and checks the step.

Every row envelope and glyph ink must remain in the safe rectangle and outside protected content. Vertical overflow preserves the complete draft and refuses the combined save. The original bounds and strict neighbour/glyph thresholds are unchanged.

## Presentation and rediscovery

Active glyphs, inactive drafts, caret, selection, hit testing, PDF mutation and reopen verification consume the same plan. Up/Down use a preferred X. Home/End use proposed row boundaries. Shift commands and mapped drag select continuous logical spans across soft wraps. Row affinity is presentation state, not a newline or history entry. WPF remains the text/selection owner.

Saved rows are independent genuine text objects. Discovery remains conservative, with no synthetic ownership tags or sidecar. An eligible first emitted row can be edited and saved again. Other rows may be independently editable or Limited, especially when separately owned Word whitespace prevents natural qualification. The app does not infer whole-paragraph ownership merely because it emitted neighbouring rows. Full paragraph round-trip editing remains limited.

Independent MuPDF/pypdf/fontTools/Poppler/pikepdf checks cover exact logical text, row separation, font programs and used mapping rules, computed glyph origins/baselines, untouched geometry, raw whitespace and 72/144-DPI outside-region pixels. Explicit natural hard breaks are reconstructed separately; positioned soft wraps always concatenate exactly without whitespace normalisation.
