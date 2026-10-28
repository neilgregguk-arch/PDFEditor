# Phase 4C.1 executed test results

Executed 28 October 2026, Windows x64, .NET 8 WPF and unchanged pinned PDFium. The App/Worker publish completed successfully. Final source/build hashes are in `phase4c1/evidence/release-manifest.json`. Unless noted, evidence paths below are relative to `phase4c1/evidence/`. Previous evidence is preserved, not overwritten by these tests.

## New engine and model checks

`insertion-tests.json`: **30/30**. Cases include middle/start/within-word/between-word/end insertion, multiple characters and separate insertions, single/consecutive/start/end deletion, whole word removal, different-length range replacement, complete title deletion, safe Arial/Calibri insertion/deletion/replacement, preserved source-pair spacing, second-generation rediscovery, mixed Word insertion/deletion plus a natural paragraph on another page, and failed final commit with no stage/partial output. Negative controls cover new fff overlap, double-space extraction mismatch, horizontal page-boundary overflow, a protected graphic ahead, unsupported glyphs and positioned newlines.

`model/model-tests.json`: **17/17**. Eleven inherited session/history/recovery guards plus six positioning invariants: unchanged adjacent pair distances, deletion seam font advance, fixed legacy substitution positions, immutable original observations, bounded processing/overflow and empty-line ownership. Source/session/revision response guards, redo branches, history size caps, corrupt/oversized recovery and preserved incompatible drafts remain covered. The final model build completed without the earlier nullable test warning.

`document-tests.json`: **17/17** combined transaction checks. Two expanding natural paragraphs, multiple positioned regions, mixed strategy, pages, collision and unsupported-one blocks-all behaviour, source/destination/identity/ownership protection, deletion with another edit, second generation and worker restart remain passing. The old position-count-only negative now tests horizontal overflow, which is the intended new boundary.

## Actual WPF controls

Designated full run: `final-release-controls/`.

| Suite | Executed result |
|---|---:|
| control | 11/11 |
| discovery-control | 5/5 |
| font-control | 4/4 |
| position-control | 6/6 |
| session-control | 12/12 |
| insertion-control | 8/8 |

Total **46/46**. `selection-verified-controls/insertion-control-tests.json` repeats the eight new checks against the final test-capture build: **8/8**, with a rendering wait before selection screenshots. Application behaviour is unchanged by that capture correction. These exercise actual native WPF controls, logical selection/routed input, shared mapped click/drag helpers, document undo/redo, recovery and Save As internals. They are not hardware mouse/keyboard or native file-picker automation.

`final-release-controls/clipboard-probe.json`: **5/5** read/write/read checks, and the copy/cut/paste control case passed. Historical intermittent Win32 5 remains open; no fix is claimed.

## Requested scenarios A–M

| Requirement | Executed result and evidence |
|---|---|
| A — one middle insertion | Worker and actual WPF input; saved and independently extracted; pass. |
| B — multiple insertion | Start/end/multiple-character and separate edits; proposed origins and complete saved output checked; pass. |
| C — delete one | Word `Office` to `Ofice`, start/end and consecutive deletion; no artificial stretch; pass. |
| D — delete word | `Phase 3 Office letter` to `Phase 3 letter`; logical remaining space retained; pass. |
| E — range replacement | Different-length word replacement through selection and worker; pass. |
| F — horizontal overflow | Full draft retained, complete export blocked at page margin and protected graphic; pass. |
| G — unsupported glyph | Draft/recovery retained, other region remains editable, no valid-only partial save; pass. |
| H — mixed multi-region | Word insertion, another Word deletion, natural edit on page two; switch/global undo/redo and combined export; pass. |
| I — original spacing | Surviving adjacent pair residuals and translated glyph ink independently checked; unchanged neighbours fixed; pass. |
| J — reopen/re-edit | Worker and UI rediscovery plus a further length edit; pass. |
| K — empty line | Genuine target removal, other objects and separate whitespace preserved, undo restores text; pass. |
| L — zoom/display | Four zooms at measured 96 DPI; custom caret/selection and mapped drag tested. Other OS scales remain manual, not claimed. |
| M — failed export/recovery | Existing/original protection, failed final directory move, blocked drafts persisted, complete mixed session recovered across processes; pass. |

`process-recovery.json` references two separate fully exited app processes, distinct PIDs and a shared isolated recovery store. Process one makes a Word insertion, a Word deletion and a natural edit on page two. Process two restores all three, undoes/redoes and exports one combined PDF. Source hash remains unchanged. This is not merely a same-window serialization roundtrip.

## Caret and selection findings

