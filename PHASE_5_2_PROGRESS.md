# Phase 5.2 progress — implementation and validation complete

Starting commit: 5f05af49d9720a628376b8fa7d0eb95293504232 on main.
Starting uncommitted file: phase5_1/run/paragraph-examples/Word-two-rows-edited-manual-test.pdf (private user test; preserve and exclude).

## Starting-state inspection (historical)
Read all six Phase 5.1 reports and reviewed discovery, marker validation, planner, transaction, identity and earlier C2 architecture. New isolated phase5_2 copies tracked Phase 5.1 sources/runtime/corpus/tools; prior evidence is not duplicated. No feature implementation yet. Starting tracked-byte preservation baseline: phase5_2/evidence/starting-preservation.json. Old releases must remain byte-identical except intentional root START_HERE update.

## Decisions and constraints
Structural paragraph ownership must precede geometry. No confidence score, fabricated spaces, synthetic source observations or private markers to qualify originals. Preserve 0.01pt/zero outside-region pixels above difference 8, native binary pin, atomic all-drafts save, guards and Phase 5.1 marker security. New corpus must use verified redistributable font resources; inherited corpus licensing is unresolved. Preserve clipboard error 5, undo granularity, ASCII/hard-break/adjacent-space restrictions. No work beyond 5.2.

## Investigations and tests
Phase 5.1 has shared native Span MCID scopes; supported transaction requires identical native semantic handles. Need inspect actual structure tree/parent tree and exact source whitespace before choosing design. Previous accepted tests: 151 worker, 37 roundtrip, 29 model, 16 separate-process paragraph controls, inherited clipboard limitation. These are baseline records, not newly executed results.

## Files changed
New phase5_2 source, tools, runtime and run assets (tracked source copy only). This progress document. Original releases untouched.

## Initial next action (historical)
Inspect genuine Word structure trees/content operations and installed/open-licensed font options. Author a fresh Word multiline fixture without any PDFEditor preprocessing; independently record its structure, text, font embedding and provenance. Determine if same supported semantic scope establishes complete paragraph ownership. Add bounded production native structure APIs only after evidence.

## Commands
Build: ./phase5_2/build.ps1
Python: .venv/Scripts/python.exe phase5_2/tools/<script>.py
Models: dotnet run --project phase5_2/Checks/Checks.csproj -c Release -- phase5_2/evidence/model phase4c1/evidence/word-spacing-analysis.json phase5_2/evidence/development-generations.json
Worker suites: test_engine.py, test_discovery.py, test_compatibility.py, test_position.py, test_insertion.py, test_document.py, test_wrap.py, test_roundtrip.py.
Independent: verify_wrap.py, verify_paragraph_structure.py, verify_positions.py, verify_independent.py. Freeze historical tests into separate evidence paths. Do not build while test workers hold the runtime DLL.

## Initial unfinished work (historical)
All Phase 5.2 implementation, new fixture verification, regression runs, handovers and final manifest remain incomplete. Do not treat copied README or copied run binary as a Phase 5.2 release. No new positive or export claim yet.

## Checkpoint 1 — original discovery implemented; NOT release-complete
Fresh authentic Word exports use the bundled renamed Bitstream-derived Prototype Sans (licence copied; fsType=4 recorded, no font substitution). Word personal properties are removed before original export. Four authored cases retained, not rewritten: cafe/letter have supported two-row members; longer original/calm cases fail exact bitmap reconstruction and remain restricted. Initial authoring/COM property failures preserved diagnostically; initial personal-metadata attempts remain ignored test-work, never public fixtures. Current final originals have no Author and blank DOCX creators.

