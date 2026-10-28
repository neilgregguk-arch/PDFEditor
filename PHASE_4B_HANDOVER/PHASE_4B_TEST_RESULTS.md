# Phase 4B executed test results

Executed locally on Windows x64 with .NET 8 WPF and pinned PDFium. Final framework-dependent App and Worker publish succeeded on 28 October 2026. Code and binary hashes are in `evidence/release-manifest.json`. No fidelity threshold was relaxed. All paths below are relative to `phase4b/evidence/` unless stated otherwise. Earlier failures are retained and described below.

## Designated release checks

| Actual WPF control suite | Result | Evidence |
|---|---:|---|
| Original inline controls | 11/11 | `final-release-controls/control-tests.json` |
| Discovery controls | 5/5 | `final-release-controls/discovery-control-tests.json` |
| Font controls | 4/4 | `final-release-controls/font-control-tests.json` |
| Position controls | 6/6 | `final-release-controls/position-control-tests.json` |
| Document session controls | 12/12 | `final-release-controls/session-control-tests.json` |

Total final control assertions: **38/38**. These use actual WPF controls, routed composition/commands, source region selection and Save As internals; they do not automate hardware input or native file pickers. `clipboard-probe.json` in the same folder has **5/5** successful read/write/read iterations. This does not prove the intermittent clipboard problem fixed.

`model/model-tests.json`: **11/11** session invariant tests, including foreign equal-revision session rejection and stale revision/hash rejection, chronological history and branch truncation, no selection-only entries, history limits, compatible recovery, malformed/corrupt/oversized recovery and retained incompatible original snapshots.

`document-tests.json`: **17/17** combined worker cases, including ten successful saved outputs. Tests cover two natural regions, two wrapped/expanding natural paragraphs, two Word regions, mixed strategies, different pages, individually successful edits rejected together for collision, unsupported one blocking all, second generation, failed final move cleanup, duplicate ownership, wrong identity/hash, source and existing destination byte protection, complete natural deletion plus another edit, no-op rejection, unchanged positional count restrictions and worker restart identities. All source fixture hashes are retained and checked.

`process-recovery.json`: **pass**, three drafts across two pages recovered between two fully exited application processes with distinct PIDs, history undo/redo and one successful combined save. Original hash preserved. The timestamped folder in this JSON contains both stage reports and isolated store.

## Requested scenarios A–K

| Scenario | Executed evidence / result |
|---|---|
| A — switch A/B/back | Actual session controls retain both latest drafts and inactive presentation; pass. |
| B — edit A/B/C then chronological undo/redo | Actual controls and model tests; inactive affected region activated, branch invalidated; pass. |
| C — combined natural | Worker single candidate, two expanding wrapped paragraphs and actual controls; pass. |
| D — two positioned Word runs | Worker and actual controls, four zooms and independent origins; pass. |
| E — natural + positioned | Genuine Word streams plus separately generated natural fixture region; worker/control/export checks pass. |
| F — combined overlap | A and B each save safely alone; combined one-point line overlap rejected with both region warnings; drafts remain; pass. |
| G — unsupported character in A, valid B | Complete save rejected; both working drafts accessible; no valid-only partial output; pass. |
| H — multiple pages | Worker, actual controls (four edits across two pages) and process recovery export; pass. |
| I — recovery | Same-window control restoration, bounded/corrupt model cases and two-process recovery; pass. |
| J — failed export | Original/existing filename protection plus final-move-to-directory failure; no stage residue/partial PDF, drafts retained; pass. |
| K — second generation | Fresh discovery from first combined output and subsequent verified edit; worker and controls pass. |

## Independent full-document checks

`document-independent-verification.json`: **21/21 PDFs**, comprising ten worker exports, ten final release control exports and one separate-process recovery export. Every page was checked at 72 and 144 DPI by Poppler; MuPDF, pypdf and pikepdf/qpdf also reopen/check the documents. Checks cover all replacements, removal of source target objects, font programs and used mapping/width rules, untouched glyphs, protected whitespace bytes, dimensions, page counts, metadata and source SHA256. Zero unexpected changed pixels were accepted outside the authorised union (channel threshold 8). Maximum observed untouched glyph shift: **0 pt**; maximum positioned target origin shift: **3.0517578e-05 pt**, within 0.01 pt. Independent whitespace-normalization is used only for extracted wrap separators; exact intended run text is separately verified by the worker.

`independent-verification.json`: **21/21 additional legacy discovery/font outputs**, checked by Poppler at both DPIs, pypdf and qpdf via pikepdf. This is a separate set from the combined outputs.

The full combined renders are in `document-poppler/`. `combined-exports-contact-sheet.png` was visually reviewed for natural, wrapped, Word, mixed and both multi-page pages. Final WPF `two-drafts.png`, `font-warning.png` and `word-refused.png` were visually reviewed: latest inactive text is present, unsupported text persists and warnings/counts are visible. Review is of rendered output, not physical input.

