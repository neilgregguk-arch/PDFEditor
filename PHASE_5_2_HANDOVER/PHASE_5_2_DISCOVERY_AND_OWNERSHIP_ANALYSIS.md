# Phase 5.2 discovery and ownership analysis

## Evidence categories

| Category | Findings |
|---|---|
| Observed | Original Word producer, unmarked text members/content order, shared native Span/MCID/Lang, raw Document/P/K/Pg and indexed ParentTree/StructParents links, exact characters, font programs/mappings, transforms, style, glyph origins/boxes, baselines and neighbours. |
| Inferred | Uniform horizontal rows/leading and common left edge support bounded reflow. Available right margin and safe bottom are conservative editing policy, not recovered Word layout instructions. |
| Unknown | Full authoring intent, the original Word layout model, truthfulness of consistently authored tags, arbitrary untagged boundaries and ambiguous missing separators. |

There is no numerical confidence score. Geometry alone cannot grant the new ownership. The shared P relationship is actual structure; compatible visual rows support its bounded editing. Consistent tags do not authenticate author intent or producer identity.

## Acceptance chain

1. Validate Phase 5.1 declarations first. Invalid private members cannot be promoted through this mechanism.
2. Identify multiple complete unmarked candidates sharing a numeric MCID, under explicit count limits. Require native Document -> P -> exactly one page-scoped content ID without conflicting supported attributes/ActualText.
3. Independently resolve required raw objects through supported xrefs. Verify page identity/backlinks, one Document root, raw P role/type, parent backlink, Pg, single K integer and the exact ParentTree entry at that MCID. Reject duplicate children/associations, missing entries and changed backlinks. Native resolved roles and raw roles must agree.
4. Require identical actual native semantic handles across all members. Matching numeric MCIDs in separate native scopes are insufficient. Account for every painting object in the scope. Only verified nonpainting whitespace after the last member may remain separately protected in the same scope.
5. Require 2–8 contiguous painting members in content order, independently eligible positioned rows, matching embedded font/mapping/size/paint, common X, ascending baselines, consistent leading and substantial continuing rows. No mixed-style or interleaved-paint reconstruction is granted.
6. Require an actual trailing space on each continuing row and no ambiguous leading/repeated boundary spaces. Concatenate the verified member strings exactly; add no invented space or newline. Missing/ambiguous separators restrict the group.
7. Construct immutable source-row observations and fingerprint-bound ownership. Apply inherited columns, graphics, neighbour, envelope and proposal checks. Structure cannot override unsupported reconstruction, clipping, rotation, collision or unsafe space.

Reasons include `ORIGINAL_PARAGRAPH_STRUCTURAL_SCOPE_UNPROVEN`, `ORIGINAL_PARAGRAPH_MEMBER_GUARD`, `ORIGINAL_PARAGRAPH_STYLE_OR_SCOPE_MISMATCH`, `ORIGINAL_PARAGRAPH_EXTRA_SCOPE_CONTENT`, `ORIGINAL_PARAGRAPH_INTERLEAVED_PAINT_ORDER`, `ORIGINAL_PARAGRAPH_SEPARATOR_AMBIGUOUS`, `ORIGINAL_PARAGRAPH_READING_ORDER_OR_LEADING`, short-row and budget refusals. Observed diagnostics retain underlying raw-structure failures. Editable originals expose `Paragraph.Evidence=ExistingDocumentParagraphSingleMcid` plus structural/separator verification.

## Text, whitespace and observations

In the cafe original, the first text object contains the actual trailing word space and the second continues the same P/MCID. MuPDF drawing traces independently equal both member strings and their concatenation. A separate final F2 space remains outside the owned union and is preserved unchanged. It is never used to manufacture an inter-row separator. Interposed standalone whitespace rejects interleaving. Foreign/next-paragraph whitespace protects its boundary; nonpainting coexistence establishes no ownership.

Every source row retains its font mapping, baseline, glyph positions/boxes, exact text and logical start. The planner's temporary flattening copy is not actual source geometry. Source-row boundaries prevent inheriting an overlap/spacing exception across unrelated rows. Identity binds the complete source hash, page/member IDs, rows, font/mapping/style/geometry, proof and envelope. Neither an ID nor cached observations override a changed source.

## First save and semantics

The in-memory original proof is created only after structural qualification. No private mark is added to the original input. First verified save inserts genuine original-font rows before the live source anchor, copies the shared native semantic mark and removes only the owned members. The original structure graph/semantic sequence remains unchanged. A fresh private declaration is then validated on the reopened candidate. Later generations use the unchanged Phase 5.1 schema and full-member validation. Every changed region must succeed together; no valid-subset save is allowed.

## Native API and conservative limitations

[PDFium's public structure API](https://pdfium.googlesource.com/pdfium/+/refs/heads/main/public/fpdf_structtree.h) and [page-tree implementation](https://pdfium.googlesource.com/pdfium/+/refs/heads/main/core/fpdfdoc/cpdf_structtree.cpp) explain native parent-tree loading. The latest header's GetRawType export is absent from the pinned binary. Available resolved-role APIs plus the raw cross-check are used; PDFium was not upgraded and a newer ABI is not assumed.

The narrow reader refuses xref-stream-only files, predictors/unsupported filters, escaped structural names, complex P children, unsupported attributes/semantic overrides, cross-page paragraph structures and exhausted budgets. Harmless documents can therefore remain unsupported. This is a second bounded structural check, not a general PDF interpreter, native sandbox or PDF/UA validator. Wider parser/native/font fuzzing remains open. No role fabrication, semantic repair or tag mutation makes an original qualify.

The new corpus uses the bundled renamed Bitstream-derived Prototype Sans. Actual embedded programs, names, hashes and fsType=4 were inspected; requested font names alone are not evidence. The attached existing licence permits redistribution/modification under its notice/naming conditions. This fixture-specific check does not resolve inherited proprietary-font corpus rights or the repository-wide licence.