The initial Calibri test failed its 0.75 pt native-caret approximation check at 1.271009 pt. The supported positioned path now paints the visible caret and selection from the proposed PDF origins; the hidden WPF caret is not asserted accurate. The failure remains in `development/native-caret-controls/`. The old title test and its historical approximation threshold remain unchanged.

| Sample | Hidden native caret max error, pt | Proposed visible caret max error, pt |
|---|---:|---:|
| Arial | 0.092000 | 2.84e-14 |
| Calibri | 1.271009 | 2.84e-14 |

The Word letter title's inserted line had 0.254002 pt native error across 75/100/150/200% zoom. The final visible geometry checks require at most 0.01 pt, and shared click/drag selected the expected `calm` range. Measurements cover every tested caret offset at all four zooms. Windows actual scale was 100%, 96 DPI; no OS scaling settings were changed. Physical input, IME and accessibility remain unverified.

Visual review includes inserted title/caret, blocked unsupported text plus another inactive draft, and the refreshed Calibri selection highlight after a render wait. Poppler contact-sheet review covers inserted/deleted Word, Arial/Calibri and both mixed-document pages. Draft appearance and verified exported PDF remain distinct.

## Independent complete-output verification

`document-independent-verification.json`: **57/57 recorded combined exports**. This includes 23 successful new worker exports, ten combined regression exports, fifteen full-run UI exports, five selection-capture rerun exports, one separate-process recovery export and three newly permitted old-position-test outputs. Every page is verified, including unchanged pages. No export is counted solely on a PDFium return code.

Tools: MuPDF glyph/text extraction; pypdf font programs, used encoding/ToUnicode/CIDToGID/width rules, raw nonembedded whitespace bytes and metadata; fontTools advances and independently recomputed alignment/proposals; pikepdf/qpdf syntax; Poppler full-page renders at 72 and 144 DPI. Exact intended replacement text is checked; geometry comparisons distinguish repositioned survivors from fixed unrelated neighbours.

Observed maximum untouched glyph shift: **0 pt**. Maximum inserted/repositioned target origin deviation from the independent proposal: **4.5776367e-05 pt**, under the unchanged 0.01 pt threshold. Outside authorised-area changed pixels are **zero** at both DPIs (channel difference threshold 8). Surviving ink bounds are independently compared after translation. Embedded font programs and used mapping/width rules remain preserved. Standalone protected spaces are compared separately and their original raw bytes survive.

`independent-verification.json`: **21/21** legacy font/discovery outputs, Poppler 72/144 DPI, pypdf and qpdf. `position-independent-verification.json`: **11/11** fixed-origin outputs including original reconstruction, unchanged target positions, two-generation substitutions and protected whitespace. Some sets overlap; do not add these counts as unique documents.

## Previous regressions

| Suite | Result | Evidence |
|---|---:|---|
| Phase 1 feasibility | 14/14 | `phase1-regression.log`, frozen saved files read |
| Active single-region engine | 18/18 | `engine-tests.json` |
| Active discovery | 22/22 | `discovery-tests.json` |
| Active font compatibility | 23/23 | `compatibility-tests.json` |
| Active positioned | 20/20 | `position-tests.json`, three intentional expectation changes |
| Frozen Phase 2 | 18/18 | `phase2-regression.json` |
| Frozen Phase 2 expectations against Phase 3 | 17/18 | `phase3-regression.json`; known obsolete manifestless-view-only assertion |
| Frozen Phase 4A engine | 18/18 | `phase4a-regression.json` |
| Frozen Phase 4A.1 engine | 18/18 | `phase4a1-regression.json` |
| Frozen Phase 3 discovery | 22/22 | `frozen-phase3-discovery/tests.json` |
| Frozen Phase 4A font compatibility | 23/23 | `frozen-phase4a/tests.json` |
| Frozen Phase 4B document | 17/17 | `frozen-phase4b-test_document/document-tests.json` |
| Frozen Phase 4B positioned | 20/20 | `frozen-phase4b-test_position/position-tests.json` |

Active engine/discovery/font/position checks total 83/83. Frozen code uses preserved workers and writes all fresh output under Phase 4C.1. The Phase 3 obsolete expectation is retained as a failure and not counted as a pass. Earlier Phase 4B clipboard/UI failures remain in that preserved release.

## Performance and resource measurements

Final eight-case UI rerun: 30 text operations, median synchronous input **3.0454 ms**, max **4.4443 ms**; median standalone proposed-position calculation **0.0168 ms**. There were **0 immediate worker requests**. These are programmatic control-handler measurements, not keyboard-to-screen latency.

`document-performance.json`, five complete preview requests per case:

| Case | Median worker roundtrip, ms | Regions |
|---|---:|---:|
| two-Word-insert-delete | 196.34 | 2 |
| two-natural | 109.25 | 2 |
| three-natural | 103.13 | 3 |
| four-two-pages | 164.16 | 4 |
| two-Word | 234.92 | 2 |
| mixed | 263.56 | 2 |

The two-Word insertion/deletion case's last sampled worker stages were planning **122.817 ms**, candidate mutation/generation/save **7.602 ms**, reopen verification **53.200 ms**. These stage observations are not separately averaged medians. End-to-end timings include IPC and remaining overhead; performance varies with concurrent local work.

Twenty-four additional alternating insertion/deletion previews after warmup: handle growth **-2**, retained twelve PDFs/twelve PNGs, worker exited. Before/after memory observations are recorded in full. This is a bounded small-corpus observation, not proof of leak freedom or large-document capacity. Alignment is capped at 512 for the recalculated path; native timeout remains 30 seconds with no in-flight native cancellation.

## Retained failures and corrections

- `development-initial-insertion-tests.json`: first 27-case run had three failures: unsupported new fff join, double-space extraction collapse and another fff-based multi-insertion. Final tests explicitly assert these safety refusals and demonstrate safe within-word/multiple insertions with other mapped characters. No glyph/pixel tolerance was relaxed.
- `development/old-position-tests.json`: three old count/wider refusal assertions fail because the new outputs safely succeed. Final tests assert their new supported behaviour; original frozen Phase 4B still passes all old expectations.
- `development/old-discovery-tests.json`: a verification-envelope mismatch after routing all positioned requests through combined output. Keeping the original fixed-origin single-request path restored the existing contract; final discovery is 22/22.
- `insertion-controls/` and `development/initial-full-controls/`: early new control tests assumed opening an existing source reset its draft. Session recovery correctly retained previous text. Tests now establish their intended initial text explicitly.
- `development/native-caret-controls/`: Calibri native error failure led to the corrected visual caret/selection. Hidden native error remains reported, not hidden by a wider tolerance.
- Parallel development harnesses initially collided on a Windows timestamp work-folder name; UUID work directories now isolate them. Initial Word-analysis JSON serialization variable reuse was corrected.
- Independent line classification initially interleaved a protected original F2 space into a shifted title; standalone-space spans now remain in preserved-neighbour checks rather than target text. Early selection screenshots were taken before rendering; the final capture rerun waits for layout/rendering.

Historical clipboard failures are still visible and not considered fixed. No physical input certification is claimed. Check `prior-phase-preservation.json` and `phase1-preservation.json` for final preservation results; `release-manifest.json` binds final source/runtime/fixtures/tools/handovers.

## Reproduction

From the project root in PowerShell, with this workstation's `.venv` development dependencies:

```powershell
./phase4c1/build.ps1
./.venv/Scripts/python.exe phase4c1/tools/analyse_spacing.py
dotnet run --project phase4c1/Checks/Checks.csproj -c Release -- "$PWD/phase4c1/evidence/model" "$PWD/phase4c1/evidence/word-spacing-analysis.json"
./.venv/Scripts/python.exe phase4c1/tools/test_insertion.py
./.venv/Scripts/python.exe phase4c1/tools/test_document.py
./.venv/Scripts/python.exe phase4c1/tools/test_position.py
./.venv/Scripts/python.exe phase4c1/tools/process_recovery.py
```

Run the executable with `--ui-test --discovery-ui-test --font-ui-test --position-ui-test --session-ui-test --insertion-ui-test --clipboard-probe --audit <new-absolute-folder>`. The window stays open. Use fresh evidence directories because fixed output names are protected; point the independent verifier at the desired final folders. The isolated test recovery store does not modify normal user recovery.

```powershell
./.venv/Scripts/python.exe phase4c1/tools/verify_document.py
./.venv/Scripts/python.exe phase4c1/tools/verify_independent.py
./.venv/Scripts/python.exe phase4c1/tools/verify_positions.py
./.venv/Scripts/python.exe phase4c1/tools/document_performance.py
./.venv/Scripts/python.exe phase4c1/tools/write_handover.py
./.venv/Scripts/python.exe phase4c1/tools/audit_release.py
```

`tools/create_insertion_corpus.py` recreates only the two new development fixtures. Regenerating PDFs changes source identities and requires rerunning their tests/evidence. `tools/run_regressions.py`, `frozen_phase4a.py` and `frozen_phase4b.py` preserve original workers with redirected output. The six handovers and runnable build are delivered. Phase 4C.2 has not started.