## Applicable prior regressions

| Suite | Executed result | Evidence |
|---|---:|---|
| Phase 1 feasibility | 14/14 | `phase1-regression.log`; frozen saved outputs read, harness not regenerated |
| Active Phase 4B single-region engine | 18/18 | `engine-tests.json` |
| Active discovery | 22/22 | `discovery-tests.json` |
| Active font compatibility | 23/23 | `compatibility-tests.json` |
| Active positioned editing | 20/20 | `position-tests.json` |
| Frozen Phase 2 engine | 18/18 | `phase2-regression.json` |
| Frozen original Phase 2 assertions against Phase 3 | 17/18 | `phase3-regression.json`; obsolete unknown-PDF-view-only expectation fails |
| Frozen Phase 4A engine | 18/18 | `phase4a-regression.json` |
| Frozen Phase 4A.1 engine | 18/18 | `phase4a1-regression.json` |
| Frozen Phase 3 discovery | 22/22 | `frozen-phase3-discovery/tests.json` |
| Frozen Phase 4A font compatibility | 23/23 | `frozen-phase4a/tests.json` |

Active worker regressions total 83/83. Frozen tests execute their preserved workers with all fresh outputs redirected under Phase 4B. The one Phase 3 failure is retained: discovery intentionally made unmanifested eligible PDFs editable after Phase 2's original policy. It is not hidden or counted as a new pass. Full unchanged old WPF contracts initially failed 14/26 because several contracts require superseded single-region behaviour; see the failure accounting below.

## Performance and bounds

`document-performance.json` has five measured previews per case, including IPC, discovery/planning, save/reopen and verification. Median milliseconds: two natural **104.8**, three natural **101.2**, four over two pages **150.6**, two Word **166.4**, mixed **213.1**. These are small local fixtures, not a large-document or physical typing guarantee.

The final actual-control 30-operation input burst measured median synchronous handler **0.7109 ms**, max **1.7234 ms**, with **0 immediate worker requests**. Validation is debounced/asynchronous. The timing covers control insertion and its synchronous change handler, not keyboard-to-screen latency.

Twenty-four extra four-region previews after warmup showed handle growth **-2**, retained twelve candidate PDFs/twelve PNGs, and worker exit. History entry/character and recovery size limits have executable tests. No total-memory or crash-orphan cleanup certification is implied.

## Failure accounting and corrections

Raw `old-control-contracts/` results show **14/26 failures**: six original, one discovery, two font and five positioned. Required global undo/recovery, source-clean rendering and free switching supersede their old native/per-region stack, single-draft, bitmap and dirty-switch expectations. Active tests now assert the document contracts; substantive glyph, caret, pixel and export safety thresholds remain. `active-controls-1/` had 25/26 passes; `release-controls/` had 37/38, both with historical clipboard Win32 5. Later `final-controls/`, `verified-controls/` and designated `final-release-controls/` passed all 38. No clipboard fix was made or claimed.

An early layer-order constructor exception was corrected before release. UTF-8 normalization fixed source arrow mojibake. Initial document test failure in `development/initial-document-tests.json` was a harness assertion that wrongly expected a protected existing destination not to exist; it now verifies unchanged bytes. The first independent wrap verifier treated trailing target spaces as unrelated neighbours; it now classifies them with the target and retains the original numerical thresholds. Earlier evidence has not been erased.

## Reproduction

From the project root, use PowerShell. `.venv` contains the development dependencies on this workstation.

```powershell
./phase4b/build.ps1
dotnet run --project phase4b/Checks/Checks.csproj -c Release -- "$PWD/phase4b/evidence/model"
./.venv/Scripts/python.exe phase4b/tools/test_document.py
./.venv/Scripts/python.exe phase4b/tools/process_recovery.py
```

To exercise controls, start `phase4b/run/PdfEditorPrototype.exe` with `--ui-test --discovery-ui-test --font-ui-test --position-ui-test --session-ui-test --clipboard-probe --audit <absolute-empty-folder>`. Allow the tests to finish; the window remains open. Flags use isolated test recovery. Close only this test instance before rebuilding. The combined verifier reads the designated `final-release-controls` export records; changing that evidence folder requires updating the verifier. Do not append another run into an existing folder with fixed output names; archive old runs first.

```powershell
./.venv/Scripts/python.exe phase4b/tools/verify_document.py
./.venv/Scripts/python.exe phase4b/tools/verify_independent.py
./.venv/Scripts/python.exe phase4b/tools/document_performance.py
./.venv/Scripts/python.exe phase4b/tools/write_handover.py
./.venv/Scripts/python.exe phase4b/tools/audit_release.py
```

The preservation audit compares earlier Phase 1–4A.1 hashes; report its result alongside these tests. A runnable build and six reports are delivered. Physical input, clipboard reliability, broad PDF semantics and clean-machine deployment remain explicitly unverified; see the issues report.
