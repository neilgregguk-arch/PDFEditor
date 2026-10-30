# Phase 5.2.2 evidence index

Final pointers: `multi-region-release.json`, `presentation-release.json`, `paragraph-controls.json`, `original-controls.json`, `controls-shipping/`, `consolidated-test-results.json`. The pointers identify exact timestamped folders; those folders are retained. Stable controls-shipping is a convenience copy; original absolute paths in successful export records stay valid.

- `baseline-multi-1793356252749531400/`: actual pre-fix WPF hit routing and shortened/u diagnostics. Expanded points resolve a source but do not activate. Field `outline` checked cmap membership only; actual outline/advance inspection later corrected that interpretation.
- First development `multi-region-release-1793356568199681000/`: 28 checks/3 failures, retained honestly. Picker restoration corrected; legitimate stale-state/two-marked-group test assumptions corrected.
- Later multi-region folders: intermediate and shipping passes, including real UI overlap adversaries, four zooms, Unicode sequences, source hashes, successful save/reopen, new-process recovery. Use the final pointer for approval.
- `subset-native-glyph-inspection.json`: independent fontTools inspection: u has cmap entry, zero hmtx advance and zero glyf contours in both Word embedded subsets. Final WPF diagnostic adds true GlyphTypeface outline/advance and visible review-advance assertions. No PDF engine change.
- `computer-use/`: initial owned Windows input observation reproduced invisible u before the review-font correction. Any shipping Windows input review is separately identified by computer-use-review.json. Automated SendInput is distinct from programmatic WPF routed tests and human acceptance.
- `visual-qa/`: labelled scaled actual control screenshots; full PNG/JSON remain in source folders. Overlap adversary placement is test-only, never a claimed production PDF geometry.
- Worker suites: *-tests.json and regression-logs/test_*.log. New phase uses inherited Core unchanged. Actual source/identity/exact-text geometry and font rules remain frozen.
- `wrap-independent-verification.json`, `paragraph-structure-verification.json`, `position-independent-verification.json`, `independent-verification.json`: successful PDF independent extraction/font/geometry/Poppler/structure checks. All UI exports, original worker outputs, wrapping/document/insertion/roundtrip saves are included. `verified-export-records.json` freezes complete expectations. `portable-pdf-index.json` retains source/destination paths/hashes when transient copies are required.
- `frozen-*`, phase*-regression.json and regression-logs: preserved worker/binary regressions, including the known frozen Phase3 engine expectation mismatch (17/18). No old source/evidence is rewritten.
- `starting-preservation.json`, `prior-phase-preservation.json`, `phase1-preservation.json`, `release-manifest.json`: starting 13,886-path baseline, only intentional START_HERE change, Phase1 353 paths, final new source/build/evidence hashes.

Full inherited WPF command (replace <out> with a new absolute evidence folder):

```powershell
./phase5_2_2/run/PdfEditorPrototype.exe --ui-test --discovery-ui-test --font-ui-test --position-ui-test --session-ui-test --insertion-ui-test --wrap-ui-test --clipboard-probe --paragraph-stage 0 --paragraph-shared <out> --audit <out>
```

Run desktop suites sequentially. Earlier inherited font-control failures expecting the exact old generic sentence are retained; the new test checks actual U+005A mapping feedback and exact retained WPF text while keeping typing/history/recovery/export assertions. Clipboard Win32 5 remains open regardless of a passing probe. Reproduce commands and physical acceptance tasks are in the handovers. No Phase5.3 or Repository Maintenance R1.
