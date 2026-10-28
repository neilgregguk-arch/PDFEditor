# Phase 4B multi-region validation

## Source-bound transaction

The request carries source SHA256, document revision and every modified region's page, ID, source fingerprint and complete draft. There must be between 1 and 128 changes. Duplicate page/region ownership, stale source, missing/ineligible regions, identity mismatch or shared target object pointers fail before mutation. Fresh discovery and original font handles come from a single loaded source. Source fingerprints are checked again before commit.

All plans are computed before replacing objects. Same-page proposed line rectangles are compared with a 0.5 point pad. The worker compares planned geometry against the union of untouched neighbours, images/graphics and page-safe bounds. It does not treat another changed source object as an untouched obstacle; it uses that region's proposed replacement geometry instead. Final reopened ink bounds are checked again against other changed regions and protected objects. Drafts survive any rejection, and affected-region warnings are returned where the conflict can be attributed.

The collision fixture deliberately places a second tiny period below the first region. Each replacement alone saves and verifies. The first becomes three lines, the second becomes a normal line; together their proposed line extents overlap by one point. The combined request fails with both region keys. This proves a conflict beyond two isolated successful exports. No unrelated text is moved and no font is shrunk.

## Strategy fidelity

Natural paragraphs retain existing eligible fonts, mappings, advances, wrapping and safe expansion boundaries. Unsupported glyphs and unsafe geometry block the whole request. Position-aware Word runs retain explicit original glyph origins, ASCII standalone embedded TrueType constraints, horizontal single-object eligibility and the pinned PDFium position setter. They permit only same-count equal-or-narrower substitutions under the established checks. A mixed request does not relax those rules. The synthetic mixed fixture combines unchanged genuine Word text streams with a separately generated eligible natural region for testing; document merging is not an application feature.

The PDFium DLL remains version 156.0.8076.0, SHA256 `bede3932ce96a2e1ed9a7e6cae71aec8914efd2907d37ab44b1b81f9c8a6d04e`.

All original target pointers are collected before replacement. The union is removed, replacement runs are created using each original font and strategy, and changed pages generate content once. One candidate PDF is saved for the entire transaction. Deletion of a supported natural paragraph is represented by removal with no replacement run; a concurrent valid edit still participates.

## Complete candidate verification

The worker saves and reopens the candidate and source. It verifies page count, dimensions, annotation counts, document info metadata, exact intended replacement run text/count, original font programs/style and glyph outlines, font reconstruction and safe bounds. Untouched object types/text/font/style/bounds and glyph Unicode/origins/bounds are compared. Unmodified pages are pixel-equal at 72 DPI. Changed pages have zero differing pixels outside the union of authorised areas at 144 DPI with channel-difference threshold 8. The current page preview PNG is not the scope of verification: all affected pages and all unmodified pages are checked.

Retained tolerances: untouched glyph/object geometry 0.01 pt; positioned origins and unchanged positioned glyph bounds 0.01 pt; natural local advance 0.05 pt, cumulative position 1 pt and baseline 0.15 pt. Changed positioned glyph ink must not overlap other letters. These limits were not relaxed for combined editing. Nonpainting zero-extent Word spacing objects retain their narrow position-strategy exception and survive as separate original objects.

Independent development verification uses MuPDF extraction and glyph geometry, pypdf font programs/used encoding/width/ToUnicode/CIDToGID rules and protected raw whitespace bytes, pikepdf/qpdf syntax checks and Poppler full-page renders at 72 and 144 DPI. Every page of each recorded successful combined export is checked, including UI, separate-process recovery and second-generation outputs. Wrapped extraction is whitespace-normalized where independent readers differ in trailing-space representation, while intended PDF run text is checked exactly by the worker. The independent parser now assigns trailing target wrap spaces to their target; no geometry or pixel threshold was weakened.

Used font programs and mapping rules remain stable. PDFium can prune unused font entries and create duplicate resource aliases, so whole unused resource dictionaries are not claimed byte-identical. All combined exports must contain all requested edits; no valid-only partial export path exists.

## Commit and failure behaviour

Original/existing destinations are rejected. A validated candidate is copied to a unique file beside the destination, checksum and source are rechecked, then File.Move with overwrite disabled commits it. Failed final moves clean their stage and preserve drafts. Candidate retention keeps twelve PDFs and twelve PNGs per work directory when cleanup is possible. Advisory cleanup errors cannot change a committed save to a failed result. Output to a non-existing filename is atomic within the destination filesystem; power-loss durability and exotic network filesystem semantics are not certified.
