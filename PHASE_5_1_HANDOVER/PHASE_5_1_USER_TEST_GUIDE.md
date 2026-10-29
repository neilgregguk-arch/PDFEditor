# Phase 5.1 user test guide

## Run and open

Use Windows x64 with .NET 8 Windows Desktop runtime. Keep `phase5_1/run/` intact. From the repository root:

```powershell
./phase5_1/Launch.ps1 -Pdf './phase5_1/run/corpus/11-word-letter.pdf'
```

Alternatively launch `phase5_1/run/PdfEditorPrototype.exe`. No Python/network is needed to use the app. Certified ready-to-open examples are `run/paragraph-examples/Word-two-rows.pdf`, `Word-three-rows.pdf`, `Word-one-row.pdf`, `Arial-two-rows.pdf`, `Calibri-two-rows.pdf` and `Mixed-two-pages.pdf`. Their manifest records the originating evidence/hashes.

## Two → three → one generations

Use the **third paragraph** beginning “A separate paragraph”; the title has less vertical room. Select that paragraph and enter this one logical line (do not press Enter):

```text
Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter
```

It should wrap into two rows. Wait for verification and Save As to a new filename. Close the document/app, reopen the saved file and click either row. Both should activate the same complete logical paragraph. The first saved file establishes its embedded identity; later generations preserve it.

Replace the whole paragraph with fifteen repetitions of “Phase 3 letter”, separated by single spaces, to make three rows. Save As again, close/reopen and click the first, middle and final row. Then replace the whole paragraph with “A separate letter.” and save/reopen a third time. Only one row should remain; no old row should be visible or selectable as residual text.

The supplied Word examples allow reviewing these states without first creating them. A legacy C2 wrapped export remains separate eligible/Limited lines: this phase does not retroactively infer its paragraph relationship.

## Caret, history and recovery

Try Left/Right across a soft boundary, Up/Down, Home/End and shift variants. Drag from the first row into the last. Backspace/Delete near the boundary and type at the paragraph start/end; Undo/Redo should restore the exact logical span and wrapping. Test all four app zooms and your actual Windows display scale. Wrapping itself should not add a history event; ordinary edit grouping remains unchanged.

Open Mixed-two-pages.pdf. Edit the wrapped Word paragraph, another Word region and the natural paragraph on page two. Switch away and return to the last row of the group. Undo/Redo should follow document chronology. Close with unsaved changes, reopen the same unchanged source and check all three drafts, then Save As once. Normal recovery is `%LocalAppData%\PdfEditorPrototype\phase5_1\sessions`; old C2 stores are not migrated. Saved outputs are new source files, and old-source recovery must not attach merely because a paragraph ID is the same.

## Refusals and external viewers

Try an unsupported symbol, a positioned hard newline, repeated spaces or excessive growth into protected content. The whole draft must remain available, but unsafe combined export must fail without saving a valid subset. Use a new destination; originals/existing files cannot be overwritten. Open successful outputs in an independent viewer: rows are genuine selectable original-font text, with no cover rectangles. Viewers may add line separators when copying; that formatting is not the stored logical paragraph definition.

Malformed/modified examples are under `phase5_1/evidence/adversarial/`. Broken or conflicting declarations should not activate a whole editable group. External tools may discard the declaration; editing then falls back to conservative legacy classifications. Clipboard error 5 remains open and needs physical desktop review.

## Reproduce automated checks

Build with the .NET 8 SDK. Use the repository's development Python requirements in an isolated environment, and make Poppler `pdftoppm` available on PATH. Python/readers are not application dependencies. Commands below assume `.venv` at the repository root:

```powershell
./phase5_1/build.ps1
.venv/Scripts/python.exe phase5_1/tools/test_roundtrip.py
.venv/Scripts/python.exe phase5_1/tools/test_paragraph_spaces.py
.venv/Scripts/python.exe phase5_1/tools/paragraph_process.py
.venv/Scripts/python.exe phase5_1/tools/paragraph_performance.py
dotnet run --project phase5_1/Checks/Checks.csproj -c Release -- phase5_1/evidence/model phase4c1/evidence/word-spacing-analysis.json phase5_1/evidence/development-generations.json
```

Current regression tools are `test_engine.py`, `test_discovery.py`, `test_compatibility.py`, `test_position.py`, `test_insertion.py`, `test_document.py` and `test_wrap.py`, under phase5_1/tools. Run those before `verify_wrap.py`, followed by `verify_paragraph_structure.py`, `verify_positions.py` and `verify_independent.py`. `frozen_phase4c2.py` and `verify_frozen_c2.py` use original C2 binaries/assertions with output redirected under this phase. Avoid running reader tools while building because a worker may hold the unchanged native DLL open.

WPF regression flags are `--ui-test --discovery-ui-test --font-ui-test --position-ui-test --session-ui-test --insertion-ui-test --wrap-ui-test --clipboard-probe --audit <new-folder>` on the executable. `paragraph_process.py` drives six separate processes and isolated stores automatically. Keep generated evidence separate from production assets. See the evidence index for approved runs, historical failures and preservation hashes. Stop for review after Phase 5.1.
