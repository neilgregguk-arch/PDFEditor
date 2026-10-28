# Phase 4A implementation report

Date: 28 October 2026. Scope: font, encoding and glyph compatibility in the existing offline Windows WPF/PDFium editor. Previous handovers, implementation and retained evidence were reviewed. The new version is additive under `phase4a/`; earlier source, samples, releases and evidence remain preserved. No Phase 4B multi-region work was started.

## Outcome

Phase 4A separates structural activation, specific draft character support and verified export. It replaces Phase 3's all-or-nothing alphabet probe with independent character observations and verifies the chosen PDF mapping's glyph outline and width. A PDF can be activated when its initial content is supported, while later unsupported input remains editable in the working draft and cannot be exported.

The demonstrated compatibility gain is `J-partial-encoding.pdf`: an independently generated MuPDF document with an embedded TrueType subset whose font cmap includes an unused `Z`, while its PDF ToUnicode map covers only used characters. The frozen Phase 3 binary reports View Only. Phase 4A activates the same bytes, genuinely replaces `cafe calm.` with `face calm.`, supports longer existing-character text and saves/reopens/edits the result again. `Z` remains blocked because a font cmap entry is not sufficient proof of an existing PDF encoding.

The small ASCII-only subset fixtures A/B/C were already editable in Phase 3. They are regression/character-refusal examples, not claimed compatibility gains. The original Word export remains view-only after its broad font blocker is resolved: its original spacing cannot be reproduced by the current inline model, and nearby whitespace objects restrict ownership. Additional Arial, Calibri and Consolas Word exports and an actual PowerPoint export remain conservatively restricted.

## Runnable application

Run `phase4a/run/PdfEditorPrototype.exe` or `phase4a/Launch.ps1`. The default is the newly supported J document. This is the existing .NET 8 Windows Desktop x64 framework-dependent build; the runtime is installed on this machine. Optional self-contained publishing remains unvalidated. There is no installer or disconnected-VM deployment certification.

The WPF interface, native RichTextBox, caret/selection, input, history, wrapping, asynchronous debouncing/revisions, recovery and protected Save As are retained. No replacement modal, permanent diagnostic panel, font shrinking or redesign was added. One changed region is committed per export; save/reopen remains required before changing another region.

## Architecture

`Core/GlyphAnalysis.cs` introduces a page-scoped font analysis object. It extracts each actual PDF font once per analysis, reuses font-program/reference information by program hash and keeps mapping results keyed by the actual native font identity. Two font dictionaries containing identical bytes but different mappings do not share a mapping result merely because their program hashes match.

For each simple ASCII character with a usable embedded cmap glyph, analysis checks:

1. A temporary original-font text object round-trips repeated characters through PDFium extraction. Space uses a verified character on either side because a standalone space is omitted by extraction.
2. The PDF's selected Unicode reverse mapping produces the same outline as an independent scratch-font instance loaded from the exact original program. Segment types, closing flags and coordinates are compared. Normalised outline tolerance is 0.000001.
3. The PDF glyph width agrees with the embedded program's advance within 2 units per 1000. Existing local/cumulative layout tolerances remain unchanged.

The scratch reference uses a simple TrueType font, which correctly handles the ReportLab Mac Roman font-program cmaps in this corpus. A CID reference incorrectly selected missing glyphs for those programs during development and was rejected. References live in a separate in-memory document; they are never inserted into the source or candidate. Temporary original-font probes are always removed and destroyed. Source bytes are never saved over.

Runtime scope remains standalone TrueType programs and ASCII horizontal text. OpenType CFF, collections, arbitrary shaping and Unicode are not broadened. No font cmap, ToUnicode, CIDToGIDMap, widths, descriptors or embedded program is extended or rebuilt in a product export. No fonts are substituted. Font-program extension and new font licensing are therefore not prerequisites for this implementation; original bytes are reused. Independent reports include raw embedding flags without asserting general licensing permission.

## Three eligibility stages

`Region.StructuralEligibility` exposes the existing Editable/Limited/View Only gate. Original glyph ownership, baseline/transform/style, font support for initial text and the conservative ownership/space rules remain necessary. A fresh natural reconstruction of each original object must also render identically in PDFium before activation. This rejects a Unicode interpretation that looks plausible in extraction but cannot reproduce the source glyphs or positioning.

