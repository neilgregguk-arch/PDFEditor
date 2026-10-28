# Phase 4B Windows user test guide

## Start

Run `phase4b/Launch.ps1` from PowerShell or open `phase4b/run/PdfEditorPrototype.exe` in Explorer. This build requires .NET 8 Windows Desktop runtime, Windows x64. Build from source with `./phase4b/build.ps1` if needed. Keep all runtime files together. Work with copies of your PDFs and choose new output filenames.

The default is `run/document-corpus/multi-natural.pdf`, a two-page fictional test document. The interface remains the spacious inline editor with Open, page, zoom, undo/redo and Save As controls, plus a small document status line. Draft text is application presentation; only a successful verified Save As produces an exported PDF.

## A / B / C / H: multiple regions, chronology and pages

1. Click the first paragraph and change it to `First changed working paragraph.`
2. Click the second and enter `Second changed working paragraph.` Return to the first: its latest text should remain, and the second draft should stay visible.
3. Change the third paragraph. Undo should reverse the third edit first, then the second, then the first. Redo should restore the same chronology. Multiple native text-change events can require multiple undo presses.
4. After undoing, type a new edit: the old redo branch should disappear. Selection and switching alone should not create text-history steps.
5. Move to page two, edit an eligible paragraph, return to page one and change zoom at each offered setting. Drafts should stay attached to their page positions.
6. Save As to a new name. All edited pages should appear in one PDF opened in an independent viewer. Original source bytes should remain unchanged. Drafts/history remain in the original session after export.

For wrapping, lengthen each of two natural paragraphs within its generous blank space. The tool must either verify both together or retain both with a clear warning. It must not move unrelated content.

## D / E: Word and mixed strategies

Open `run/corpus/11-word-letter.pdf`. Change the title `Phase 3 Office letter` to `Phace 3 Office letter` (same count, narrower substitution). In the longer supported Word paragraph replace `should` with `chould`. Save both at once. Unchanged letters should remain in their original positions. Inserting a character must be blocked for export, while retaining the draft.

Open `run/document-corpus/mixed.pdf`. Make the same title substitution and change the lower natural paragraph to `Neutral paragraph retains its original font.` Save As. Both strategies must participate in the same output; natural wrapping must not unlock Word insertion.

## F / G: blocked drafts stay accessible

Open `run/document-corpus/collision.pdf`. Change the first area to three lines, each `alpha area.`. Click the small period below and replace it with `alpha area.`. Each proposed change has a successful isolated automated control, but their combined geometry overlaps. Combined export must be rejected, both drafts retained, and no partial PDF created. Correct one draft and retry.

In the ordinary multi-natural fixture, add a snowman character to area A and make a valid ASCII edit in B. Both must remain accessible when switching. Save must not silently export B alone. Remove the unsupported character and validate/save again.

## I / J / K: recovery, failure and next generation

Edit several regions on both pages, close the window normally, reopen the same original PDF and confirm compatible drafts and undo/redo return. Recovery is debounced; allow a moment before deliberately terminating a process. Normal files live in `%LocalAppData%/PdfEditorPrototype/phase4b/sessions/`. Do not delete them while evaluating recovery. A modified external source should open as a new source session, with previous hash-keyed recovery preserved and no stale edits applied.

Try saving to the original or an existing filename: both are protected. Test a denied/non-writable destination if available. Failure must keep drafts and leave no partial destination. Ordinary region switching must not show a discard/save modal.

Open a successfully exported PDF, rediscover supported text and edit again to a second new filename. This starts a fresh source-bound session. There is no automatic rebasing of the previous session.

## Manual checks still required

Physically test mouse placement, selection drag, typing, Ctrl+Z/Ctrl+Y, copy/cut/paste, file pickers and zoom on your display scale. Clipboard error 5 remains a known intermittent issue; record the error and whether drafts survive, rather than treating a later successful paste as proof of a fix. Automated WPF checks do not establish physical input behaviour. Unsupported document areas should explain that they cannot be edited safely.

Evidence and technical limits are in the accompanying five reports and `phase4b/evidence/README.md`. Phase 4C has not been started.
