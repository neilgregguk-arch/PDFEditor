# Phase 4A.1 test results

28 October 2026. Actual local execution against the final framework-dependent Windows x64 build. Evidence paths below are relative to `phase4a1/evidence/`. Programmatic WPF controls and independent readers are distinguished from physical input.

| Executed suite | Result | Evidence |
|---|---|---|
| Active original worker checks | 18/18 | engine-tests.json |
| Active discovery checks | 22/22 | discovery-tests.json |
| Active font compatibility checks | 23/23 | compatibility-tests.json |
| Position-aware checks | 20/20 | position-tests.json |
| Actual WPF original editor | 11/11 | release-verified-controls/control-tests.json |
| Actual WPF discovery | 5/5 | release-verified-controls/discovery-control-tests.json |
| Actual WPF font controls | 4/4 | release-verified-controls/font-control-tests.json |
| Actual WPF position controls | 6/6 | release-verified-controls/position-control-tests.json |
| Frozen Phase 2 binary/original worker suite | 18/18 | phase2-regression.json |
| Frozen Phase 3 binary/original worker assertions | 17/18; known obsolete manifest assertion | phase3-regression.json |
| Frozen Phase 3 discovery suite/binary | 22/22 | frozen-phase3-discovery/tests.json |
| Frozen Phase 4A worker suite/binary | 18/18 | phase4a-regression.json |
| Frozen Phase 4A compatibility suite/binary | 23/23 | frozen-phase4a/tests.json |
| General independent exports | 21 PDFs, 72/144 DPI | independent-verification.json |
| Position-specific independent exports | 11 PDFs, 72/144 DPI | position-independent-verification.json |

The independent sets overlap on two Word outputs: **30 distinct PDFs** were verified. MuPDF checks all positioned target/neighbor origins and unchanged boxes; pypdf checks exact intended Unicode, font programs and mapping/width rules; Poppler checks outside-area pixels at two resolutions; qpdf through pikepdf checks syntax. All approved positioned outputs have measured zero origin shift and zero unchanged-box shift; all outside-area pixel counts are zero. Original reconstruction has zero changed full-page pixels. Font program sets, info metadata and Word F2 raw whitespace bytes are preserved. Resource aliases may increase while referencing the same unchanged font dictionary.

## Negative evidence and regression changes

The frozen original manifestless-view-only assertion became obsolete in Phase 3 and remains recorded as a raw failure. In this phase, six old assertions expecting Word/spacing activation to be refused were initially rerun unchanged: discovery had 2 failures, compatibility 4 failures. Their raw logs remain in `development/initial-*`. The active copies now assert actual positioned Word activation and real saves, while ReportLab metric-rounding fixtures remain refused. No unrelated test or threshold was weakened; original files are untouched.

Early Arial/Calibri `calm` -> `call` candidates failed exact extraction because a large gap created an extra space. This remains a deliberate candidate-refusal WPF test. An initially accepted synthetic kerning candidate failed MuPDF at 0.012009 pt unchanged-space shift; the new metric gate refuses that class. Pre-guard outputs/data remain explicitly labeled development evidence. An unwanted native word wrap during title activation was corrected by sizing the input control independently of the narrow export boundary. The final title caret test asserts <0.75 pt and measured maximum 0.254002 pt across four zooms.

The WPF suite covers click-selection, original-position presentation, native undo/redo, live revision verification, first export, rediscovery and second narrower export, complete longer/wider/unmapped/newline draft recovery and refusals, plus failed-candidate draft preservation and terminal-newline paste/history/recovery. Existing tests cover native routed input/navigation/deletion, clipboard/history, natural wrapping, overflow, unsupported character recovery, original/destination protection, stale results and worker restart. The final clipboard probe records five read/write/read matches. Historical intermittent Win32 5 clipboard failures have **not been fixed** and remain an issue.

Physical mouse/keyboard interaction, real file-picker traversal, hardware caret blinking/dragging and cross-application clipboard acceptance were not verified. Prior automation activation failures were not rerun. User comfort feedback from the earlier prototype is prior feedback, not new physical acceptance.

## Performance and resources

Side-by-side inspection used the same bytes for 34 PDFs, including five added position/ownership cases. Fresh-worker medians were 61.65 ms for Phase 4A and 63.65 ms for Phase 4A.1 across this small mixed corpus. Fresh Word inspection was 445.21 ms; cached inspection median 44.45 ms. These include IPC and rendering, are not isolated input latency, and are not a real-world acceptance benchmark.

The 32-distinct-fingerprint resource probe crosses the eight-page cache limit, repeatedly verifies eight original objects, and shows 0 handle growth after warm-up. The worker exits successfully. Six cached Word preview candidates had median 83.31 ms. Exact memory snapshots and timings are in resource-probe.json. This does not prove leak freedom, large-document responsiveness or bounded temp disk. Analysis is cached, candidate work is debounced/asynchronous, and there is no in-flight cancellation.

## Reproduction and preservation

Build with `phase4a1/build.ps1`. Development checks use the existing project `.venv/Scripts/python.exe` and `phase4a1/tools/test_engine.py`, `test_discovery.py`, `test_compatibility.py`, `test_position.py`, `compare_positions.py`, `resource_probe.py`, `verify_independent.py`, `verify_positions.py`. `analyse_positions.py` creates the detailed source analysis. They are development tools, not shipped runtime dependencies. Tests create fresh destinations rather than overwrite input PDFs.

WPF: launch `run/PdfEditorPrototype.exe --ui-test --discovery-ui-test --font-ui-test --position-ui-test --clipboard-probe --audit <new-folder>`. The flags execute actual window/control methods; they are not physical automation. Test recovery is isolated.

prior-phase-preservation.json and release-manifest.json record preservation and final source/runtime/document hashes. Corpus source hashes are checked before/after. Prior sources/builds/evidence were not edited. This is not disconnected-VM, installer, security-sandbox or hostile-document certification.
