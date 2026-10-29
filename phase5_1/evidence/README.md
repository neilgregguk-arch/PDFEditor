# Phase 5.1 evidence index

Start at [the handover](../../PHASE_5_1_HANDOVER/PHASE_5_1_IMPLEMENTATION_REPORT.md) and [test results](../../PHASE_5_1_HANDOVER/PHASE_5_1_ROUNDTRIP_TEST_RESULTS.md).

- [Starting state](starting-state.json), [prior baseline](prior-baseline.json), [preservation](prior-phase-preservation.json), [release manifest](release-manifest.json).
- [Round trips/adversaries](roundtrip-tests.json): 37 checks; [separate processes](paragraph-controls.json): 16 checks; [model](model/model-tests.json): 29 checks; [exact-space refusal](paragraph-space-restriction.json).
- Current worker suites: engine 18, discovery 22, compatibility 23, position 20, insertion 30, document 17, wrap 21.
- [Final inherited WPF suites](controls-shipping/) and [summary](control-summary.json): 56/57, with the same clipboard failure in [untouched C2](frozen-c2-controls/). Retry/probe failures are retained. Older folder names containing “approved” are development labels and do not override controls-shipping.
- [Combined independent index](wrap-independent-verification.json): 206 PDFs; [structure index](paragraph-structure-verification.json): 287 group instances. [Records](verified-export-records.json) identify exact certified exports. Fixed-position and legacy reports cover 11 and 21 additional outputs.
- [Frozen C2 worker suites](frozen-phase4c2/) and [original-engine independent report](frozen-c2-readers/wrap-independent-verification.json): 73 PDFs; older frozen suites/logs remain under this phase. The Phase 2-on-Phase 3 obsolete expectation and clipboard failures remain visible.
- [Performance](paragraph-performance.json), [32-group export records](paragraph-performance-records.json), wrap-performance.json and controls-shipping/wrap-control-tests.json provide timing/resource evidence.
- [Visual review](visual-qa.md), visual-contact-sheet.png and export-contact-sheet.png; [sample hashes](../run/paragraph-examples/manifest.json).
- Development folders retain failed/partial attempts: initial fixture/scalar/whitespace tests, content-stream/metadata-size/space-extent/reconstruction issues, PID reuse, output-redirection and reader mistakes. Earlier successful prototype files outside certified indexes are diagnostic, not supported release examples.

No previous release evidence is overwritten. Some JSON contains original workstation or transient paths. Retained exported PDFs and source fixtures are the portable artifacts; excluded test-work/fonts/candidates can be regenerated. No credentials or private user PDFs are part of the evidence. The exact export and preservation manifests, not every loose prototype file, define this release.
