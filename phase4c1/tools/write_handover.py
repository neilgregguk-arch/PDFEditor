from pathlib import Path
R=Path(__file__).resolve().parents[1];H=R.parent/'PHASE_4C1_HANDOVER';H.mkdir(exist_ok=True);E=R/'evidence'
docs={
'IMPLEMENTATION_REPORT':'''# Phase 4C.1 implementation report

Delivered 28 October 2026. All implementation, building and tests took place in Codex. The separate `phase4c1/` source and runnable Windows x64 build extend Phase 4B. Prior releases, fixtures and evidence are preserved by a before/after hash audit. Phase 4C.2 has not started.

## Outcome and architecture

Supported position-aware Word lines now permit mapped-character insertion, deletion, range replacement with different lengths and complete line removal. Subsequent glyphs receive explicitly calculated origins. The line stays anchored at its original source x and baseline; it does not wrap, shrink its font or move unrelated objects. Unsafe spacing, unsupported glyphs, overflow, protected-content collision or failed candidate verification block the complete export while retaining every draft.

The two editing strategies remain distinct. Natural-layout paragraphs retain bounded wrapping and expansion. Existing equal-or-narrower substitutions retain fixed original origins. Other supported positioned changes use surviving source-pair spacing and original-font advances at edited joins.

The Phase 4B document session, chronological history, recovery, asynchronous worker, revision guards and atomic Save As are reused. Undo grouping is unchanged: one native text-change event records one history unit, with explicit control changes grouped as before. No word-based or time-based grouping has been added.

## Implementation map

- `Core/PositionLayout.cs`: immutable source observations, bounded character alignment, replacement/deletion classification, proposed origins and ink, single-line bounds and spacing rules.
- `Core/Models.cs`: `Layout.Positioned` pointer-free proposed geometry and proposed-origin hit testing.
- `Core/DocumentTransaction.cs`: consumes the complete per-region plan, writes explicit offsets, verifies proposed origins/ink and reports planning, candidate generation and reopen verification timing.
- `Core/PdfEngine.cs`: existing fixed-origin single-request path retained; spacing-recalculated positioned requests route through the document transaction.
- `Core/DocumentSession.cs`: retains source-based identity, including safe horizontal bound; working draft never becomes a synthetic source.
- `App/PositionedInk.cs`: source-font glyph presentation plus aligned visible caret and selection, using the same proposed origins as export.
- `App/PositionSelection.cs`: mapped click, drag, shift selection and word/line selection helpers. Logical text/selection and input remain with the existing RichTextBox.
- `App/EditorWindow.cs`, `App/SessionEditing.cs`: immediate editor width update, inactive drafts and source-clean page presentation, validation and source-bound recovery.
- `App/InsertionControlTests.cs`, `Checks/Program.cs`, `tools/test_insertion.py`: executable interaction, model and worker checks. Development independent readers are separate from application runtime.

## Source and draft model

`PositionedSource` retains original glyphs/origins/bounds, explicit offsets, verified original-font ink offsets, protected objects, coexisting nonpainting whitespace and the conservative page-margin horizontal limit. Original observations are never changed by planning. Native scratch objects measure verified glyph ink and are removed before the source is used. No native pointer survives in a session or cache observation.

`PositionedDraft` contains absolute proposed origins, PDFium N-1 float offsets, original surviving-character indices, character kinds, replacement-source indices, deleted original indices, per-glyph ink bounds, policy and ambiguity observation. Replacement attribution is deterministic, not a claim about original author intent. Only unchanged adjacent source pairs carry measured spacing forward.

The existing fixed-origin pathway remains available for same-count equal-or-narrower substitutions. Recalculated layouts are bounded to 512 source/draft characters, avoiding unbounded quadratic alignment on the input thread. A larger fixed-origin source is not newly prohibited solely by this recalculation limit. Unsupported or excessive drafts remain editable/recoverable within the inherited recovery size limit.

## Live interaction

The active original-font ink follows the proposal immediately; inactive regions retain their latest draft. Validation remains debounced by 300 ms and recovery by 350 ms. Input does not wait for a PDF candidate. Replies must match session instance, source hash and revision. Candidate verification does not replace the current ink presentation, so it does not introduce a new text-position jump.

Testing exposed a Calibri native-caret discrepancy of 1.271 pt after insertion. The supported positioned path now hides WPF's natural-spacing caret and highlight and paints them at the proposal. Mouse placement/drag use the same origin hit mapping; RichTextBox still owns text, offsets, keyboard commands and history. Unsupported drafts use the visible native fallback with a warning; their appearance is not a verified layout. The custom caret blinks, with its timer stopped for inactive/unloaded layers.

## Genuine output and integration

The transaction freshly resolves every region against original source hash/identity, checks all strategies together, creates text with each original font, sets explicit positions and removes only owned source objects. One complete candidate is saved, reopened and verified. Predicted glyph origins and ink are checked at 0.01 pt; untouched neighbours retain the same strict tolerance. Source programs, mappings/style/outlines, page properties and outside-area pixels are protected. Separate whitespace objects remain owned by the source and are never absorbed into line deletion.

Save stages beside a new destination, rechecks checksums/source and commits without overwrite. Failure retains all drafts; existing destinations and source cannot be replaced. Save retains the original working base and history, so reopen an output to start a freshly discovered generation. Recovery uses the private `phase4c1/sessions` directory and does not migrate older phase sessions.

## Build and delivery

Run `phase4c1/Launch.ps1` or `phase4c1/run/PdfEditorPrototype.exe`. Framework-dependent .NET 8 Windows Desktop x64 runtime is required. Build with `phase4c1/build.ps1`. The separate worker and unchanged PDFium 156.0.8076.0 DLL ship together; DLL SHA256 is `bede3932ce96a2e1ed9a7e6cae71aec8914efd2907d37ab44b1b81f9c8a6d04e`. Python/readers are development-only. No cloud dependency, installer or font substitution was added. Review the tests, spacing analysis, compatibility matrix, issues and manual guide alongside this report.
''',
'WORD_SPACING_ANALYSIS':'''# Phase 4C.1 Word spacing analysis

## Evidence and interpretation

`phase4c1/evidence/word-spacing-analysis.json` records fresh source hashes, producer, original content streams, TJ/Tj/Tf/Tm/Tc/Tw/Tz operands, font programs, ToUnicode data, raw encoded character codes, Unicode mappings, CID/GID observations, font advances, original glyph origins/bounds, style, transforms and protected objects. The sources are genuine Word-produced `corpus/11-word-letter.pdf`, `font-corpus/Word-Arial.pdf` and `font-corpus/Word-Calibri.pdf`. Development fixture composition does not re-author their Word text.

The existing source eligibility checks remain: complete single horizontal object, identity supported transform, opaque supported style, verified standalone embedded TrueType program and reverse character mapping, exact original reconstruction, glyph baseline/ownership and native metric compatibility. Multi-font/fragmented lines, visible whitespace interference, clipping/rotation, graphics through original text and unsupported mappings remain restricted.

Measured maximum absolute inter-glyph residuals are 0.333984 / 0.166168 / 0.683907 pt for the three letter lines; Arial sample lines 0.096001 / 0.146011 pt; Calibri lines 0.302124 / 0.302094 pt. These are `next origin - current origin - verified font advance`. They include Word/PDF spacing and width effects. They are observations, not proof of deliberate author kerning. The horizontal outer limit is approximately x=523.296 pt, inferred from the original page's conservative right margin. Protected objects can block a proposed line before that limit.

The letter source uses embedded Type0 Identity-H Arial. Its five separate nonembedded F2 whitespace objects remain independent. Code zero and code six can both decode as space in F1 while referring to different glyph identities; existing outline/width/context roundtrip checks choose safe mappings. The planner never invents raw codes or substitutes fonts. The letter font has 32 verified ASCII mappings, the Arial and Calibri samples 16 each; having a Unicode character in the original TrueType program alone is not sufficient for eligibility.

## Explicit mapping policy

For existing equal-or-narrower same-count substitutions, preserve every original glyph origin exactly as before. New replacement glyphs must fit and survive the existing extraction/outline/geometry checks; that legacy path is not reset to natural spacing.

Other edits use a bounded longest common subsequence between immutable original Unicode and current draft. Equal symbols match immediately; if deletion and insertion branches tie, skip an original symbol. Ambiguity is recorded, including alternative equal-symbol matches. This deterministic policy does not infer typing history or author intent, and repeated letters/words can align differently from the user's conceptual edit. It is stable for the same source and draft after recovery.

Mapped unchanged characters are `Surviving`. Unmatched old/new symbols between consecutive surviving anchors are paired in order as `Replaced`; extra new symbols are `Inserted`; remaining old symbols are `Deleted`. Replacement-source indices are separate from surviving indices. Classification of ambiguous replacements is descriptive only: it never grants preservation of a spacing relationship between changed characters.

## Position calculation

The first surviving or inserted draft glyph is anchored to the original line x. For each following glyph, add the preceding draft glyph's verified original-font advance. Add an original measured residual only if this glyph and its immediate predecessor map to consecutive unchanged original characters. At inserted/replaced joins and deletion seams the adjustment is zero. Accumulate in double precision; pass N-1 float offsets relative to source x to the pinned native API. Reopened origins must agree within 0.01 pt.

An unchanged source subsequence therefore keeps its internal measured distances and glyph shapes, translated as a block when edits precede it. Prefixes before an edit remain fixed. After deletion, the new join closes using the surviving preceding glyph's advance; text is not stretched to the old width. Beginning insertion shifts the original sequence to the right; beginning deletion moves the remainder to the original anchor. Unchanged adjacent pairs preserve their observed residuals even when their absolute origins shift.

Inserted glyph ink is measured through the same original PDF font in temporary native text objects. Surviving glyph bounds are translated from immutable original observations. New edited joins cannot introduce overlapping letter bounds. Overlap already evidenced inside a fully surviving original sequence is retained, rather than treating every original f/f ink overlap as a new defect. Final saved glyph ink and outlines are checked independently of the planner's logical width.

## Boundaries and known refusals

The planner checks logical extent and ink against the conservative right limit and vertical line envelope, then protected objects with a 0.5 pt pad. Combined transaction validation also checks other edited regions and final saved extents. Authorised pixel comparison covers only original and proposed extents plus the existing two-point verification padding, not the whole available blank page width. No font shrinking, moving neighbours or positioned wrapping is used.

A newly inserted third f in `Offfice` is refused because it introduces overlapping glyph bounds at a new join. Existing original `ff` relationships are preserved. A double-space insertion is refused when PDFium's saved extraction collapses the intended text. These are documented safe refusals, not certified insertions. Removing a complete line removes only that region's text object; the five separately owned F2 strings/objects in the letter fixture survive unchanged, with independent raw-byte checks.

## Independent and presentation evidence

Independent verification recomputes the alignment, reads advances from fontTools original font metrics and uses MuPDF source glyph geometry to recalculate expected surviving-pair origins. It compares each saved inserted/repositioned origin to that independent proposal, checks translated survivor bounds and retains strict neighbour geometry. pypdf checks font/mapping/width rules and protected whitespace bytes; qpdf and Poppler verify complete files and pixels.

The independent line parser initially mixed an unchanged separate F2 space into the horizontally expanded title when sorting glyphs by x. It now identifies standalone all-space spans separately; those spaces remain in the untouched-object comparison and raw-byte checks. Intended text is still checked exactly. No position or pixel threshold was changed.

Visible positioned caret/selection now use proposed geometry. Hidden native WPF caret measurements are retained separately; they are not a PDF geometry tolerance. Tests exercise four zooms at the workstation's actual 96 DPI. Other OS display scales and hardware interaction remain manual review items.
''',
'COMPATIBILITY_MATRIX':'''# Phase 4C.1 compatibility matrix

The matrix describes executed local fixtures, not arbitrary PDFs with the same producer/font name. Every newly allowed character must have a verified original PDF mapping; no font program is rebuilt or replaced.

| Source / feature | Phase 4B | Phase 4C.1 evidence |
|---|---|---|
| Genuine Word letter, three Arial lines | Same-count equal/narrower substitutions | Preserved, plus start/middle/end insertion, multiple insertions, deletion/range replacement, empty title and second generation |
| Word-Arial `cafe calm. cafe calm.` | Fixed-origin substitutions; narrower-gap extraction failure possible | Insert ` cafe`, remove word/characters, different-length replacement; verified outputs preserve source font and surviving pair spacing |
| Word-Calibri same sample | Fixed-origin substitutions | Same insertion/deletion/replacement cases verified; visible caret/selection corrected for measured native drift |
| Natural Prototype paragraphs | Bounded wrapping/expansion | Existing engine/discovery/font tests remain passing; combined natural + Word edits on different pages pass |
| Same-count wider mapped replacement | Refused | Recalculated single-line path allowed only if spacing/ink/bounds and complete export verify; tested letter `...letWer` |
| Fixed-origin equal/narrower replacement | Supported under existing gates | Same fixed origins and original-font checks retained |
| New f/f/f overlap | Refused by old count rule | Refused by new ink-overlap rule; draft retained |
| Double-space insertion with extraction collapse | Refused by old count rule | Saved text mismatch blocks output; draft retained |
| Unsupported snowman / unmapped punctuation | Refused | Refused; other drafts remain editable, complete export blocked |
| Horizontal overflow or protected graphic ahead | Refused by old count rule | Eligible source activates, but expanding draft is refused without wrapping or moving graphics |
| Positioned newline / paragraph reflow | Refused | Still refused; natural paragraph wrapping is a separate strategy |
| Word-multiple-runs mixed-font line | Ambiguous/restricted | Remains restricted; no run merging |
| Word Consolas / PowerPoint protected cases | Existing ownership/graphic restrictions | Not newly promoted; no expanded compatibility claim |
| ReportLab artificial character spacing / kerning metric mismatch | Metric gate refused | Gate retained; no 0.01 pt relaxation |
| Visible or nonzero separately owned whitespace | Protected/restricted | Still protected; only verified nonpainting zero-extent coexistence exception retained |
| Signatures, encryption, forms/annotations, unsupported transforms/clipping | Existing safety gates | Unchanged; no authoring support added |

The final tests include source-hash and identity rejection, destination protection, worker restart, chronological multi-region history, recovery across distinct exited processes, combined output and second-generation rediscovery. A source may expose several eligible lines while still containing unsupported regions. Reopening a fully deleted line cannot recreate its former region: it has genuinely been removed; other surviving regions remain discoverable.

Spacing recalculation supports up to 512 original/draft characters per positioned line. Existing fixed-origin substitutions retain their prior path. Combined export retains the Phase 4B maximum of 128 modified regions. The same-source session base remains original after Save As; reopen the output for a new generation. See the test report for exact counts and the issues report for semantic PDF, recovery and packaging limits.
''',
'OPEN_ISSUES':'''# Phase 4C.1 open issues

## Deliberate safety limits

This is controlled single-line editing, not Word paragraph reflow. Positioned newlines/wrapping remain blocked. Original-font character eligibility, transforms, paint, clipping and ownership gates are unchanged. Only mappings actually verified in each PDF can be inserted. Natural paragraphs retain their separate bounded wrapping model. No font substitution, subset rebuilding, moving unrelated objects, OCR, merging/splitting, forms, annotations, signatures, AI or cloud functionality was added.

Spacing at edited joins uses verified advances with zero borrowed original residual. It is not a new kerning engine. Original pair residuals are retained only for surviving adjacent characters. Repeated-symbol alignment is deterministic and conservative, without author-intent reconstruction. A conceptual replacement may be classified differently from a user's typing history. Classification does not authorize extra spacing changes.

New `fff` ink overlap and double-space extraction collapse are concrete refused cases. Other pairs can also fail strict reconstruction/extraction even when local planning initially passes. Every draft remains available; a failed candidate blocks the complete transaction. An entire line can be removed safely in tested fixtures, but an empty region is absent on later rediscovery.

## Presentation and interaction

Calibri exposed a 1.271 pt difference between WPF natural-spacing caret and positioned glyphs. Supported positioned drafts now show a custom proposed-position caret/highlight and map mouse selection accordingly. Hidden native geometry is still recorded; it is not claimed fixed internally. Invalid drafts fall back to native presentation with warnings and may scroll or wrap temporarily. They are not a verified PDF layout.

Actual controls/shared click and drag methods, routed input/commands and saved output were tested. No hardware mouse/keyboard or native Windows file-picker automation took place. Four zooms were measured at the actual 96 DPI / 100% Windows display scale. 125%, 150%, 200% OS scaling, IME, accessibility tools, touch, high contrast and complex bidirectional/shaped scripts are not certified. Manual checks are in the guide. WPF control tests do not establish new physical comfort feedback.

The intermittent clipboard Win32 5 defect remains open. This phase does not attempt a clipboard fix. Passing release copy/cut/paste checks and five successful probes do not prove reliability. Earlier phase failures remain preserved. Undo grouping is unchanged by request.

## Document integrity and persistence

Untouched visual/glyph/font checks are strict, but full tag trees/MCID semantics, accessibility, logical reading order, XMP, PDF/A, complete annotation dictionaries and signature preservation are not certified. Replacement stream order can differ from visual reading order. Font resource aliases may accumulate; unused resource entries can be pruned. Used font programs and mapping/width rules are independently checked.

Recovery is private to Phase 4C.1, hash-keyed and atomically replaced. Earlier phase sessions are preserved rather than migrated. A changed source is a new session. History remains bounded to 2,000 entries / 2,000,000 UTF-16 before+after characters. Recovery is limited to 16 MB; oversize drafts stay in memory and the prior file survives. Multiple app instances have no recovery merge or locking; do not edit the same source concurrently. Incompatible snapshots can require technical inspection of retained JSON; no orphan-draft UI is added.

The application retains the original source binding and drafts/history after Save As; it does not automatically rebase or mark drafts clean. Source and existing destinations cannot be overwritten. Atomic stage/move failure is tested, but crash/power-loss durability and unusual network-filesystem semantics are not certified.

## Performance and packaging

Recalculated alignment is bounded at 512 source/draft characters; fixed-origin substitutions retain the earlier pathway. Native work retains the 30-second worker timeout and revision/session guards, with no in-flight native cancellation. Analysis cache and candidate retention remain eight observed pages and twelve candidate PDFs/twelve PNGs per work directory. Total session/font memory is not hard capped; clean-close cleanup is best effort and crashes can leave orphan directories.

Measured timings cover small local fixtures and programmatic WPF handlers, not large documents or keyboard-to-screen latency. Framework-dependent .NET 8 Windows Desktop x64 is the delivered build. No self-contained clean-machine or installer certification was performed. Development independent readers are not runtime dependencies; normal Save As uses the built-in worker's PDFium structural/glyph/outline/pixel verification.

## Retained failures and corrections

The first insertion test expected every proposed example to pass: the `fff` and double-space cases exposed genuine safety limits and are now explicit negative controls. The passing within-word/multi-insertion cases use other safely mapped letters; no numeric threshold was relaxed. Initial independent glyph sorting incorrectly included protected F2 spaces inside expanded titles; they are now tracked separately and still strictly preserved.

Old positioned tests expected longer, shorter and wider replacements to fail; original results are retained and those three expectations intentionally changed. An initial discovery test found a verification-envelope compatibility break after routing all positioned single requests through combined output; the original fixed-origin single-request path is retained, restoring the old contract. Parallel test work-folder names collided at equal Windows timestamps; UUID work directories fixed the harness collision. A Word-analysis JSON serialization error from reusing a raw-byte variable was corrected.

Early WPF insertion tests assumed reopening an existing source reset its session. It correctly restored prior drafts; tests now explicitly restore the original text before isolated editing assertions. Native Calibri caret failure is retained in development evidence and led to the aligned visual layer. Selection screenshots now wait for rendering after changing selection; this is a capture correction, not a geometry tolerance change. Consult the test report for designated release evidence and all retained failures.

Stop at Phase 4C.1. Phase 4C.2 requires review.
''',
'USER_TEST_GUIDE':'''# Phase 4C.1 user test guide

## Run

Open `phase4c1/run/PdfEditorPrototype.exe` or run `./phase4c1/Launch.ps1`. Requires Windows x64 and .NET 8 Windows Desktop runtime. Rebuild with `./phase4c1/build.ps1` if needed. Keep the worker, native DLL and assets together. Work on fictional samples or copies and always choose a new output filename.

Open `phase4c1/run/corpus/11-word-letter.pdf`. It is the genuine Word letter used for the positioning tests. The existing interface is unchanged: click supported text and type directly. A small summary shows draft count, attention and export readiness. Draft ink and proposed positions are immediate; only a successful Save As produces a verified output.

## Insertion, deletion and selection

1. In the title `Phase 3 Office letter`, click after `Phas` and type `s`: expect `Phasse 3 Office letter`.
2. Undo and redo. Selection or switching alone should not add text history. Individual-character undo grouping remains unchanged.
3. Select `Office ` including its following space and delete it: expect `Phase 3 letter`. The rest should close naturally, without being stretched to the old title width.
4. Replace `Office` with `letter`, a different length. Try adding `Phase ` at the start, ` letter` at the end, or `letter ` between words. Try several separate insertions, such as `Phasse 33 Office letterr`.
5. Save As to a new PDF, open it independently and check text extraction as well as visual placement. Original font, baseline and untouched paragraphs should remain stable. Reopen that output in the editor and make another supported edit.
6. Select and remove the whole title. Save to another new name. The other lines and separately owned original whitespace must remain; the title is genuinely removed. Undo in the working session should restore its prior text.

Only original-font mapped characters are available. Not every ASCII letter is safely encoded by every Word sample. The title's original `ff` is preserved, but adding a third f to make `Offfice` is a known refused join. A double-space insertion is another known candidate-extraction refusal. These warnings retain your complete draft.

## Arial, Calibri and display

Open `run/font-corpus/Word-Arial.pdf`, then `Word-Calibri.pdf`. The first line is `cafe calm. cafe calm.`. Append ` cafe`, remove the first `calm` and its neighbouring space appropriately, or replace the first `cafe` with `calm`. Save to new names. Use only characters with verified mappings.

At 75%, 100%, 150% and 200% zoom, physically check clicking between letters, drag selection, shift-click, word double-click, home/end, arrows, backspace/delete and typing. Supported positioned text uses a proposed-position caret/highlight because native WPF spacing differs for some Calibri text. Text input and document history remain in the same editor. The automated tests used 96 DPI; test your own Windows display scale, especially 125% or 150%, and report any visible caret drift.

## Mixed document, history and recovery

Open `run/document-corpus/mixed-multipage.pdf`, a development fixture with genuine Word text on page one and a natural paragraph page on page two. Insert `s` in the title. In the third Word line remove `should ` including its following space. On page two change the first paragraph to `First changed working paragraph.`.

Switch back through all three areas; drafts should stay visible. Undo should reverse the natural edit first, then Word deletion, then title insertion, navigating to affected pages/regions. Redo restores the chronology. Save As must include all changes in one file. Natural paragraphs can still wrap within their verified bounds; Word lines cannot wrap.

Close normally after editing, reopen the same original and verify drafts/history return. Recovery is under `%LocalAppData%/PdfEditorPrototype/phase4c1/sessions/`; it does not import your Phase 4B recovery. Saving retains the original working base and drafts. Reopen a saved output for a fresh source session.

## Warnings and failures

- Append enough ` letter` words to run out of horizontal space. Expect a warning and blocked complete export, with all text retained and no font shrinking/wrapping.
- Open `run/document-corpus/word-horizontal-obstacle.pdf`; expand the eligible title toward the black rectangle. The rectangle must remain fixed and the colliding draft must not export.
- Add a snowman or unsupported punctuation in one region while another holds a valid edit. Both drafts must remain accessible; Save As must not export only the valid one.
- Insert a newline in a Word line. It is retained in the draft but blocked for this phase.
- Try the original filename, an existing destination, or a non-writable location. Original/existing bytes must remain unchanged; failed saves must preserve every draft.

Physically test copy/cut/paste and native file pickers. Clipboard Win32 5 remains intermittent; a later passing paste does not prove it fixed. Record source/sample, steps, zoom, Windows display scale and full warning. No hardware/file-picker testing is claimed by the automated evidence. Detailed executed results and limits are in the other five reports. Do not start Phase 4C.2 without review.
'''
}
for name,text in docs.items():(H/('PHASE_4C1_'+name+'.md')).write_text(text,encoding='utf-8',newline='\n')
print('Wrote five Phase 4C.1 reports; test report follows final evidence.')

