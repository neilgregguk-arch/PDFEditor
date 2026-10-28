# Phase 2 implementation report

Date: 27 October 2026. Scope: a local Windows interactive PDF editing prototype, not a complete editor. The Phase 1 consolidated report and evidence index were read before implementation. Phase 1 source, reports, handover, PDFs and experimental results were preserved.

## Outcome and qualification

A runnable WPF application and separate PDFium worker have been built. The actual WPF document surface supports an inline editable paragraph, caret placement from original PDF glyph mappings, selection/input commands, wrapping, vertical expansion, warnings, undo/redo and a separate recoverable draft. The application can generate, reopen, validate and save genuinely modified PDF content to a new filename.

**Verification is incomplete:** the final backend suite passes 18/18 tests; the actual WPF window/control suite passes 10/11 checks. Its clipboard check fails because this execution host returns **Win32 5, Access denied** when opening the system clipboard. Physical mouse/keyboard interaction and file-dialog traversal could not be certified because the desktop automation helper failed to activate the application. These are retained failures/gaps, not counted as passes. The prototype is delivered for the manual tests in the user guide; Phase 2's complete usability acceptance must not yet be called fully certified.

## Run and source locations

- Runnable build: `phase2/run/PdfEditorPrototype.exe` in the project root.
- Launcher: `phase2/Launch.ps1`.
- Runtime prerequisite: **.NET 8 Windows Desktop Runtime, x64**. The test machine has 8.0.33 installed. No production installer was built.
- All application/worker source: `phase2/App/`, `phase2/Core/`, `phase2/Worker/`.
- Build: `phase2/build.ps1`; development helpers/tests: `phase2/tools/`.
- Native prerequisite assets and licenses: `phase2/runtime/`, copied into `phase2/run/` by the build.
- Complete working evidence: `phase2/evidence/`. This handover's `evidence/` contains a compact review subset.

The delivered build is framework-dependent and runs on this Windows machine. Optional self-contained publication is available in the build script but **was not executed or validated**. First-time build/restoration can require downloads; document operations do not use a server or network service.

## Architecture and technology

```text
WPF document window
  actual PDFium page image + aligned native RichTextBox when editing
                 |
  logical draft / selection / native undo history / monotonically increasing revision
                 |
  debounced JSON lines over child-process standard input/output
                 v
PdfWorker.exe (.NET console component)
  inspect + ownership/font/glyph mapping
  layout + boundary/collision checks
  remove original text objects + insert original-font paragraph lines
  save temporary candidate -> reopen -> validate
                 |
  stage checksum-verified file in destination directory
  move to NEW destination; never replace source/existing file
```

The preferred WPF/PDFium architecture was retained. A managed P/Invoke adapter is used rather than a custom C++ binary. The worker also uses WPF font metrics and PNG encoding; PDF parsing/rendering/modification remains native PDFium. Calls are serialized within the worker, and the application waits asynchronously, with a 30-second response timeout and worker restart after termination. This is process isolation, **not an operating-system security sandbox**.

Tested build tools/runtime: .NET SDK **10.0.303**, target **net8.0-windows**, x64, installed Windows Desktop runtime **8.0.33**. PDFium is pinned to **156.0.8076.0**, from the Windows x64 `pypdfium2 5.14.0` wheel. The PDFium DLL SHA256 is `bede3932ce96a2e1ed9a7e6cae71aec8914efd2907d37ab44b1b81f9c8a6d04e`.

**No Python or PyMuPDF is part of the application runtime.** Build-time font subsetting and development verification use Python tools, including fontTools, pypdf, Pillow and NumPy; those are not shipped as runtime libraries. The native PDFium build's supplied dependency license texts and the Bitstream Vera license are included. PDFium's BSD-style native licensing and exact dependency notices remain relevant to distribution. No commercial SDK, paid API, cloud service, OCR or AI feature was added. Application licensing has not been chosen on the user's behalf.

## Supported document and text model

This phase intentionally edits only the four supplied controlled PDF samples with adjacent `.pdf.region.json` ownership manifests. A manifest binds the PDF's SHA256 to a known page, exact text-object indices/content, horizontal transforms, original embedded font hash, style, paragraph width and safe vertical boundary. The worker rechecks the actual PDF/font against those values; it does not authorize editing simply because a filename looks familiar.

Other digital PDFs, scans and saved outputs without a matching ownership manifest open for **viewing**, with an explicit unsupported-editing message. Arbitrary paragraph discovery is not implemented. The JSON manifests are local experimental ownership declarations, not signed trust certificates or a general untrusted-document policy.

Supported editing style: original embedded **Prototype Sans ASCII subset** (a properly renamed derivative of Bitstream Vera), regular weight, **12 pt**, opaque RGB **(35,56,72)**, left-aligned simple horizontal text. Glyph support is U+0020-U+007E plus explicit line breaks in the draft. Font file hash is `ced1b2cb9d52bc4373ee3178af5bdd2cd8853bc49c5d06420dc3114f336ef398`. The standalone subset was renamed to comply with the original font's redistribution terms; its outlines/advances are inherited from Vera. There is no silent font replacement in exported PDFs. Unsupported draft glyphs may receive provisional Windows display fallback, with a visible diagnostic and blocked export; that is not claimed to preserve the original font.

All samples use a **420 pt** owned paragraph width, x=**60 pt**, first baseline=**150 pt**, and **18 pt** line spacing. A/B/D permit growth to top-down y=**620 pt**. C's safe boundary is **190 pt**, ahead of a protected neighbouring block. The original word or sentence bounding rectangle is not used as the typing limit.

