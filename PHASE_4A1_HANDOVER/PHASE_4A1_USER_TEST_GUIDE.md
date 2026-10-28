# Phase 4A.1 user test guide

28 October 2026. This offline Windows prototype supports selected single-line substitutions in genuine Word PDFs. The familiar editing window is retained. It does not support general Word paragraph reflow.

## Start

Run `phase4a1/Launch.ps1` or double-click `phase4a1/run/PdfEditorPrototype.exe`. Keep the whole run folder together. Windows x64 with .NET 8 Windows Desktop runtime is required; it is installed on this computer. The original Word letter opens by default. Earlier applications remain available in their previous folders.

## First edit

1. Click the title `Phase 3 Office letter` directly on the page. The native inline editor activates with the original Arial style and positions.
2. Change only `Phase` to `Phace`. You can select the title and type `Phace 3 Office letter` if easier. Keyboard, selection and Undo/Redo remain available.
3. Pause for candidate validation. Use Save As and choose a **new** filename. The original and existing destinations cannot be overwritten.
4. Open the new PDF. Click its title and change it to `Phace 3 Oflice letter` (the second f becomes l). Save to another new filename.
5. Reopen it and confirm both changes remain. The spelling is intentionally a technical glyph-position test.

Caret/selection may be slightly offset from the positioned glyphs: tested title maximum 0.254002 pt across four zooms. Display rasterisation differs from the PDF image. This is not a pixel-perfect input claim.

## Refusals and drafts

Try adding ` extra`, deleting a character, entering a newline, changing a narrow character to a wider one, or inserting `!` in this title. Input remains in the working draft, but export is refused when the original mapping/positions cannot be preserved. Continue typing, use Undo, or restore the supported title. Draft recovery retains the working text. A candidate may also be refused after deeper PDF verification; the draft still remains.

Save/reopen before editing another region. This version commits one region per exported PDF; it does not combine edits to multiple regions.

## Other supplied examples

Open `run/font-corpus/Word-Arial.pdf` or `Word-Calibri.pdf`. In the first line, replace `cafe calm. cafe calm.` with `ccfe calm. cafe calm.`. Save/reopen, then try `ccfe cclm. cafe calm.`. These are verified narrower mapped-character probes.

Word Consolas and the mixed-font first line in `run/position-corpus/Word-multiple-runs.pdf` remain restricted. ReportLab metric-rounding fixtures, visible whitespace mapped to a glyph, nearby graphics and ambiguous labels remain restricted. Do not interpret a clickable line as permission for every possible replacement.

For ordinary natural wrapping, open the earlier controlled samples in `run/samples/` or the partial-encoding case `run/font-corpus/J-partial-encoding.pdf`; their existing behavior is retained. Unsupported characters remain in the draft and cannot be saved.

## Manual review still needed

The automated checks exercised actual WPF controls/shared save paths, not hardware input or Open/Save As picker traversal. Please check physical click/caret placement, drag selection, sustained typing, Ctrl+Z/Ctrl+Y, clipboard between applications, four zooms, dialogs, source preservation and recovery on your interactive desktop. Intermittent clipboard failures are still tracked; a current pass does not establish a permanent fix.

Detailed scope, measured tests and limits are in the five accompanying handover reports. No Phase 4B work has begun.
