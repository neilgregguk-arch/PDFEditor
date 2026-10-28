# Phase 4A user test guide

## Launch and newly supported case

Double-click `phase4a/run/PdfEditorPrototype.exe`, or run `phase4a/Launch.ps1`. Keep the whole run folder together. It needs .NET 8 Desktop Runtime x64, already installed on this machine; no Python service is required.

The default file is **J-partial-encoding.pdf**. It contains an embedded subset with an extra glyph that the PDF does not map. The frozen Phase 3 engine refuses this same source; Phase 4A can edit its verified existing characters.

1. Click directly into **cafe calm.** The familiar inline editor should activate without a modal.
2. Replace it with **face calm.** Try native selection, arrows, Home/End, Backspace/Delete and undo/redo. Check caret placement at all four zoom levels.
3. Try a longer repetition of `cafe calm. face calm.`. It should wrap and grow into available space without moving the reference block.
4. Wait for candidate verification, then Save As to a **new filename**. The original and any existing destination are protected.
5. Open your saved PDF, click the changed region, add another supported word and save to another new filename. Inspect it in another PDF viewer too.

One changed region is exported at a time. Save/reopen before editing another region. No multi-region transaction or document-wide undo was added.

## Unsupported characters must keep your work

1. In J, type **Z**. This embedded font contains Z, but the PDF has no verified existing encoding for it. A clear warning should block export while keeping the whole draft.
2. Continue typing after Z. Undo and redo. Nothing should be discarded or truncated.
3. Try Save As. It must not produce a verified export, and all text must remain available.
4. Remove Z or undo to a supported draft; verification should become available again.
5. Open **A-subset-existing.pdf** and repeat Z. This case has no usable Z in the embedded subset's cmap, so the explanation differs. A/B/C are useful regressions but were already editable in Phase 3.
6. A snowman or other unsupported Unicode can display provisionally in the draft, but cannot be silently substituted into a saved PDF.

## Other sources

- **C-subset-bold.pdf:** check that bold remains bold in the active editor and saved output.
- **G-duplicate-unicode.pdf:** existing supported text can be edited because the selected glyph mapping is proved; no arbitrary alias is invented.
- **D/E/F/H/I:** fragmented, spaced, kerned, wrong-Unicode and missing-Unicode cases must remain restricted.
- **corpus/11-word-letter.pdf** and **font-corpus/Word-Arial.pdf**, **Word-Calibri.pdf**, **Word-Consolas.pdf:** these remain view-only for documented spacing/ownership reasons. Resolving part of their font mapping is not a promise of Word compatibility.
- **PowerPoint-Arial-subset.pdf:** remains restricted by spacing and intersecting object bounds.

Unsupported text should stay visible. Clicking it should show understandable status feedback without a permanent technical panel. Detailed reason codes are retained in the evidence JSON.

## Interaction acceptance

Please check actual mouse drag selection, caret blinking, sustained typing, keyboard focus after zoom changes and real Open/Save As dialogs. Automated controls pass, but physical input is a separate acceptance item. Clipboard shortcuts passed this execution; earlier intermittent access-denied failures remain unresolved. Test copy/cut/paste with another application and record the exact error if it returns.

If file-picker access is unavailable, a source path can be supplied directly:

```powershell
& .\phase4a\Launch.ps1 -Pdf 'C:\path\to\your.pdf'
```

Do not use the files under `phase4a/evidence/api-lab/` as approved product examples. Some deliberately contain missing/wrong glyphs to test unsafe API successes. The compatibility matrix and test results identify verified product outputs separately.

Phase 4A is ready for review within these limits. Phase 4B has not begun.