import json
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
C=E/'final-release-controls';S=E/'selection-verified-controls'
ind=read(E/'document-independent-verification.json');assert ind['success']
new=read(E/'insertion-tests.json');model=read(E/'model/model-tests.json');assert new['failures']==model['failures']==0
ui=read(S/'insertion-control-tests.json');assert ui['failures']==0
metrics=ui['rows'][-1]['detail'];performance=read(E/'document-performance.json')
legacy=read(E/'independent-verification.json');positions=read(E/'position-independent-verification.json')
maxshift=max(p['maxUntouchedGlyphShiftPt'] for c in ind['cases'] for p in c['pages']);maxorigin=max(p['maxPositionedTargetOriginShiftPt'] for c in ind['cases'] for p in c['pages'])
counts=[]
for name in ['control','discovery-control','font-control','position-control','session-control','insertion-control']:
 d=read(C/(name+'-tests.json'));assert d['failures']==0;counts.append((name,d['tests']))
fontmetrics=next(x['detail']['samples'] for x in ui['rows'] if x['name']=='L-Arial-Calibri-caret-and-selection-geometry')
caretrows='\n'.join('| '+v['font']+' | '+f"{v['maxHiddenNativeCaretErrorPt']:.6f}"+' | '+f"{v['maxVisibleCaretErrorPt']:.3g}"+' |' for v in fontmetrics)
previewrows='\n'.join('| '+v['name']+' | '+f"{v['medianMs']:.2f}"+' | '+str(v['changedRegions'])+' |' for v in performance['cases'])
controlrows='\n'.join('| '+n+' | '+str(k)+'/'+str(k)+' |' for n,k in counts)
text=f'''# Phase 4C.1 executed test results

Executed 28 October 2026, Windows x64, .NET 8 WPF and unchanged pinned PDFium. The App/Worker publish completed successfully. Final source/build hashes are in `phase4c1/evidence/release-manifest.json`. Unless noted, evidence paths below are relative to `phase4c1/evidence/`. Previous evidence is preserved, not overwritten by these tests.

## New engine and model checks

`insertion-tests.json`: **{new['tests']}/{new['tests']}**. Cases include middle/start/within-word/between-word/end insertion, multiple characters and separate insertions, single/consecutive/start/end deletion, whole word removal, different-length range replacement, complete title deletion, safe Arial/Calibri insertion/deletion/replacement, preserved source-pair spacing, second-generation rediscovery, mixed Word insertion/deletion plus a natural paragraph on another page, and failed final commit with no stage/partial output. Negative controls cover new fff overlap, double-space extraction mismatch, horizontal page-boundary overflow, a protected graphic ahead, unsupported glyphs and positioned newlines.

`model/model-tests.json`: **{model['tests']}/{model['tests']}**. Eleven inherited session/history/recovery guards plus six positioning invariants: unchanged adjacent pair distances, deletion seam font advance, fixed legacy substitution positions, immutable original observations, bounded processing/overflow and empty-line ownership. Source/session/revision response guards, redo branches, history size caps, corrupt/oversized recovery and preserved incompatible drafts remain covered. The final model build completed without the earlier nullable test warning.

`document-tests.json`: **17/17** combined transaction checks. Two expanding natural paragraphs, multiple positioned regions, mixed strategy, pages, collision and unsupported-one blocks-all behaviour, source/destination/identity/ownership protection, deletion with another edit, second generation and worker restart remain passing. The old position-count-only negative now tests horizontal overflow, which is the intended new boundary.

## Actual WPF controls

Designated full run: `final-release-controls/`.

| Suite | Executed result |
|---|---:|
{controlrows}

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
{caretrows}

The Word letter title's inserted line had 0.254002 pt native error across 75/100/150/200% zoom. The final visible geometry checks require at most 0.01 pt, and shared click/drag selected the expected `calm` range. Measurements cover every tested caret offset at all four zooms. Windows actual scale was 100%, 96 DPI; no OS scaling settings were changed. Physical input, IME and accessibility remain unverified.

Visual review includes inserted title/caret, blocked unsupported text plus another inactive draft, and the refreshed Calibri selection highlight after a render wait. Poppler contact-sheet review covers inserted/deleted Word, Arial/Calibri and both mixed-document pages. Draft appearance and verified exported PDF remain distinct.

## Independent complete-output verification

`document-independent-verification.json`: **{len(ind['cases'])}/{len(ind['cases'])} recorded combined exports**. This includes 23 successful new worker exports, ten combined regression exports, fifteen full-run UI exports, five selection-capture rerun exports, one separate-process recovery export and three newly permitted old-position-test outputs. Every page is verified, including unchanged pages. No export is counted solely on a PDFium return code.

Tools: MuPDF glyph/text extraction; pypdf font programs, used encoding/ToUnicode/CIDToGID/width rules, raw nonembedded whitespace bytes and metadata; fontTools advances and independently recomputed alignment/proposals; pikepdf/qpdf syntax; Poppler full-page renders at 72 and 144 DPI. Exact intended replacement text is checked; geometry comparisons distinguish repositioned survivors from fixed unrelated neighbours.

Observed maximum untouched glyph shift: **{maxshift:.8g} pt**. Maximum inserted/repositioned target origin deviation from the independent proposal: **{maxorigin:.8g} pt**, under the unchanged 0.01 pt threshold. Outside authorised-area changed pixels are **zero** at both DPIs (channel difference threshold 8). Surviving ink bounds are independently compared after translation. Embedded font programs and used mapping/width rules remain preserved. Standalone protected spaces are compared separately and their original raw bytes survive.

`independent-verification.json`: **{len(legacy['cases'])}/{len(legacy['cases'])}** legacy font/discovery outputs, Poppler 72/144 DPI, pypdf and qpdf. `position-independent-verification.json`: **{len(positions['cases'])}/{len(positions['cases'])}** fixed-origin outputs including original reconstruction, unchanged target positions, two-generation substitutions and protected whitespace. Some sets overlap; do not add these counts as unique documents.

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

Final eight-case UI rerun: 30 text operations, median synchronous input **{metrics['medianInputMs']:.4f} ms**, max **{metrics['maxInputMs']:.4f} ms**; median standalone proposed-position calculation **{metrics['medianCalculationMs']:.4f} ms**. There were **{metrics['workerRequests']} immediate worker requests**. These are programmatic control-handler measurements, not keyboard-to-screen latency.

`document-performance.json`, five complete preview requests per case:

| Case | Median worker roundtrip, ms | Regions |
|---|---:|---:|
{previewrows}

The two-Word insertion/deletion case's last sampled worker stages were planning **{performance['cases'][0]['lastWorkerTimingsMs']['planning']:.3f} ms**, candidate mutation/generation/save **{performance['cases'][0]['lastWorkerTimingsMs']['candidateGeneration']:.3f} ms**, reopen verification **{performance['cases'][0]['lastWorkerTimingsMs']['reopenVerification']:.3f} ms**. These stage observations are not separately averaged medians. End-to-end timings include IPC and remaining overhead; performance varies with concurrent local work.

Twenty-four additional alternating insertion/deletion previews after warmup: handle growth **{performance['handleGrowth']}**, retained twelve PDFs/twelve PNGs, worker exited. Before/after memory observations are recorded in full. This is a bounded small-corpus observation, not proof of leak freedom or large-document capacity. Alignment is capped at 512 for the recalculated path; native timeout remains 30 seconds with no in-flight native cancellation.

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
'''
(H/'PHASE_4C1_TEST_RESULTS.md').write_text(text,encoding='utf-8',newline='\n')
(R/'README.md').write_text('''# PDF Editor V2 - Phase 4C.1

Windows x64 .NET 8 WPF prototype with controlled original-font character insertion/deletion in eligible positioned Word lines. Natural paragraph wrapping, multi-region sessions, document chronology, recovery and one verified atomic Save As are retained. No positioned wrapping or Phase 4C.2 work.

Run `./Launch.ps1` or `run/PdfEditorPrototype.exe`; open `run/corpus/11-word-letter.pdf` for the insertion demo. Requires .NET 8 Windows Desktop runtime. Build with `./build.ps1` (.NET SDK required). Keep App/Worker/native DLL/assets together. Python and independent PDF readers are development tools only.

Read `../PHASE_4C1_HANDOVER/PHASE_4C1_USER_TEST_GUIDE.md`. All six reports and `evidence/README.md` describe executed checks and restrictions. Drafts are never silently discarded; unsupported glyphs, unsafe spacing, horizontal overflow and failed complete verification prevent all export. Save requires a new filename and retains the original session base/history.

The visible positioned caret/selection uses proposed glyph geometry; the underlying native Calibri spacing discrepancy is recorded. Hardware input and non-100% OS display scales need manual testing. The intermittent clipboard issue remains open. Prior phases and their recovery are preserved.
''',encoding='utf-8',newline='\n')
(E/'README.md').write_text('''# Phase 4C.1 evidence index

See `../../PHASE_4C1_HANDOVER/PHASE_4C1_TEST_RESULTS.md` for executed counts, failures, timings and reproduction. Final acceptance evidence:

- `word-spacing-analysis.json`: genuine Word sources, raw encoded codes, Unicode/GID/font metrics, TJ data, measured residuals, glyph geometry and protected objects.
- `insertion-corpus.json`: hashes/provenance of development fixtures; no product merge feature or ownership hints.
- `insertion-tests.json`: 30 worker cases, 23 successful saved records, including negative overlap/extraction/overflow/graphic controls.
- `model/model-tests.json`: 17 session/history/recovery/position invariants.
- `document-tests.json`: 17 combined transaction regressions.
- `position-tests.json`: 20 active position checks, including three intentional support changes.
- `final-release-controls/`: 46 actual WPF checks, five clipboard probes, captured requests/results and screenshots. No hardware/file-picker automation.
- `selection-verified-controls/`: final eight new control checks repeated with rendering wait for selection screenshots; five successful exports included in independent checks.
- `process-recovery.json`: exact folder for two exited processes restoring insertion/deletion/natural drafts and history, followed by combined export.
- `document-independent-verification.json`: 57 complete recorded combined exports checked by MuPDF/pypdf/fontTools/qpdf/Poppler, every page at 72/144 DPI. `document-poppler/` indices follow its case order.
- `independent-verification.json`, `position-independent-verification.json`: 21 legacy discovery/font and 11 fixed-position outputs, respectively. Sets can overlap.
- `engine-tests.json`, `discovery-tests.json`, `compatibility-tests.json`: unchanged active worker contracts, alongside active position tests (83 total checks).
- `phase1-regression.log`, `phase*-regression.json`, `frozen-phase3-discovery/`, `frozen-phase4a/`, `frozen-phase4b-test_document/`, `frozen-phase4b-test_position/`: applicable preserved-worker regressions, with output redirected here. Phase 3's obsolete unknown-PDF-view-only expectation remains a documented 17/18 failure.
- `document-performance.json`: roundtrip/stage times, repeated-edit handles/memory and candidate retention.
- `prior-baseline.json`, `prior-phase-preservation.json`, `phase1-preservation.json`, `release-manifest.json`: preservation and final deliverable hashes.
- `combined-exports-contact-sheet.png`, `visual-review.json`: inspected complete-output and live-presentation checkpoints.

Development evidence remains under `development/`, `development-initial-insertion-tests.json`, `insertion-controls/` and timestamped files. Earlier failures are not final acceptance. The test report explains fixture/example refusals, changed old expectations, session-isolation test corrections, Calibri native caret failure and parser/capture corrections. Raw development outputs outside designated records are not all claimed independently certified.

Clipboard Win32 5 remains intermittent. Actual measured Windows scale was 100% / 96 DPI. There is no physical input, OS display-scale sweep, large-document or broad semantic PDF certification.
''',encoding='utf-8',newline='\n')
print('All six Phase 4C.1 handovers and README/evidence index written.')