`Region.Characters` records per-character state, glyph ID where available, advance and technical reason. `ProposedTextEligibility` on a region says DependsOnDraft. Layout checks only characters actually present in the proposed draft. Character issues distinguish verified existing mappings, a font glyph without a verified PDF encoding, unavailable subset coverage, missing font Unicode cmap and a mismatched/ambiguous selected glyph. Unavailable cmap coverage is not claimed as proof that no unencoded outline physically exists.

`EditResult.ProposedTextEligibility` and `ExportEligibility` separate supported draft characters from a verified complete export. Supported characters can still fail overflow, collision or integrity checks. The full text remains in the editor/recovery on every failed validation. User messages explain the limitation in plain language; technical codes remain in JSON. Unknown metrics now report `GLYPH_SPACING_UNASSESSABLE`, rather than falsely presenting a derived zero-advance comparison as an independent spacing measurement.

Paragraph joins also require matching character profiles, avoiding a merge merely because two font dictionaries contain the same program but support different mappings. Fragment/column/table rules and numerical collision thresholds were not relaxed.

## Stronger export verification

The original verifier still checks genuine object removal, exact replacement extraction, original font programs/styles, surrounding objects, pages, annotations, selected metadata, unchanged pages, outside-region raster differences, source hash and new-destination protection.

Phase 4A additionally checks every neighbouring glyph's Unicode, origin and bounding box within 0.01 pt. Each replacement glyph must match its planned row/baseline and supported local/cumulative advances. Reopened replacement outlines are compared with the original font mapping, and each saved text object must reproduce its own Unicode interpretation in an exact object render. These supplement raster checks; they do not replace them. This directly addresses Phase 1's shifted-punctuation blind spot.

Controlled manifest fixtures retain their earlier ownership/asset validation route. The new automatic character analysis applies to automatically discovered regions; the stronger candidate verification applies to both routes. Manifests remain experimental ownership declarations, not a signed security policy for arbitrary sidecars.

## PDFium API conclusions

The exact shipped DLL is unchanged: PDFium 156.0.8076.0, SHA256 `bede3932ce96a2e1ed9a7e6cae71aec8914efd2907d37ab44b1b81f9c8a6d04e`. Export availability and actual calls were tested against that binary. `SetText`, `SetCharcodes`, `SetPositions`, character ownership/origins and glyph/font APIs are available. Experimental raw-code/position APIs are declared but **not used by product editing**.

The known-object API laboratory successfully reconstructs the Word title's original positioning and performs an equal-width `Phase` to `Phace` modification while preserving other glyph origins. It also demonstrates that an unmapped character can disappear despite a successful SetText return, and that a wrong space code can extract as a space while rendering the wrong glyph. This is feasibility evidence, not automatic Word editing support. The ordinary inline editor does not yet reproduce arbitrary original kerning positions.

Public contracts/source were checked against [fpdf_edit.h](https://pdfium.googlesource.com/pdfium/+/refs/heads/main/public/fpdf_edit.h) and [fpdf_edittext.cpp](https://pdfium.googlesource.com/pdfium/+/refs/heads/main/fpdfsdk/fpdf_edittext.cpp); the pinned binary's actual behaviour is separately recorded in `api-investigation.json`. A matching release-branch header snapshot was not retrieved; no binary update was made.

## Performance, resources and delivery limits

Pointer-free discoveries remain fingerprint/page cached with an eight-page limit. Native reference fonts are disposed after each page analysis, and repeated objects using the same native font reuse character results within that analysis. The final small-corpus measurements and exact timings are in the test report. There is no in-flight native cancellation, hard per-page font count bound or total session-disk bound. No large/adversarial-document performance guarantee is made.

No Python or external PDF toolkit was added to the runtime. Development uses independent ReportLab/MuPDF/Office generators and pypdf, MuPDF, Poppler and qpdf checks. Runtime processing remains local; no cloud, paid service or network dependency was introduced. Native notices and font licenses accompany the build. Multi-region editing, document-wide undo, OCR, forms, annotation systems and production installation remain out of scope.
