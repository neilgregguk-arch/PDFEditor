# Phase 5.2.1 Windows user test guide

Use Windows x64 with .NET 8 Windows Desktop runtime and keep the complete run folder together.

```powershell
./phase5_2_1/Launch.ps1 -Pdf './phase5_2_1/run/original-paragraphs/Word-cafe-paragraph.pdf'
```

## Recheck the original workflow

Click either row of the original cafe paragraph. First replace the entire paragraph with a longer string; then Undo and try appending the same string. Reuse your original pasted text if available. Our controlled reproduction used 30 repetitions of `cafe calm.`: 329 characters when replacing, 439 when appended with one separating space. Seventy repetitions test the separate 512-positioning-limit path.

Rejected text must stay inside an amber area, with an explicit retained-draft/not-PDF-layout message and Save As unavailable. Scroll inside that area to review all characters, including the tail. Click the toolbar, another region and back. Text, ordered selection and usable caret must survive; the protected reference must remain visible and fixed. Amber native wrapping is a correction aid, not a promise that those rows can be exported.

Try Home/End/Up/Down and shift variants, native drag selection, insertion/deletion, a multi-row selected replacement, Undo/Redo and returning after focus loss. Repeat at 75/100/150/200% app zoom, narrow/wide windows and your real Windows display scale. Confirm that the page does not pan horizontally toward a hidden native caret during valid positioned editing.

## A fitting edit and verified export

Select the whole paragraph and enter this one logical line, without Enter:

```text
calm cafe. calm cafe. calm cafe. calm cafe. calm cafe. calm cafe. calm cafe. calm cafe. calm cafe. calm cafe. calm cafe.
```

It should fit in two proposed PDF rows. Initially the status says pending and Save As remains disabled. After current complete verification, Save As enables. Save to a new filename, close/reopen it and click either row; the complete paragraph must still activate and edit. The reference must not move. An independent viewer should show genuine selectable original-font text without amber UI borders or cover rectangles.

For the controlled `cafe calm.` string, thirteen repetitions fit and fourteen exceed the current height allowance. Other strings have different widths; this is not a universal character limit. Do not expect the correction to move the next paragraph, reduce font size, enlarge ownership or enable general reflow.

## Safety and recovery

Keep another region modified while the cafe draft is invalid. The complete combined save must stay blocked, with every draft retained. Try a positioned hard newline, an unsupported character, repeated spaces and excessive growth; existing restrictions remain. After an output filename error, text stays available and current verification is retried. Existing files/originals must not be overwritten.

Close with unsaved valid and invalid text and reopen the same unchanged source. Recovery is isolated under `%LocalAppData%\PdfEditorPrototype\phase5_2_1\sessions`; older phase stores remain intact and are not migrated automatically. Source changes must not silently acquire the old drafts. Character-by-character undo remains unchanged.

System clipboard Win32 5 remains an intermittent open issue. If clipboard fails, retain the draft and retry on your ordinary interactive desktop; typing can exercise the same presentation. Physical clipboard, mouse dragging, native dialogs, OS scales and accessibility still need your testing. Automated tests use WPF controls/routed input and shared paste processing.

## Reproduce the checks

Use the .NET 8 SDK, the repository development Python environment and Poppler pdftoppm on PATH. Python/Word are not app runtime requirements.

```powershell
./phase5_2_1/build.ps1
.venv/Scripts/python.exe phase5_2_1/tools/presentation_process.py
.venv/Scripts/python.exe phase5_2_1/tools/visual_presentation.py
.venv/Scripts/python.exe phase5_2_1/tools/test_engine.py
.venv/Scripts/python.exe phase5_2_1/tools/test_discovery.py
.venv/Scripts/python.exe phase5_2_1/tools/test_compatibility.py
.venv/Scripts/python.exe phase5_2_1/tools/test_position.py
.venv/Scripts/python.exe phase5_2_1/tools/test_insertion.py
.venv/Scripts/python.exe phase5_2_1/tools/test_document.py
.venv/Scripts/python.exe phase5_2_1/tools/test_wrap.py
.venv/Scripts/python.exe phase5_2_1/tools/test_roundtrip.py
.venv/Scripts/python.exe phase5_2_1/tools/test_original.py
.venv/Scripts/python.exe phase5_2_1/tools/paragraph_process.py
.venv/Scripts/python.exe phase5_2_1/tools/original_process.py
.venv/Scripts/python.exe phase5_2_1/tools/verify_wrap.py
.venv/Scripts/python.exe phase5_2_1/tools/verify_paragraph_structure.py
.venv/Scripts/python.exe phase5_2_1/tools/verify_positions.py
.venv/Scripts/python.exe phase5_2_1/tools/verify_independent.py
.venv/Scripts/python.exe phase5_2_1/tools/archive_verified.py
.venv/Scripts/python.exe phase5_2_1/tools/audit_release.py
```

The position reader uses the supplied controls-shipping evidence. Preserve timestamped failure/partial folders; do not overwrite them to manufacture clean results. Frozen tools redirect output into the new phase. Model command:

```powershell
dotnet run --project phase5_2_1/Checks/Checks.csproj -c Release -- phase5_2_1/evidence/model phase4c1/evidence/word-spacing-analysis.json phase5_2/evidence/development-generations.json phase5_2/evidence/original-source-observations.json
```

Do not build while test workers hold runtime DLLs. Stop after reviewing Phase 5.2.1; Phase 5.3 has not begun.

Optional full-text reproduction: pass a local text-file path as the final argument to presentation_process.py. The delivered run used the supplied clarification brief in both modes (11,568/11,678 characters); only lengths/hashes are retained. Default reproduction executes 27 checks; supplying the payload adds two checks for 29. Do not treat the --presentation-baseline flag on corrected code as the old executable: launch the preserved 5.2 build manually to reproduce old presentation, or inspect the retained pre-fix captures.
