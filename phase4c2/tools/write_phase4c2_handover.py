"""Generate only this phase's handovers from completed final evidence."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];E=R/'evidence';H=R.parent/'PHASE_4C2_HANDOVER';H.mkdir(exist_ok=True)
def load(n):return json.loads((E/n).read_text(encoding='utf-8'))
def write(n,s):(H/('PHASE_4C2_'+n+'.md')).write_text(s.strip()+'\n',encoding='utf-8',newline='\n')
ui=[load(str(p.relative_to(E))) for p in (E/'final-controls-approved').glob('*tests.json')]
assert len(ui)==7 and all(v['failures']==0 for v in ui)
v=load('wrap-tests.json');ind=load('wrap-independent-verification.json');fixed=load('position-independent-verification.json');perf=load('wrap-performance.json')
assert v['failures']==0 and ind['success'] and fixed['success']
wr=load('final-controls-approved/wrap-control-tests.json')['rows']
typing=next(x['detail'] for x in wr if x['name']=='continuous-routed-typing-through-soft-wrap')
cost=next(x['detail'] for x in wr if x['name']=='three-plus-lines-and-input-cost')
write('IMPLEMENTATION_REPORT','''# Phase 4C.2 implementation report

Completed 28 October 2026. The Windows x64 application is `phase4c2/run/PdfEditorPrototype.exe`; keep the complete run directory together. It requires the .NET 8 Windows Desktop runtime. The build is framework-dependent, with no Python dependency for users. Build from source using `phase4c2/build.ps1` and the .NET 8 SDK.

## Delivered behaviour

Eligible original-font positioned text can grow into multiple genuine PDF text runs inside a conservative available rectangle. Genuine Microsoft Word letter, Arial and Calibri sources demonstrate this. One exact logical draft underlies all soft rows. Wrapping adds neither newline characters nor history events. Multi-region/page drafts, document-wide undo/redo, source-bound recovery and atomic combined Save As remain operational.

## Layout and editing architecture

`Core/PositionLayout.cs` retains the original single-line planner as PlanSingle. Safe single-row edits retain their prior origin policy. Horizontal overflow or protected-content contact can invoke wrapping. The deterministic plan records each row's logical start, text, baseline, origins, relative positions and ink, plus the available area. A pure expanded-width source clone obtains alignment and measurements; it does not grant ownership. Final rows must satisfy the original real-area/protected-object checks. Source observations remain immutable.

`Core/Models.cs` delegates positioned hit testing to the plan. `App/PositionedInk.cs` displays original-font glyph runs, caret and selection per row. `App/PositionSelection.cs` maps rows to logical offsets and implements Up/Down/Home/End and shift variants with preferred X and soft-boundary affinity. WPF owns text, text selection and input; horizontal movement remains native. `SessionEditing.cs` finds inactive drafts through proposed row bounds, allowing a click on a newly created second row to reactivate its draft.

`Core/DocumentTransaction.cs` emits one real text object per planned row, preserving original font, colour, size and verified mapping. The first baseline stays original. Each later row resets X to the original anchor. Native spacing offsets are skipped for a one-character run because no inter-character offsets exist; its anchor/origin is still strictly verified. This edge-case fix also covers reconstruction and the legacy writer. Empty drafts retain source ownership without a replacement object.

## Combined verification and boundaries

All modified source identities are resolved against the immutable original before mutation. Intersecting changed envelopes block both drafts. One candidate contains all safe edits; it is reopened and checked before atomic save to a different filename. Unsupported/unsafe changes retain every draft and block the combined save. Fingerprint, revision, session and navigation guards reject stale or foreign responses.

Positioned target and unrelated geometry remain at 0.01 pt. Outside-region changed pixels must be zero above the existing per-channel difference threshold of 8. Existing natural-path tolerances remain unchanged. Glyph mapping, outlines, original font programs, protected whitespace and exact extraction remain verified. No tolerance was relaxed to obtain a pass.

The recalculation path is bounded to 512 logical characters and eight rows, with available height often tighter. Inferred leading is deliberately conservative. Positioned hard newlines and failed exact-space extraction remain blocked without modifying the draft. Reopening can expose independently justified emitted rows, with no whole-paragraph ownership guarantee. General reflow, moving neighbours, mixed-font reconstruction, cross-page flow, OCR, merge/split, forms, signatures, undo grouping and installers were not added.

Native PDFium remains pinned to 156.0.8076.0, SHA256 `bede3932ce96a2e1ed9a7e6cae71aec8914efd2907d37ab44b1b81f9c8a6d04e`. Existing third-party notices accompany runtime/run. Development Python readers are not shipped application dependencies. No new licensing conclusion is implied.

The preservation audit covers 3,689 pre-existing files and the separate 353-file Phase 1 manifest. Historical phase source/build/evidence/handovers remain unchanged. START_HERE is the sole intentional pre-existing repository-entry documentation update, recorded with before/after hashes. The new release manifest hashes source, build, tools and handovers. This phase stops for review; no next phase has started.
''')
write('WRAPPING_AND_SPACING_ANALYSIS','''# Phase 4C.2 wrapping and spacing analysis

## Logical text and word breaks

Concatenating positioned plan row texts reproduces the exact draft. A separator at a soft break stays in the preceding text run. Leading, trailing and adjacent spaces are not trimmed or normalised. The greedy planner fits verified advances and measured ink, prefers the last fitting space and falls back to a character boundary for an uninterrupted word. A glyph too wide for the available area blocks export. Typed newlines are hard breaks: positioned export remains refused, and the draft/recovery retain the newline. Existing natural paragraph hard-break behaviour is retained.

## Conservative ownership

The left edge is the original anchor. The right edge uses the previously established safe limit, reduced by protected content ahead of the original line. The bottom uses source SafeBottom and nearby protected objects below the original baseline, with existing separation. Eight rows impose a further cap. This is a conservative editing envelope, not ownership of arbitrary empty page space. Neighbours never move.

Original source observations, indices, font probes and identity remain immutable. The position path's existing exception covers independently verified nonpainting, zero-extent coexisting whitespace only; these objects remain untouched in the PDF. Natural ownership rules are not broadened. Combined edited envelopes are checked together. The collision fixture proves actual proposed descender/ascender ink overlap, beyond merely overlapping envelopes.

## Glyph positioning

The C1 equal-length/equal-or-narrower substitution path keeps fixed origins. Other edits use bounded deterministic longest-common-subsequence alignment, without claiming the user's intended correspondence. Surviving adjacent source pairs can retain their observed residual on row one. Insertions and changed joins use verified original-font advances.

Each later row starts at the original X and advances naturally using the original font. No source residual crosses a new row boundary or is transplanted into later rows. Surviving glyph ink translates with the proposed X/baseline; it is not resized. New joins must satisfy ink checks. Only an original surviving sequence on row one retains the existing overlap exception. New rows have no blanket exception.

Each PDF run uses its own row-relative offsets. A one-character run has zero offsets and uses only its transform. Calling the native SetPositions API with count zero caused a real development export failure; the unnecessary call is now omitted. Tests cover a single-character draft and a 68-character uninterrupted word that emits rows of 67 and one characters.

## Baselines and leading

The first baseline stays original. Step is `max(2 * originalFontSize, verifiedInkHeight + 3 pt)`, spanning the measured supported glyph ink. Demonstrated 12 pt Word fonts use 24 pt leading. This is an intentionally generous inference for legibility and conservative line rediscovery, not recovered Word paragraph formatting. Saved baselines must match within 0.01 pt; fontTools independently derives font bounds and checks the step.

Every row envelope and glyph ink must remain in the safe rectangle and outside protected content. Vertical overflow preserves the complete draft and refuses the combined save. The original bounds and strict neighbour/glyph thresholds are unchanged.

## Presentation and rediscovery

Active glyphs, inactive drafts, caret, selection, hit testing, PDF mutation and reopen verification consume the same plan. Up/Down use a preferred X. Home/End use proposed row boundaries. Shift commands and mapped drag select continuous logical spans across soft wraps. Row affinity is presentation state, not a newline or history entry. WPF remains the text/selection owner.

Saved rows are independent genuine text objects. Discovery remains conservative, with no synthetic ownership tags or sidecar. An eligible first emitted row can be edited and saved again. Other rows may be independently editable or Limited, especially when separately owned Word whitespace prevents natural qualification. The app does not infer whole-paragraph ownership merely because it emitted neighbouring rows. Full paragraph round-trip editing remains limited.

Independent MuPDF/pypdf/fontTools/Poppler/pikepdf checks cover exact logical text, row separation, font programs and used mapping rules, computed glyph origins/baselines, untouched geometry, raw whitespace and 72/144-DPI outside-region pixels. Explicit natural hard breaks are reconstructed separately; positioned soft wraps always concatenate exactly without whitespace normalisation.
''')
write('TEST_RESULTS',f'''# Phase 4C.2 test results

Executed on Windows x64, 28 October 2026. Approved final controls are in `phase4c2/evidence/final-controls-approved/`. Other control folders retain development attempts. Counts represent suite checks, not physical input sessions.

| Final suite | Result | Evidence under phase4c2/evidence |
|---|---:|---|
| Current engine | 18/18 | engine-tests.json |
| Current discovery | 22/22 | discovery-tests.json |
| Current compatibility | 23/23 | compatibility-tests.json |
| Current position | 20/20 | position-tests.json |
| Current insertion | 30/30 | insertion-tests.json |
| Current document transaction | 17/17 | document-tests.json |
| New wrapping worker | {v['tests']}/{v['tests']} | wrap-tests.json |
| Session/layout model | 22/22 | model/model-tests.json |
| WPF controls, seven suites | 57/57 | final-controls-approved/*tests.json |
| Independent combined exports | {len(ind['cases'])}/{len(ind['cases'])} | wrap-independent-verification.json |
| Independent fixed-position exports | {len(fixed['cases'])}/{len(fixed['cases'])} | position-independent-verification.json |
| Independent legacy font/discovery | 21/21 | independent-verification.json |
| Recovery across exited processes | Pass | process-recovery.json |

The 57 controls comprise 46 inherited checks and 11 new wrapping checks. The separate clipboard probes do not close the historical intermittent clipboard defect.

## Coverage and expected results

New worker cases cover genuine Word two-row and three-plus-row text, Arial/Calibri, long-word fallback, punctuation/descenders, exact-space refusal, hard-break retention, vertical limits, graphics/paragraphs below, actual combined ink collision, mixed natural/positioned pages, two genuine Word pages, original overwrite protection, unsupported glyph blocks-all, independent-line second generation and one-character/one-character-tail exports. Expected refusals preserve all drafts and create no destination.

Controls cover per-character routed TextInput, exact undo/redo, every logical caret offset at four app zooms, Up/Down/Home/End/shift, mapped selection drag, soft-boundary deletion, inactive second-row activation, cross-page chronology, unsafe-draft recovery, combined collision and Calibri selection. They invoke actual WPF handlers/commands and shared mapping. They do not certify physical input or native file pickers. WPF screenshots use 96 DPI; app zoom is not OS display-scale coverage.

## Frozen regression results

Phase 1 Python: 14/14. Frozen Phase 2: 18/18; Phase 4A: 18/18; Phase 4A.1: 18/18; frozen Phase 3 discovery: 22/22; frozen Phase 4A compatibility: 23/23; frozen Phase 4B document: 17/17 and position: 20/20. Original C1 binaries retain insertion 30/30, document 17/17 and position 20/20 with outputs redirected under C2.

Original Phase 2 tests against Phase 3 retain 17/18: the obsolete manifestless-view-only expectation conflicts with automatic discovery. This known frozen result is preserved, not called a new pass. One current C1 insertion expectation intentionally changes: text beside a protected graphic may now wrap safely in reduced width. The original failing policy assertion is retained in development/previous-insertion-contract.json. No threshold was relaxed.

## Independent verification

MuPDF extraction, pypdf objects, fontTools metrics, Poppler at 72/144 DPI and qpdf syntax through pikepdf verify indexed successful combined outputs. This includes successful UI exports retained in failed development runs, final controls, worker cases, probes and recovery. Fixed and legacy exports have separate reader reports. Checks cover exact intended characters and row separation, source/destination hashes, all region identities, page count/dimensions, metadata, original programs/used encoding-width-ToUnicode-CID rules, proposed positioned origins/baselines within 0.01 pt, unrelated glyphs/boxes within 0.01 pt, protected raw whitespace and zero outside-region changed pixels above difference 8. Production verification also checks outlines/mapping.

Early collision outputs whose source was deliberately replaced remain diagnostic artifacts; their archived source and provenance are retained. Reader reports identify certified saved PDFs, distinct from loose transient candidates. Exact positioned text is never trimmed or normalised to pass. Explicit existing natural newlines are reconstructed from line structure.

## Performance and stability

Final routed input: {typing['characters']} characters, median {typing['medianInputMs']:.2f} ms and maximum {typing['maxInputMs']:.2f} ms including dispatcher processing; {typing['immediateWorkerRequests']} immediate worker calls. Thirty alternating replacements: median {cost['medianInputMs']:.2f} ms, max {cost['maxInputMs']:.2f} ms; local planning median {cost['medianCalculationMs']:.3f} ms; {cost['immediateWorkerRequests']} immediate worker calls.

Five preview samples per case, end-to-end medians: {', '.join(x['name']+' '+format(x['medianMs'],'.2f')+' ms' for x in perf['cases'])}. Detailed planning/generation/reopen timings are retained. Thirty worker wrap/unwrap alternations: handle growth {perf['handleGrowth']}, retained PDFs/PNGs {perf['retainedPdfs']}/{perf['retainedPngs']}, worker exited {perf['workerExited']}; recovery file {perf['recoveryFileBytes'][0]:,} bytes. Measurements use small local fixtures, not large-document certification. Existing 30-second timeout/revision rejection remains; no new in-flight cancellation is claimed.

## Investigated failures

The fixture parser initially omitted ToUnicode bfrange arrays; it now reads them without altering genuine Word streams/maps. Initial collision fixtures overlapped envelopes without ink; a revised draft then exceeded its bound by approximately 0.18 pt. Fixture geometry/content was corrected, with no tolerance change. The final case exports each edit alone and proves actual ink overlap together.

An early combined WPF run exposed retained-session assumptions. Tests now establish their own drafts/history. Clicking an inactive new row required an app fix to search proposed rows. The same run exposed the native zero-offset single-character export defect, now fixed and covered. Several TextInput tests asserted before queued WPF editing completed; awaiting dispatcher idle per character proves exact input. An earlier counter included the later export call; the final counter is captured before export. All failed runs remain.

The reader initially concatenated natural explicit hard breaks as soft rows; reconstruction now respects explicit breaks without changing text. One build could not recopy unchanged pdfium.dll while a reader worker held it; the final build completed after release. Visual QA and preservation reports are indexed separately. Clipboard, physical input, OS scaling and rediscovery limitations remain explicit.
''')
write('COMPATIBILITY_MATRIX','''# Phase 4C.2 compatibility matrix

These results apply to the retained corpus and verified mappings, not every Word/PDF file.

| Actual source/operation | C1 | C2 |
|---|---|---|
| Genuine Word letter fitting insertion/deletion | Verified single row | Retained same original-font/source-pair policy |
| Genuine Word title grows beyond width | Refused overflow | Verified two real text rows, exact logical draft |
| Genuine Word third paragraph grows | Refused overflow | Verified three-plus rows within available height |
| Genuine Word Arial/Calibri | Fitting edits supported | Two-row exports verified; Calibri live selection/caret checked |
| Uninterrupted word | Overflow refused | Character fallback; one-character final row verified |
| Punctuation/descenders | Fitting edits only | Verified wraps, inferred leading and ink checks |
| Adjacent spaces | Exact extraction required | Exact draft retained; demonstrated multi-space export refused |
| Positioned hard newline | Refused | Still refused without normalising the draft |
| Protected paragraph/graphic below | Overflow refused | Insufficient height blocks wrapping |
| Protected graphic ahead | Contact/width refused | Can wrap safely in reduced width; intentional policy expansion |
| Two independently safe wrapped edits | No wrap support | Each exports alone; actual combined ink collision rejects both |
| Mixed natural/positioned and multiple pages | Combined fitting changes | Wrapped/unwrapped combined export and global history verified |
| Two genuine Word pages | No wrapping | Wrapped changes on each page verified; no cross-page flow |
| Single-character positioned draft | Empty-offset native edge case | Verified without unnecessary offset API call |
| Reopen wrapped export | Not applicable | Eligible emitted line re-edited separately; no full paragraph ownership claim |
| Mixed styles/fonts, unsupported mappings | Restricted | Same conservative restrictions |
| ReportLab metric-rounding conflict | Restricted | Still restricted; no tolerance relaxation |
| Existing natural paragraphs/hard breaks | Bounded natural editing | Retained and independently checked |

Sources are the unchanged genuine `run/corpus/11-word-letter.pdf` and `run/font-corpus/Word-Arial.pdf` / `Word-Calibri.pdf`. Development fixtures append obstacles using the original map without simplifying genuine Word streams. A development two-page composition retains original Word pages for transaction testing; merge is not an application feature. Corpus provenance/hashes are in wrap-corpus.json.

Indexed successful exports pass original-program/mapping, exact text, origins/baselines, neighbour/whitespace and raster checks. Visual similarity never grants ownership. Full-paragraph rediscovery remains a documented limitation.
''')
write('OPEN_ISSUES','''# Phase 4C.2 open issues

## Deliberate boundaries

- Whole wrapped paragraphs are not reliably rediscovered as one region. Saved rows are separate genuine PDF objects. Existing rules can justify an individual emitted line; short rows may remain Limited because separately owned Word whitespace cannot be claimed. No ownership tags/sidecar were added.
- Positioned hard newlines remain unsupported and block combined export while retaining the exact draft and recovery. Soft wrapping never inserts a hard break.
- Some adjacent-space drafts fail exact native extraction. They remain unsaved and unchanged; no trimming/normalisation workaround is used.
- Available area and leading are conservative inferences. Demonstrated 12 pt text uses 24 pt leading, not recovered Word paragraph formatting. Plausible edits can be refused. Neighbours never move and text never flows across pages.
- Recalculation is bounded to 512 characters/eight rows, often constrained further by height. Mixed fonts, unsupported mappings/transforms/styles, unsafe joins and ambiguous ownership retain prior restrictions.

## Physical interaction and accessibility

WPF tests cover routed text events, commands/shared hit mapping, four app zooms and 96-DPI capture. They do not certify physical keyboard/mouse, native file pickers, IME, touch, screen readers, high contrast or multiple OS display scales. The positioned visual layer overlays WPF's logical surface; assistive-technology behaviour needs dedicated review. Native text events are queued, so automated assertions wait for dispatcher processing.

The historical intermittent clipboard Win32 error 5 remains open. A passing probe is local evidence, not a reliability fix. Undo still records ordinary edit events without grouping improvement, as requested.

## Operational limits

Performance measurements use small local corpus documents. Large PDFs, many changed regions, damaged files, memory pressure and prolonged sessions need broader coverage. Existing limits remain: 128 changed regions per transaction; bounded history (2,000 entries/2 million history characters), 16 MB recovery protection, source fingerprint/revision rejection, cache and candidate retention caps, 30-second worker timeout. No new native-operation cancellation is claimed. Recovery contains source-bound text under the user's local application data.

Retained failed control runs are development evidence; final-controls-approved is authoritative. Early collision outputs referencing a replaced source are diagnostic, with the original fixture archived. Strict reader reports identify certified files. Historical JSON may contain workstation-specific/transient paths; retained exports/fixtures are usable after cloning, and checks can be regenerated. No installer or broad production readiness is claimed.

The frozen Phase 2-on-Phase 3 obsolete view-only expectation remains documented. The protected-graphic policy now permits safe wrapping. Neither is concealed by loosening thresholds. Development stops at Phase 4C.2 pending review.
''')
write('USER_TEST_GUIDE','''# Phase 4C.2 user test guide

## Open the genuine Word example

Windows x64 and .NET 8 Windows Desktop runtime are required. Keep `phase4c2/run/` intact. From the repository root:

```powershell
./phase4c2/Launch.ps1 -Pdf './phase4c2/run/corpus/11-word-letter.pdf'
```

Or launch `phase4c2/run/PdfEditorPrototype.exe` and use Open PDF. No Python/network is needed. Save As always requires a new filename; the original cannot be overwritten.

## Wrap and navigate

Click “Phase 3 Office letter”, select its text and type this single logical line, with one space between words:

```text
Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter Phase 3 letter
```

It should form two visual rows while the next paragraph stays fixed. Wait for verification and Save As. Open the saved file in an independent viewer: the content is real selectable PDF text. Readers may add row separators when copying; technical checks verify the intended characters and row geometry directly.

For more rows, edit the third paragraph beginning “A separate paragraph” to twenty repetitions of “Phase 3 letter” on one logical line. This fixture has room for three-plus rows. Check all four app zoom choices.

Move across a soft break with Left/Right, then Up/Down, Home/End and shift variants. Drag selection from the first row into the second. Delete a space at a wrap and Undo. Wrapping alone creates no history entry. Ordinary edits retain the existing fine-grained history; grouping was not changed.

Edit another region, then click the new second row of the inactive first draft. It should reactivate at that row. On `run/document-corpus/mixed-multipage.pdf`, edit the Word title/third paragraph on page one and a natural paragraph on page two. Undo/Redo follows document chronology; one safe Save As includes every changed region/page.

## Refusals and recovery

Repeat the title phrase sixteen times: it should exceed the space above the next paragraph and block export. Enter within a positioned draft retains the newline but refuses export. An unsupported symbol such as a snowman blocks the combined save without losing other drafts. Multiple adjacent spaces can trigger exact-extraction refusal. Restore a supported draft to continue.

Close with unsaved wrapped edits and reopen the same unchanged source. Check all page drafts/history. Normal recovery is `%LocalAppData%\\PdfEditorPrototype\\phase4c2\\sessions`; tests use separate stores. A changed source fingerprint prevents blind application of old drafts.

Development PDFs in `run/wrap-corpus/` test graphics/paragraphs below. For combined-collision.pdf, the technical test edits the third paragraph to 35 repetitions of “gyp” and its small “..” region to 12 repetitions of “fictional letter”. Each is safe alone; both together must be refused with both drafts retained. These are adversarial development fixtures, not merge functionality.

## Reopen and review

Reopen a verified wrapped PDF. An eligible emitted first row can be edited and saved separately. Do not expect the entire former paragraph to become one region: other rows may be independently editable or Limited under conservative ownership rules.

Manual priorities are physical continuous typing/caret comfort, row selection at your OS display scale, page navigation, clipboard reliability and recovery. Record source, page, exact draft, zoom/display scale, warning and expected/actual behaviour. Automated controls do not replace these manual checks. Read OPEN_ISSUES and TEST_RESULTS, plus the evidence index. Stop at Phase 4C.2 for review.
''')
(E/'README.md').write_text(f'''# Phase 4C.2 evidence index

Approved WPF run: [final-controls-approved/](final-controls-approved/), 57 passing checks (46 inherited, 11 wrapping). Other control folders retain development attempts, including failures.

- [Wrapping worker](wrap-tests.json): {v['tests']} checks, {len(v['saved'])} successful saves. [Model](model/model-tests.json): 22 checks.
- Current worker JSON: engine-tests (18), discovery-tests (22), compatibility-tests (23), position-tests (20), insertion-tests (30), document-tests (17).
- [Combined independent reader index](wrap-independent-verification.json): {len(ind['cases'])} saved PDFs, including successful retained development UI exports. Each source/destination hash and page's geometry/text/font/whitespace/72/144-DPI comparisons is recorded.
- [Fixed-position reader index](position-independent-verification.json): {len(fixed['cases'])} PDFs; [legacy reader index](independent-verification.json): 21.
- [Process recovery](process-recovery.json): three drafts/two pages across exited processes. [Performance](wrap-performance.json): preview stages, repeated operations, handles, cache, exit and recovery size.
- [Corpus provenance](wrap-corpus.json), [baseline](prior-baseline.json), [prior preservation](prior-phase-preservation.json), [Phase 1 preservation](phase1-preservation.json), [release manifest](release-manifest.json).
- Frozen regression JSON/logs are under this directory and frozen phase subdirectories. Phase 2-on-Phase 3 retains one obsolete expectation failure.
- [Visual QA](visual-qa.md), [contact sheet](visual-contact-sheet.png), approved control images and Poppler rasters.
- Development retains initial collision/wrap attempts, the earlier graphic-policy assertion, failed combined controls and wrap-controls through wrap-controls-6. TEST_RESULTS explains each. Early collision exports referring to a replaced source are diagnostic, not certified; the original fixture is archived.

Prior phases remain byte-identical. START_HERE is the separately recorded intentional repository-entry update. Some JSON paths refer to original workstation/transient candidates; exported PDFs/source fixtures remain, while test-work/bin/obj/caches are excluded. Development patch/probe scripts preserve provenance and are not the normal build path. Reader reports identify certified saved outputs.
''',encoding='utf-8',newline='\n')
print('Wrote six Phase 4C.2 handovers and evidence index')
