# Phase 5.2 progress — INCOMPLETE

Starting commit: 5f05af49d9720a628376b8fa7d0eb95293504232 on main.
Starting uncommitted file: phase5_1/run/paragraph-examples/Word-two-rows-edited-manual-test.pdf (private user test; preserve and exclude).

## Current state
Read all six Phase 5.1 reports and reviewed discovery, marker validation, planner, transaction, identity and earlier C2 architecture. New isolated phase5_2 copies tracked Phase 5.1 sources/runtime/corpus/tools; prior evidence is not duplicated. No feature implementation yet. Starting tracked-byte preservation baseline: phase5_2/evidence/starting-preservation.json. Old releases must remain byte-identical except intentional root START_HERE update.

## Decisions and constraints
Structural paragraph ownership must precede geometry. No confidence score, fabricated spaces, synthetic source observations or private markers to qualify originals. Preserve 0.01pt/zero outside-region pixels above difference 8, native binary pin, atomic all-drafts save, guards and Phase 5.1 marker security. New corpus must use verified redistributable font resources; inherited corpus licensing is unresolved. Preserve clipboard error 5, undo granularity, ASCII/hard-break/adjacent-space restrictions. No work beyond 5.2.

## Investigations and tests
Phase 5.1 has shared native Span MCID scopes; supported transaction requires identical native semantic handles. Need inspect actual structure tree/parent tree and exact source whitespace before choosing design. Previous accepted tests: 151 worker, 37 roundtrip, 29 model, 16 separate-process paragraph controls, inherited clipboard limitation. These are baseline records, not newly executed results.

## Files changed
New phase5_2 source, tools, runtime and run assets (tracked source copy only). This progress document. Original releases untouched.

## Exact next action
Inspect genuine Word structure trees/content operations and installed/open-licensed font options. Author a fresh Word multiline fixture without any PDFEditor preprocessing; independently record its structure, text, font embedding and provenance. Determine if same supported semantic scope establishes complete paragraph ownership. Add bounded production native structure APIs only after evidence.

## Commands
Build: ./phase5_2/build.ps1
Python: .venv/Scripts/python.exe phase5_2/tools/<script>.py
Models: dotnet run --project phase5_2/Checks/Checks.csproj -c Release -- phase5_2/evidence/model phase4c1/evidence/word-spacing-analysis.json phase5_2/evidence/development-generations.json
Worker suites: test_engine.py, test_discovery.py, test_compatibility.py, test_position.py, test_insertion.py, test_document.py, test_wrap.py, test_roundtrip.py.
Independent: verify_wrap.py, verify_paragraph_structure.py, verify_positions.py, verify_independent.py. Freeze historical tests into separate evidence paths. Do not build while test workers hold the runtime DLL.

## Open / unfinished
All Phase 5.2 implementation, new fixture verification, regression runs, handovers and final manifest remain incomplete. Do not treat copied README or copied run binary as a Phase 5.2 release. No new positive or export claim yet.

## Checkpoint 1 — original discovery implemented; NOT release-complete
Fresh authentic Word exports use the bundled renamed Bitstream-derived Prototype Sans (licence copied; fsType=4 recorded, no font substitution). Word personal properties are removed before original export. Four authored cases retained, not rewritten: cafe/letter have supported two-row members; longer original/calm cases fail exact bitmap reconstruction and remain restricted. Initial authoring/COM property failures preserved diagnostically; initial personal-metadata attempts remain ignored test-work, never public fixtures. Current final originals have no Author and blank DOCX creators.

Added OriginalParagraphs.cs and OriginalStructureProof.cs. Narrow Document -> P -> one page MCID + identical actual Span handles, original-font mappings/style, complete ordered contiguous members, explicit source trailing word spaces, stable horizontal rows, no interleaving/conflicting scope. Protected final standalone space is not absorbed. Cross-check raw page StructParents, parent-tree indexed associations and backlinks: public native tree loading alone does not prove the indexed association. A strict bounded structural reader accepts classic/hybrid Flate xref/object streams (Word's original format), refuses unsupported syntax; caps file/decompression/nodes/pages/revisions/tokens/depth. PDFium continues parsing/rendering content and fonts. No raw text parsing/geometry grant. Cache stores only bounded hash-bound MCID sets/diagnostics, not native pointers.

Failures corrected: pinned DLL lacks newly documented GetRawType (removed; native resolved role plus raw structural cross-check instead); absent structure attributes return -1; hybrid classic free placeholders require stream type-1/2 overrides; actual Word structure lives in ObjStm. No fidelity tolerance changed. A first original cafe edit exported successfully before indexed-structure hardening; must rerun final acceptance. Nonpainting separately retained whitespace no longer incorrectly caps vertical available space.

Next action: build final discovery, add adversarial parent-tree/order/semantic/spacing tests, generations and mixed/recovery/WPF coverage, run all current/frozen and independent suites. No final handover/manifest yet. New first-original-export.pdf is development evidence, not final certified result.
