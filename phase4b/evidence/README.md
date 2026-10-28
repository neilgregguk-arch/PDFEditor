# Phase 4B evidence index

The designated final build control run is **final-release-controls/**: 38/38 checks and five clipboard probes. Read `../../PHASE_4B_HANDOVER/PHASE_4B_TEST_RESULTS.md` for full results and limitations. Earlier failed runs remain for audit, not as the final acceptance run.

## Final evidence

- `document-tests.json`: 17 combined worker checks and ten complete export records.
- `model/model-tests.json`: 11 session/history/recovery invariants.
- `process-recovery.json`: two distinct exited app processes, three recovered drafts on two pages and one export; references exact timestamped folder.
- `final-release-controls/`: original, discovery, font, positioned and session control JSON, export audit records, screenshots and clipboard probes. Native WPF controls; no hardware/file-picker automation.
- `document-independent-verification.json`: 21 combined exports (ten worker, ten final UI, one recovery), every page with independent readers and Poppler 72/144 DPI.
- `document-poppler/`: final combined independent page rasters; indices follow the case order in the JSON, not file-name sorting.
- `combined-exports-contact-sheet.png`, `visual-review.json`: reviewed visual checkpoints.
- `independent-verification.json`, `poppler/`: 21 additional legacy discovery/font outputs.
- `engine-tests.json`, `discovery-tests.json`, `compatibility-tests.json`, `position-tests.json`: active worker regressions, 83/83.
- `phase1-regression.log`, `phase*-regression.json/.log`, `frozen-phase3-discovery/tests.json`, `frozen-phase4a/tests.json`: applicable frozen regressions. The original Phase 2 unknown-PDF policy test against Phase 3 remains a documented 17/18 failure.
- `document-performance.json`: measured preview time, handle observations and candidate bounds.
- `prior-baseline.json`, `prior-phase-preservation.json`, `phase1-preservation.json`: before/after preservation evidence.
- `release-manifest.json`: final implementation, tools, runtime, fixtures and six handover file hashes.

## Retained development evidence

`old-control-contracts/` contains 14/26 historical UI-contract failures. `active-controls-1/` and `release-controls/` contain intermittent clipboard failures (25/26 and 37/38 respectively). `final-controls/` and `verified-controls/` are superseded passing checkpoints. Other `session-controls*` folders are intermediate runs. `development/initial-document-tests.json` retains an initial test-helper failure. Timestamped exports and recovery stores remain; only the records referenced by designated JSON are the approved final verification set. Do not interpret every development output as an independently certified deliverable.

No clipboard fix or physical input verification is claimed. Preservation excludes generated bin/obj/test-work caches; prior source/runtime/evidence/handover content is checked. See the issues report for semantic PDF and packaging limits.
