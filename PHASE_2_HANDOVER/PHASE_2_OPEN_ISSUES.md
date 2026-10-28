# Phase 2 open issues

Date: 27 October 2026. The prototype is implemented; acceptance remains qualified by the failures and scope below.

| Priority | Issue | Evidence / impact | Next action |
|---|---|---|---|
| High | System clipboard execution fails on the development host | WPF OLE returned “Class not registered”; native Unicode adapter receives Win32 5, Access denied. Final control suite retains this failure. Copy/cut/paste is implemented but not certified operational here. | Reproduce on an accessible interactive Windows desktop. Verify normal shortcuts and cross-application Unicode text. Do not mask the failure with a fake clipboard. |
| High | Physical UI input and file-dialog flow not certified | Desktop helper returned `failed to activate captured window`, including a refreshed binding/retry. Captures did not represent the app correctly. No shared cause with clipboard denial has been proven. | Complete the manual guide. Confirm caret blinking, click/drag, keyboard focus, clipboard and Open/Save As picker traversal. |
| High scope limit | Only hash-bound controlled paragraph regions editable | There is no general PDF paragraph detector, ownership inference or arbitrary selection-to-operator mapping. Unknown PDFs and exported files without manifests are view-only. | Review the demonstrated ownership model before broadening supported documents. Do not infer general editing reliability. |
| High scope limit | Reconstruction rather than original paragraph identity preservation | The worker removes owned text objects and appends replacement line objects using the original embedded font. Extraction/content order may differ even when visual neighbours are preserved. | Add reading-order/accessibility tests before making logical-structure preservation promises. |
| Medium-High | WPF/PDF layout fidelity not universally identical | Sampled horizontal caret error reaches ~0.179 pt. Only one longer UI draft had live/worker wrap positions compared exactly. Glyph-edge differences, trailing spaces and unusual text sequences need more coverage. | Broaden glyph/baseline/line-break checks, fonts and display DPI cases before promising exact matching. |
| High scope limit | Original-font ASCII subset only | No new glyphs, Unicode shaping, bidi/IME, mixed formatting, arbitrary sizes/colours/weights/alignment or missing-font recovery. Unsupported draft glyph display may be provisional fallback; export is blocked. | Decide the next eligible text/font class after review; do not silently substitute fonts. |
| Medium | Clipboard handles Unicode plain text only | Formatted/HTML/image/file clipboard content is not a supported paste source. | Validate and document plain-text behaviour before adding richer content. |
| Medium | Session history is not persistent | Draft text is recovered by source hash, but undo/redo history is lost on reopen/document switch. | Decide recovery/history requirements. Test power-loss and recovery corruption separately if needed. |
| Medium | Temporary candidate cache is retained | Debounced previews create PDFs/PNGs under `%TEMP%\PdfEditorPrototype`; retention is not bounded or automatically cleaned in this phase. | Add session cache lifecycle/resource limits in a later authorized milestone. |
| Medium | Source/destination save checks have limited failure injection | Original/existing/locked destination rejection and source hash guards pass. Atomic staging is implemented, but mid-write disk-full, power-loss and in-flight crashes are not exhaustively tested. | Add controlled failure injection before production persistence claims. |
| High scope limit | Generic PDF integrity not certified | Runtime checks include neighbouring object geometry, font programs, page dimensions, annotation counts, selected metadata and render changes. Full annotation dictionaries, forms, images/colour semantics, signatures, encryption, tags and incremental history were not validated as editing cases. | Define explicit document eligibility and independent structure tests before expansion. |
| Medium | No general performance/security benchmark | Debouncing and an out-of-process worker are implemented; page raster allocations are capped, but input-to-paint latency, large documents and adversarial files were not benchmarked. Worker is not OS-sandboxed. | Profile representative workloads, cancellation/resource limits and engine security updates. |
| Medium | Framework-dependent Windows build | Requires .NET 8 Desktop x64. Optional self-contained publishing and a clean disconnected VM were not tested. No installer is included. | Verify deployment prerequisites or authorize a portable packaging spike separately. |
| Medium | Experimental native API surface | PDFium glyph-to-object APIs and wrappers are pinned to the tested native build. | Keep the DLL/version/notices pinned and rerun tests before updating. |

## Corrections retained in development evidence

- WPF internal-margin caret displacement was corrected; the earlier failing result is retained in `phase2/evidence/development/control-initial.json`.
- Document-switch image caching was caught in visual review and corrected with source-fingerprint render keys and image-cache bypass; a new actual-bitmap comparison covers C/D/A switching.
- Native wrapping/initial text alignment and line-spacing configuration were corrected and rechecked through actual control renders.
- An extended synthetic routed-input history driver produced a failed intermediate text state and a following wrap failure. The history test now uses explicit native control insertion after layout pumping to isolate undo/redo, while routed TextInput remains a separate test. `control-sixth.json` retains the failures. This is not a claim that repeated physical typing has been tested.
- `pdftotext` was absent. Its attempted error is retained; independent geometry checks use pypdf run origins/style instead. Poppler rendering checks ran successfully.

## Review decision

There is enough working code and controlled evidence to review the in-place editing approach. **There is not an all-green UI acceptance result.** Resolve the clipboard/physical-input verification gaps and evaluate the known ownership/font limits before authorizing broader application development. No Phase 3/full-editor work has been started.
