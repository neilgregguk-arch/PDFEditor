# Phase 4C.2 user test guide

## Open the genuine Word example

Windows x64 and .NET 8 Windows Desktop runtime are required. Keep `phase4c2/run/` intact. From the repository root:

```powershell
./phase4c2/Launch.ps1 -Pdf './phase4c2/run/corpus/11-word-letter.pdf'
```

Or launch `phase4c2/run/PdfEditorPrototype.exe` and use Open PDF. No Python/network is needed. Save As always requires a new filename; the original cannot be overwritten.

## Wrap and navigate

Click “Phase 3 Office letter”, select its text and type this single logical line, with one space between words:

```text
Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter
```

It should form two visual rows while the next paragraph stays fixed. Wait for verification and Save As. Open the saved file in an independent viewer: the content is real selectable PDF text. Readers may add row separators when copying; technical checks verify the intended characters and row geometry directly.

For more rows, edit the third paragraph beginning “A separate paragraph” to twenty repetitions of “Phase 3 letter” on one logical line. This fixture has room for three-plus rows. Check all four app zoom choices.

Move across a soft break with Left/Right, then Up/Down, Home/End and shift variants. Drag selection from the first row into the second. Delete a space at a wrap and Undo. Wrapping alone creates no history entry. Ordinary edits retain the existing fine-grained history; grouping was not changed.

Edit another region, then click the new second row of the inactive first draft. It should reactivate at that row. On `run/document-corpus/mixed-multipage.pdf`, edit the Word title/third paragraph on page one and a natural paragraph on page two. Undo/Redo follows document chronology; one safe Save As includes every changed region/page.

## Refusals and recovery

Repeat the title phrase sixteen times: it should exceed the space above the next paragraph and block export. Enter within a positioned draft retains the newline but refuses export. An unsupported symbol such as a snowman blocks the combined save without losing other drafts. Multiple adjacent spaces can trigger exact-extraction refusal. Restore a supported draft to continue.

Close with unsaved wrapped edits and reopen the same unchanged source. Check all page drafts/history. Normal recovery is `%LocalAppData%\PdfEditorPrototype\phase4c2\sessions`; tests use separate stores. A changed source fingerprint prevents blind application of old drafts.

Development PDFs in `run/wrap-corpus/` test graphics/paragraphs below. For combined-collision.pdf, the technical test edits the third paragraph to 35 repetitions of “gyp” and its small “..” region to 12 repetitions of “fictional letter”. Each is safe alone; both together must be refused with both drafts retained. These are adversarial development fixtures, not merge functionality.

## Reopen and review

Reopen a verified wrapped PDF. An eligible emitted first row can be edited and saved separately. Do not expect the entire former paragraph to become one region: other rows may be independently editable or Limited under conservative ownership rules.

Manual priorities are physical continuous typing/caret comfort, row selection at your OS display scale, page navigation, clipboard reliability and recovery. Record source, page, exact draft, zoom/display scale, warning and expected/actual behaviour. Automated controls do not replace these manual checks. Read OPEN_ISSUES and TEST_RESULTS, plus the evidence index. Stop at Phase 4C.2 for review.
