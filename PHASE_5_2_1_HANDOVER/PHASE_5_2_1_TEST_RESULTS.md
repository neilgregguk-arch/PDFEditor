# Phase 5.2.1 test results

Executed in Codex on Windows x64. The final rebuild succeeds and its runtime hashes equal the tested binaries (evidence/final-build.json). All twelve Core C# files remain byte-identical to 5.2. No layout/export tolerance or discovery rule changed.

| Suite | Executed result |
|---|---:|
| Dedicated actual WPF corrective matrix | 29/29 |
| Existing worker engine/discovery/compatibility/position/insertion/document/wrap | 151/151 |
| Phase 5.1 marked roundtrip/adversaries | 37/37 |
| Phase 5.2 original discovery/editing/adversaries | 31/31 |
| Model/session invariants on retained real 5.2 observations | 35/35 |
| Existing six-process paragraph controls | 16/16 |
| Existing five-process original controls | 12/12 |
| Shipping inherited WPF controls | 56/57; clipboard Win32 5 only |
| Independent combined exports | 165/165 |
| Private/semantic structure verification | 165/165 PDFs; 178 group instances |
| Independent position / legacy outputs | 11/11 and 21/21 |
| Frozen C2 workers / independent combined outputs | 151/151 and 52/52 |

Authoritative files are presentation-release.json, the seven current *-tests.json files, roundtrip-tests.json, original-tests.json, model/model-tests.json, paragraph-controls.json, original-controls.json, controls-shipping/, and the independent verification reports. portable-pdf-index.json maps 218 checked source/destination paths to retained PDFs. Some independently valid PDF outputs come from intermediate UI runs; that does not certify an incomplete intermediate UI run as a whole.

## Corrective WPF matrix

The 29 checks cover:

- Replacement/append at 329/439 and 769/879 characters, exact active/inactive text, matching contained surface dimensions, return, refused save and unchanged source hash.
- Original, pending/verified valid edit, inactive valid edit, safe Save As, reopen and activation of the complete marked output.
- Eight combinations of 75/100/150/200% app zoom and 780x650/1120x900 windows, each testing 164/329/769-character rejected drafts, visible endpoint caret, internal scrolling and bounded page extent.
- Paste at beginning/middle/end with document undo/redo, plus 329 individual routed TextInput events compared with shared paste processing.
- Incremental 8–18 repetitions: 13 (142 characters) fit; 14 (153) exceed the height allowance for this particular font/text. This is not a universal character capacity.
- Invalid native Home/End/Up/shift selection, native hit testing, selected replacement, undo and source-bound recovery; exact ordered selection restoration after region switching.
- An actual WPF pixel comparison of the protected reference during rejected editing and native focus loss: 22,208 pixel bytes compared, zero changed bytes.
- Natural-layout safe editing and retained overflow, a real protected-graphic fixture, unchanged verification after presentation-only formatting, existing-destination refusal followed by fresh verification, and disabled save/cleared layout while opening another document.
- Actual worker responses held at delivery and released after a newer edit or document switch. Older responses cannot approve or repaint the current view.

These are real WPF controls, native text views/hit tests, routed commands and the shared paste path. They are not physical typing/mouse automation, native dialog certification or proof that system clipboard access is reliable. The supplied full clarification brief was additionally tested as a possible paste: 11,568 characters replacing, 11,678 appending, with exact active/inactive/returned content and no approval. Only lengths/hashes are distributed for these payload cases; the original screenshot workflow/mode remains unconfirmed.

## Failures and evidence corrections

The pre-fix four-case reproduction logs all four refusals successfully; it is a reproduction record, not a passing UI correctness suite. Its screenshots show unsafe ink over the reference, page spill and the 36-DIP inactive fallback.

The first corrective visual run exposed an infinite-width Open error from measuring a collapsed editor. This was corrected, and final tests explicitly assert successful Open and matching inactive text/bounds. A partial expanded run was interrupted to add a same-logical-text guard and incremental case checkpoints; it remains identified as partial. Completed intermediate matrices of 21/24/25/26 checks and the final 29-check result remain retained.

One earlier inherited check reported “Failed candidate lost draft” solely because it searched for singular `draft retained` while the new message used `all drafts retained`. The exact draft was present. Its replacement assertion is stronger: null failed result, exact live/session text, unverified revision and no output. It now passes.

The shipping clipboard check still fails with Win32 5. An intermediate full run passed clipboard, demonstrating its intermittent nature; no related production code was changed and no resolution is claimed.

Visual review also caught immediate screenshots showing the previous pending TextBlock render while JSON already recorded successful verification at the current revision. Capture now waits for actual layout/render quiescence. The final verified PNG and JSON agree. This harness correction is distinct from the application correction.

## Independent and historical checks

MuPDF drawing traces, fontTools mappings/metrics, pypdf, pikepdf/qpdf syntax and Poppler at 72/144 DPI verify complete logical text, original font programs/used mapping rules, glyph origins/baselines, original semantic graph/mark sequences, page properties, protected whitespace and neighbours. Geometry remains 0.01pt and changed pixels outside authorised areas remain zero above channel threshold 8. One additional successful visual-suite export was checked separately and merged into the 165-output report. Reader tools retain their non-vacuous content/group coverage assertions.

Frozen historical results retain prior counts: Phase 1 14/14; Phase 2 engine 18/18; 4A/4A.1 engine 18/18 each; Phase 3 discovery 22/22; 4A compatibility 23/23; 4B document 17/17 and position 20/20; C1 insertion 30/30, document 17/17 and position 20/20. The old Phase 2 suite against Phase 3 remains 17/18 due to the historical manifestless-view-only expectation; this is not a new current-engine failure.

Character-by-character input and formatting-no-revalidation checks passed. Invalid audit prefix-caret enumeration is capped at 32 (valid positioned audits retain 200); explicit native endpoint/selection checks are separate. No standalone large-document performance or memory-leak claim is made.