Added OriginalParagraphs.cs and OriginalStructureProof.cs. Narrow Document -> P -> one page MCID + identical actual Span handles, original-font mappings/style, complete ordered contiguous members, explicit source trailing word spaces, stable horizontal rows, no interleaving/conflicting scope. Protected final standalone space is not absorbed. Cross-check raw page StructParents, parent-tree indexed associations and backlinks: public native tree loading alone does not prove the indexed association. A strict bounded structural reader accepts classic/hybrid Flate xref/object streams (Word's original format), refuses unsupported syntax; caps file/decompression/nodes/pages/revisions/tokens/depth. PDFium continues parsing/rendering content and fonts. No raw text parsing/geometry grant. Cache stores only bounded hash-bound MCID sets/diagnostics, not native pointers.

Failures corrected: pinned DLL lacks newly documented GetRawType (removed; native resolved role plus raw structural cross-check instead); absent structure attributes return -1; hybrid classic free placeholders require stream type-1/2 overrides; actual Word structure lives in ObjStm. No fidelity tolerance changed. A first original cafe edit exported successfully before indexed-structure hardening; must rerun final acceptance. Nonpainting separately retained whitespace no longer incorrectly caps vertical available space.

Next action: build final discovery, add adversarial parent-tree/order/semantic/spacing tests, generations and mixed/recovery/WPF coverage, run all current/frozen and independent suites. No final handover/manifest yet. New first-original-export.pdf is development evidence, not final certified result.

## Validation checkpoint 2 — still INCOMPLETE
Final candidate now passes 25/25 new authentic/negative/mixed worker cases. Genuine cafe and letter originals qualify; other authored original/calm remain bitmap-restricted. Three fresh-worker generations, cross-row insertion/deletion/replacement and four-region atomic export pass. New WPF stages 7–11 pass 12/12 checks in five exited processes: every source row, all caret offsets at four zooms, navigation/drag/selection/deletion, three save generations, four-region history/recovery and unsafe whole-draft/no-subset refusal. Physical input/OS DPI certification is not claimed.

Initial new tests caught an unsafe 14-repeat three-row draft (correctly blocked at next paragraph), a test replacement that accidentally introduced adjacent spaces (correctly refused exact extraction), and an incorrectly relocated page-0 marker to page 1 (correctly rejected page binding). Tests now preserve these failures and establish the page-1 marker through an actual verified save after combination. No marker forgery or source fixture simplification. The 5.1 protected-whitespace regression exposed an overbroad vertical-space exemption; corrected it to the same actual paragraph semantic scope only. Separate paragraph/foreign whitespace still protects its boundary. A full 5.1 roundtrip rerun is active.

Raw structural proof now handles genuine Word hybrid xref and Flate object streams with exact object-stream index checks, duplicate/range budgets and revision precedence. Unsupported xref-stream-only/predictor/escaped-name cases restrict original grouping. PDFium and raw indexed MCID proof must agree. Original source path is explicit in every Discover call, including candidate re-open. No native-pointer or synthetic source cache. Checkpoint 9bcb222 is incomplete baseline work, not release.

Current commands/jobs: release worker suites passed 151/151 before final scope correction; rerun targeted roundtrip, original tests, inherited WPF process controls and resource/historical suites ongoing. Full independent readers, final model additions, final rebuild/retests, handovers and preservation/manifest still required.
Exact next action: finish regression results; rerun all release suites after final production changes, add structural parser adversaries, then independent PDF/font/semantic/72/144-DPI verification. Do not build while current workers hold run DLLs.

## Final completion state

Completed source/build under phase5_2; all six PHASE_5_2_HANDOVER reports and entry/evidence/corpus guides supplied. Latest authoritative results: 151/151 current workers, 37/37 prior roundtrip, 31/31 new original checks, 35/35 models, 16/16 existing paragraph process controls, 12/12 new original/recovery process controls. Independent verification: 119 combined exports/124 group instances, 11 position and 21 legacy outputs; 174 source/output PDF paths retained. Frozen C2: 151 workers/52 combined independent exports; historical counts and the obsolete Phase 3 expectation are documented. Final engine/worker/native hashes remain identical. Final app phase caption corrected to 5.2, followed by 3/3 fresh original WPF checks and independent export verification.

Full inherited WPF run was 55/57 (clipboard plus transient diagnostic assertion). Basic retries on current and untouched 5.1 are both 10/11, failing clipboard only. Other 46 checks pass. No unrelated defect is claimed fixed. Five authentic new Word fixtures retain two positives, two bitmap-restricted examples and separate paragraphs; open-font/provenance checks completed. Rendered PDF/WPF contacts inspected. Same-file resource samples show zero handle growth; RSS deltas are samples, not leak proof.

Files changed: isolated phase5_2 source/runtime/run/tools/evidence, six new handovers, this progress log and intentional START_HERE update. Original phases/manual output remain untouched. No temporary workers, credentials, bin/obj/test-work or private manual PDF staged. New source fixture author properties are removed. Failed investigations/tests remain explicitly indexed. No unfinished production experiment is enabled; unsupported raw proof structures stay restricted.

Exact final engineering action: run release/preservation manifest audit, commit all Phase 5.2 deliverables and push main without force; verify remote SHA. The completion message records the final commit. After publication, next action is human Phase 5.2 testing using the user guide; do not start Phase 5.3 without acceptance. Historical incomplete checkpoint sections above describe development history, not current status.

Additional commands: original_process.py, original_performance.py, original_page_performance.py, archive_verified.py and audit_release.py under phase5_2/tools. Model command also accepts phase5_2/evidence/original-source-observations.json as fourth argument. Final reader logs: independent-final-release.log and structure-final-release.log. All full current worker suites were rerun after the whitespace-scope correction; the only subsequent app change is the phase caption, covered by the additional fresh WPF/reader smoke. Final engine/worker/native hashes remain unchanged.

Final-caption-only change and its source hash delta are recorded in phase-caption-change.json. The additional export is included in the authoritative 119-output/124-group independent reports and 174-path portable index. All source/build/evidence handovers are prepared; final preservation/staging/publication checks follow.

Final audit correction: the initial copy step had migrated lowercase phase5_1 path prefixes inside the baseline JSON. The original hash values were intact. Restored exact starting-tree keys and independently verified all 8,671 paths against 4,119 Git blobs at starting SHA; the erroneous diagnostic copy is retained. Audit now confirms every prior tracked byte unchanged except intentional START_HERE, and all 353 Phase 1 manifest entries unchanged. The inherited examples' provenance manifest retains its original Phase 5.1 evidence references. No historical files were repaired or altered to satisfy this audit.

Engineering work is complete; publication action is final commit/push and remote-SHA verification. No unfinished experiment is enabled. Next product action remains the user's Phase 5.2 review.
