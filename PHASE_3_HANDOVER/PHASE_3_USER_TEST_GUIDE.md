# Phase 3 user test guide

## Start

Double-click `phase3/run/PdfEditorPrototype.exe` in the project folder, or run `phase3/Launch.ps1`. This machine already has the required .NET 8 Desktop x64 runtime. The application runs locally and needs no Python service. Keep the complete `run` folder together.

The manifestless **01-letter.pdf** opens automatically. The earlier Phase 2 application remains in `phase2/run/`; its controlled samples are also retained in `phase3/run/samples/` with their manifests.

## Ordinary letter

1. Click the paragraph starting **“This ordinary digital letter…”**. Its two lines should become editable in place, with native caret/selection and no replacement-text modal.
2. Type, select, delete and undo/redo. Try 75%, 100%, 150% and 200% zoom. Confirm the original font, size, colour and start position remain comfortable.
3. Replace it with a longer paragraph. Wrapping can use the available inferred width and grow toward the next protected block. It must not move the next paragraph.
4. Wait for **Candidate reopened and verified**. Save As to a **new** filename. Existing files and the source are protected.
5. The working draft stays open after saving. Save/export applies to the active region only. To edit a different region, reopen the newly saved PDF first. A changed draft prevents direct switching to another region; it is not discarded.

Original visual line breaks enter the draft as explicit breaks. This prototype cannot reliably recover whether a PDF line break was authored or was merely a soft wrap.

## Reopen and edit again

1. Open your new PDF using Open PDF. No `.region.json` file is needed.
2. Click the paragraph you changed. Discovery should reassess it and activate it where it remains eligible.
3. Append a short second edit, then Save As to another new filename.
4. Reopen that second output in the prototype and another PDF viewer. Check both edits, font/colour, neighbouring paragraphs and page count.
5. Confirm the starting PDF remains unchanged. A document may become restricted after a structural change; the application must explain refusal and retain your draft.

## Styles, space and unsupported cases

Use Open PDF to browse `phase3/run/corpus/`:

| File | Manual check |
|---|---|
| `02-report.pdf` | Regular body, blue 10 pt note and bold summary are separate regions. Edit one, save/reopen, then edit another. Page two should remain unchanged. |
| `09-mupdf-letter.pdf` | A source from a different PDF generator supports simple original-font editing. |
| `13-shuffled-order.pdf` | The paragraph appears in visual order despite unusual underlying object order. |
| `03-adjacent.pdf`, `04-two-columns.pdf`, `05-table.pdf` | Labels, columns and table content should not become a single editable paragraph. Unsupported text stays visible. |
| `06-ambiguous.pdf` | Clicking either short line gives Limited feedback and does not activate editing. |
| `07-rotated.pdf`, `08-nonembedded.pdf` | Unsupported transform/font feedback; no substitution or damaged export. |
| `10-mupdf-subset.pdf`, `11-word-letter.pdf` | These are intentionally unsupported by the current mapping rules. The Word file is a real Office export, not evidence of Word PDF editing support. |
| `12-image-overlap.pdf`, `14-annotation.pdf`, `15-letter-spacing.pdf` | Restricted overlap, annotation and spacing scenarios remain view-only/limited. |

For a supported paragraph, add **☃** (U+2603), or enter enough text to reach protected content. A warning must appear, export must fail, and all your text must remain available. Undo/redo and shortening the draft should still work. Some consecutive-space edits can fail exact extraction verification; their drafts must also remain intact.

## Clipboard and physical acceptance

Try Ctrl+C, Ctrl+X and Ctrl+V within the paragraph and with another application. Clipboard access passed earlier automated controls but later returned intermittent Win32 5. If unavailable, the application reports it; there is no substitute clipboard. Record whether the desktop is locked/remote, the error and any other clipboard applications running, without changing security settings.

Also verify mouse drag selection, caret blinking, sustained typing, keyboard focus after zoom/page changes, and actual Open/Save As file dialogs. Automated WPF controls do not certify these. Native automation could capture the window but could not activate it for input in this environment.

If a file picker is unavailable, launching a document path is supported:

```powershell
& .\phase3\Launch.ps1 -Pdf 'C:\path\to\your.pdf'
```

Use copies of documents for manual evaluation. No general-purpose fidelity or semantic paragraph guarantee is claimed. Phase 3 ends at this review; Phase 4 has not begun.
