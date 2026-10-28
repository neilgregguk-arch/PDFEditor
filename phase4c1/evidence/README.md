# Phase 4C.1 evidence index

See `../../PHASE_4C1_HANDOVER/PHASE_4C1_TEST_RESULTS.md` for executed counts, failures, timings and reproduction. Final acceptance evidence:

- `word-spacing-analysis.json`: genuine Word sources, raw encoded codes, Unicode/GID/font metrics, TJ data, measured residuals, glyph geometry and protected objects.
- `insertion-corpus.json`: hashes/provenance of development fixtures; no product merge feature or ownership hints.
- `insertion-tests.json`: 30 worker cases, 23 successful saved records, including negative overlap/extraction/overflow/graphic controls.
- `model/model-tests.json`: 17 session/history/recovery/position invariants.
- `document-tests.json`: 17 combined transaction regressions.
- `position-tests.json`: 20 active position checks, including three intentional support changes.
- `final-release-controls/`: 46 actual WPF checks, five clipboard probes, captured requests/results and screenshots. No hardware/file-picker automation.
- `selection-verified-controls/`: final eight new control checks repeated with rendering wait for selection screenshots; five successful exports included in independent checks.
- `process-recovery.json`: exact folder for two exited processes restoring insertion/deletion/natural drafts and history, followed by combined export.
- `document-independent-verification.json`: 57 complete recorded combined exports checked by MuPDF/pypdf/fontTools/qpdf/Poppler, every page at 72/144 DPI. `document-poppler/` indices follow its case order.
- `independent-verification.json`, `position-independent-verification.json`: 21 legacy discovery/font and 11 fixed-position outputs, respectively. Sets can overlap.
- `engine-tests.json`, `discovery-tests.json`, `compatibility-tests.json`: unchanged active worker contracts, alongside active position tests (83 total checks).
- `phase1-regression.log`, `phase*-regression.json`, `frozen-phase3-discovery/`, `frozen-phase4a/`, `frozen-phase4b-test_document/`, `frozen-phase4b-test_position/`: applicable preserved-worker regressions, with output redirected here. Phase 3's obsolete unknown-PDF-view-only expectation remains a documented 17/18 failure.
- `document-performance.json`: roundtrip/stage times, repeated-edit handles/memory and candidate retention.
- `prior-baseline.json`, `prior-phase-preservation.json`, `phase1-preservation.json`, `release-manifest.json`: preservation and final deliverable hashes.
- `combined-exports-contact-sheet.png`, `visual-review.json`: inspected complete-output and live-presentation checkpoints.

Development evidence remains under `development/`, `development-initial-insertion-tests.json`, `insertion-controls/` and timestamped files. Earlier failures are not final acceptance. The test report explains fixture/example refusals, changed old expectations, session-isolation test corrections, Calibri native caret failure and parser/capture corrections. Raw development outputs outside designated records are not all claimed independently certified.

Clipboard Win32 5 remains intermittent. Actual measured Windows scale was 100% / 96 DPI. There is no physical input, OS display-scale sweep, large-document or broad semantic PDF certification.
