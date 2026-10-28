from pathlib import Path
R=Path(__file__).resolve().parents[1];H=R.parent/'PHASE_4B_HANDOVER';H.mkdir(exist_ok=True)
docs={
'IMPLEMENTATION_REPORT':'''# Phase 4B implementation report

Delivered 28 October 2026. This local Windows prototype extends Phase 4A.1 in a separate `phase4b/` directory. Earlier source, builds, fixtures and handovers are preserved; preservation hashes are in `phase4b/evidence/`. Phase 4C has not started.

## Working application

Launch `phase4b/Launch.ps1` or `phase4b/run/PdfEditorPrototype.exe`. The default two-page fictional document has three editable natural paragraphs on page one and two on page two. This release is a framework-dependent .NET 8 WPF Windows x64 build, with a separate PDF worker and the existing pinned PDFium binary. Python, ReportLab, MuPDF, pypdf, pikepdf and Poppler are development verification dependencies, not application runtime dependencies. No network service is used.

## Architecture and implementation map

- `Core/DocumentSession.cs`: source-bound working state, region snapshots, chronology, validation, bounded history and atomic recovery.
- `Core/DocumentTransaction.cs`: fresh source discovery, combined planning, one candidate save, reopen verification and protected final commit.
- `Core/PdfEngine.cs`: original discovery/eligibility and clean draft backgrounds, removing source text objects from temporary page renders.
- `App/SessionEditing.cs`: inactive draft presentation, global undo/redo commands, selection persistence, document summary, export audit and work cleanup.
- `App/EditorWindow.cs`: source/session navigation, asynchronous validation, Save As and recovery integration.
- `App/WorkerClient.cs`: isolated worker requests, existing timeout/restart and serialized access; no UI-owned native PDF handles.
- `App/SessionControlTests.cs`, `App/ProcessRecoveryTests.cs`, `Checks/`: executable tests of actual controls, separate-process recovery and session invariants.

A session stores source path and immutable SHA256, current page/page count and observed dimensions, active key, original editable regions, font/glyph strategy information, drafts, caret/selection offsets, validation messages, revision, last verified revision and global history. A region fingerprint includes source hash, page, original object references/text, font hash/style, layout geometry and explicit positioning data. Temporary extracted font-file paths are excluded. Identical-byte source copies can rebind a recovered path, but edits remain bound to the same source bytes.

Preview and export always resolve identities against the original source. They never use indices from a previous generated candidate as authority. A changed or incompatible identity retains its original snapshot and draft in the session and blocks export.

## User-visible behaviour

Multiple regions and pages retain independent text without intermediate saving or switching prompts. The active original-font editor remains in place; inactive drafts are transparent application-owned text over a source-clean render. Original graphics remain in the render. This temporary presentation is explicitly a working draft, with a small document summary showing changed areas, attention and readiness. Invalid text stays visible and editable. Zoom uses page coordinates and does not discard text.

The clean background removes all modified source text on that page plus the currently selected text, avoiding duplicate original text underneath drafts. Final files use genuine PDF text-object replacement, without white cover rectangles.

Undo/redo follows one chronological document stack and activates the affected region/page. Native RichTextBox undo is disabled. Ctrl+Z, Ctrl+Y and toolbar commands route to this stack. Source selection and programmatic restoration do not produce text-history entries.

Validation is debounced by 300 ms; persistence by 350 ms. Input performs local text/layout work, then the worker validates the complete modified set asynchronously. Responses must match the session instance, source hash and revision. An old response cannot mark an unrelated session verified even when its revision counter matches. Save captures a complete request; a successfully saved older snapshot does not mark subsequent working text saved.

## Export and retained working base

Every modified area participates, including blocked drafts. The worker rejects an unsafe set rather than silently saving its valid subset. It loads one source, plans all changes, removes the union of original objects, applies each region's existing strategy, generates changed page content and saves one temporary PDF. Reopen checks cover every changed region, untouched objects/pages, fonts and outside-area pixels. Only then is a checksummed file staged beside the selected new destination and moved without overwrite. Source and existing destinations are protected. Temporary candidate cleanup is advisory and cannot turn a committed save into a reported failure.

Save As retains the original source binding, working text and history. It does not reset the session to the exported file or mark drafts clean. Reopen an exported PDF to start a newly discovered session; second-generation tests exercise this path. Export audit JSON records the captured changes and verification result.

## Boundaries and review

Natural wrapping retains previous region/font restrictions. Position-aware text retains same-count, equal-or-narrower substitutions and original glyph positions; insertion, deletion and reflow remain blocked. Mixed edits preserve each strategy separately. See the validation report for tolerances and the issues report for remaining limits. Review the test report and manual guide before wider use. This remains a constrained prototype, without installer or broad PDF compatibility certification.
''',
'HISTORY_AND_RECOVERY':'''# Phase 4B history and recovery

## One chronology

Each text-change event records region key, complete before/after text and caret offsets. An A, B, C edit sequence undoes C, B, A and redoes A, B, C, even when another region is active. Navigation opens the affected source page and restores its draft and caret. Ordinary selection changes only update caret/selection state. Programmatic restoration suppresses text recording. New input after undo removes the redo tail. Native RichTextBox undo is disabled to avoid contradictory stacks; toolbar and routed undo/redo commands share document history.

There is no time-based word grouping: one native text-change event is one history unit, and an explicit control BeginChange/EndChange can group an operation. This can produce finer undo steps than a word processor. History is bounded to 2,000 entries and 2,000,000 UTF-16 characters across before/after strings. Old entries are evicted first. Full current draft text remains intact when history is evicted, with an eviction count recorded. Restoring history never reconstructs current text by truncating it.

## Recovery storage

Normal sessions are stored under `%LocalAppData%/PdfEditorPrototype/phase4b/sessions/<source-SHA256>.session.json`. Schema version 1 includes source identity, page observations, region original snapshots and fingerprints, strategies/font/glyph information, working text, caret/selection, revision, validation and history including redo tail. This is private local prototype data, not data embedded into the PDF.

Writes serialize to a temporary file, flush it, then replace the session file atomically. Switching documents and clean closure persist immediately; text changes use a 350 ms debounce. A power loss before a scheduled write can lose that short interval. Recovery files are limited to 16,000,000 bytes. Oversize serialization leaves the previous recovery file and complete in-memory draft intact and reports the failure; larger work is not guaranteed recoverable until reduced or exported.

Restore checks schema, matching source hash, region source identity, cursor/entry bounds, history character budget and before/after consistency by traversing history in both directions. Verified revision is reset. Fresh source discovery must confirm restored regions before they can be trusted for export. Compatible observations refresh transient font paths. Incompatible identities retain the original snapshot and draft as blocked; they are never rebased onto guessed object indices.

Malformed/partial/contradictory files are rejected; the UI preserves invalid data with an `.invalid-<GUID>` name. Changed source bytes get a separate hash-keyed session when explicitly reopened, leaving old recovery untouched. A changed original cannot silently receive stale drafts. A same-byte copy is eligible for the same source-bound recovery after fresh checks. Older phases' single-region recovery files are not migrated or altered.

## Executed evidence

`evidence/model/model-tests.json`: 11 passing invariants, including chronology, redo branching, no selection entries, session/revision/hash response rejection, both history limits, atomic recovery with redo, changed-source refusal, malformed and corrupt history retention, oversize recovery and identity mismatch retention.

`evidence/process-recovery.json`: three edited regions across two pages persisted in one app process; that process exited. A different PID reopened the original with an isolated shared recovery store, restored all three drafts, undid/redid and saved all three in one output. The source hash remained unchanged. This is separate-process recovery, not merely a same-window serialization test. `final-release-controls/session-control-tests.json` additionally tests control restoration and explicitly changed-source reopening.

## Limitations

Recovery is not multi-process locked; concurrent instances editing the same source have no reconciliation and a later writer may replace earlier recovery. Recovery JSON contains draft text and is not encrypted. Abrupt termination can leave temporary work directories. Identity changes across a future analyser version may block initial restoration before a region is displayed: unresolved text remains in the preserved recovery file for technical inspection, with no dedicated orphan-draft UI. The normal same-build path is tested. There is no automatic merge or migration of incompatible recovery.
''',
'MULTI_REGION_VALIDATION':'''# Phase 4B multi-region validation

## Source-bound transaction

The request carries source SHA256, document revision and every modified region's page, ID, source fingerprint and complete draft. There must be between 1 and 128 changes. Duplicate page/region ownership, stale source, missing/ineligible regions, identity mismatch or shared target object pointers fail before mutation. Fresh discovery and original font handles come from a single loaded source. Source fingerprints are checked again before commit.

All plans are computed before replacing objects. Same-page proposed line rectangles are compared with a 0.5 point pad. The worker compares planned geometry against the union of untouched neighbours, images/graphics and page-safe bounds. It does not treat another changed source object as an untouched obstacle; it uses that region's proposed replacement geometry instead. Final reopened ink bounds are checked again against other changed regions and protected objects. Drafts survive any rejection, and affected-region warnings are returned where the conflict can be attributed.

The collision fixture deliberately places a second tiny period below the first region. Each replacement alone saves and verifies. The first becomes three lines, the second becomes a normal line; together their proposed line extents overlap by one point. The combined request fails with both region keys. This proves a conflict beyond two isolated successful exports. No unrelated text is moved and no font is shrunk.

## Strategy fidelity

Natural paragraphs retain existing eligible fonts, mappings, advances, wrapping and safe expansion boundaries. Unsupported glyphs and unsafe geometry block the whole request. Position-aware Word runs retain explicit original glyph origins, ASCII standalone embedded TrueType constraints, horizontal single-object eligibility and the pinned PDFium position setter. They permit only same-count equal-or-narrower substitutions under the established checks. A mixed request does not relax those rules. The synthetic mixed fixture combines unchanged genuine Word text streams with a separately generated eligible natural region for testing; document merging is not an application feature.

The PDFium DLL remains version 156.0.8076.0, SHA256 `bede3932ce96a2e1ed9a7e6cae71aec8914efd2907d37ab44b1b81f9c8a6d04e`.

All original target pointers are collected before replacement. The union is removed, replacement runs are created using each original font and strategy, and changed pages generate content once. One candidate PDF is saved for the entire transaction. Deletion of a supported natural paragraph is represented by removal with no replacement run; a concurrent valid edit still participates.

## Complete candidate verification

The worker saves and reopens the candidate and source. It verifies page count, dimensions, annotation counts, document info metadata, exact intended replacement run text/count, original font programs/style and glyph outlines, font reconstruction and safe bounds. Untouched object types/text/font/style/bounds and glyph Unicode/origins/bounds are compared. Unmodified pages are pixel-equal at 72 DPI. Changed pages have zero differing pixels outside the union of authorised areas at 144 DPI with channel-difference threshold 8. The current page preview PNG is not the scope of verification: all affected pages and all unmodified pages are checked.

Retained tolerances: untouched glyph/object geometry 0.01 pt; positioned origins and unchanged positioned glyph bounds 0.01 pt; natural local advance 0.05 pt, cumulative position 1 pt and baseline 0.15 pt. Changed positioned glyph ink must not overlap other letters. These limits were not relaxed for combined editing. Nonpainting zero-extent Word spacing objects retain their narrow position-strategy exception and survive as separate original objects.

Independent development verification uses MuPDF extraction and glyph geometry, pypdf font programs/used encoding/width/ToUnicode/CIDToGID rules and protected raw whitespace bytes, pikepdf/qpdf syntax checks and Poppler full-page renders at 72 and 144 DPI. Every page of each recorded successful combined export is checked, including UI, separate-process recovery and second-generation outputs. Wrapped extraction is whitespace-normalized where independent readers differ in trailing-space representation, while intended PDF run text is checked exactly by the worker. The independent parser now assigns trailing target wrap spaces to their target; no geometry or pixel threshold was weakened.

Used font programs and mapping rules remain stable. PDFium can prune unused font entries and create duplicate resource aliases, so whole unused resource dictionaries are not claimed byte-identical. All combined exports must contain all requested edits; no valid-only partial export path exists.

## Commit and failure behaviour

Original/existing destinations are rejected. A validated candidate is copied to a unique file beside the destination, checksum and source are rechecked, then File.Move with overwrite disabled commits it. Failed final moves clean their stage and preserve drafts. Candidate retention keeps twelve PDFs and twelve PNGs per work directory when cleanup is possible. Advisory cleanup errors cannot change a committed save to a failed result. Output to a non-existing filename is atomic within the destination filesystem; power-loss durability and exotic network filesystem semantics are not certified.
''',
'OPEN_ISSUES':'''# Phase 4B open issues and limits

## User interaction

Historical clipboard error Win32 5 remains intermittent. Earlier runs in this phase failed the clipboard control case; later probes and the designated release run passed. No clipboard fix is claimed. Prior evidence sometimes reported a valid owner with holder PID zero/unknown; this does not establish the cause. Draft/history safeguards still apply when clipboard operations fail.

WPF test code exercises the actual controls, routed text composition, editing commands, shared region hit-testing and export paths. It does not send hardware mouse/keyboard input or manually operate Windows file pickers. Physical clicking, typing, IME, keyboard shortcuts and dialogs remain manual checks in the guide. The Word title's WPF caret has the inherited small sub-point approximation; exact PDF glyph position checks are separate. No new physical comfort assessment is claimed.

Inactive invalid drafts are application presentation, not certified PDF appearance. Expansion is not automatic content movement. A blocked area does not stop editing another area but prevents a complete Save As until corrected. Recovery identity mismatch can require inspection of preserved JSON; there is no orphan-draft editor. Save retains drafts against the original, so reopening an output is required to start a new source base.

## PDF scope

Eligibility remains deliberately narrow. No general Word reflow, positioned insertion/deletion, font substitution, subset rebuilding, OCR, forms, signatures, annotation editing, merging/splitting or cloud features were added. Rotated/clipped/complex/unsupported font runs remain gated. Broad mixed-document coverage is not established by the small fixture corpus. Tags, MCID/structure trees, accessibility, XMP, PDF/A conformance, complete annotation dictionaries and semantic reading order are not certified. Replacements can be appended in a different content-stream order despite identical visual geometry. Existing protected-document gates remain necessary.

Font aliases may accumulate, and unused dictionary entries can be pruned by PDFium; used embedded programs and mappings are verified. Existing documents without safely reusable mappings remain ineligible.

## Performance, persistence and packaging

History is bounded to 2,000 entries / 2,000,000 stored UTF-16 characters. Current draft text is never truncated. Recovery max is 16 MB; a larger draft remains in memory with previous on-disk recovery retained. Up to 128 modified regions per transaction are supported. Per-analysis cache and candidate retention are bounded (eight analyses; twelve candidate PDFs and twelve PNGs), but extracted fonts, observed region snapshots and total session memory have no comprehensive hard cap.

Clean-close temporary cleanup is best effort. Font locks or crashes can leave orphan work directories; no global crash-orphan collector is included. Separate instances can race on one recovery file, with no merge/lock. Native operations have the existing 30-second worker timeout, without in-flight native cancellation. Small-corpus performance is measured; large documents and prolonged production workloads are unqualified.

The delivered executable needs the .NET 8 Windows Desktop runtime on Windows x64. A self-contained switch exists in build.ps1 but that variant and clean-machine installation were not certified. No installer, deployment or production support claim is made. Independent reader tools are development-only and are not invoked for every normal user save; runtime save verification uses PDFium plus structural/glyph/pixel checks.

## Development failures retained

An early layer insertion before page-child construction caused a constructor exception; placement was corrected. Mixed source encodings produced arrow mojibake; new source files were normalized to UTF-8. An early destination-protection test incorrectly expected a pre-existing protected file not to exist; it now asserts byte preservation. An independent parser initially misclassified trailing target spaces as neighbours; target classification was corrected without loosening fidelity limits.

The unchanged old UI contract suite had 14/26 failures, including obsolete per-region undo, single-draft recovery, dirty-switch and bitmap assumptions plus intermittent clipboard behaviour. Raw files remain in `old-control-contracts/`. Active copies were adapted to the required document model while retaining substantive control, geometry and fidelity assertions. Intermediate active runs had 25/26 and 37/38 passes because of clipboard error 5; those are retained rather than erased. Frozen Phase 2 assertions against Phase 3 retain one known obsolete manifestless-view-only expectation (17/18). Consult the test report for the designated final evidence.

Stop at Phase 4B. Phase 4C requires review.
''',
'USER_TEST_GUIDE':'''# Phase 4B Windows user test guide

## Start

Run `phase4b/Launch.ps1` from PowerShell or open `phase4b/run/PdfEditorPrototype.exe` in Explorer. This build requires .NET 8 Windows Desktop runtime, Windows x64. Build from source with `./phase4b/build.ps1` if needed. Keep all runtime files together. Work with copies of your PDFs and choose new output filenames.

The default is `run/document-corpus/multi-natural.pdf`, a two-page fictional test document. The interface remains the spacious inline editor with Open, page, zoom, undo/redo and Save As controls, plus a small document status line. Draft text is application presentation; only a successful verified Save As produces an exported PDF.

## A / B / C / H: multiple regions, chronology and pages

1. Click the first paragraph and change it to `First changed working paragraph.`
2. Click the second and enter `Second changed working paragraph.` Return to the first: its latest text should remain, and the second draft should stay visible.
3. Change the third paragraph. Undo should reverse the third edit first, then the second, then the first. Redo should restore the same chronology. Multiple native text-change events can require multiple undo presses.
4. After undoing, type a new edit: the old redo branch should disappear. Selection and switching alone should not create text-history steps.
5. Move to page two, edit an eligible paragraph, return to page one and change zoom at each offered setting. Drafts should stay attached to their page positions.
6. Save As to a new name. All edited pages should appear in one PDF opened in an independent viewer. Original source bytes should remain unchanged. Drafts/history remain in the original session after export.

For wrapping, lengthen each of two natural paragraphs within its generous blank space. The tool must either verify both together or retain both with a clear warning. It must not move unrelated content.

## D / E: Word and mixed strategies

Open `run/corpus/11-word-letter.pdf`. Change the title `Phase 3 Office letter` to `Phace 3 Office letter` (same count, narrower substitution). In the longer supported Word paragraph replace `should` with `chould`. Save both at once. Unchanged letters should remain in their original positions. Inserting a character must be blocked for export, while retaining the draft.

Open `run/document-corpus/mixed.pdf`. Make the same title substitution and change the lower natural paragraph to `Neutral paragraph retains its original font.` Save As. Both strategies must participate in the same output; natural wrapping must not unlock Word insertion.

## F / G: blocked drafts stay accessible

Open `run/document-corpus/collision.pdf`. Change the first area to three lines, each `alpha area.`. Click the small period below and replace it with `alpha area.`. Each proposed change has a successful isolated automated control, but their combined geometry overlaps. Combined export must be rejected, both drafts retained, and no partial PDF created. Correct one draft and retry.

In the ordinary multi-natural fixture, add a snowman character to area A and make a valid ASCII edit in B. Both must remain accessible when switching. Save must not silently export B alone. Remove the unsupported character and validate/save again.

## I / J / K: recovery, failure and next generation

Edit several regions on both pages, close the window normally, reopen the same original PDF and confirm compatible drafts and undo/redo return. Recovery is debounced; allow a moment before deliberately terminating a process. Normal files live in `%LocalAppData%/PdfEditorPrototype/phase4b/sessions/`. Do not delete them while evaluating recovery. A modified external source should open as a new source session, with previous hash-keyed recovery preserved and no stale edits applied.

Try saving to the original or an existing filename: both are protected. Test a denied/non-writable destination if available. Failure must keep drafts and leave no partial destination. Ordinary region switching must not show a discard/save modal.

Open a successfully exported PDF, rediscover supported text and edit again to a second new filename. This starts a fresh source-bound session. There is no automatic rebasing of the previous session.

## Manual checks still required

Physically test mouse placement, selection drag, typing, Ctrl+Z/Ctrl+Y, copy/cut/paste, file pickers and zoom on your display scale. Clipboard error 5 remains a known intermittent issue; record the error and whether drafts survive, rather than treating a later successful paste as proof of a fix. Automated WPF checks do not establish physical input behaviour. Unsupported document areas should explain that they cannot be edited safely.

Evidence and technical limits are in the accompanying five reports and `phase4b/evidence/README.md`. Phase 4C has not been started.
'''
}
for name,body in docs.items():(H/('PHASE_4B_'+name+'.md')).write_text(body,encoding='utf-8',newline='\n')
(R/'README.md').write_text('''# PDF Editor V2 — Phase 4B

Local Windows x64 WPF prototype: multiple source-bound text drafts, chronological document undo/redo, recovery and one verified atomic Save As. Natural and narrowly constrained position-aware editing retain separate fidelity rules.

Run `./Launch.ps1` or `run/PdfEditorPrototype.exe`. Requires .NET 8 Windows Desktop runtime. The default fictional two-page document supports multiple natural edits. Build with `./build.ps1` (.NET SDK required); the delivered framework-dependent build is under `run/`.

Read `../PHASE_4B_HANDOVER/PHASE_4B_USER_TEST_GUIDE.md` first. Architecture, tests, recovery, validation and limitations are in that handover directory. Approved evidence is indexed in `evidence/README.md`. Previous phases are preserved. No installer, cloud dependency or Phase 4C work is included.

Save As requires a new destination. It retains the original source binding and working drafts/history. Reopen an output PDF for a fresh session. Unsupported glyphs, positional insertion and combined collisions block the whole export without discarding drafts. Clipboard error 5 remains intermittent; physical input remains a manual evaluation item.
''',encoding='utf-8',newline='\n')
print('Wrote five technical/manual reports and README; test report is generated after final evidence.')

