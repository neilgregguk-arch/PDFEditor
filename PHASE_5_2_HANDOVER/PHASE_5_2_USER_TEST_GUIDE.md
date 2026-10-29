# Phase 5.2 Windows user test guide

## Open an authentic original

Use Windows x64 with .NET 8 Windows Desktop runtime. Keep phase5_2/run together. From the repository root:

```powershell
./phase5_2/Launch.ps1 -Pdf './phase5_2/run/original-paragraphs/Word-cafe-paragraph.pdf'
```

This is an original Microsoft Word export without a PDFEditor private declaration. Click either row beginning “cafe calm.” Both must activate the same complete paragraph. A protected reference follows it. Word-letter-paragraph.pdf is a second positive. Word-calm-paragraph.pdf and Word-original-multiline.pdf intentionally remain restricted; Word-separate-paragraphs.pdf must not merge its short paragraphs.

## Edit, save and reopen

Try Up/Down/Home/End and shift variants. Drag across the original row boundary and replace the selection. Try Backspace/Delete at that boundary, then Undo/Redo. Insert “cafe ” there. Test four app zooms and your actual Windows display scale. Text must stay exact; wrapping must not insert a logical newline or a history event by itself.

For a reproducible two-row edit, select the paragraph and enter this single logical line without Enter:

```text
calm cafe. calm cafe. calm cafe. calm cafe. calm cafe. calm cafe. calm cafe. calm cafe. calm cafe. calm cafe.
```

Wait for verification and Save As to a new filename. Close/reopen the output in a fresh app and click either row. Replace it with eleven repetitions of “cafe calm.” separated by single spaces; save/reopen again. Then shorten to “calm cafe.” and save/reopen once more. Only one row should remain. Edited leading can expand from Word's original spacing; protected content must stay fixed.

Ready-to-open states are in run/original-examples: Word-first-export.pdf, Word-second-generation.pdf and Word-third-generation.pdf. examples.json records evidence sources and hashes.

## Four-region history/recovery

Open run/original-examples/Mixed-original-marked-natural.pdf. Page 1 has an original paragraph, page 2 a valid marked paragraph, and pages 3/4 natural regions. Make a small change in each. Return to the last row on page 1. All drafts must survive switching; Undo/Redo must follow document chronology. Close with drafts, reopen the same unchanged source, check recovery, then Save As once. Mixed-recovered-edited.pdf is a certified comparison.

Recovery is source-bound under `%LocalAppData%\PdfEditorPrototype\phase5_2\sessions`; 5.1 stores are not migrated. Saved files establish new source hashes. Old recovery must not attach solely through matching paragraph IDs.

## Refusals and physical checks

Try an unsupported symbol, Enter/hard newline, excessive growth or adjacent spaces. The complete draft must stay available while unsafe export is blocked, even when another region is valid. No valid subset should save. Undo/shorten and retry. Use new filenames; originals/existing destinations cannot be overwritten. Clipboard error 5 remains open; typing can be used for these tests.

Open successful PDFs independently and check selectable genuine text, original appearance, exact words, fixed references and no cover rectangles. Viewers may add visual line breaks when copying. Automated tests do not certify physical input, native dialogs or OS display scales; those remain your review.

## Reproduce automated checks

Use .NET 8 SDK, the repository Python development environment and Poppler pdftoppm on PATH. They are development tools, not app requirements.

```powershell
./phase5_2/build.ps1
.venv/Scripts/python.exe phase5_2/tools/test_engine.py
.venv/Scripts/python.exe phase5_2/tools/test_discovery.py
.venv/Scripts/python.exe phase5_2/tools/test_compatibility.py
.venv/Scripts/python.exe phase5_2/tools/test_position.py
.venv/Scripts/python.exe phase5_2/tools/test_insertion.py
.venv/Scripts/python.exe phase5_2/tools/test_document.py
.venv/Scripts/python.exe phase5_2/tools/test_wrap.py
.venv/Scripts/python.exe phase5_2/tools/test_roundtrip.py
.venv/Scripts/python.exe phase5_2/tools/test_original.py
.venv/Scripts/python.exe phase5_2/tools/paragraph_process.py
.venv/Scripts/python.exe phase5_2/tools/original_process.py
.venv/Scripts/python.exe phase5_2/tools/original_performance.py
.venv/Scripts/python.exe phase5_2/tools/original_page_performance.py
.venv/Scripts/python.exe phase5_2/tools/verify_wrap.py
.venv/Scripts/python.exe phase5_2/tools/verify_paragraph_structure.py
.venv/Scripts/python.exe phase5_2/tools/verify_positions.py
.venv/Scripts/python.exe phase5_2/tools/verify_independent.py
.venv/Scripts/python.exe phase5_2/tools/archive_verified.py
.venv/Scripts/python.exe phase5_2/tools/audit_release.py
```

Model command used for delivery:

```powershell
dotnet run --project phase5_2/Checks/Checks.csproj -c Release -- phase5_2/evidence/model phase4c1/evidence/word-spacing-analysis.json phase5_2/evidence/development-generations.json phase5_2/evidence/original-source-observations.json
```

Supplied observation files bind executed real cases; regenerate them by fresh worker inspection when recreating all evidence. Inherited WPF flags are --ui-test --discovery-ui-test --font-ui-test --position-ui-test --session-ui-test --insertion-ui-test --wrap-ui-test --clipboard-probe, with --audit set to a fresh folder. The release supplies controls-shipping for reader input; preserve failure/retry folders. Close only test processes before building. Frozen tools redirect outputs into this phase.

Original fixture authoring requires local Word and temporarily registers/removes the bundled font in that session. Delivered PDFs require neither Word nor Python. Stop for Phase 5.2 review; Phase 5.3 is not included.
