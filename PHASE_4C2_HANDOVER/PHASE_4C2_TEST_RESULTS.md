# Phase 4C.2 test results

Executed on Windows x64, 28 October 2026. Approved final controls are in `phase4c2/evidence/final-controls-approved/`. Other control folders retain development attempts. Counts represent suite checks, not physical input sessions.

| Final suite | Result | Evidence under phase4c2/evidence |
|---|---:|---|
| Current engine | 18/18 | engine-tests.json |
| Current discovery | 22/22 | discovery-tests.json |
| Current compatibility | 23/23 | compatibility-tests.json |
| Current position | 20/20 | position-tests.json |
| Current insertion | 30/30 | insertion-tests.json |
| Current document transaction | 17/17 | document-tests.json |
| New wrapping worker | 21/21 | wrap-tests.json |
| Session/layout model | 22/22 | model/model-tests.json |
| WPF controls, seven suites | 57/57 | final-controls-approved/*tests.json |
| Independent combined exports | 142/142 | wrap-independent-verification.json |
| Independent fixed-position exports | 11/11 | position-independent-verification.json |
| Independent legacy font/discovery | 21/21 | independent-verification.json |
| Recovery across exited processes | Pass | process-recovery.json |

The 57 controls comprise 46 inherited checks and 11 new wrapping checks. The separate clipboard probes do not close the historical intermittent clipboard defect.

## Coverage and expected results

New worker cases cover genuine Word two-row and three-plus-row text, Arial/Calibri, long-word fallback, punctuation/descenders, exact-space refusal, hard-break retention, vertical limits, graphics/paragraphs below, actual combined ink collision, mixed natural/positioned pages, two genuine Word pages, original overwrite protection, unsupported glyph blocks-all, independent-line second generation and one-character/one-character-tail exports. Expected refusals preserve all drafts and create no destination.

Controls cover per-character routed TextInput, exact undo/redo, every logical caret offset at four app zooms, Up/Down/Home/End/shift, mapped selection drag, soft-boundary deletion, inactive second-row activation, cross-page chronology, unsafe-draft recovery, combined collision and Calibri selection. They invoke actual WPF handlers/commands and shared mapping. They do not certify physical input or native file pickers. WPF screenshots use 96 DPI; app zoom is not OS display-scale coverage.

## Frozen regression results

Phase 1 Python: 14/14. Frozen Phase 2: 18/18; Phase 4A: 18/18; Phase 4A.1: 18/18; frozen Phase 3 discovery: 22/22; frozen Phase 4A compatibility: 23/23; frozen Phase 4B document: 17/17 and position: 20/20. Original C1 binaries retain insertion 30/30, document 17/17 and position 20/20 with outputs redirected under C2.

Original Phase 2 tests against Phase 3 retain 17/18: the obsolete manifestless-view-only expectation conflicts with automatic discovery. This known frozen result is preserved, not called a new pass. One current C1 insertion expectation intentionally changes: text beside a protected graphic may now wrap safely in reduced width. The original failing policy assertion is retained in development/previous-insertion-contract.json. No threshold was relaxed.

## Independent verification

MuPDF extraction, pypdf objects, fontTools metrics, Poppler at 72/144 DPI and qpdf syntax through pikepdf verify indexed successful combined outputs. This includes successful UI exports retained in failed development runs, final controls, worker cases, probes and recovery. Fixed and legacy exports have separate reader reports. Checks cover exact intended characters and row separation, source/destination hashes, all region identities, page count/dimensions, metadata, original programs/used encoding-width-ToUnicode-CID rules, proposed positioned origins/baselines within 0.01 pt, unrelated glyphs/boxes within 0.01 pt, protected raw whitespace and zero outside-region changed pixels above difference 8. Production verification also checks outlines/mapping.

Early collision outputs whose source was deliberately replaced remain diagnostic artifacts; their archived source and provenance are retained. Reader reports identify certified saved PDFs, distinct from loose transient candidates. Exact positioned text is never trimmed or normalised to pass. Explicit existing natural newlines are reconstructed from line structure.

## Performance and stability

Final routed input: 134 characters, median 6.24 ms and maximum 55.68 ms including dispatcher processing; 0 immediate worker calls. Thirty alternating replacements: median 4.29 ms, max 94.76 ms; local planning median 0.328 ms; 0 immediate worker calls.

Five preview samples per case, end-to-end medians: two-lines 195.25 ms, three-plus-lines 187.52 ms, long-word 183.45 ms, combined-pages 288.12 ms. Detailed planning/generation/reopen timings are retained. Thirty worker wrap/unwrap alternations: handle growth 0, retained PDFs/PNGs 12/12, worker exited True; recovery file 247,456 bytes. Measurements use small local fixtures, not large-document certification. Existing 30-second timeout/revision rejection remains; no new in-flight cancellation is claimed.

## Investigated failures

The fixture parser initially omitted ToUnicode bfrange arrays; it now reads them without altering genuine Word streams/maps. Initial collision fixtures overlapped envelopes without ink; a revised draft then exceeded its bound by approximately 0.18 pt. Fixture geometry/content was corrected, with no tolerance change. The final case exports each edit alone and proves actual ink overlap together.

An early combined WPF run exposed retained-session assumptions. Tests now establish their own drafts/history. Clicking an inactive new row required an app fix to search proposed rows. The same run exposed the native zero-offset single-character export defect, now fixed and covered. Several TextInput tests asserted before queued WPF editing completed; awaiting dispatcher idle per character proves exact input. An earlier counter included the later export call; the final counter is captured before export. All failed runs remain.

The reader initially concatenated natural explicit hard breaks as soft rows; reconstruction now respects explicit breaks without changing text. One build could not recopy unchanged pdfium.dll while a reader worker held it; the final build completed after release. Visual QA and preservation reports are indexed separately. Clipboard, physical input, OS scaling and rediscovery limitations remain explicit.