import json,hashlib
E=R/'evidence';D=E/'final-release-controls'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
controls=[('Original inline controls','control-tests'),('Discovery controls','discovery-control-tests'),('Font controls','font-control-tests'),('Position controls','position-control-tests'),('Document session controls','session-control-tests')]
for _,name in controls:
 d=read(D/(name+'.json'));assert d['failures']==0
assert all(x['readWriteReadMatches'] for x in read(D/'clipboard-probe.json'))
ind=read(E/'document-independent-verification.json');assert ind['success'] and len(ind['cases'])==21
model=read(E/'model/model-tests.json');assert model['failures']==0
perf=read(E/'document-performance.json');burst=next(x['detail'] for x in read(D/'session-control-tests.json')['results'] if x['name'].startswith('typing-burst'))
table='\n'.join('| '+label+' | '+str(read(D/(name+'.json'))['tests'])+'/'+str(read(D/(name+'.json'))['tests'])+' | `final-release-controls/'+name+'.json` |' for label,name in controls)
maxshift=max(p['maxUntouchedGlyphShiftPt'] for c in ind['cases'] for p in c['pages'])
position=max(p['maxPositionedTargetOriginShiftPt'] for c in ind['cases'] for p in c['pages'])
body=f'''# Phase 4B executed test results

Executed locally on Windows x64 with .NET 8 WPF and pinned PDFium. Final framework-dependent App and Worker publish succeeded on 28 October 2026. Code and binary hashes are in `evidence/release-manifest.json`. No fidelity threshold was relaxed. All paths below are relative to `phase4b/evidence/` unless stated otherwise. Earlier failures are retained and described below.

## Designated release checks

| Actual WPF control suite | Result | Evidence |
|---|---:|---|
{table}

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

`document-independent-verification.json`: **21/21 PDFs**, comprising ten worker exports, ten final release control exports and one separate-process recovery export. Every page was checked at 72 and 144 DPI by Poppler; MuPDF, pypdf and pikepdf/qpdf also reopen/check the documents. Checks cover all replacements, removal of source target objects, font programs and used mapping/width rules, untouched glyphs, protected whitespace bytes, dimensions, page counts, metadata and source SHA256. Zero unexpected changed pixels were accepted outside the authorised union (channel threshold 8). Maximum observed untouched glyph shift: **{maxshift:.8g} pt**; maximum positioned target origin shift: **{position:.8g} pt**, within 0.01 pt. Independent whitespace-normalization is used only for extracted wrap separators; exact intended run text is separately verified by the worker.

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

The final actual-control 30-operation input burst measured median synchronous handler **{burst['medianHandlerMs']:.4f} ms**, max **{burst['maxHandlerMs']:.4f} ms**, with **{burst['workerRequestsDuringBurst']} immediate worker requests**. Validation is debounced/asynchronous. The timing covers control insertion and its synchronous change handler, not keyboard-to-screen latency.

Twenty-four extra four-region previews after warmup showed handle growth **{perf['handleGrowth']}**, retained twelve candidate PDFs/twelve PNGs, and worker exit. History entry/character and recovery size limits have executable tests. No total-memory or crash-orphan cleanup certification is implied.

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
'''
(H/'PHASE_4B_TEST_RESULTS.md').write_text(body,encoding='utf-8',newline='\n')
(E/'README.md').write_text('''# Phase 4B evidence index

The designated final build control run is **final-release-controls/**: 38/38 checks and five clipboard probes. Read `../.. /PHASE_4B_HANDOVER/PHASE_4B_TEST_RESULTS.md` (remove the space in this prose path) for full results and limitations. Earlier failed runs remain for audit, not as the final acceptance run.

## Final evidence

- `document-tests.json`: 17 combined worker checks and ten complete export records.
- `model/model-tests.json`: 11 session/history/recovery invariants.
- `process-recovery.json`: two distinct exited app processes, three recovered drafts on two pages and one export; references exact timestamped folder.
- `final-release-controls/`: original, discovery, font, positioned and session control JSON, export audit records, screenshots and clipboard probes. Native WPF controls; no hardware/file-picker automation.
- `document-independent-verification.json`: 21 combined exports (ten worker, ten final UI, one recovery), every page with independent readers and Poppler 72/144 DPI.
- `document-poppler/`: final combined independent page rasters; indices follow the case order in the JSON, not file-name sorting.
- `combined-exports-contact-sheet.png`, `visual-review.json`: reviewed visual checkpoints.
- `independent-verification.json`, `poppler/`: 21 additional legacy discovery/font outputs.
- `engine-tests.json`, `discovery-tests.json`, `compatibility-tests.json`, `position-tests.json`: active worker regressions, 83/83.
- `phase1-regression.log`, `phase*-regression.json/.log`, `frozen-phase3-discovery/tests.json`, `frozen-phase4a/tests.json`: applicable frozen regressions. The original Phase 2 unknown-PDF policy test against Phase 3 remains a documented 17/18 failure.
- `document-performance.json`: measured preview time, handle observations and candidate bounds.
- `prior-baseline.json`, `prior-phase-preservation.json`, `phase1-preservation.json`: before/after preservation evidence.
- `release-manifest.json`: final implementation, tools, runtime, fixtures and six handover file hashes.

## Retained development evidence

`old-control-contracts/` contains 14/26 historical UI-contract failures. `active-controls-1/` and `release-controls/` contain intermittent clipboard failures (25/26 and 37/38 respectively). `final-controls/` and `verified-controls/` are superseded passing checkpoints. Other `session-controls*` folders are intermediate runs. `development/initial-document-tests.json` retains an initial test-helper failure. Timestamped exports and recovery stores remain; only the records referenced by designated JSON are the approved final verification set. Do not interpret every development output as an independently certified deliverable.

No clipboard fix or physical input verification is claimed. Preservation excludes generated bin/obj/test-work caches; prior source/runtime/evidence/handover content is checked. See the issues report for semantic PDF and packaging limits.
'''.replace('`../.. /','`../../').replace(' (remove the space in this prose path)',''),encoding='utf-8',newline='\n')
print('Wrote final test report and evidence index; all six handovers present.')
