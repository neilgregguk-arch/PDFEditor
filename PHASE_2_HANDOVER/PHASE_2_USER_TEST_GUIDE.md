# Phase 2 user test guide

This is a local Windows prototype. It edits only the supplied controlled paragraph regions, not arbitrary PDFs. All tests below are **manual verification items**; the automated execution status is in the test report.

## Launch

1. In the project folder, open `phase2/run/` and double-click **PdfEditorPrototype.exe**. Alternatively run `phase2/Launch.ps1` from PowerShell.
2. The machine needs **.NET 8 Windows Desktop Runtime x64**. It is already installed on the machine used for development. There is no installer in this phase and no Python requirement to run the application.
3. Sample A opens automatically. Use **Open PDF** to choose another file in `phase2/run/samples/`.

If the native file picker cannot open on your Windows session, the application reports that error without discarding the draft. You can also launch with an absolute PDF path, for example:

```powershell
& .\phase2\Launch.ps1 -Pdf '.\phase2\run\samples\B-Longer.pdf'
```

## A - Click and edit on the page

1. Open **A-Simple.pdf**. Keep its adjacent `.region.json` file in the same folder.
2. Click directly between characters of the paragraph beginning **“Edit this original paragraph…”**.
3. Confirm the caret appears at the intended position and blinks. Editing should stay on the page; no text-edit modal should open.
4. Type a few words. Try Left/Right, Home/End, Backspace/Delete, Shift-selection and mouse drag selection.
5. Click a header or unrelated blank area before activating a paragraph: it should not activate unrelated text as editable.

Record any displaced caret, text jump or selection mismatch. The prototype uses the original embedded font for supported ASCII text, but WPF and PDF rendering are not claimed pixel-identical.

## B - Replace with longer text

1. Open **B-Longer.pdf**, click its sentence and press Ctrl+A within the active paragraph.
2. Type or paste:

> A much longer replacement remains editable and wraps naturally within its owned paragraph. Keep typing to demonstrate that the old sentence rectangle does not limit the draft. The paragraph should grow into the available space while unrelated content remains fixed.

3. Confirm text wraps and the editing region grows vertically. Continue typing beyond the original sentence length.
4. Wait for status to change from a draft/checking message to **“Candidate reopened and verified”** if the layout is supported.
5. Undo back to the original. The status should indicate that there are no text changes to export, rather than remain in a permanent checking state.

No font shrinking or automatic movement of the reference block should occur.

## C - Unsafe expansion preserves the draft

1. Open **C-Restricted.pdf** and activate the paragraph.
2. Enter enough text to occupy at least three lines; continue for several more lines.
3. Confirm a warning identifies unsafe expansion or collision. Every typed character should remain available.
4. Try **Save As**. Unsafe content should not be exported as a verified PDF.
5. Press Undo and Redo. The long draft should return without retyping. Shorten it until it fits, then try saving again.

The working draft may visibly extend toward the protected block while warned. That does not mean PDF content has been committed or the neighbour has moved.

## D - Original font limitations

1. Open **D-Font.pdf** and activate its text.
2. Add a snowman **☃** (U+2603), for example `Keep my snowman ☃ draft.`
3. Confirm a code-point diagnostic appears and export is blocked. The snowman and surrounding draft must remain available.
4. Remove the snowman or Undo. A supported ASCII draft should become exportable again.

A provisional glyph may be displayed using Windows fallback in the draft. No replacement font should be silently introduced into a saved PDF; this prototype blocks unsupported export.

## E - Zoom and caret accuracy

Test **75%, 100%, 150% and 200%** using the zoom control. Ctrl+1/Ctrl+2/Ctrl+3/Ctrl+4 are shortcuts for those settings.

At each zoom, click the beginning, middle, end and spaces of the original paragraph. Check caret placement, selection highlights and typing. Scroll the page if needed at large zoom. Record the zoom and character position for any mismatch. Existing automated coverage checks 16 sampled positions in the actual WPF control; your physical-click check remains necessary.

## F - Clipboard and history

1. Select a few words. Test Ctrl+C, Ctrl+X and Ctrl+V within the paragraph, then between the paragraph and another ordinary local text application if convenient.
2. Make separate typing, deletion and replacement actions. Use Ctrl+Z/Ctrl+Y or the Undo/Redo buttons repeatedly and check the resulting text.
3. Repeat after an overflow warning. Draft text should not disappear.

**Known development-host limitation:** Windows denied clipboard access (Win32 5). This is an unresolved verification item, not a passing clipboard test. If it happens in your session, retain the draft and record the status. Do not assume copy/cut/paste was completed. The application uses Unicode text only, not formatted clipboard content.

## G - Save and reopen

1. In A or B, replace the entire original paragraph with a distinctive ASCII sentence, such as **“This replacement is genuinely saved in the PDF.”**
2. Wait for candidate verification, then choose **Save As** and select a **new filename**.
3. Confirm the status says **verified PDF saved**. Do not confuse the earlier draft/candidate status with a saved destination.
4. Reopen that output in the prototype or another local PDF reader. Confirm it shows the replacement. Copy/extract text if available and confirm the original paragraph is absent.
5. The saved output normally opens as **view-only** in this prototype because it has no original ownership manifest. Continue editing through the existing working draft, or reopen the original sample to recover its cached draft.
6. Try saving to the original or an existing destination. The operation must fail without overwriting it and without deleting your draft. Choose another filename to recover.

Original-source files are never overwritten in this phase. Save As intentionally does not replace existing files.

## Draft recovery and limits

Draft text is cached under `%LOCALAPPDATA%\PdfEditorPrototype\drafts` using the original PDF hash. Closing and reopening the same source may restore unsaved text. Undo history is not retained across sessions or different opened documents. Recovery is a prototype convenience, not a power-loss guarantee; keep verified exports of work you need.

Only simple horizontal ASCII paragraphs in the supplied controlled files are editable. No arbitrary paragraph discovery, full-document reflow, OCR, complex scripts, arbitrary font substitution or multi-document editing is supported.

## What to report before review

Record sample, zoom, actions, expected/actual caret and text, warning/save status, whether the draft survived, and output filename. In particular, complete physical typing/selection, clipboard, Save As dialog and reopen checks: the development environment could not certify those through desktop automation. Stop for architectural review after this phase; do not treat this prototype as a production PDF editor.
