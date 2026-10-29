"""Write the six Phase 5.1 review documents from final evidence."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];E=R/'evidence';H=R.parent/'PHASE_5_1_HANDOVER';H.mkdir(exist_ok=True)
def load(n):return json.loads((E/n).read_text(encoding='utf-8'))
def write(n,s):(H/('PHASE_5_1_'+n+'.md')).write_text(s.strip()+'\n',encoding='utf-8',newline='\n')
rt=load('roundtrip-tests.json');ui=load('paragraph-controls.json');model=load('model/model-tests.json');ind=load('wrap-independent-verification.json');structure=load('paragraph-structure-verification.json');perf=load('paragraph-performance.json');frozen=load('frozen-c2-readers/wrap-independent-verification.json')
assert rt['failures']==ui['failures']==model['failures']==0 and ui['success'] and ind['success'] and structure['success']
groups=sum(len(r['groups']) for r in structure['cases']);assert groups>0
recovery=max(p.stat().st_size for p in Path(ui['folder']).glob('store5/*.session.json'))
activation=[d for run in ui['runs'] for row in run['result']['rows'] if row['status']=='pass' for d in row.get('detail',{}).get('activationMs',[])]
write('IMPLEMENTATION_REPORT','''# Phase 5.1 implementation report

Delivered 29 October 2026. Starting commit: `d864fbf265db32127a34e5862b30b4c72717caa9`, with no uncommitted work or partial Phase 5 implementation. The starting-state record and 5,453-file preservation baseline are under `phase5_2_1/evidence/`. All implementation, compilation and automated testing took place in Codex. The final commit SHA is reported in the completion message and is available with `git log -1`.

## Outcome and scope

Supported paragraphs newly exported by Phase 5.1 carry a bounded embedded declaration. A fresh process validates their actual text objects, reconstructs the exact logical text and opens every row as one in-place region. The genuine Word third paragraph passes consecutive two-row, three-row and one-row save/reopen generations. Arial and Calibri also pass repeated generations. Removed rows are actually removed; no white cover or invisible text replacement is used.

The implementation is isolated under `phase5_2_1/`. Earlier source, delivered binaries, evidence and handovers remain unchanged. START_HERE is the sole intentional pre-existing entry-guide update and is audited separately. Generic discovery of original Word paragraphs and retroactive grouping of unmarked C2 exports were not added. Development stops after Phase 5.1.

## Source map

- `Core/ParagraphMarks.cs`: PDFium public marked-content bindings, bounded schema, persistent row declarations, actual-member validation, document-wide duplicate-ID index, existing semantic-mark handling and pointer-free ownership observations.
- `Core/Discovery.cs`: validates declarations before existing proximity/natural grouping. Rejected marked members stay Limited/View Only. The document index is cached by exact source hash, while the existing eight-page discovery cache remains.
- `Core/Models.cs`: optional logical text and paragraph ownership distinguish soft rows from natural explicit newlines. Discovery timing is non-authoritative and excluded from identity.
- `Core/PositionLayout.cs`: immutable actual source rows, exact unchanged-row presentation, bounded flattening for alignment during edits, and a surviving-sequence check that cannot borrow an overlap exception across a source soft boundary.
- `Core/DocumentSession.cs`: source identity includes the validated declaration and complete row observations. Stable paragraph ID never substitutes for the new source fingerprint.
- `Core/DocumentTransaction.cs`: inserts genuine original-font rows before their still-live source anchor, preserving the content stream, paint order and shared accessibility scope. Only owned originals are removed. Untouched objects are not detached. The candidate must rediscover its complete declared groups before Save As commits.
- `Core/PdfEngine.cs`: grouped logical glyph offsets omit synthetic newlines; all grouped single requests use the combined transaction. Preserved-object snapshots also compare content-mark signatures.
- `App/PositionSelection.cs`: the page follows the proposed caret and suppresses hidden unwrapped-caret scroll requests.
- `App/ParagraphControlTests.cs`, `tools/paragraph_process.py`, `Checks/Program.cs`: fresh-process interaction, recovery and model coverage. Independent Python readers are development-only.

## Editing and transaction behaviour

The existing proposed-position glyph/caret/selection layer is reused. WPF owns text, input and selection; Up/Down, Home/End, shift selection and mapped drag work across reopened rows. The unchanged source uses observed row geometry. Edits flatten only an ephemeral alignment copy, retaining source-row boundaries for spacing exceptions. New rows reset to the anchor and use verified original-font advances. No source observation is rewritten by layout planning.

Every request still resolves source identities against the immutable opened file, includes all modified regions, rejects collisions and stale/source-changed requests, creates one candidate, reopens it and atomically saves to a new destination. New paragraph IDs are allocated on first marked export and retained when editing a validated marked source. Save As retains the original working session; reopening the output starts a new fingerprint-bound session.

Target/unaffected geometry stays at 0.01 pt and outside-region changed pixels must remain zero above the existing channel-difference threshold of 8. Natural tolerances are unchanged. Font programs, used mapping/width rules, glyph identities/outlines, whitespace objects, page properties and existing accessibility structures remain checked. No fidelity threshold was relaxed.

## Distribution

Run `phase5_2_1/run/PdfEditorPrototype.exe` or `phase5_2_1/Launch.ps1`. Windows x64 and the .NET 8 Windows Desktop runtime are required; this is a framework-dependent build. Build with `phase5_2_1/build.ps1`. Python and Poppler are verification tools, not application dependencies. No paid SDK, network/cloud feature, installer, font substitution, subset rebuilding, undo grouping or new production dependency was introduced.

The pinned PDFium 156.0.8076.0 binary remains SHA256 `bede3932ce96a2e1ed9a7e6cae71aec8914efd2907d37ab44b1b81f9c8a6d04e`. Existing PDFium/native/font notices remain in runtime/run. Inherited embedded fonts and development-library licensing warrant a dedicated distribution audit; this phase does not make a new licence or redistribution-rights determination.
''')
write('PARAGRAPH_OWNERSHIP_ANALYSIS','''# Phase 5.1 paragraph ownership analysis

## Evidence categories

Observed document facts are complete text objects, transforms, style/paint, embedded programs, verified mappings, actual Unicode glyphs, origins, bounds, baselines, page properties and neighbouring objects. Embedded declarations supply a proposed stable identity, ordered members, exact logical string, soft boundaries and an envelope cap. Inference remains limited to conservative available-space/leading policy. Neither visual proximity nor the declaration alone proves paragraph ownership or authentic editor origin.

| Candidate mechanism | Assessment |
|---|---|
| Proximity/indent/font/leading alone | Insufficient to establish ownership; no new heuristic promotion was added. |
| File sidecar | Loses portability and binds to external state; not used to satisfy reopening. |
| Document XMP/custom catalog metadata | Portable but separated from members; would require a separate PDF object-reference writer/resolver. Not selected. |
| Accessibility StructTree/MCID identity | Existing semantics must be preserved, not invented or repurposed as application storage. Not selected for paragraph identity. |
| Custom marked content attached to each actual row | Selected: public APIs in the pinned PDFium expose it, it travels with genuine content, can be bounded and independently inspected, and need not claim accessibility semantics. |

The PDF model for marked content is described in [Adobe PDF Reference 1.7, section 10.5](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/pdfreference1.7old.pdf). Public mark and insertion APIs are documented in [PDFium fpdf_edit.h](https://pdfium.googlesource.com/pdfium/+/main/public/fpdf_edit.h). These APIs are experimental; this implementation is tested against the pinned shipped binary, not arbitrary future builds.

## Final schema and lifecycle

Tag `/PDFEditorV2_Paragraph` has exactly `/Data` and integer `/Row`. Data is a UTF-8 JSON blob with schema Version 1. A new lowercase 32-hex GUID is allocated for the first marked export. Later generations retain it, even when row count changes. Identity is unique across pages within a file. Members carry identical common payloads and distinct contiguous row indices. Physical object indices are rediscovered from the actual marked objects, never dereferenced from an arbitrary metadata path/reference.

The payload contains page index/dimensions, exact ASCII-model logical text, original font-program and verified-character-mapping hashes, size/colour/anchor/ascent/line height, envelope cap, existing semantic-mark signature, and ordered rows with text, baseline, origins and observed character boxes. Row starts are obtained by exact cumulative lengths. Soft rows concatenate without newlines; no whitespace is trimmed. Metadata geometry is rounded to 0.001 pt to keep the blob compact. Actual observed origins remain full precision, reconstruction bitmaps use those exact observed offsets, and the existing 0.01 pt checks are unchanged. Character boxes include native space extents, which are not visible ink.

The envelope is a cap, not permission to occupy everything inside it. Current page margins, protected objects, source-safe bottom, eight-row cap and per-proposal collisions remain authoritative. Reopening rebuilds those observations from the new file. An external neighbour can reduce available space; the declaration cannot remove that neighbour or expand past the independently checked page margins.

## Acceptance and rejection

Acceptance requires the complete member set, one mark per member, identical payloads, valid row sequence, exact actual row text, original font/mapping agreement, supported transforms/paint/clipping, expected baselines, strictly ordered origins, measured glyph boxes and exact row reconstruction. The whole grouped source must fit its envelope and the source's current protected-content rules. Unsupported/ambiguous members cannot be promoted by metadata.

IDs, object/page counts, text lengths, types, finite numbers, schema keys, duplicate JSON keys and cross-page conflicts are checked. Limits: 512 logical characters, eight members, 28,000 bytes per payload, 16 marks/parameters per object/mark, 128 groups/1,024 claims per page, 4,096 page objects, 8 MiB metadata budget, and a bounded document index of 256 pages/65,536 objects. JSON depth is 16. Index caching is capped at four source hashes. Budget failure restricts grouping; no unbounded scan, external file lookup, URI execution or executable action is driven by metadata.

Missing, duplicated, changed or conflicting members reject the group. Rejected marked objects do not fall back into new proximity grouping. A member whose mark is entirely removed can still qualify independently under unchanged legacy single-object rules; it is never silently reabsorbed into the old group. If all marks are stripped, only the previous unmarked classifications remain. A fully consistent declaration can be authored by another tool: this is content consistency and conservative ownership validation, not cryptographic authentication of the producing editor or proof of human paragraph intent.

## Existing accessibility and reading order

The genuine Word fixtures already contain `/Span` MCIDs and language. Replacement rows share the original native semantic mark and are inserted before the source object while that object still supplies its content-stream anchor. This avoids appending a second MCID sequence at page end. Group members must share the same actual semantic scope, not merely matching MCID numbers. Only supported existing Span/MCID/Lang scopes are transferred. Different, unsupported or changed semantics are refused rather than stripped or recreated.

The private mark adds no MCID, ActualText, Alt, Artifact designation, RoleMap entry or structure-tree paragraph role. Existing semantic sequences, StructTreeRoot graph, page StructParents, MarkInfo and document Lang are independently compared. Source structure preservation is not PDF/UA certification or repair of pre-existing accessibility defects.

## External editing and compatibility

A pikepdf save that retains consistent declarations passes another editing generation. Text/position changes, missing/duplicated rows, conflicting IDs, modified semantics and malformed payloads are refused. Other applications may discard private marks; the file remains ordinary selectable PDF text, but whole-paragraph re-editing is then unavailable. Legacy C2 wrapped outputs lack the declaration and are not retroactively promoted. General original Word multi-line discovery, mixed-font reconstruction and cross-page paragraph continuation remain out of scope.
''')
write('ROUNDTRIP_TEST_RESULTS',f'''# Phase 5.1 round-trip test results

Executed in Codex on Windows x64, 29 October 2026. Source start was `d864fbf265db32127a34e5862b30b4c72717caa9`, clean. Exact commands are in the user guide. Evidence paths below are relative to `phase5_2_1/evidence/`.

| Suite | Actual result | Evidence |
|---|---:|---|
| Active engine/discovery/compatibility/position/insertion/document/wrap | 151/151 | seven *-tests.json files |
| Dedicated paragraph generations/adversaries | {rt['tests']}/{rt['tests']} | roundtrip-tests.json |
| Separate WPF-process paragraph controls | {ui['tests']}/{ui['tests']} | paragraph-controls.json |
| Session/layout models | {model['tests']}/{model['tests']} | model/model-tests.json |
| Reopened repeated-space restriction | Pass; draft exact, export refused | paragraph-space-restriction.json |
| Inherited WPF controls, final build | 56/57 | controls-shipping/ |
| Same WPF suites, untouched C2 build | 56/57, same clipboard failure | frozen-c2-controls/ |
| Clipboard/basic-suite retry | 10/11, same failure | controls-basic-retry/ |
| Frozen C2 worker suites | 151/151 | frozen-phase4c2/ |
| Frozen C2 model | 22/22 | frozen-c2-model/model-tests.json |
| Current combined exports, independent readers | {len(ind['cases'])}/{len(ind['cases'])} | wrap-independent-verification.json |
| Current embedded/semantic structures | {len(structure['cases'])}/{len(structure['cases'])}; {groups} group instances | paragraph-structure-verification.json |
| Fixed-position / legacy independent exports | 11/11 and 21/21 | position-independent-verification.json; independent-verification.json |
| Frozen C2 combined independent exports | {len(frozen['cases'])}/{len(frozen['cases'])} | frozen-c2-readers/wrap-independent-verification.json |

The failing inherited check is native-copy-cut-paste-undo-redo: Win32 error 5, valid owner window, no identified clipboard holder. It also fails in untouched C2 and on retry; clipboard probes likewise fail in this desktop session. It is retained as the historical intermittent defect/environment limitation, not marked pass or claimed fixed. The new paragraph controls do not use the system clipboard.

## What the generations prove

The actual Word third paragraph passes two rows → three rows → one row through fresh native workers and again through separately exited WPF applications. The same embedded ID is retained while each new file establishes a new source hash and source object observations. Word Arial and Calibri pass three editing generations. Exact row/member counts, original fonts and complete logical text are asserted. Deleting the whole paragraph removes its text members with no invisible tombstone.

Six WPF processes use fresh isolated stores for generations; separate stages intentionally share a store to test recovery. Every row activates the same group. Checks cover all logical caret offsets at four app zooms, viewport containment, visible caret alignment at 0.01 pt, Up/Down/Home/End/shift, mapped multi-row drag, Backspace/Delete at soft boundaries, endpoint routed input, undo/redo after rewrapping, switching regions, three drafts across two pages, exited-process recovery and combined export. These are actual WPF commands/routed events/shared hit handlers, not physical keyboard/mouse or file-picker automation. Capture DPI is 96; app zoom does not certify OS display scales.

Adversarial cases include unmarked nearby matching lines, missing/duplicated members, external text/position changes, conflicting IDs including cross-page reuse, unknown schema/keys, broken/duplicate-key JSON, oversized/null/excessive member payloads, fractional row indices, wrong page/font/map/envelope claims, altered accessibility semantics and separately owned whitespace in a row gap. Later unsupported glyphs, hard breaks, vertical growth, source changes and failed Save As are refused. Two marked groups export safely alone and collide when combined; both drafts are retained.

## Independent checks and reader corrections

MuPDF text-drawing traces, fontTools cmap/glyph IDs/metrics, pypdf object structures, qpdf syntax through pikepdf and Poppler at 72/144 DPI check exact text, all modified regions, original programs/used mapping rules, origins/baselines, page properties, untouched glyphs/whitespace and zero outside-region changed pixels above threshold 8. Source/destination hashes are checked. Trace spans retain a separately owned Word F2 space that rawdict could merge into the edited span after reading order was preserved. No actual character is dropped or normalised; those spaces remain in untouched-object and raw-byte checks.

Independent structure checks inspect balanced custom marks, complete row indices, identical payloads, exact trace text and origins, absence of application-added accessibility semantics, existing semantic sequence equality and unchanged structure graphs/page StructParents. Coverage assertions require expected paragraph IDs to be encountered, so a vacuous zero-group scan cannot pass. A pypdf ContentStream truthiness guard initially skipped operations; it was corrected to an explicit `is not None` check, also strengthening the inherited font-rule reader. Frozen outputs are checked with their original engine/identity scheme. Historical prototype snapshots are matched back to actual source facts at the same tolerances; they are not trusted by an old opaque identity alone.

## Performance

The final 32-group fixture is a development-only untagged page derived from the existing fictional Word title TJ/font resources, not an untouched Word export. Size is 595.32 × 3400 pt. Two complete marked-save generations succeed. Cold rediscovery including render: {perf['markedColdRediscoveryMs']:.2f} ms; paragraph validation: {perf['groupValidationMs']:.2f} ms, excluding earlier font analysis. Warm median: {perf['warmRediscoveryMedianMs']:.2f} ms. Saves: {perf['firstSaveMs']:.2f} and {perf['secondSaveMs']:.2f} ms; generation/planning/reopen stages are recorded. Twenty repeated inspections show handle growth {perf['handleGrowth']}, RSS growth {perf['rssGrowth']:,} bytes and worker exit. The same-file C2/current engine comparison is in paragraph-performance.json.

Fresh-process group activation (including Open and dispatcher work) ranges {min(activation):.2f}–{max(activation):.2f} ms in this run. Recovery store example: {recovery:,} bytes. Local input/layout timing and 30 wrap/unwrap operations are retained in controls-shipping/wrap-control-tests.json and wrap-performance.json. Measurements were under local/concurrent test load and do not certify large-document latency. Existing 30-second worker timeout, stale-response protections and cache/candidate caps remain.

## Retained failures and qualifications

Development caught content-stream append/reorder mistakes, a 32,767-byte string truncation, inaccurate guessed space extents, bitmap differences from reconstructing quantized claims instead of exact observations, and the one-character final-row edge case. The final writer inserts at the live source anchor, stores compact observed boxes under a 28,000-byte cap and reconstructs from exact observations. No geometry or bitmap tolerance was widened.

Two initial adversarial fixture errors were corrected: scalar pikepdf operands needed instruction replacement, and a whitespace obstacle was initially outside the horizontal edit area. One WPF test read an uninitialised cached layout rather than the source plan; corrected coverage uses the shared plan. Windows reused a PID, so fresh-process proof now pairs PID with OS creation time and isolated stores. Frozen-run output redirection and the reader's mixed-version fingerprint selection were corrected without touching old releases. Visual QA also exposed hidden native-caret panning at high zoom; the page now follows the proposed caret, with viewport containment tested at four zooms. Display strings were restored to correct UTF-8 after a development encoding mistake. Raw attempts are retained under development and timestamped control folders.

Earlier frozen suites also pass their previous counts: Phase 1 14/14, Phase 2 18/18, Phase 4A 18/18, Phase 4A.1 18/18, Phase 3 discovery 22/22, Phase 4A compatibility 23/23, Phase 4B document 17/17/position 20/20 and C1 insertion 30/30/document 17/17/position 20/20. The original Phase 2 suite against Phase 3 remains 17/18 because of the obsolete manifestless-view-only expectation. The C2 line-only rediscovery assertion is intentionally replaced by whole-declaration rediscovery; its earlier failure is retained and the original assertion still passes against frozen C2. Visual QA and byte-preservation audits are indexed separately.
''')
write('COMPATIBILITY_MATRIX','''# Phase 5.1 compatibility matrix

| Actual fixture / behaviour | Phase 4C.2 | Phase 5.1 |
|---|---|---|
| Genuine Word letter, fitting single row | Verified original-font editing | Retained; eligible bounded exports can carry one-row identity |
| Genuine Word third paragraph, new two-row export | Wrapped output, independent rows on reopen | Complete logical group in a fresh process |
| Consecutive two → three → one generations | No whole-paragraph relationship | Verified stable ID, new source bindings and exact row removal |
| Word Arial / Calibri | Verified wrapping, limited paragraph rediscovery | Repeated whole-group generations; inherited font/caret policies retained |
| Legacy unmarked C2 wrapped PDF | Independent eligible/Limited lines | Same conservative classifications; no retroactive grouping |
| General original Word multi-line layout | Ambiguous cases restricted | No new generic heuristic promotion |
| Natural paragraphs | Bounded existing discovery/editing | Retained; not converted into arbitrary editor-marked Word groups |
| Reopened group + other Word + natural on another page | Could not restore whole group | History, recovery and combined export verified |
| Two groups whose expansions collide | Combined collision protection | Same refusal, both full drafts retained |
| Long word ending in a one-character row | Verified C2 export | Verified export and validated member set |
| Whole paragraph deletion | Text removal | All members removed, no invisible ownership tombstone |
| External save retaining consistent marks | No group mechanism | pikepdf save/re-edit verified; not a guarantee for every editor |
| Changed/missing/duplicate/conflicting members | Independent-line fallback | Marked group restricted; no new proximity recovery |
| Stripped private marks | Not applicable | Legacy classifications; whole group no longer promised |
| Repeated spaces / positioned hard breaks | Exact-extraction/newline restrictions | Exact draft/recovery retained; demonstrated unsafe exports still refused |
| Unsupported glyphs/fonts, mixed styles, transforms | Restricted | Existing restrictions retained; metadata cannot override them |
| Unsupported existing accessibility scope | No round-trip mechanism | Refused rather than stripped or fabricated |
| Clipboard Win32 error 5 | Historical intermittent issue | Still fails in this session on both versions |

Genuine inputs remain the existing `run/corpus/11-word-letter.pdf` and `run/font-corpus/Word-Arial.pdf` / `Word-Calibri.pdf`. Read-only copies of certified outputs are supplied under `run/paragraph-examples/`; their manifest identifies the originating evidence and SHA256. The 32-group performance page and adversarial files are explicitly derived development fixtures, not simplified substitutes for the genuine Word acceptance cases.

Support applies to the demonstrated bounded ASCII/original-font model. No font substitution, subset rebuilding, OCR, mixed-font reconstruction or cross-page paragraph flow was introduced. Structure preservation does not constitute PDF/UA or arbitrary-editor compatibility certification.
''')
write('OPEN_ISSUES','''# Phase 5.1 open issues

## Retained restrictions

- Unmarked C2 exports and arbitrary original Word multi-line paragraphs are not automatically grouped. Nearby matching text is insufficient ownership evidence. Older prototype marker formats from development are diagnostic and are not release inputs; the final published schema is Version 1.
- Positioned hard newlines and demonstrated adjacent-space extraction failures still block export while preserving the exact draft and recovery. Unsupported Unicode/glyph mapping is retained and refused; this does not expand the inherited ASCII editing model.
- Empty paragraph deletion intentionally leaves no invisible tombstone. A completely deleted group has no remaining text region to click/re-edit.
- Mixed fonts/styles, unsupported transforms/clipping/paint, cross-page paragraphs and general document reflow remain out of scope. No unrelated object is moved.
- Marker validation is bounded: 512 characters/eight rows/28,000 bytes, page/group/object budgets and a 256-page/65,536-object document mark index. Larger marked operations can be restricted. The envelope is a cap plus freshly checked exclusions, not blanket ownership of empty page space.

## Trust and external tools

The declaration is not a signature or proof of producing-editor authenticity. A third party can author a fully consistent declaration; the app validates actual content, supported geometry and safe ownership. External tools may remove private marks or change font/tag structure, which can prevent group-level editing. An external save preserving validated data is demonstrated only with pikepdf. Raw PDF parser normalisation and malformed native input need broader security/fuzzing review; bounded application metadata validation is not a native sandbox.

Supported existing accessibility scopes are narrow: shared Span marks with MCID/Lang. Other or independently changed semantics are refused. Existing semantic sequence, structure graph and page linkage preservation is checked, but pre-existing accessibility defects are not repaired and PDF/UA is not certified. Screen readers, high contrast, IME, touch and unusual reading-order structures require dedicated evaluation.

## Interaction and operations

The inherited clipboard Win32 error 5 is still reproducible in both the final build and untouched C2 in this session, including a retry. It is explicitly not fixed or counted as passing. Physical Windows testing is still required for clipboard reliability, typing comfort, actual mouse selection, native dialogs and OS display scales. Automated controls use WPF routed input/commands/shared mapping at 96 DPI and four app zooms.

Small-fixture timings are descriptive. Larger/complex files, malicious fonts, memory pressure and prolonged sessions need additional testing. Existing 30-second worker timeout, source/revision guards, bounded caches/candidates, 2,000-entry/2-million-character history and 16 MB recovery protection remain; no new in-flight native cancellation is claimed. Undo grouping is unchanged.

## Repository and compliance

No new production dependencies, paid SDKs or cloud requirements were added. Python readers/Poppler are development-only. Existing native/font notices are preserved. Embedded Arial/Calibri resources and inherited development-library licences require a dedicated distribution/compliance audit; this phase makes no new redistribution-rights determination and does not restructure the repository licence.

Evidence contains workstation-specific paths and some references to excluded transient fonts/candidates. Certified exported PDFs, source fixtures, independent reports and reproducible tools are retained. Virtual environments, bin/obj/test-work/caches and temporary credentials/private user files are excluded. Frozen historical failures, development attempts and initial reader/test-harness mistakes remain visible. Read the evidence index to identify the final approved feature runs.

Phase 5.1 is the review stop point. Phase 5.2 has not started.
''')
write('USER_TEST_GUIDE','''# Phase 5.1 user test guide

## Run and open

Use Windows x64 with .NET 8 Windows Desktop runtime. Keep `phase5_2_1/run/` intact. From the repository root:

```powershell
./phase5_2_1/Launch.ps1 -Pdf './phase5_2_1/run/corpus/11-word-letter.pdf'
```

Alternatively launch `phase5_2_1/run/PdfEditorPrototype.exe`. No Python/network is needed to use the app. Certified ready-to-open examples are `run/paragraph-examples/Word-two-rows.pdf`, `Word-three-rows.pdf`, `Word-one-row.pdf`, `Arial-two-rows.pdf`, `Calibri-two-rows.pdf` and `Mixed-two-pages.pdf`. Their manifest records the originating evidence/hashes.

## Two → three → one generations

Use the **third paragraph** beginning “A separate paragraph”; the title has less vertical room. Select that paragraph and enter this one logical line (do not press Enter):

```text
Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter
```

It should wrap into two rows. Wait for verification and Save As to a new filename. Close the document/app, reopen the saved file and click either row. Both should activate the same complete logical paragraph. The first saved file establishes its embedded identity; later generations preserve it.

Replace the whole paragraph with fifteen repetitions of “Phase 3 letter”, separated by single spaces, to make three rows. Save As again, close/reopen and click the first, middle and final row. Then replace the whole paragraph with “A separate letter.” and save/reopen a third time. Only one row should remain; no old row should be visible or selectable as residual text.

The supplied Word examples allow reviewing these states without first creating them. A legacy C2 wrapped export remains separate eligible/Limited lines: this phase does not retroactively infer its paragraph relationship.

## Caret, history and recovery

Try Left/Right across a soft boundary, Up/Down, Home/End and shift variants. Drag from the first row into the last. Backspace/Delete near the boundary and type at the paragraph start/end; Undo/Redo should restore the exact logical span and wrapping. Test all four app zooms and your actual Windows display scale. Wrapping itself should not add a history event; ordinary edit grouping remains unchanged.

Open Mixed-two-pages.pdf. Edit the wrapped Word paragraph, another Word region and the natural paragraph on page two. Switch away and return to the last row of the group. Undo/Redo should follow document chronology. Close with unsaved changes, reopen the same unchanged source and check all three drafts, then Save As once. Normal recovery is `%LocalAppData%\\PdfEditorPrototype\\phase5_2_1\\sessions`; old C2 stores are not migrated. Saved outputs are new source files, and old-source recovery must not attach merely because a paragraph ID is the same.

## Refusals and external viewers

Try an unsupported symbol, a positioned hard newline, repeated spaces or excessive growth into protected content. The whole draft must remain available, but unsafe combined export must fail without saving a valid subset. Use a new destination; originals/existing files cannot be overwritten. Open successful outputs in an independent viewer: rows are genuine selectable original-font text, with no cover rectangles. Viewers may add line separators when copying; that formatting is not the stored logical paragraph definition.

Malformed/modified examples are under `phase5_2_1/evidence/adversarial/`. Broken or conflicting declarations should not activate a whole editable group. External tools may discard the declaration; editing then falls back to conservative legacy classifications. Clipboard error 5 remains open and needs physical desktop review.

## Reproduce automated checks

Build with the .NET 8 SDK. Use the repository's development Python requirements in an isolated environment, and make Poppler `pdftoppm` available on PATH. Python/readers are not application dependencies. Commands below assume `.venv` at the repository root:

```powershell
./phase5_2_1/build.ps1
.venv/Scripts/python.exe phase5_2_1/tools/test_roundtrip.py
.venv/Scripts/python.exe phase5_2_1/tools/test_paragraph_spaces.py
.venv/Scripts/python.exe phase5_2_1/tools/paragraph_process.py
.venv/Scripts/python.exe phase5_2_1/tools/paragraph_performance.py
dotnet run --project phase5_2_1/Checks/Checks.csproj -c Release -- phase5_2_1/evidence/model phase4c1/evidence/word-spacing-analysis.json phase5_2_1/evidence/development-generations.json
```

Current regression tools are `test_engine.py`, `test_discovery.py`, `test_compatibility.py`, `test_position.py`, `test_insertion.py`, `test_document.py` and `test_wrap.py`, under phase5_2_1/tools. Run those before `verify_wrap.py`, followed by `verify_paragraph_structure.py`, `verify_positions.py` and `verify_independent.py`. `frozen_phase4c2.py` and `verify_frozen_c2.py` use original C2 binaries/assertions with output redirected under this phase. Avoid running reader tools while building because a worker may hold the unchanged native DLL open.

WPF regression flags are `--ui-test --discovery-ui-test --font-ui-test --position-ui-test --session-ui-test --insertion-ui-test --wrap-ui-test --clipboard-probe --audit <new-folder>` on the executable. `paragraph_process.py` drives six separate processes and isolated stores automatically. Keep generated evidence separate from production assets. See the evidence index for approved runs, historical failures and preservation hashes. Stop for review after Phase 5.1.
''')
(E/'README.md').write_text(f'''# Phase 5.1 evidence index

Start at [the handover](../../PHASE_5_1_HANDOVER/PHASE_5_1_IMPLEMENTATION_REPORT.md) and [test results](../../PHASE_5_1_HANDOVER/PHASE_5_1_ROUNDTRIP_TEST_RESULTS.md).

- [Starting state](starting-state.json), [prior baseline](prior-baseline.json), [preservation](prior-phase-preservation.json), [release manifest](release-manifest.json).
- [Round trips/adversaries](roundtrip-tests.json): {rt['tests']} checks; [separate processes](paragraph-controls.json): {ui['tests']} checks; [model](model/model-tests.json): {model['tests']} checks; [exact-space refusal](paragraph-space-restriction.json).
- Current worker suites: engine 18, discovery 22, compatibility 23, position 20, insertion 30, document 17, wrap 21.
- [Final inherited WPF suites](controls-shipping/) and [summary](control-summary.json): 56/57, with the same clipboard failure in [untouched C2](frozen-c2-controls/). Retry/probe failures are retained. Older folder names containing “approved” are development labels and do not override controls-shipping.
- [Combined independent index](wrap-independent-verification.json): {len(ind['cases'])} PDFs; [structure index](paragraph-structure-verification.json): {groups} group instances. [Records](verified-export-records.json) identify exact certified exports. Fixed-position and legacy reports cover 11 and 21 additional outputs.
- [Frozen C2 worker suites](frozen-phase4c2/) and [original-engine independent report](frozen-c2-readers/wrap-independent-verification.json): {len(frozen['cases'])} PDFs; older frozen suites/logs remain under this phase. The Phase 2-on-Phase 3 obsolete expectation and clipboard failures remain visible.
- [Performance](paragraph-performance.json), [32-group export records](paragraph-performance-records.json), wrap-performance.json and controls-shipping/wrap-control-tests.json provide timing/resource evidence.
- [Visual review](visual-qa.md), visual-contact-sheet.png and export-contact-sheet.png; [sample hashes](../run/paragraph-examples/manifest.json).
- Development folders retain failed/partial attempts: initial fixture/scalar/whitespace tests, content-stream/metadata-size/space-extent/reconstruction issues, PID reuse, output-redirection and reader mistakes. Earlier successful prototype files outside certified indexes are diagnostic, not supported release examples.

No previous release evidence is overwritten. Some JSON contains original workstation or transient paths. Retained exported PDFs and source fixtures are the portable artifacts; excluded test-work/fonts/candidates can be regenerated. No credentials or private user PDFs are part of the evidence. The exact export and preservation manifests, not every loose prototype file, define this release.
''',encoding='utf-8',newline='\n')
print('Wrote six Phase 5.1 handovers and evidence index')
