# Phase 4A test results

28 October 2026. All results refer to actual local execution. Worker tests, WPF control integration and physical interaction are distinct evidence categories.

## Executed suites

| Suite | Result | Evidence under `phase4a/evidence/` |
|---|---|---|
| Frozen Phase 2 worker tests against frozen binary | 18/18 pass | `phase2-regression.json` |
| Frozen original worker assertions against Phase 3 | 17/18; one obsolete assertion retained | `phase3-regression.json`: manifestless supported copies are intentionally discoverable since Phase 3 |
| Frozen Phase 3 discovery source against frozen binary | 22/22 pass | `frozen-phase3-discovery/tests.json` |
| Active Phase 4A worker regression | 18/18 pass | `engine-tests.json`; obsolete manifestless-view-only assertion updated with an explanation; original source/evidence retained |
| Existing discovery tests against Phase 4A | 22/22 pass | `discovery-tests.json` |
| New compatibility tests | 23/23 pass | `compatibility-tests.json` |
| Frozen Phase 2 WPF controls | 11/11 pass in this execution | `ui-phase2/control-tests.json` |
| Frozen Phase 3 WPF controls and discovery controls | 11/11 and 5/5 pass | `ui-phase3/` |
| Final Phase 4A original WPF controls | 11/11 pass | `final-controls/control-tests.json` |
| Final Phase 4A existing discovery controls | 5/5 pass | `final-controls/discovery-control-tests.json` |
| Final Phase 4A new subset controls | 4/4 pass | `final-controls/font-control-tests.json` |
| Independently verified product exports | 19 PDFs at 72 and 144 DPI | `independent-verification.json` |
| Pinned-binary API mechanisms | 8 experiments, including two negative controls | `api-investigation.json`, `api-independent-verification.json`; not product-approved exports |

No failing test was silently disabled. The active test replacing `test_unknown_pdf_view_only` checks that a supported manifestless copy is discovered. This expectation became obsolete in Phase 3; its frozen raw failure is still recorded. The previously recorded clipboard failures also remain in earlier phases. Earlier development/control runs for this phase are retained separately from `final-controls/`.

## Compatibility tests

The 23 tests cover structural activation without complete alphabet coverage; equal-width glyph reordering; longer existing-glyph wrapping; an original-characters-only font; missing subset coverage; bold subsets; refusal of fragmented objects, explicit character spacing and kerning; selected safe reverse mapping with a duplicate Unicode alias; wrong/missing Unicode refusal; separate Word font/spacing/ownership blockers; Arial/Calibri/Consolas Word exports; second-generation subset editing; probe cleanup and stable cached observations; overflow refusal; distinct missing-cmap handling; the newly supported partial-encoding case; refusal of its retained but unmapped Z; a second edit to that case; a direct frozen Phase 3 refusal assertion; and a conservative PowerPoint refusal.

Before/after classifications were executed against both binaries for all **29 source PDFs**: the existing 15-document corpus and 14 targeted sources, including three new Word exports and one PowerPoint export. This is not a real-world acceptance percentage. The useful product compatibility gain is the valid J partial-encoding scenario, not the already-supported tiny ASCII-only subsets.

Product export checks retain exact extracted Unicode, genuine original object removal, original font bytes/style, source integrity, page dimensions/count, annotation count, selected info metadata, unchanged pages, collisions and outside-region pixels. New checks also verify neighbouring glyph origins/bounds, replacement glyph geometry, reopened outlines and object-level glyph appearance. No collision or geometry threshold was relaxed.

Independent checks use pypdf extraction/font programs/run origins/info metadata, qpdf syntax inspection through pikepdf, MuPDF per-glyph origins/bounds and Poppler rasterisation. All 19 product outputs have **zero changed pixels outside the allowed edit area** at both resolutions. Independent neighbouring glyph shift is **0 pt** in these fixtures. Every saved replacement is extractable, and font program sets match. These are measured fixture results, not complete PDF object/tag/XMP equivalence or print fidelity certification.

## Actual WPF integration

The unchanged original suite exercises 16 sampled caret mappings across four zooms, bitmap switching, native input/navigation/selection commands, multi-action undo/redo, clipboard/history, native wrapping, overflow preservation, unsupported-character recovery, real export/original overwrite rejection, stale responses and worker restart.

New subset controls use the actual shared click-selection method and RichTextBox on J. They measure 16 caret samples at indices 0/2/4/9 and zoom 75/100/150/200%; verify undo/redo and an actual original-font save; continue typing after unsupported Z, preserve both invalid draft revisions through undo/redo and recovery, and reject export without losing text; verify bold subset display and human-readable Word refusal. A related layout or control test is not called physical typing or mouse input.

The final control exports are independently extractable through the same save method used by Save As. Actual Open/Save As picker traversal, physical mouse drag/caret blinking, sustained hardware typing and cross-application clipboard acceptance remain manual items. This milestone did not rerun the failing external activation automation; its prior failure is documented. The user's earlier comfort confirmation is retained as prior feedback, not converted into Phase 4A physical acceptance.

Clipboard read/copy/cut/paste/history passed in all completed WPF suites in this execution; the standalone final probe also records its actual outcomes. There was **no clipboard fix**. Earlier Win32 5 failures were intermittent, and this run does not establish their root cause or a permanent resolution.

## API laboratory: expected versus observed

The actual pinned DLL's exports and matching native wrapper hash were checked. Successful return values were followed by save/reopen, Unicode/font checks, glyph-origin checks and independent renders.

| Scenario | Expected / actual conclusion |
|---|---|
| Existing text via SetText | Intended replacement extracts and renders; unrelated glyphs unchanged. A known-object mechanism, not automatic eligibility. |
| Existing verified raw codes | Same intended render as existing-character SetText. |
| Unmapped `!` | API returns success but text differs after reopen; negative control correctly demonstrates insufficiency of return value. |
| Original text with explicit positions, both setters | Nonempty position calls succeed; original target origins survive; full-page Poppler renders are identical at 72/144 DPI. |
| Equal-width `Phase` -> `Phace`, both setters plus positions | Genuine changed glyph; other origins retained; font programs and document info metadata unchanged; outside-title pixels zero. Not promoted into the natural inline editor. |
| Wrong raw space code | Unicode matches but visible glyph differs from correct-code output by 235/730 pixels at 72/144 DPI. Negative control is not a safe export. |

The lab driver initially used ctypes pointer-wrapper equality, producing empty ownership arrays. That intermediate JSON is retained with an explicit initial-driver name. Native-address comparisons, nonempty glyph-count assertions and successful nonempty position-call assertions now guard the rerun. Production C# IntPtr comparison was unaffected. No earlier vacuous geometry result is used as final proof.

## Performance and preservation

The recorded compatibility run's inspect calls, including IPC and rendering, are approximately **31-295 ms**, median approximately **77 ms**. Exact per-call timings are retained; small variations between repeated runs are expected. Compared with the earlier small Phase 3 measurement, the additional per-character/object checks cost time, while remaining in the background worker. This is not an isolated input-latency or large-document benchmark.

The final preservation and release manifests enumerate earlier files and current source/build hashes. All **353 Phase 1 artifacts** and **454 earlier baseline files** remain byte-identical. No earlier sample, test or handover was rewritten. Corpus input hashes are also checked before/after compatibility execution. Exact counts/results are in `prior-phase-preservation.json` and `phase1-preservation.json`.

Resource limits remain qualified: an eight-page analysis cache is bounded, but temporary candidate/font/render disk usage and fonts per page are not. No production installer, disconnected VM, native sandbox, disk-full/power-loss campaign or hostile PDF test was added.