## Actual page display, hit testing and caret

The viewer displays PDFium rasterizations of real PDF pages. It does not reconstruct a complete document in WPF. While a supported paragraph is active, a second actual PDFium render with those original text objects removed supplies the background, and only that paragraph is presented through the native editor. This is a transient draft surface; saved outputs go through genuine content modification and validation. Render filenames include the source fingerprint, and WPF image-cache reuse is disabled. This corrects a document-switch bug found during visual review; a control check now compares displayed bitmap pixels with the current document's PNG across three document switches.

For initial clicks, page coordinates are recovered from the WPF transformed page surface, accounting for PDF points, device-independent pixels and zoom. PDFium maps original characters to text objects, glyph boxes and origins. The nearest supported logical character is selected on the clicked line. A blank-page click does not silently snap to unrelated text. Once active, WPF supplies caret navigation and mouse/keyboard selection within the paragraph.

WPF's internal selection margin initially displaced the text/caret by 3.75 pt. The editor now calibrates its actual content origin and initial vertical line offset. The control test checks indices **0, 5, 20 and 50** at **75%, 100%, 150% and 200%**. All 16 mappings pass; maximum observed horizontal caret-origin error is approximately **0.179 pt**. This is sampled control geometry, not a universal hit-testing accuracy claim or physical-click certification. Physical caret blinking and mouse dragging remain manual checks.

## Draft management, wrapping and warnings

The draft is not written back to the original PDF. Typing updates the native editor locally; candidate generation is debounced by 300 ms and happens in the child worker. Every request/response carries a revision identifier. Older responses cannot replace newer text or mark an older revision as the current verified candidate.

The editor wraps at the declared paragraph width and grows vertically as text grows, up to the available page display area; very large drafts scroll within the active control. The tested 363-character replacement produces six visual lines matching the worker's planned lines. No font shrinking or movement of unrelated PDF content is used. Width fitting uses the original font's advances and a deliberately simple Latin layout model; arbitrary shaping, rich text and document reflow are not supported.

Boundary warnings and worker collision checks prevent unsafe export, **not continued typing**. Unsupported glyphs and a blocked save leave the entire draft in memory. Recovery snapshots are written under `%LOCALAPPDATA%\PdfEditorPrototype\drafts`, keyed by source hash. Reopening the same source can restore text; native undo history is per opened session and is not persisted. There is no discard-on-overflow workflow or replacement-text modal.

Clipboard commands use Unicode-text-only Windows clipboard integration. WPF's OLE clipboard path initially reported “Class not registered”; the native Unicode adapter still receives Access denied on this host. There is no fake clipboard or silent in-application fallback. This remains an explicitly failing host-level test, requiring manual interactive-desktop verification.

## Genuine content modification and save validation

The implemented commit mechanism is **owned-region reconstruction with the original embedded font**. It does not claim to mutate every original word in place or preserve the original paragraph object identity.

For a changed, supported draft:

1. Recheck source hash, ownership, font program and original object styles/transforms.
2. Lay out the draft using the original font advances; check safe bounds and intersections with neighbouring PDF objects.
3. Create replacement line objects using the original PDF font handle, size and colour.
4. Remove/destroy the targeted original text objects; generate actual page content. No covering white rectangle is used.
5. Write a new temporary, non-incremental candidate PDF and reopen it.
6. Check replacement runs match planned lines, original objects are removed, original full text is absent unless deliberately retained as part of the new draft, embedded font program/style match, and neighbouring object text/font/colour/geometry match within 0.01 pt.
7. Check page count/dimensions, annotation count, selected document metadata, untouched-page rendering, and 144 DPI pixels outside the owned edit area.
8. For Save As, checksum a temporary file in the destination directory and move it to a **new** filename. Reject the original path and any existing destination. Keep the working draft after both success and failure.

Appending to the original sentence is valid: the new draft can intentionally contain that sentence once. Validation therefore distinguishes original-object removal from an inappropriate global substring-absence rule. Secure deletion of every historical byte/resource is not claimed.

The final WPF control suite exported its live draft to `evidence/G-UI-saved.pdf` through the same save method used after the Save As dialog. Independent pypdf extraction confirms the replacement exists and the old paragraph is absent. Dialog traversal itself was not automated.

## Fidelity evidence and limits

Backend saves record zero changed pixels outside the owned edit area and zero neighbouring-object geometry shift on the successful controlled cases. Independent Poppler comparisons of A/B at **72 and 144 DPI** also record zero outside pixels. pypdf independently confirms matching embedded font programs and unchanged origins/style for four neighbouring text runs per sample.

The active WPF paragraph and saved PDF use different rendering stacks. Small glyph-edge/caret differences are expected; the sampled maximum horizontal caret error is recorded rather than described as pixel-perfect equality. A single wrapping sample was checked for identical live/saved line breaks. General text/line metrics, trailing spaces, tabs, bidi/IME and arbitrary fonts remain outside the demonstrated class.

Metadata verification covers selected info fields; annotation verification covers counts, not every annotation dictionary. Images, forms, signatures, tagging, complex clipping and full structural equivalence were not validated as Phase 2 editing scenarios. No production fidelity or security guarantee is made.

## Deliverable boundary

The prototype implements the requested narrow interactive layer and verified PDF export path, with the test and host limitations stated above. No OCR, signatures, merge/split, cloud, full document reflow, multi-document tabs, elaborate theme, production installer or broader editor development was started. The next action is independent/manual review of this Phase 2 prototype, not automatic continuation.
