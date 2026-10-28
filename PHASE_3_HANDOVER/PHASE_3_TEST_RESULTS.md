# Phase 3 test results

28 October 2026. Evidence is in `../phase3/evidence/`. Backend, actual WPF control integration and physical input are reported separately.

## Results

| Check | Recorded result | Evidence / interpretation |
|---|---|---|
| Frozen Phase 2 worker suite | **18/18 pass** | `phase2-regression.json`; original test class and earlier runnable build, redirected evidence output |
| Original worker suite against Phase 3 | **17/18 pass; one superseded expectation fails** | `phase3-regression.json`; `test_unknown_pdf_view_only` expects a manifestless copy to have no region. Phase 3 intentionally discovers it. This raw failure is retained, not disabled or called a pass. All other original assertions pass. |
| Automatic discovery / editing suite | **22/22 pass** | `discovery-tests.json` and `.log`; actual worker, source fingerprints and saved PDF records |
| Frozen Phase 2 WPF controls rerun | **11/11 pass in this run** | `phase2-controls/control-tests.json`; clipboard access worked at that time. This does not establish a durable clipboard fix. |
| Phase 3 original WPF controls | Final **10/11**, clipboard failure; earlier **11/11** | `release-controls/control-tests.json` records the final build. `phase3-controls/` retains the earlier pass; `final-controls/` retains the first repeat failure. Caret, wrapping, history, draft retention, export, revision and restart checks pass. |
| New discovery WPF controls | Final **5/5 pass** | `release-controls/discovery-control-tests.json`; shared click-selection path, original text, real editor styles, two exports, recovery and unsupported feedback. Earlier run retained in `discovery-controls/`. |
| Independent PDF verification | **8 PDFs x 2 resolutions pass** | `independent-verification.json`: Poppler at 72/144 DPI, pypdf extraction/font/geometry/metadata, qpdf syntax check via pikepdf |
| Independent WPF output extraction | **Pass** | `ui-independent-extraction.json`: both first and second WPF edit markers extracted from the second output |
| Native UI automation | **Input blocked** | Window screenshot/accessibility capture worked; Open PDF click returned `failed to activate captured window`, again after a fresh binding. No dialog traversal or physical input pass is claimed. |
| Previous artifacts | **Unchanged** | `phase1-preservation.json`: all 353 earlier Phase 1 hashes; `prior-phase-preservation.json`: 198 pre-existing Phase 2/handover files checked, none changed |

The final source/build inventory is recorded in `release-manifest.json`. Earlier intermediate failures are retained in `discovery-initial.json`, failed candidate diagnostics under `phase3/test-work/`, and the control-run folders. Where paths differ between repeated runs, the current JSON contains the exact tested output filenames.

## Discovery suite coverage

1. Manifestless ReportLab letter: five separate regions; two body lines join; actual glyph ownership and observed/inferred records present.
2. Report: three-line paragraph, second page analysed on request, genuine save with untouched-page verification.
3. Regular original-font replacement.
4. Bold original-font replacement, with bold face observed.
5. Blue 10 pt replacement, original size and colour preserved.
6. MuPDF-generated source edited through PDFium, independently of the source generator.
7. First output reopened without a sidecar; three-line paragraph rediscovered; second edit/export; both edit markers extracted; final output rediscovered again.
8. Adjacent label/value kept separate and unsupported; isolated body remains editable.
9. Ten two-column lines remain separate and unsupported.
10. Table cells remain unsupported; path boundaries observed.
11. Two ambiguous short lines remain Limited and unmerged.
12. Rotated text refused.
13. Nonembedded standard font refused; no substitution.
14. MuPDF subset and actual Word export refused with mapping/ownership reasons.
15. Deliberate expansion beyond available space refused with no destination created.
16. U+2603 refused with a code-point diagnostic; the WPF suite checks full draft retention.
17. Limited or invented region IDs cannot commit.
18. Cached observations are stable and render names use the source fingerprint.
19. Image objects are observed; overlapping text/image region remains unsupported.
20. Reversed object order `[1,2,0]` yields the correct visual paragraph and a genuine safe save.
21. A page containing an actual link annotation remains view-only.
22. Explicit character spacing is refused by observed glyph geometry.

All 15 corpus source hashes remain unchanged during the suite. Independent verification checks eight successful outputs: report, letter, bold, colour, MuPDF, generation one, generation two and shuffled-order paragraph. Every outside-region Poppler comparison is zero thresholded changed pixels; runtime neighbour shift is zero on these cases. These checks cover these fixtures, not arbitrary graphics, accessibility or complete PDF object equivalence.

## WPF and clipboard evidence

The unchanged original control tests exercise 16 sampled caret mappings across 75/100/150/200% zoom, actual bitmap switching, native editing commands/routed input, three-step history, copy/cut/paste/history, live wrapping against the worker, overflow history, missing-glyph recovery, real export/original overwrite rejection, stale revisions and worker restart.

New control tests use the same region-selection method as the page click handler and the actual RichTextBox. They activate a discovered two-object paragraph with 152 glyphs; save/reopen/edit/save through the real export method; verify bold weight and 10 pt colour-region sizing; retain U+2603 through a rejected save and attempted region switch; and refuse Limited text. These are **programmatic control tests**, not physical clicks/typing or a file-picker pass.

Clipboard behaviour is intermittent. It passed in both first WPF reruns, then failed again with Win32 5. Added diagnostics capture the error immediately after OpenClipboard rather than after a delay. A five-attempt standalone window probe failed five times: owner HWND valid, no identifiable open-clipboard holder (PID 0). This rules out an invalid application owner handle in those observations, but does not establish a root cause. No system settings, alternate clipboard or fake success path were introduced. Physical cross-application clipboard acceptance remains pending.

The user previously confirmed Phase 2's direct editing feels comfortable. This is useful prior usability feedback; it is not substituted for Phase 3 physical acceptance.

## Performance observations

The 22-test small-corpus run recorded discovery calls, including IPC and page rendering, around **2.4-271 ms**, with median around **39 ms** in the recorded run. Exact per-call timings are in `discovery-tests.json`; this is a small local sample, not an input-latency benchmark or a large-document guarantee. Native analysis runs in the worker; WPF awaits it asynchronously. Pointer-free page analysis is fingerprint-cached, and only the requested page is analysed. Cancellation of in-flight native work and cache lifetime bounds remain open issues.

## Corrections found during implementation

- The WPF font directory cache failed to recognise later extracted files. Separate directories per font hash resolved the reproduced cases.
- Detached font-probe text objects did not have usable text-page mappings. Probes are temporarily inserted, extracted using a fresh text page and removed before display/save.
- A 0.35 pt cumulative metric test rejected long ordinary lines because PDF widths and WPF advances differ slightly. The supported rule now checks small local spacing differences plus a bounded 1 pt cumulative discrepancy. Non-natural character spacing still fails.
- Reopened wrapped text contains observed line breaks. The append verifier now recognises intentional original text in the planned replacement lines, while retaining exact extraction and object-removal checks.
- A test append containing two consecutive spaces exposed PDFium extraction collapsing a space. The commit was refused. The normal second-generation scenario uses one intentional space; the double-space limitation remains documented, rather than accepting a changed draft silently.

Physical caret blinking, drag selection, sustained real typing, Open/Save As picker traversal and cross-application clipboard behaviour still need manual verification on the user's interactive desktop.
