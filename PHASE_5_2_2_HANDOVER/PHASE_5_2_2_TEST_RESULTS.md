# Phase 5.2.2 test results

Windows tests use the supplied shipping build. No engine change was made to pass UI tests.

| Suite | Result |
|---|---|
| Dedicated multi-region WPF including separate recovery process | 29/29 passing |
| Inherited 5.2.1 presentation WPF | 27/27 passing |
| Marked paragraph fresh-process WPF | 16/16 passing in six processes |
| Original paragraph fresh-process WPF | 12/12 passing in five processes |
| Current worker engine/discovery/compatibility/position/insertion/document/wrap | 18+22+23+20+30+17+21 = 151 passing |
| Paragraph worker round trips | 37/37 passing |
| Original paragraph workers | 31/31 passing |
| Session models | 35/35 passing |
| Inherited full WPF controls | 57/57 passing (clipboard issue still open historically) |
| Combined successful PDFs, independent readers | 198 passing |
| Paragraph structure | 198 candidates, 225 groups passing |
| Standalone position readers | 11 passing |
| Legacy independent readers | 21 passing |
| Frozen C2 independent readers | 52 passing |

See consolidated-test-results.json and controls-shipping/*.json for exact inherited 57-check WPF/clipboard results. Historical intermittent clipboard Win32 5 is not declared resolved if a run passes. Frozen sources/binaries are executed with outputs redirected into this phase. Frozen Phase 3 engine retains its historical expectation mismatch (17/18); Phase 3 discovery 22/22 passes. Other historical exact counts are retained in phase*-regression / frozen-* reports.

Dedicated coverage (actual editor keyboard-focus assertions included): both invalid, each mixed valid/invalid combination, repeated original/expanded clicks, interactive overlap/source priority, preview overlap/source selector, selection restoration, exact-original and different-safe shortening, stale verification, actual u/CRLF/LF/multiple/trailing paragraphs/tab/NBSP/unmapped symbol/mapped-only sequences, held old responses, document history, four zooms, rejected combined export, incomplete delivery, separate-process recovery, corrected combined save/reopen/re-edit. Source hashes are checked across refusal/success.

Baseline two cases are diagnostics that demonstrate active=true/false outcomes, not passing acceptance tests. First development matrix: 28 checks, 3 failures retained. Snapshotting selection fixed an implementation bug; two test assumptions were corrected (same previously verified text can legitimately be stale; two edited regions produce two marked groups). Intermediate and final corrected runs remain separately inspectable. Earlier inherited font-control results expected an obsolete generic sentence; the shipping assertion checks current U+005A mapping feedback and exact WPF text, retaining typing/history/recovery/export checks.

## Reproduction

Build `./phase5_2_2/build.ps1`. Run `.venv/Scripts/python.exe phase5_2_2/tools/<name>.py` for each of: test_engine, test_discovery, test_compatibility, test_position, test_insertion, test_document, test_wrap, test_roundtrip, test_original; then multi_region_process, presentation_process, paragraph_process, original_process. Run UI suites sequentially to avoid focus interference. They create new timestamped evidence folders. Full inherited flags are recorded in evidence/README.md.

Models: `dotnet run --project phase5_2_2/Checks/Checks.csproj -c Release -- phase5_2_2/evidence/model phase4c1/evidence/word-spacing-analysis.json phase5_2/evidence/development-generations.json phase5_2/evidence/original-source-observations.json`.

Independent checks: tools/verify_wrap.py, verify_paragraph_structure.py, verify_positions.py, verify_independent.py, verify_frozen_c2.py, archive_verified.py and audit_release.py, using the same Python command. These use Poppler renders, pypdf, MuPDF, pikepdf and fontTools; no reader result replaces actual WPF visual review. Frozen commands: frozen_phase4a/b/c1/c2.py, run_regressions.py. Preserve recorded absolute diagnostic paths and portable-pdf-index.json rather than moving evidence folders.
