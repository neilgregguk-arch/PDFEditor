# Phase 4A.1 implementation report

28 October 2026. Offline Windows .NET 8/WPF/PDFium prototype. New source, runnable build, tests and evidence are under `phase4a1/`. The six documents in `PHASE_4A1_HANDOVER/` describe this release independently of earlier reports. Earlier phases remain retained. Phase 4B has not begun.

## Delivered behavior

The original genuine Word 16 export now activates through automatic discovery and the existing inline RichTextBox. A title edit from `Phase 3 Office letter` to `Phace 3 Office letter` is saved by the actual WPF editing model. Reopening rediscoveries work without sidecars; a second, narrower change to `Phace 3 Oflice letter` survives another export. Separate Word Arial and Calibri documents also have independently checked first and second exports. This establishes selected single-object substitutions, not unrestricted Word editing.

Stage A reconstructs the original object with explicit origins: full-page Poppler renders are identical at 72 and 144 DPI. Stage B changes an equal-advance glyph. Stage C supports a narrower mapped glyph while every surrounding origin remains fixed; replacing the second `f` of `Office` with `l` reduces its program advance by approximately 0.668 pt. Stage D was investigated and is deliberately **not exportable**: insertions/deletions/newlines requiring different positions or wrapping retain the complete draft and show a limitation. Equal character count alone is insufficient; wider substitutions are refused.

## Architecture and data

`Core/PositionLayout.cs` adds a pointer-free `PositionedSource` alongside the existing natural layout model. It retains original logical offsets, source object indices, glyph Unicode/GID evidence, origins, bounds, relative position array, supported strategy and protected objects. The Region retains the source SHA256, original text, font SHA256/extracted program, size, color, baseline and original matrix observations. Original geometry is a separate source snapshot and is never updated by draft editing. No native handle is cached. Glyph arrays are used as read-only observations by the implementation; they are not an external ownership certificate.

The product uses verified Unicode `FPDFText_SetText` plus `FPDFText_SetPositions`, with exactly N-1 float offsets relative to the text-object origin. Raw PDF codes are independently recorded in `word-position-analysis.json`; **the product does not need or guess raw codes**. Existing Phase 4A Unicode roundtrips, original embedded cmap GIDs, glyph outlines and advances remain necessary. No font substitution, cmap/ToUnicode extension or subset rebuilding occurs.

The native position path requires SHA256 `bede3932ce96a2e1ed9a7e6cae71aec8914efd2907d37ab44b1b81f9c8a6d04e` (PDFium 156.0.8076.0), both on activation and each edit. Bindings use x64 pointer-sized counts. Reconstruction, real changes and save/reopen tests exercise the exact pinned binary. The [public experimental API contract](https://pdfium.googlesource.com/pdfium/+/refs/heads/main/public/fpdf_edit.h) was checked; its moving header is supporting documentation, not substituted for pinned-binary testing.

## Discovery gates and whitespace

Position fallback runs only when initial mapping/style/ownership are otherwise supported and the original natural reconstruction/spacing fails. It requires one horizontal complete text object, monotonic X origins on one baseline, embedded standalone TrueType ASCII mappings, exact original positioned object render, page/margin rules and all existing unsupported-page gates. It never merges position-sensitive objects into a paragraph. Natural documents retain the earlier wrapping path.

An additional position-only metric check rejects fonts where any verified mapping's PDFium width differs from its program advance by more than 0.01 pt. This guard was added after MuPDF exposed a 0.012009 pt unchanged-space drift in the ReportLab kerning fixture. Its pre-guard candidate and measurements remain development negative evidence; that class is restricted in the release. This empirical guard is conservative fixture evidence, not a proof for every PDF reader/font.

Ownership is limited to the original object's observed bounds. Other objects remain protected. A separately retained text object may coexist only if it has fill-only opaque paint, empty/ASCII-space extraction, zero object extent and no contribution to a 144-DPI full-page render when its fill is temporarily disabled. Paint is restored in `finally`; no source file is saved. This is a nonpainting observation, not an inference that the object lacks semantics. Only this narrow position strategy permits coexistence. All such objects remain in snapshots and saved outputs; independent parsing verifies the Word F2 raw space bytes and font rules. Nonzero visible whitespace, mixed runs, graphics and ambiguous neighbors still block editing.

## Inline interaction

The existing window, toolbar, click-selection path, RichTextBox, native caret/selection, keyboard commands, history, recovery, zoom and asynchronous revision handling remain. A hit-test-transparent `PositionedInk` layer draws the verified source font glyphs at recorded origins while the existing native editor owns input. Unsupported drafts use the normal editable presentation and remain recoverable. The input control has enough width to avoid an accidental word wrap when activating a fixed-position line.

The native caret/selection geometry is approximate. On the tested title its maximum horizontal caret discrepancy was 0.254002 pt across 75/100/150/200% zoom. The drawn glyph origin plan matches the recorded source positions, but WPF/PDFium rasterisation differs; pixel-perfect editing is **not claimed**. Caret/selection for other position-sensitive lines is not exhaustively measured. Physical mouse, keyboard and file-picker traversal remain unverified for this phase.

TextPointer lookup now counts the next segment instead of repeatedly copying the entire text prefix. This removes unnecessary work exposed by the regression harness while retaining native selection semantics.

## Commit verification and delivery

Existing collision, original-object removal, exact extraction, font/style, neighbor object/glyph, page count/dimensions, annotations, selected info metadata, untouched pages, outside-region raster, source-hash and protected-destination checks remain. Positioned runs additionally reopen with every glyph origin within 0.01 pt of the source, unchanged target bounds within 0.01 pt, verified outlines and exact positioned object reconstruction. Changed ink must fit the permitted line and avoid protected letters/objects. A narrower glyph that creates an extra extracted space is rejected. No prior geometry threshold was relaxed.

The analysis cache remains eight fingerprint/page entries with font-file hash checks. Rendering/verification stays in the separate worker with 300-ms debounce and revision checks; no original geometry is recalculated in response to each immediate TextChanged event. Preview still saves/reopens a candidate and can be costly on large documents. No in-flight cancellation or total disk bound was added.

Run `phase4a1/Launch.ps1` or `phase4a1/run/PdfEditorPrototype.exe`; it opens the Word letter. The entire `run/` folder must remain together. Requires Windows x64 and .NET 8 Windows Desktop runtime (installed here). `phase4a1/build.ps1` rebuilds App and Worker; optional self-contained mode remains unvalidated. No installer, hosting, network dependency, Python runtime dependency, multi-region transaction or document-wide history was introduced. Existing PDFium/font notices accompany the build.
