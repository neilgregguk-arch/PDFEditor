# Phase 5.2 evidence index

Authoritative release: seven current worker reports (151 checks), roundtrip-tests.json (37), original-tests.json (31), model/model-tests.json (35), paragraph-controls.json (16), original-controls.json (12), final-build.json (tested engine/worker/native hashes unchanged; app phase-caption correction and 3/3 fresh smoke checks).

Independent: wrap-independent-verification.json (119 outputs), paragraph-structure-verification.json (119 outputs/124 actual groups), position-independent-verification.json (11), independent-verification.json (21). portable-pdf-index.json maps 174 checked PDF paths to retained files. run/original-examples/examples.json maps ready-to-open copies to their evidence.

controls-shipping is the full inherited run (55/57). Timestamped basic retries are 10/11 on current and untouched 5.1, failing clipboard only; the initial diagnostic assertion passes on retry. New paragraph/original controls pass completely. Historical counts/obsolete Phase 3 expectation are detailed in the test report; frozen-c2-readers verifies 52 C2 combined exports.

Original provenance, actual text/font/structure observations and ABI investigation: investigation/, original-tests.json, original-source-observations.json and run/original-paragraphs. Resource samples: original-performance.json and original-page-performance.json. Visual contacts in visual-qa were rendered and inspected. WPF screenshots capture editing/validation; result JSON establishes successful export.

Development failures remain in original-tests-development*, original-tests-before-extra-adversaries*, development-before-scope-fix*, earlier original-tests*/adversaries, and investigation. development-export-record* files are diagnostic. Raw logs may refer to transient fonts/candidates, which are not app dependencies. Frozen outputs stay in their designated folders.

starting-preservation.json records 8,671 pre-existing tracked files. prior-phase-preservation.json permits only the audited START_HERE update. release-manifest.json hashes source, runtime/run, tools, retained evidence, handovers and progress, excluding itself and ignored caches/bin/obj/test-work. Historical checkpoint sections are not current release claims.

Baseline verification: baseline-git-verification.json reconstructs all starting paths/hashes directly from Git. development-starting-preservation-rewritten-keys.json retains the copy-migration bookkeeping defect; no old-phase bytes changed. Final engine/worker/native hashes remain tested; final-caption-smoke.json adds 3/3 WPF checks and one independently verified export, included in the 119/124 totals.
