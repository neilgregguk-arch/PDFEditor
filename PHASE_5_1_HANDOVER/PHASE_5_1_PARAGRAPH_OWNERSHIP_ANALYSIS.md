# Phase 5.1 paragraph ownership analysis

## Evidence categories

Observed document facts are complete text objects, transforms, style/paint, embedded programs, verified mappings, actual Unicode glyphs, origins, bounds, baselines, page properties and neighbouring objects. Embedded declarations supply a proposed stable identity, ordered members, exact logical string, soft boundaries and an envelope cap. Inference remains limited to conservative available-space/leading policy. Neither visual proximity nor the declaration alone proves paragraph ownership or authentic editor origin.

| Candidate mechanism | Assessment |
|---|---|
| Proximity/indent/font/leading alone | Insufficient to establish ownership; no new heuristic promotion was added. |
| File sidecar | Loses portability and binds to external state; not used to satisfy reopening. |
| Document XMP/custom catalog metadata | Portable but separated from members; would require a separate PDF object-reference writer/resolver. Not selected. |
| Accessibility StructTree/MCID identity | Existing semantics must be preserved, not invented or repurposed as application storage. Not selected for paragraph identity. |
| Custom marked content attached to each actual row | Selected: public APIs in the pinned PDFium expose it, it travels with genuine content, can be bounded and independently inspected, and need not claim accessibility semantics. |

The PDF model for marked content is described in [Adobe PDF Reference 1.7, section 10.5](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/pdfreference1.7old.pdf). Public mark and insertion APIs are documented in [PDFium fpdf_edit.h](https://pdfium.googlesource.com/pdfium/+/main/public/fpdf_edit.h). These APIs are experimental; this implementation is tested against the pinned shipped binary, not arbitrary future builds.

## Final schema and lifecycle

Tag `/PDFEditorV2_Paragraph` has exactly `/Data` and integer `/Row`. Data is a UTF-8 JSON blob with schema Version 1. A new lowercase 32-hex GUID is allocated for the first marked export. Later generations retain it, even when row count changes. Identity is unique across pages within a file. Members carry identical common payloads and distinct contiguous row indices. Physical object indices are rediscovered from the actual marked objects, never dereferenced from an arbitrary metadata path/reference.

The payload contains page index/dimensions, exact ASCII-model logical text, original font-program and verified-character-mapping hashes, size/colour/anchor/ascent/line height, envelope cap, existing semantic-mark signature, and ordered rows with text, baseline, origins and observed character boxes. Row starts are obtained by exact cumulative lengths. Soft rows concatenate without newlines; no whitespace is trimmed. Metadata geometry is rounded to 0.001 pt to keep the blob compact. Actual observed origins remain full precision, reconstruction bitmaps use those exact observed offsets, and the existing 0.01 pt checks are unchanged. Character boxes include native space extents, which are not visible ink.

The envelope is a cap, not permission to occupy everything inside it. Current page margins, protected objects, source-safe bottom, eight-row cap and per-proposal collisions remain authoritative. Reopening rebuilds those observations from the new file. An external neighbour can reduce available space; the declaration cannot remove that neighbour or expand past the independently checked page margins.

## Acceptance and rejection

Acceptance requires the complete member set, one mark per member, identical payloads, valid row sequence, exact actual row text, original font/mapping agreement, supported transforms/paint/clipping, expected baselines, strictly ordered origins, measured glyph boxes and exact row reconstruction. The whole grouped source must fit its envelope and the source's current protected-content rules. Unsupported/ambiguous members cannot be promoted by metadata.

IDs, object/page counts, text lengths, types, finite numbers, schema keys, duplicate JSON keys and cross-page conflicts are checked. Limits: 512 logical characters, eight members, 28,000 bytes per payload, 16 marks/parameters per object/mark, 128 groups/1,024 claims per page, 4,096 page objects, 8 MiB metadata budget, and a bounded document index of 256 pages/65,536 objects. JSON depth is 16. Index caching is capped at four source hashes. Budget failure restricts grouping; no unbounded scan, external file lookup, URI execution or executable action is driven by metadata.

Missing, duplicated, changed or conflicting members reject the group. Rejected marked objects do not fall back into new proximity grouping. A member whose mark is entirely removed can still qualify independently under unchanged legacy single-object rules; it is never silently reabsorbed into the old group. If all marks are stripped, only the previous unmarked classifications remain. A fully consistent declaration can be authored by another tool: this is content consistency and conservative ownership validation, not cryptographic authentication of the producing editor or proof of human paragraph intent.

## Existing accessibility and reading order

The genuine Word fixtures already contain `/Span` MCIDs and language. Replacement rows share the original native semantic mark and are inserted before the source object while that object still supplies its content-stream anchor. This avoids appending a second MCID sequence at page end. Group members must share the same actual semantic scope, not merely matching MCID numbers. Only supported existing Span/MCID/Lang scopes are transferred. Different, unsupported or changed semantics are refused rather than stripped or recreated.

The private mark adds no MCID, ActualText, Alt, Artifact designation, RoleMap entry or structure-tree paragraph role. Existing semantic sequences, StructTreeRoot graph, page StructParents, MarkInfo and document Lang are independently compared. Source structure preservation is not PDF/UA certification or repair of pre-existing accessibility defects.

## External editing and compatibility

A pikepdf save that retains consistent declarations passes another editing generation. Text/position changes, missing/duplicated rows, conflicting IDs, modified semantics and malformed payloads are refused. Other applications may discard private marks; the file remains ordinary selectable PDF text, but whole-paragraph re-editing is then unavailable. Legacy C2 wrapped outputs lack the declaration and are not retroactively promoted. General original Word multi-line discovery, mixed-font reconstruction and cross-page paragraph continuation remain out of scope.
