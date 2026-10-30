# R1 validation results

Latest accepted Phase 5.2.2 source rebuilt with Build-Current.ps1 into .local-generated/R1-validation/run. No application source was edited. Actual WPF executables launched and closed across the suites; inventory/rebuilt-application-wpf.png is a genuine rendered-control capture. Programmatic WPF testing is not human mouse/keyboard/DPI/accessibility certification.

| Check | Result |
|---|---|
| Current engine/discovery/compatibility/position/insertion/document/wrap workers |151/151 |
| Phase 5.1 paragraph worker round trips |37/37 |
| Phase 5.2 original Word workers |31/31 |
| Session/layout models |35/35 |
| Phase 5.2.2 multi-region WPF including separate recovery process |29/29 |
| Phase 5.2.1 presentation WPF |27/27 |
| Marked paragraph new-process WPF |16/16 |
| Original Word new-process WPF |12/12 |
| Inherited WPF controls |57/57 |
| Independent combined PDF candidates |110 passing |
| Independent paragraph structure |117 groups passing |
| Frozen Phase 2 original source/binary |18/18 |
| Cleanup audit/dry-run/refusal/WhatIf safety |18/18, no removal |
| Ignore boundary rules |14/14 |
| Pinned runtime/font/notices |19/19 SHA256 matched |
| Explicit historical-stamp host launch/inspect smoke |1/1; no source mutation |

Compact details: inventory/validation-summary.json, validated-build-identity.json, build-reproduction.json, frozen-phase2-validation.json, cleanup-safety-tests.json, ignore-rule-tests.json. Full generated logs/PDFs/JSON/renders remain in the ignored stage, not duplicated into Git. Archived older source/evidence hashes are checked against baseline; the compatibility suite also invokes a frozen Phase 3 worker. Full historical suites were not all repeated: maintenance changes no application logic, and no historical binary/evidence was removed. The prior frozen Phase 3 expectation mismatch and historical intermittent clipboard Win32 5 remain open; a passing current probe does not establish a fix.

One harness attempt failed before presentation launch because wrapper CLI arguments were interpreted as an optional reproduction filename. Clearing inherited sys.argv fixed invocation; completed worker/multi-region results were reused and the remaining suites resumed. Only path/argument bindings change in memory, not inherited test or application logic. Recipes record source test hashes.

Reproduce: run Build-Current.ps1 with a new output folder; `.venv/Scripts/python.exe REPOSITORY_MAINTENANCE_R1/tools/validate_r1.py --stage <output>` (add --resume only for the same unchanged build), and run the model command recorded in LOCAL_CLEANUP_GUIDE. Frozen smoke: tools/validate_frozen_phase2.py. Safety: tools/test_cleanup_safety.py. Ignore: tools/test_ignore_rules.py. Independent readers use pypdf, pikepdf, MuPDF, fontTools and Poppler; no PyMuPDF is added to the shipped application.

**No approved destructive cleanup occurred.** These establish build/run after maintenance, not after an unperformed cleanup. After any separately approved real cleanup, rebuild and rerun critical checks using a fresh stage before declaring cleanup successful. A live junction test was not created; ancestor rejection is implemented and inspected. Clean is deliberately file-by-file, not an atomic directory transaction.
