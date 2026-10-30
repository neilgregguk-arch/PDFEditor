# Phase 5.2.2 user test guide

From repository root:

```powershell
./phase5_2_2/Launch.ps1 -Pdf './phase5_2_2/run/original-paragraphs/Word-cafe-paragraph.pdf'
```

Use the new Phase 5.2.2 window, not an already open 5.2.1 executable. Keep the entire run folder and supporting files. Requires Windows x64/.NET 8 Desktop runtime. Source files stay immutable.

1. Click the lower Protected reference paragraph. Replace it with about 70 repeats of `cafe calm.`. Amber is expected because this exceeds supported recalculation. Full text remains available with internal scrolling.
2. Click the upper original, enter the same long draft, then return to the lower original and different points inside its amber preview. Switch both ways repeatedly. Use **Text area** above the page to return to either source identity, especially if previews overlap. Selection/caret should survive legitimate switching.
3. Restore the lower exact original: `Protected reference block remains in place.` Its amber clears; the upper invalid draft still blocks the whole export. Restore upper or replace it with `calm cafe.`. Try different supported, safely fitting text in both. Wait for complete current verification before Save As enables.
4. Enter one ordinary `u`: expect U+0075 / PDF encoding round-trip failure, not “or newline”. Paste `cafe`, a genuine newline, then `calm`: expect an explicit hard-break reason. Tabs/NBSP/unmapped symbols must remain recoverable and refuse export. Shorter is not automatically valid.
5. Test click-away/return, end-of-draft scroll, multirow/drag selection, Home/End, Up/Down, Shift selection, Backspace/Delete and global chronological Undo/Redo. Try 75/100/150/200% zoom, resize and page scrolling. Focus/zoom alone must never approve text.
6. Correct both areas to supported text, wait for verification, Save As to a new filename, reopen and re-edit. Confirm protected neighbours and source unchanged. Existing destination must not be overwritten. One invalid area must block combined export and retain all drafts.
7. Close/reopen source with unsaved drafts: confirm text/history restored but fresh validation required. Separately reopen an exported PDF in a fresh process without relying on source recovery.

For a problem report include phase/window title, fixture, exact pasted text and replacement/insertion mode, Text area, zoom/window size, current reason and screenshot. Clipboard Win32 5 remains separately tracked. Stop for manual acceptance after this phase.
