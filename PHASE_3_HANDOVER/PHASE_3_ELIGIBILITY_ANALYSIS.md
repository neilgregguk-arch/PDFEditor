# Phase 3 eligibility analysis

28 October 2026. Classification is a conservative implementation gate, not proof of recovered author semantics. Final export still requires independent candidate reopening and preservation checks.

## Observations versus inference

Observed data comprises page object indices/types/bounds, each text object's PDFium extraction, character ownership, origins/bounds, baseline, transform, font size, fill colour/alpha and original embedded font program identity. Region `Observed`, `ObservedBounds`, `Glyphs`, `Objects`, `OriginalLines` and document `PageObjects` make these inspectable.

Candidate visual lines are complete top-level text objects. Candidate paragraphs are ordered geometrically and joined only when left edge, font, size, colour, natural spacing and regular leading agree, and the preceding line is at least 70% of the conservative width. `Inferred` records grouping and margin/space rules. PDF extraction order is not treated as reading order. PDF tagging is not currently used to prove paragraph semantics; nested form text is unsupported.

Width is the page width minus the left origin and a symmetric right margin of at least 20 pt. This deliberately refuses many indented/right-column cases. Safe bottom is the page boundary minus 20 pt, capped by the nearest lower overlapping object minus 3 pt. A proposed line box must also avoid every unrelated object's bounds. This keeps content fixed rather than moving it to make room. The nominal font line box can be more restrictive than visible ink.

## States

| State | Meaning in this implementation | Examples / reason codes |
|---|---|---|
| Editable | Complete object/glyph mapping, original embedded font cmap and encoding probe, supported horizontal spacing/paint and usable inferred space. Commit still conditional on the full verifier. | `COMPLETE_OBJECT_OWNERSHIP`, `EMBEDDED_FONT_CMAP_AND_ENCODING_PROBED`, `NATURAL_HORIZONTAL_GLYPH_GEOMETRY`, `CONSERVATIVE_SPACE_AVAILABLE` |
| Limited | Identifiable text with an ownership/space restriction. Editing is disabled for this phase; no implicit permission to reconstruct it. | `AMBIGUOUS_SHORT_LINE_PARAGRAPH_BOUNDARY`, `GRAPHIC_IMAGE_OR_TABLE_INTERSECTION`, `INSUFFICIENT_VERTICAL_SPACE` |
| View Only | The required modification mapping, font or supported paint/structure is unavailable. Other restriction reasons may also be attached. | `FONT_NOT_EMBEDDED`, `ORIGINAL_FONT_MAPPING_UNAVAILABLE`, `INCOMPLETE_GLYPH_OWNERSHIP`, `NON_NATURAL_GLYPH_SPACING`, `UNSUPPORTED_TRANSFORM`, `UNUSABLE_EMBEDDED_FONT` |

Document signatures, encryption, AcroForm type, current-page rotation/annotations or top-level form objects cause conservative view-only classification. Non-ASCII text, unsupported transforms, non-fill rendering, transparency, clipping, unsupported sizes and bad page bounds also block editing. The raw diagnostic remains machine-readable; the prototype status displays reason codes. A View Only region can carry additional layout reasons without being promoted to Limited.

## Corpus examples

| Document in `phase3/run/corpus/` | Actual classification / grouping |
|---|---|
| `01-letter.pdf` | Five Editable regions. The two body lines join; heading, salutation, next paragraph and closing remain separate. |
| `02-report.pdf` | Heading, three-line regular paragraph, blue 10 pt note and bold 14 pt summary remain separate Editable regions. Page two is analysed only when requested. |
| `03-adjacent.pdf` | Same-baseline label/value are unsupported; isolated body text remains Editable. |
| `04-two-columns.pdf` | Ten separate unsupported lines; no cross-column joins. Right-column margin assumptions and extraction-generated spaces add refusal reasons. |
| `05-table.pdf` | Six unsupported cell text regions; path objects observed. No cell reflow or table reconstruction. |
| `06-ambiguous.pdf` | Two Limited regions. Short preceding line means a paragraph join cannot be justified. |
| `07-rotated.pdf` | View Only: unsupported transform. |
| `08-nonembedded.pdf` | View Only: original embedded font unavailable; no substitution. |
| `09-mupdf-letter.pdf` | Three Editable regions from an independent generator. Genuine save verified. |
| `10-mupdf-subset.pdf` | View Only: current cmap/encoding probe cannot establish usable full ASCII mapping. |
| `11-word-letter.pdf` | Actual Microsoft Word 16.0 export. View Only: subset mapping and object/space restrictions; Word editing support is not claimed. |
| `12-image-overlap.pdf` | Limited intersecting text/image area; image boundary observed. |
| `13-shuffled-order.pdf` | One Editable paragraph in visual order `[1,2,0]`, despite reversed content-object order. Genuine save verified. |
| `14-annotation.pdf` | View Only page with a link annotation. |
| `15-letter-spacing.pdf` | View Only because observed character positions do not follow the supported natural spacing model. |

## Correct and potentially incorrect grouping

The letter/report and reversed-object-order examples demonstrate intended joins. The adjacent labels, columns, table and short-line example demonstrate joins deliberately refused. A larger vertical gap or style change ends a paragraph. Stable normal leading and a long preceding line are necessary, not sufficient, evidence of semantic continuity.

An author can place two unrelated long lines at identical left edges, styles and normal leading. Those can satisfy the current rule and be incorrectly grouped. A tight heading with the same font can also be ambiguous. Conversely, justified text, kerning, indents, hanging lists, mixed styles and fragmented office lines can be rejected even when a human sees a simple paragraph. These are unresolved false-positive/false-negative risks, not measured probabilities. Corpus correctness must not be generalised to arbitrary PDFs.

Original visual line breaks are imported as explicit draft breaks; authored hard breaks cannot be reliably distinguished from visual wraps. This phase does not recover a complete word-processing paragraph model. Users should inspect the activated text and save to a new file. A region's Editable label alone does not establish general document fidelity, accessibility order, tagging or annotation integrity.
