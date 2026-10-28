# Phase 4C.2 evidence index

Approved WPF run: [final-controls-approved/](final-controls-approved/), 57 passing checks (46 inherited, 11 wrapping). Other control folders retain development attempts, including failures.

- [Wrapping worker](wrap-tests.json): 21 checks, 15 successful saves. [Model](model/model-tests.json): 22 checks.
- Current worker JSON: engine-tests (18), discovery-tests (22), compatibility-tests (23), position-tests (20), insertion-tests (30), document-tests (17).
- [Combined independent reader index](wrap-independent-verification.json): 142 saved PDFs, including successful retained development UI exports. Each source/destination hash and page's geometry/text/font/whitespace/72/144-DPI comparisons is recorded.
- [Fixed-position reader index](position-independent-verification.json): 11 PDFs; [legacy reader index](independent-verification.json): 21.
- [Process recovery](process-recovery.json): three drafts/two pages across exited processes. [Performance](wrap-performance.json): preview stages, repeated operations, handles, cache, exit and recovery size.
- [Corpus provenance](wrap-corpus.json), [baseline](prior-baseline.json), [prior preservation](prior-phase-preservation.json), [Phase 1 preservation](phase1-preservation.json), [release manifest](release-manifest.json).
- Frozen regression JSON/logs are under this directory and frozen phase subdirectories. Phase 2-on-Phase 3 retains one obsolete expectation failure.
- [Visual QA](visual-qa.md), [contact sheet](visual-contact-sheet.png), approved control images and Poppler rasters.
- Development retains initial collision/wrap attempts, the earlier graphic-policy assertion, failed combined controls and wrap-controls through wrap-controls-6. TEST_RESULTS explains each. Early collision exports referring to a replaced source are diagnostic, not certified; the original fixture is archived.

Prior phases remain byte-identical. START_HERE is the separately recorded intentional repository-entry update. Some JSON paths refer to original workstation/transient candidates; exported PDFs/source fixtures remain, while test-work/bin/obj/caches are excluded. Development patch/probe scripts preserve provenance and are not the normal build path. Reader reports identify certified saved outputs.
