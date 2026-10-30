"""Phase 5.2.2 handovers; current evidence is required before generation."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];E=R/'evidence';H=R.parent/'PHASE_5_2_2_HANDOVER';H.mkdir(exist_ok=True)
def load(n):return json.loads((E/n).read_text(encoding='utf-8'))
def write(n,s):(H/('PHASE_5_2_2_'+n+'.md')).write_text(s.strip()+'\n',encoding='utf-8',newline='\n')
m=load('multi-region-release.json');p=load('presentation-release.json');o=load('original-controls.json');a=load('paragraph-controls.json');ind=load('wrap-independent-verification.json');st=load('paragraph-structure-verification.json');pos=load('position-independent-verification.json');leg=load('independent-verification.json');fr=load('frozen-c2-readers/wrap-independent-verification.json')
assert m['failures']==p['result']['failures']==o['failures']==a['failures']==0
assert all(d['success'] for d in [ind,st,pos,leg,fr])
write('ROOT_CAUSE_ANALYSIS',r'''# Phase 5.2.2 root-cause analysis

Starting release: 22228b4bf414912d803fe8ccc1f52b6a9fbe0df6. Evidence paths below are relative to phase5_2_2/evidence. Tests use genuine Word-cafe-paragraph.pdf and actual WPF controls.

## A: confirmed activation-policy mismatch

FindRegionAt recognised expanded retained-preview bounds; SelectRegionAt separately required original/proposed PDF bounds. A 769-character retained draft exceeds the existing 512-character recalculation limit and has no proposed line boxes. Baseline click at page (503.296,184.808) resolved lower p0-o4, navigated to it, but left active=false. Original observed bounds: (73.200,139.808,259.716,11.736). Retained bounds: (72.024,139.808,451.272,682.112). The same mismatch affected upper p0-original-0 at (503.296,118.928). Original-source clicks worked. See baseline-multi-1793356252749531400/multi-region-tests.json.

Actual baseline InputHitTest was Image. inactiveDrafts was non-hit-testable, child index 1; editor index 3, ZIndex 0. Overlay interception is ruled out for this reproduction, not assumed for every unrecorded user action. Logs include page points, mapped screen points after activation, hit target, before/after active identities, original/retained bounds, stacking and focus. Original user mouse coordinates/text were unavailable.

Correction: reuse the resolved source-bound target for activation. Original observed source bounds take priority; expanded-preview ties use stable source order. Dedicated adversary moves the interactive upper WPF editor over the lower source without changing PDF geometry: InputHitTest enters that editor but the Window preview route activates the lower source. A Text area selector exposes every editable source identity when presentation previews overlap.

## B: genuine current restrictions and historical classification coupling

Exact-original shortening already cleared amber in the baseline, so a universal exact-restoration defect was not reproduced. Short length is not proof of validity. In this Word subset U+0075 (ordinary lowercase u) is glyph 86, FontPresentEncodingUnavailable / PDF_ENCODING_ROUNDTRIP_FAILED, advance -1. The cmap entry exists, but independent fontTools inspection shows zero advance and zero contours for u in both embedded subsets. The baseline field named outline only checked cmap membership and was not a true outline measurement; this was corrected during visual review. The verified PDF encoding round trip fails. This is not Unicode corruption or a newline; a short u correctly remains rejected. Its native subset glyph was also invisible, independently reproduced using Windows input. Rejected drafts now use a clearly labelled Segoe UI review font, identically active/inactive, so such characters remain visible and selectable. Current valid/original text restores the embedded original font. The PDF engine never receives a substitute font. See subset-native-glyph-inspection.json and final WPF glyph-geometry evidence.

The old DraftReason combined character failure with “or hard line break”. Actual LF/CR is a separate restriction. Tests inspect current Unicode sequences and mapping for u, CRLF, LF, multiple paragraphs, trailing breaks, tab, NBSP, an unmapped symbol and mapped-only text. Existing WPF CRLF/CR-to-LF canonicalisation remains explicit; no breaks or characters are dropped to approve export. The actual original clipboard payload was not established.

The old exception path marked every modified region Blocked with one combined failure message. A fitting neighbour could inherit an unrelated/incomplete failure; Validation/Message persisted across registration/recovery without current exact-text evidence. Current App evidence is bound to session instance, source hash, source identity, exact text and document revision. Local current restrictions remain rejected. Attributable worker rejections remain rejected. Unknown combined failure is incomplete validation, not an invented geometry rejection for every region. Exact original is unchanged; a different safe correction is pending/stale until whole-document verification succeeds. Changed text cannot reuse a historical failure reason. Save failure clears approval, retains text and retries without implying geometry corruption.

## Other hypotheses

Existing owner/revision/hash/navigation guards correctly discard delayed responses; no pre-existing response-order bug was demonstrated. Held delivery tests cover newer edits, region switches and inherited document switches. Zoom/scroll/stacking were tested; no PDF ownership, safe bottom, font size, neighbouring content or geometry threshold changed. There is no demonstrated invalid successful export in the user's report. Core files are byte-identical to 5.2.1. A Windows input spot-check reproduced both retained drafts, clicked the lower expanded preview beyond its original bounds, entered visible rejected u, then corrected the lower to safely fitting text. UIA reported an anonymous readonly document as focused, but native Keyboard.FocusedElement/editor.IsKeyboardFocusWithin, visible Ctrl+A selection and actual input delivery confirmed the owned editor had keyboard focus. No additional native focus-loss root cause is claimed. Inactive preview RichTextBox/FlowDocument controls are explicitly non-focusable and excluded from tab stops as defensive isolation; dedicated activation assertions now require actual keyboard focus. See computer-use-review.json.
''')
write('IMPLEMENTATION_REPORT',r'''# Phase 5.2.2 implementation report

Isolated corrective release under phase5_2_2. Earlier accepted releases are preserved. Final commit SHA is reported in the completion message and `git log -1`; the source checkpoint was explicitly labelled incomplete. No Phase 5.3 or Repository Maintenance R1.

## Implementation

- App/EditorWindow.cs uses the source-bound resolved hit target for activation, including bounded retained surfaces. Blank clicks do not snap to unrelated text. Existing async guards remain. Audits include current per-region presentation state.
- App/SessionEditing.cs prioritises original observed identities and deterministically resolves expanded surfaces. Only current attributable worker rejection affects a fitting region. Global summary and Save As require complete current-session verification.
- App/PresentationState.cs implements unchanged, pending, verified, rejected and stale states with session/source/identity/exact-text/revision evidence. Text area offers explicit access to overlapping regions. Caret and selection are snapshotted before activation/focus events can overwrite them; selecting the current inactive area also activates it.
- App/DraftPresentation.cs derives amber from current restrictions/rejection, rather than historical Blocked alone. Bounded native scrollable drafts use an explicitly labelled Segoe UI review font to keep unsupported subset characters visible. Valid/original presentation restores the embedded original family; no PDF mapping/font rule changes. Diagnostics distinguish current hard breaks and scalar/mapping failures.
- Dedicated multi-region/recovery WPF tests exercise hit routing, overlap, current characters, delayed responses, global history, new-process recovery and corrected save/reopen/re-edit. Diagnostic point override exists only during tests and is null for normal input.

PDF engine Core source is byte-identical to 5.2.1. Font identity/mapping, source ownership, safe envelopes, row/512-character limits, protected whitespace/collision checks, recovery schema, atomic transactions, exact text extraction and reopened candidate verification are unchanged. Presentation bounds do not confer extra PDF ownership. A pending positioned preview is a proposal; focus never grants approval.

## Delivery and preservation

run/PdfEditorPrototype.exe, PdfWorker.exe, managed assemblies/configuration, pinned pdfium.dll, assets and fixture folders form the runnable Windows x64 build. Requires .NET 8 Windows Desktop runtime (framework-dependent). `./phase5_2_2/build.ps1` rebuilds it. Optional existing `-Portable` publishes self-contained; that is not the tested shipping configuration. No new native dependency; Segoe UI is the Windows UI review font only. No PDF font substitution. Native SHA256: bede3932ce96a2e1ed9a7e6cae71aec8914efd2907d37ab44b1b81f9c8a6d04e.

Starting preservation baseline covers 13,886 tracked paths. START_HERE.md is the sole intentional previous-path update. Phase 1's separate 353-file manifest is checked too. The user's untracked manual-test PDF under phase5_1 remains untouched, excluded from new phase copies and staging. See prior-phase-preservation.json, phase1-preservation.json and release-manifest.json. All final successes have portable source/destination hashes in portable-pdf-index.json.
''')
write('TEST_RESULTS',f'''# Phase 5.2.2 test results

Windows tests use the supplied shipping build. No engine change was made to pass UI tests.

| Suite | Result |
|---|---|
| Dedicated multi-region WPF including separate recovery process | {m['tests']}/{m['tests']} passing |
| Inherited 5.2.1 presentation WPF | {p['result']['tests']}/{p['result']['tests']} passing |
| Marked paragraph fresh-process WPF | {a['tests']}/{a['tests']} passing in six processes |
| Original paragraph fresh-process WPF | {o['tests']}/{o['tests']} passing in five processes |
| Current worker engine/discovery/compatibility/position/insertion/document/wrap | 18+22+23+20+30+17+21 = 151 passing |
| Paragraph worker round trips | 37/37 passing |
| Original paragraph workers | 31/31 passing |
| Session models | 35/35 passing |
| Inherited full WPF controls | 57/57 passing (clipboard issue still open historically) |
| Combined successful PDFs, independent readers | {len(ind['cases'])} passing |
| Paragraph structure | {len(st['cases'])} candidates, {sum(len(c['groups']) for c in st['cases'])} groups passing |
| Standalone position readers | {len(pos['cases'])} passing |
| Legacy independent readers | {len(leg['cases'])} passing |
| Frozen C2 independent readers | {len(fr['cases'])} passing |

See consolidated-test-results.json and controls-shipping/*.json for exact inherited 57-check WPF/clipboard results. Historical intermittent clipboard Win32 5 is not declared resolved if a run passes. Frozen sources/binaries are executed with outputs redirected into this phase. Frozen Phase 3 engine retains its historical expectation mismatch (17/18); Phase 3 discovery 22/22 passes. Other historical exact counts are retained in phase*-regression / frozen-* reports.

Dedicated coverage (actual editor keyboard-focus assertions included): both invalid, each mixed valid/invalid combination, repeated original/expanded clicks, interactive overlap/source priority, preview overlap/source selector, selection restoration, exact-original and different-safe shortening, stale verification, actual u/CRLF/LF/multiple/trailing paragraphs/tab/NBSP/unmapped symbol/mapped-only sequences, held old responses, document history, four zooms, rejected combined export, incomplete delivery, separate-process recovery, corrected combined save/reopen/re-edit. Source hashes are checked across refusal/success.

Baseline two cases are diagnostics that demonstrate active=true/false outcomes, not passing acceptance tests. First development matrix: 28 checks, 3 failures retained. Snapshotting selection fixed an implementation bug; two test assumptions were corrected (same previously verified text can legitimately be stale; two edited regions produce two marked groups). Intermediate and final corrected runs remain separately inspectable. Earlier inherited font-control results expected an obsolete generic sentence; the shipping assertion checks current U+005A mapping feedback and exact WPF text, retaining typing/history/recovery/export checks.

## Reproduction

Build `./phase5_2_2/build.ps1`. Run `.venv/Scripts/python.exe phase5_2_2/tools/<name>.py` for each of: test_engine, test_discovery, test_compatibility, test_position, test_insertion, test_document, test_wrap, test_roundtrip, test_original; then multi_region_process, presentation_process, paragraph_process, original_process. Run UI suites sequentially to avoid focus interference. They create new timestamped evidence folders. Full inherited flags are recorded in evidence/README.md.

Models: `dotnet run --project phase5_2_2/Checks/Checks.csproj -c Release -- phase5_2_2/evidence/model phase4c1/evidence/word-spacing-analysis.json phase5_2/evidence/development-generations.json phase5_2/evidence/original-source-observations.json`.

Independent checks: tools/verify_wrap.py, verify_paragraph_structure.py, verify_positions.py, verify_independent.py, verify_frozen_c2.py, archive_verified.py and audit_release.py, using the same Python command. These use Poppler renders, pypdf, MuPDF, pikepdf and fontTools; no reader result replaces actual WPF visual review. Frozen commands: frozen_phase4a/b/c1/c2.py, run_regressions.py. Preserve recorded absolute diagnostic paths and portable-pdf-index.json rather than moving evidence folders.
''')
write('VISUAL_AND_INTERACTION_REVIEW',r'''# Phase 5.2.2 visual and interaction review

Actual WPF RenderTargetBitmap PNGs and JSON states remain beside baseline-multi-* and the folders referenced by multi-region-release.json and presentation-release.json. visual-qa contact sheets only crop/scale these genuine captures; full-resolution originals remain available. They are not mock-ups.

Review two-invalid-upper-active / two-invalid-return, lower-exact-original, shortened-pending / shortened-verified, invalid-upper-valid-lower / valid-upper-invalid-lower, source-picker-lower-restored, both-retained-zoom-0..3, both-corrected-verified and reopened-reedited-verified. The two explicit adversaries are labelled: interactive editor placed over another source and preview placed over another preview. Those positions are test-only; no PDF geometry changes.

Observed: both drafts stay bounded and internally scrollable; Text area exposes both original identities; selection restoration remains visible; safe correction returns to positioned ink; exact-original restoration removes amber; a safe neighbour is not amber solely because another draft is rejected. Save As remains disabled for rejected, pending, stale or incomplete combined validation. Protected graphic/paragraph states and inherited valid/invalid active/inactive captures are preserved by the 27-case presentation suite.

Hit logs record InputHitTest targets, page points and screen mapping, source/retained bounds, layer index/ZIndex, focus and selected identity. The programmatic harness raises actual WPF preview/bubble events with an explicit diagnostic page-point override. It is not physical mouse injection. Any separate SendInput computer-use observations are identified in computer-use-review.json; those are automated Windows actions, not human manual acceptance or OS/DPI/accessibility certification. The user must still repeat the guide on their normal setup.
''')
write('OPEN_ISSUES',r'''# Phase 5.2.2 open issues

- Manual acceptance remains required: repeat the original two-region sequence, original/expanded clicks, Text area access, safe shortening and keyboard/caret/selection operations on the user's actual Windows setup. Automated WPF and any SendInput review are labelled separately.
- Historical intermittent clipboard Win32 5 is not claimed fixed. Actual platform clipboard tests are separate from deterministic shared-paste tests; inspect the current probe and inherited suite result.
- Exact original clipboard payload and physical click coordinates were unavailable. No claim that every original user action was reproduced. A limited automated Windows click/input spot-check is recorded separately; UIA can name an anonymous readonly document despite native editor keyboard focus, so accessibility certification remains open. The genuine fixture and explicit multi-region/character cases were exercised.
- Word subset U+0075 has a cmap entry but zero advance/no contours and lacks verified PDF encoding. No substitute font/mapping invented. Hard breaks, tabs, NBSP, unmapped glyphs, 512-character recalculation, row limits and safe-envelope refusals remain existing restrictions. Existing CRLF/CR-to-LF logical representation is explicit; no character/break is dropped for approval.
- An incomplete combined worker call leaves a fitting candidate pending, with a global failure reason. It does not establish which region is invalid, and cannot approve export. Recovery restores text/history, not approval.
- Expanded UI overlap is resolved by original source priority plus explicit Text area access. It does not enlarge PDF ownership or move protected neighbours.
- Frozen Phase 3 engine retains its historical one-expectation mismatch (17/18). Earlier evidence and tests are preserved. Multi-monitor/DPI/high-contrast/accessibility/third-party PDF coverage needs separate review.
- Windows x64/.NET 8 Desktop runtime is required for this supplied framework-dependent configuration. No Phase 5.3 or Repository Maintenance R1 work is included.

All observed failures and their disposition are recorded in the progress and final results, rather than silently weakening fidelity checks. Stop for Phase 5.2.2 manual acceptance.
''')
write('USER_TEST_GUIDE',r'''# Phase 5.2.2 user test guide

From repository root:

```powershell
./phase5_2_2/Launch.ps1 -Pdf './phase5_2_2/run/original-paragraphs/Word-cafe-paragraph.pdf'
```

Use the new Phase 5.2.2 window, not an already open 5.2.1 executable. Keep the entire run folder and supporting files. Requires Windows x64/.NET 8 Desktop runtime. Source files stay immutable.

1. Click the lower Protected reference paragraph. Replace it with about 70 repeats of `cafe calm.`. Amber is expected because this exceeds supported recalculation. Full text remains available with internal scrolling.
2. Click the upper original, enter the same long draft, then return to the lower original and different points inside its amber preview. Switch both ways repeatedly. Use **Text area** above the page to return to either source identity, especially if previews overlap. Selection/caret should survive legitimate switching.
3. Restore the lower exact original: `Protected reference block remains in place.` Its amber clears; the upper invalid draft still blocks the whole export. Restore upper or replace it with `calm cafe.`. Try different supported, safely fitting text in both. Wait for complete current verification before Save As enables.
4. Enter one ordinary `u`: expect U+0075 / PDF encoding round-trip failure, not “or newline”. Paste `cafe`, a genuine newline, then `calm`: expect an explicit hard-break reason. Tabs/NBSP/unmapped symbols must remain recoverable and refuse export. Shorter is not automatically valid.
5. Test click-away/return, end-of-draft scroll, multirow/drag selection, Home/End, Up/Down, Shift selection, Backspace/Delete and global chronological Undo/Redo. Try 75/100/150/200% zoom, resize and page scrolling. Focus/zoom alone must never approve text.
6. Correct both areas to supported text, wait for verification, Save As to a new filename, reopen and re-edit. Confirm protected neighbours and source unchanged. Existing destination must not be overwritten. One invalid area must block combined export and retain all drafts.
7. Close/reopen source with unsaved drafts: confirm text/history restored but fresh validation required. Separately reopen an exported PDF in a fresh process without relying on source recovery.

For a problem report include phase/window title, fixture, exact pasted text and replacement/insertion mode, Text area, zoom/window size, current reason and screenshot. Clipboard Win32 5 remains separately tracked. Stop for manual acceptance after this phase.
''')
print('Wrote six Phase 5.2.2 handovers')
