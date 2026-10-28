# Phase 4C.1 user test guide

## Run

Open `phase4c1/run/PdfEditorPrototype.exe` or run `./phase4c1/Launch.ps1`. Requires Windows x64 and .NET 8 Windows Desktop runtime. Rebuild with `./phase4c1/build.ps1` if needed. Keep the worker, native DLL and assets together. Work on fictional samples or copies and always choose a new output filename.

Open `phase4c1/run/corpus/11-word-letter.pdf`. It is the genuine Word letter used for the positioning tests. The existing interface is unchanged: click supported text and type directly. A small summary shows draft count, attention and export readiness. Draft ink and proposed positions are immediate; only a successful Save As produces a verified output.

## Insertion, deletion and selection

1. In the title `Phase 3 Office letter`, click after `Phas` and type `s`: expect `Phasse 3 Office letter`.
2. Undo and redo. Selection or switching alone should not add text history. Individual-character undo grouping remains unchanged.
3. Select `Office ` including its following space and delete it: expect `Phase 3 letter`. The rest should close naturally, without being stretched to the old title width.
4. Replace `Office` with `letter`, a different length. Try adding `Phase ` at the start, ` letter` at the end, or `letter ` between words. Try several separate insertions, such as `Phasse 33 Office letterr`.
5. Save As to a new PDF, open it independently and check text extraction as well as visual placement. Original font, baseline and untouched paragraphs should remain stable. Reopen that output in the editor and make another supported edit.
6. Select and remove the whole title. Save to another new name. The other lines and separately owned original whitespace must remain; the title is genuinely removed. Undo in the working session should restore its prior text.

Only original-font mapped characters are available. Not every ASCII letter is safely encoded by every Word sample. The title's original `ff` is preserved, but adding a third f to make `Offfice` is a known refused join. A double-space insertion is another known candidate-extraction refusal. These warnings retain your complete draft.

## Arial, Calibri and display

Open `run/font-corpus/Word-Arial.pdf`, then `Word-Calibri.pdf`. The first line is `cafe calm. cafe calm.`. Append ` cafe`, remove the first `calm` and its neighbouring space appropriately, or replace the first `cafe` with `calm`. Save to new names. Use only characters with verified mappings.

At 75%, 100%, 150% and 200% zoom, physically check clicking between letters, drag selection, shift-click, word double-click, home/end, arrows, backspace/delete and typing. Supported positioned text uses a proposed-position caret/highlight because native WPF spacing differs for some Calibri text. Text input and document history remain in the same editor. The automated tests used 96 DPI; test your own Windows display scale, especially 125% or 150%, and report any visible caret drift.

## Mixed document, history and recovery

Open `run/document-corpus/mixed-multipage.pdf`, a development fixture with genuine Word text on page one and a natural paragraph page on page two. Insert `s` in the title. In the third Word line remove `should ` including its following space. On page two change the first paragraph to `First changed working paragraph.`.

Switch back through all three areas; drafts should stay visible. Undo should reverse the natural edit first, then Word deletion, then title insertion, navigating to affected pages/regions. Redo restores the chronology. Save As must include all changes in one file. Natural paragraphs can still wrap within their verified bounds; Word lines cannot wrap.

Close normally after editing, reopen the same original and verify drafts/history return. Recovery is under `%LocalAppData%/PdfEditorPrototype/phase4c1/sessions/`; it does not import your Phase 4B recovery. Saving retains the original working base and drafts. Reopen a saved output for a fresh source session.

## Warnings and failures

- Append enough ` letter` words to run out of horizontal space. Expect a warning and blocked complete export, with all text retained and no font shrinking/wrapping.
- Open `run/document-corpus/word-horizontal-obstacle.pdf`; expand the eligible title toward the black rectangle. The rectangle must remain fixed and the colliding draft must not export.
- Add a snowman or unsupported punctuation in one region while another holds a valid edit. Both drafts must remain accessible; Save As must not export only the valid one.
- Insert a newline in a Word line. It is retained in the draft but blocked for this phase.
- Try the original filename, an existing destination, or a non-writable location. Original/existing bytes must remain unchanged; failed saves must preserve every draft.

Physically test copy/cut/paste and native file pickers. Clipboard Win32 5 remains intermittent; a later passing paste does not prove it fixed. Record source/sample, steps, zoom, Windows display scale and full warning. No hardware/file-picker testing is claimed by the automated evidence. Detailed executed results and limits are in the other five reports. Do not start Phase 4C.2 without review.
