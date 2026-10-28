from pathlib import Path
import json,collections
R=Path(__file__).resolve().parents[1];E=R/'evidence';H=R.parent/'PHASE_4A1_HANDOVER';H.mkdir(exist_ok=True)
matrix=json.loads((E/'position-matrix.json').read_text());perf=json.loads((E/'resource-probe.json').read_text());position=json.loads((E/'position-tests.json').read_text());ui=json.loads((E/'release-verified-controls/position-control-tests.json').read_text());caret=ui['results'][0]['metrics']['maxNativeCaretErrorPt']
def write(n,s):(H/('PHASE_4A1_'+n+'.md')).write_text(s.strip()+'\n',encoding='utf-8')
write('IMPLEMENTATION_REPORT',f'''
# Phase 4A.1 implementation report

28 October 2026. Offline Windows .NET 8/WPF/PDFium prototype. New source, runnable build, tests and evidence are under `phase4a1/`. The six documents in `PHASE_4A1_HANDOVER/` describe this release independently of earlier reports. Earlier phases remain retained. Phase 4B has not begun.

## Delivered behavior

The original genuine Word 16 export now activates through automatic discovery and the existing inline RichTextBox. A title edit from `Phase 3 Office letter` to `Phace 3 Office letter` is saved by the actual WPF editing model. Reopening rediscoveries work without sidecars; a second, narrower change to `Phace 3 Oflice letter` survives another export. Separate Word Arial and Calibri documents also have independently checked first and second exports. This establishes selected single-object substitutions, not unrestricted Word editing.

Stage A reconstructs the original object with explicit origins: full-page Poppler renders are identical at 72 and 144 DPI. Stage B changes an equal-advance glyph. Stage C supports a narrower mapped glyph while every surrounding origin remains fixed; replacing the second `f` of `Office` with `l` reduces its program advance by approximately 0.668 pt. Stage D was investigated and is deliberately **not exportable**: insertions/deletions/newlines requiring different positions or wrapping retain the complete draft and show a limitation. Equal character count alone is insufficient; wider substitutions are refused.

## Architecture and data

`Core/PositionLayout.cs` adds a pointer-free `PositionedSource` alongside the existing natural layout model. It retains original logical offsets, source object indices, glyph Unicode/GID evidence, origins, bounds, relative position array, supported strategy and protected objects. The Region retains the source SHA256, original text, font SHA256/extracted program, size, color, baseline and original matrix observations. Original geometry is a separate source snapshot and is never updated by draft editing. No native handle is cached. Glyph arrays are used as read-only observations by the implementation; they are not an external ownership certificate.

The product uses verified Unicode `FPDFText_SetText` plus `FPDFText_SetPositions`, with exactly N-1 float offsets relative to the text-object origin. Raw PDF codes are independently recorded in `word-position-analysis.json`; **the product does not need or guess raw codes**. Existing Phase 4A Unicode roundtrips, original embedded cmap GIDs, glyph outlines and advances remain necessary. No font substitution, cmap/ToUnicode extension or subset rebuilding occurs.

The native position path requires SHA256 `bede3932ce96a2e1ed9a7e6cae71aec8914efd2907d37ab44b1b81f9c8a6d04e` (PDFium 156.0.8076.0), both on activation and each edit. Bindings use x64 pointer-sized counts. Reconstruction, real changes and save/reopen tests exercise the exact pinned binary. The [public experimental API contract](https://pdfium.googlesource.com/pdfium/+/refs/heads/main/public/fpdf_edit.h) was checked; its moving header is supporting documentation, not substituted for pinned-binary testing.

## Discovery gates and whitespace

Position fallback runs only when initial mapping/style/ownership are otherwise supported and the original natural reconstruction/spacing fails. It requires one horizontal complete text object, monotonic X origins on one baseline, embedded standalone TrueType ASCII mappings, exact original positioned object render, page/margin rules and all existing unsupported-page gates. It never merges position-sensitive objects into a paragraph. Natural documents retain the earlier wrapping path.

An additional position-only metric check rejects fonts where any verified mapping's PDFium width differs from its program advance by more than 0.01 pt. This guard was added after MuPDF exposed a 0.012009 pt unchanged-space drift in the ReportLab kerning fixture. Its pre-guard candidate and measurements remain development negative evidence; that class is restricted in the release. This empirical guard is conservative fixture evidence, not a proof for every PDF reader/font.

Ownership is limited to the original object's observed bounds. Other objects remain protected. A separately retained text object may coexist only if it has fill-only opaque paint, empty/ASCII-space extraction, zero object extent and no contribution to a 144-DPI full-page render when its fill is temporarily disabled. Paint is restored in `finally`; no source file is saved. This is a nonpainting observation, not an inference that the object lacks semantics. Only this narrow position strategy permits coexistence. All such objects remain in snapshots and saved outputs; independent parsing verifies the Word F2 raw space bytes and font rules. Nonzero visible whitespace, mixed runs, graphics and ambiguous neighbors still block editing.

## Inline interaction

The existing window, toolbar, click-selection path, RichTextBox, native caret/selection, keyboard commands, history, recovery, zoom and asynchronous revision handling remain. A hit-test-transparent `PositionedInk` layer draws the verified source font glyphs at recorded origins while the existing native editor owns input. Unsupported drafts use the normal editable presentation and remain recoverable. The input control has enough width to avoid an accidental word wrap when activating a fixed-position line.

The native caret/selection geometry is approximate. On the tested title its maximum horizontal caret discrepancy was {caret:.6f} pt across 75/100/150/200% zoom. The drawn glyph origin plan matches the recorded source positions, but WPF/PDFium rasterisation differs; pixel-perfect editing is **not claimed**. Caret/selection for other position-sensitive lines is not exhaustively measured. Physical mouse, keyboard and file-picker traversal remain unverified for this phase.

TextPointer lookup now counts the next segment instead of repeatedly copying the entire text prefix. This removes unnecessary work exposed by the regression harness while retaining native selection semantics.

## Commit verification and delivery

Existing collision, original-object removal, exact extraction, font/style, neighbor object/glyph, page count/dimensions, annotations, selected info metadata, untouched pages, outside-region raster, source-hash and protected-destination checks remain. Positioned runs additionally reopen with every glyph origin within 0.01 pt of the source, unchanged target bounds within 0.01 pt, verified outlines and exact positioned object reconstruction. Changed ink must fit the permitted line and avoid protected letters/objects. A narrower glyph that creates an extra extracted space is rejected. No prior geometry threshold was relaxed.

The analysis cache remains eight fingerprint/page entries with font-file hash checks. Rendering/verification stays in the separate worker with 300-ms debounce and revision checks; no original geometry is recalculated in response to each immediate TextChanged event. Preview still saves/reopens a candidate and can be costly on large documents. No in-flight cancellation or total disk bound was added.

Run `phase4a1/Launch.ps1` or `phase4a1/run/PdfEditorPrototype.exe`; it opens the Word letter. The entire `run/` folder must remain together. Requires Windows x64 and .NET 8 Windows Desktop runtime (installed here). `phase4a1/build.ps1` rebuilds App and Worker; optional self-contained mode remains unvalidated. No installer, hosting, network dependency, Python runtime dependency, multi-region transaction or document-wide history was introduced. Existing PDFium/font notices accompany the build.
''')
write('WORD_EDITING_ANALYSIS','''
# Phase 4A.1 Word editing analysis

28 October 2026. Primary source: `phase3/run/corpus/11-word-letter.pdf`, unchanged; copied into `phase4a1/run/corpus/`. Producer is Microsoft Word 16.0. Source SHA256 is `d6201ddefe84b6476804cdc022360313998c465d250207fae02cd6ede01f872f`.

## Observations

One A4 page, approximately 595.32 × 841.92 pt. Eight top-level text objects. Visible objects 0, 3 and 6 contain complete lines, not one object per TJ fragment. Baselines are approximately 83.30, 131.30 and 179.18 pt. Identity horizontal transforms, regular Arial 12 pt, opaque fill. The source content includes Word marked content, language/MCID information and full-page clipping operators. Page-level clip context is not assumed to establish semantic ownership.

`phase4a1/evidence/word-position-analysis.json` contains all 154 visible characters: logical offset, original PDF code, Unicode, font GID, program advance, explicit origin, baseline and bounding box, together with all eight object matrices, raw strings, TJ adjustments, original content and protected object observations. Codes/TJ arrays come from pypdf; font cmaps, GIDs and advances from fontTools; geometry from pinned PDFium. Font resource/CIDToGID/ToUnicode data and probes are also retained in `font-investigation.json`. Object references are source-local indices, bound to the source hash, not persistent identities across rewritten files. Rediscovery after save is fresh.

The F1 `/BCDEEE+ArialMT` font is embedded Type0 Identity-H/CIDFontType2 TrueType. Codes 0 and 6 both extract as space, but code 0 is GID 0/notdef while code 6 is GID 3/space. Source visible spaces use the correct code. Existing outline/advance/Unicode proofs select the correct reverse mapping; raw-code guessing is not introduced. Many retained program glyphs still cannot be encoded by the PDF; these remain refused.

Natural reconstruction fails: original TJ adjustments produce measured local advance differences up to approximately 0.3340, 0.1662 and 0.6839 pt on the three lines. These are actual source positions, not new semantic paragraph constraints. Explicit N-1 offsets restore the original object bitmap and produce identical full-page independent renders for the tested title reconstruction.

## Separately retained whitespace

Objects 1, 4 and 7 are raw code 0x20 in F2 `/BCDFEE+ArialMT`, separately owned trailing spaces near x=180.53, 484.20 and 366.31. Objects 2 and 5 are corresponding spaces at intervening baselines 107.30/155.30. F2 is not embedded. PDFium returns empty standalone extraction and zero extent for these objects; MuPDF/pypdf expose their spaces. Their trailing/blank-paragraph roles are plausible **inferences**, not established semantic ownership.

The title's trailing object lies inside its bounding-box vicinity; ignoring whitespace generically would be unsafe. Instead, activation measures zero painted contribution at 144 DPI and retains these separate objects. It does not delete, move, absorb, normalize or recreate them as title spaces. Candidate checks preserve their original count, bounds and style, and independent stream parsing preserves all five F2 0x20 strings. The independent checks also compare encoding, CIDToGIDMap, ToUnicode, widths and font program sets. Visible whitespace or nonzero geometry is not granted this exception. Accessibility/tag-tree equivalence is not certified; retaining bytes/geometry is stronger than dropping spaces but is not a full semantic validation.

## Implemented stages

| Stage | Actual result |
|---|---|
| A: original reconstruction | Same source mapping and recorded offsets; all original glyph origins retained; Poppler full-page pixels identical at 72/144 DPI. |
| B: equal advance | Actual WPF selection/editor/history/ExportTo changes `Phase` to `Phace`; s and c have equal Arial advance. Other origins/bounds remain fixed. |
| C: narrower advance | Reopen first output and change `Office` to `Oflice`; the second f becomes l, approximately 0.668 pt narrower. Fixed surrounding origins, no overlap, correct extraction, same font and independent verification. Separate Arial/Calibri samples have two verified narrower-substitution generations. |
| C: excessive narrowing | `cafe calm.` -> `cafe call.` creates a large gap; PDFium inserts a space before the period in extraction. Exact extraction rejects it; WPF retains the full draft/recovery. |
| D: longer text | Insertions, deletions and newlines are allowed in the draft but refused for export. No general reflow or surrounding movement is implemented. |

A synthetic kerning fixture initially passed PDFium but shifted a space 0.012009 pt in MuPDF. It is development negative evidence (`development/independent-kerning-negative.json`), not a release capability. Additional font-metric gating now restricts that fixture and related ReportLab character-spacing examples. No tolerance was raised.

Word Arial and Calibri first lines activate and pass two-generation exports (`cafe calm. cafe calm.` -> `ccfe calm. cafe calm.` -> `ccfe cclm. cafe calm.`). Reference lines can activate but were not independently edited here. Word Consolas remains limited: its already-natural line hits the existing ownership check; coexistence was not extended to the natural model. The new genuine Word multiple-run document remains ambiguous on its mixed-font first line; no run merging or mixed-style editing is added. PowerPoint remains restricted by graphics/ownership. See the per-document matrix for counts and evidence.

Repeated saves may add another resource **alias** pointing to the same existing font dictionary (observed object 5 under FXF2 and FXF3). Independent checks distinguish aliases from new font programs or mappings. Alias accumulation is retained as an open issue, not described as font extension or byte-identical resource dictionaries.
''')
write('TEST_RESULTS',f'''
# Phase 4A.1 test results

28 October 2026. Actual local execution against the final framework-dependent Windows x64 build. Evidence paths below are relative to `phase4a1/evidence/`. Programmatic WPF controls and independent readers are distinguished from physical input.

| Executed suite | Result | Evidence |
|---|---|---|
| Active original worker checks | 18/18 | engine-tests.json |
| Active discovery checks | 22/22 | discovery-tests.json |
| Active font compatibility checks | 23/23 | compatibility-tests.json |
| Position-aware checks | {position['tests']}/{position['tests']} | position-tests.json |
| Actual WPF original editor | 11/11 | release-verified-controls/control-tests.json |
| Actual WPF discovery | 5/5 | release-verified-controls/discovery-control-tests.json |
| Actual WPF font controls | 4/4 | release-verified-controls/font-control-tests.json |
| Actual WPF position controls | 6/6 | release-verified-controls/position-control-tests.json |
| Frozen Phase 2 binary/original worker suite | 18/18 | phase2-regression.json |
| Frozen Phase 3 binary/original worker assertions | 17/18; known obsolete manifest assertion | phase3-regression.json |
| Frozen Phase 3 discovery suite/binary | 22/22 | frozen-phase3-discovery/tests.json |
| Frozen Phase 4A worker suite/binary | 18/18 | phase4a-regression.json |
| Frozen Phase 4A compatibility suite/binary | 23/23 | frozen-phase4a/tests.json |
| General independent exports | 21 PDFs, 72/144 DPI | independent-verification.json |
| Position-specific independent exports | 11 PDFs, 72/144 DPI | position-independent-verification.json |

The independent sets overlap on two Word outputs: **30 distinct PDFs** were verified. MuPDF checks all positioned target/neighbor origins and unchanged boxes; pypdf checks exact intended Unicode, font programs and mapping/width rules; Poppler checks outside-area pixels at two resolutions; qpdf through pikepdf checks syntax. All approved positioned outputs have measured zero origin shift and zero unchanged-box shift; all outside-area pixel counts are zero. Original reconstruction has zero changed full-page pixels. Font program sets, info metadata and Word F2 raw whitespace bytes are preserved. Resource aliases may increase while referencing the same unchanged font dictionary.

## Negative evidence and regression changes

The frozen original manifestless-view-only assertion became obsolete in Phase 3 and remains recorded as a raw failure. In this phase, six old assertions expecting Word/spacing activation to be refused were initially rerun unchanged: discovery had 2 failures, compatibility 4 failures. Their raw logs remain in `development/initial-*`. The active copies now assert actual positioned Word activation and real saves, while ReportLab metric-rounding fixtures remain refused. No unrelated test or threshold was weakened; original files are untouched.

Early Arial/Calibri `calm` -> `call` candidates failed exact extraction because a large gap created an extra space. This remains a deliberate candidate-refusal WPF test. An initially accepted synthetic kerning candidate failed MuPDF at 0.012009 pt unchanged-space shift; the new metric gate refuses that class. Pre-guard outputs/data remain explicitly labeled development evidence. An unwanted native word wrap during title activation was corrected by sizing the input control independently of the narrow export boundary. The final title caret test asserts <0.75 pt and measured maximum {caret:.6f} pt across four zooms.

The WPF suite covers click-selection, original-position presentation, native undo/redo, live revision verification, first export, rediscovery and second narrower export, complete longer/wider/unmapped/newline draft recovery and refusals, plus failed-candidate draft preservation and terminal-newline paste/history/recovery. Existing tests cover native routed input/navigation/deletion, clipboard/history, natural wrapping, overflow, unsupported character recovery, original/destination protection, stale results and worker restart. The final clipboard probe records five read/write/read matches. Historical intermittent Win32 5 clipboard failures have **not been fixed** and remain an issue.

Physical mouse/keyboard interaction, real file-picker traversal, hardware caret blinking/dragging and cross-application clipboard acceptance were not verified. Prior automation activation failures were not rerun. User comfort feedback from the earlier prototype is prior feedback, not new physical acceptance.

## Performance and resources

Side-by-side inspection used the same bytes for 34 PDFs, including five added position/ownership cases. Fresh-worker medians were {matrix['timings']['phase4aMedianMs']:.2f} ms for Phase 4A and {matrix['timings']['phase4a1MedianMs']:.2f} ms for Phase 4A.1 across this small mixed corpus. Fresh Word inspection was {matrix['timings']['wordColdMs']:.2f} ms; cached inspection median {matrix['timings']['wordWarmMedianMs']:.2f} ms. These include IPC and rendering, are not isolated input latency, and are not a real-world acceptance benchmark.

The 32-distinct-fingerprint resource probe crosses the eight-page cache limit, repeatedly verifies eight original objects, and shows {perf['handlesGrowthAfterWarmup']} handle growth after warm-up. The worker exits successfully. Six cached Word preview candidates had median {perf['previewMedianMs']:.2f} ms. Exact memory snapshots and timings are in resource-probe.json. This does not prove leak freedom, large-document responsiveness or bounded temp disk. Analysis is cached, candidate work is debounced/asynchronous, and there is no in-flight cancellation.

## Reproduction and preservation

Build with `phase4a1/build.ps1`. Development checks use the existing project `.venv/Scripts/python.exe` and `phase4a1/tools/test_engine.py`, `test_discovery.py`, `test_compatibility.py`, `test_position.py`, `compare_positions.py`, `resource_probe.py`, `verify_independent.py`, `verify_positions.py`. `analyse_positions.py` creates the detailed source analysis. They are development tools, not shipped runtime dependencies. Tests create fresh destinations rather than overwrite input PDFs.

WPF: launch `run/PdfEditorPrototype.exe --ui-test --discovery-ui-test --font-ui-test --position-ui-test --clipboard-probe --audit <new-folder>`. The flags execute actual window/control methods; they are not physical automation. Test recovery is isolated.

prior-phase-preservation.json and release-manifest.json record preservation and final source/runtime/document hashes. Corpus source hashes are checked before/after. Prior sources/builds/evidence were not edited. This is not disconnected-VM, installer, security-sandbox or hostile-document certification.
''')
lines=['# Phase 4A.1 compatibility matrix','','28 October 2026. Both binaries inspected identical bytes. E/L/V are counts of Editable/Limited/View Only regions, not document acceptance percentages. Activation does not guarantee every draft can export. Position models use fixed origins; natural models retain wrapping. Full observations/timings are in `phase4a1/evidence/position-matrix.json`.','','| Source under run/ | Phase 4A E/L/V | Phase 4A.1 E/L/V | Actual edit evidence or restriction |','|---|---|---|---|']
def counts(rs):return '/'.join(str(sum(r['Eligibility']==s for r in rs)) for s in ['Editable','Limited','View Only'])
for row in matrix['cases']:
 name=row['name'].replace('\\','/');note='Natural-layout behavior retained; specific saves and negative cases in discovery/compatibility suites.'
 if name=='corpus/11-word-letter.pdf':note='Position title reconstruction, Phace, narrower Oflice, rediscovery/second save; other two lines activation measured.'
 elif name.endswith(('Word-Arial.pdf','Word-Calibri.pdf')):note='Fixed-position first line: ccfe, then cclm; two independent verified saves. Other line activation only.'
 elif name.endswith('Word-Consolas.pdf'):note='Natural glyphs but separately owned space still blocks conservative ownership; not promoted.'
 elif 'Word-multiple-runs' in name:note='Mixed-font first line remains ambiguous; no mixed-run merging. Other regions assessed individually.'
 elif any(x in name for x in ['E-character-spacing','F-kerning','15-letter-spacing']):note='Restricted: additional position metric-rounding guard; no release export claimed.'
 elif 'PowerPoint' in name:note='Graphics/background ownership restriction retained.'
 elif 'visible-whitespace' in name:note='Visible glyph mapped to space; nonzero geometry remains protected. Refused.'
 elif 'position-corpus' in name:note='Adjacent label, intersecting graphic or restricted boundary: first region refused.'
 elif 'J-partial' in name:note='Phase 4A gain retained: existing mapped-character edits and longer natural wrapping; unmapped Z refused.'
 elif not any(r['Eligibility']=='Editable' for r in row['phase4a1']):note='Remains restricted; exact font/transform/ownership reasons in JSON. No export claimed.'
 lines.append(f"| {name} | {counts(row['phase4a'])} | {counts(row['phase4a1'])} | {note} |")
lines+=['','Saved and reopened outputs are tested separately in position-tests.json and the WPF position-control evidence. Position-aware edit eligibility is reassessed each generation; no synthetic ownership metadata is attached. More resource aliases can appear on later saves while pointing to the same unchanged font dictionary.','','Equal character count is required but insufficient. Only mapped ASCII substitutions no wider than the original slot are planned; actual ink/extraction/candidate checks can still refuse. Missing cmap, wrong Unicode, missing encoding, unsupported transforms/pages and unrelated ownership checks remain active. No general Word support, mixed formatting, arbitrary kerning, longer positioned text or multi-region commit is claimed.']
write('COMPATIBILITY_MATRIX','\n'.join(lines))
write('OPEN_ISSUES','''
# Phase 4A.1 open issues

28 October 2026. Narrow Word single-object substitutions are implemented. These limits remain and must guide review before Phase 4B.

| Priority | Issue and practical consequence |
|---|---|
| High | Native caret/selection uses natural WPF geometry while positioned ink uses original origins. Title caret max error is 0.254002 pt; other lines/styles/DPI are not exhaustive. WPF/PDFium rasterisation differs. No pixel-perfect interactive promise. |
| High | Font metric rounding can cause cross-reader drift despite PDFium verification. The demonstrated 0.012009 pt fixture is now gated; the additional <=0.01 pt width discrepancy rule is empirical, not a general proof across every reader/font. Expand independent adverse coverage before broadening claims. |
| High | Physical input, dialogs and cross-app clipboard are unverified this phase. Historical intermittent Win32 5 clipboard failures remain unresolved; final passing probes are not a fix. |
| High | Separately retained zero-extent nonpainting text can carry extraction/tag meaning. Raw Word spaces, geometry and font rules are preserved; full tags/MCIDs/reading-order/accessibility equivalence is not certified. Do not generalize the coexistence exception to visible or ambiguous whitespace. |
| High scope | Same-count equal/narrower substitutions only for positioned text. Wider glyphs, inserted/deleted characters, newlines, shaping/Unicode, mixed runs, arbitrary transforms and reflow are unsupported. Drafts remain editable/recoverable. Excessive narrowing can still create extra extracted spaces and is rejected. |
| Medium | Word Consolas natural lines remain ownership-limited. Mixed-font Word first lines and PowerPoint background/graphics remain restricted. No automatic other-font space ownership or run merging. |
| Medium | Repeated export can add a resource alias pointing to the same existing font dictionary (second-generation Word observed FXF2/FXF3 -> object 5). Programs, widths and mapping rules remain unchanged. No alias cleanup or large-generation growth test implemented. |
| Medium | WPF TextRange assignment can absorb a trailing newline. The shared paste path now restores the missing terminal paragraph break; the six position controls include two trailing newlines plus undo/redo/recovery. Cross-application clipboard transport still needs physical acceptance. |
| Medium | Eight-page pointer-free cache, but no total temp disk/font-per-page bound, in-flight native cancellation, adversarial PDF campaign or large-document latency guarantee. Small resource probe is not leak certification. |
| High scope | Font cmap absence, retained but unencodable glyphs, CFF/collections, variable/color fonts, simulated styles, nonzero crop contexts, arbitrary bidi/IME and subset rebuilding remain unsupported or uncertified. No substitution or rights inference added. |
| High scope | Metadata/page/raster/glyph tests do not certify PDF/A, all XMP, tags, complete annotation dictionaries, forms, encryption or signatures. Unsupported-page gates remain. |
| Medium | Natural paragraph inference remains geometric and can join unrelated long lines. One changed region per export; no document-wide history, region transaction or ownership sidecars added. |
| Medium | Framework-dependent Windows x64 build. No installer, clean disconnected VM, OS sandbox, crash/power-loss/disk-full certification. |

Development failures and superseded assertions remain under `phase4a1/evidence/development/`; they are not approved release exports. Phase 4A.1 stops here. Do not start Phase 4B without review.
''')
write('USER_TEST_GUIDE','''
# Phase 4A.1 user test guide

28 October 2026. This offline Windows prototype supports selected single-line substitutions in genuine Word PDFs. The familiar editing window is retained. It does not support general Word paragraph reflow.

## Start

Run `phase4a1/Launch.ps1` or double-click `phase4a1/run/PdfEditorPrototype.exe`. Keep the whole run folder together. Windows x64 with .NET 8 Windows Desktop runtime is required; it is installed on this computer. The original Word letter opens by default. Earlier applications remain available in their previous folders.

## First edit

1. Click the title `Phase 3 Office letter` directly on the page. The native inline editor activates with the original Arial style and positions.
2. Change only `Phase` to `Phace`. You can select the title and type `Phace 3 Office letter` if easier. Keyboard, selection and Undo/Redo remain available.
3. Pause for candidate validation. Use Save As and choose a **new** filename. The original and existing destinations cannot be overwritten.
4. Open the new PDF. Click its title and change it to `Phace 3 Oflice letter` (the second f becomes l). Save to another new filename.
5. Reopen it and confirm both changes remain. The spelling is intentionally a technical glyph-position test.

Caret/selection may be slightly offset from the positioned glyphs: tested title maximum 0.254002 pt across four zooms. Display rasterisation differs from the PDF image. This is not a pixel-perfect input claim.

## Refusals and drafts

Try adding ` extra`, deleting a character, entering a newline, changing a narrow character to a wider one, or inserting `!` in this title. Input remains in the working draft, but export is refused when the original mapping/positions cannot be preserved. Continue typing, use Undo, or restore the supported title. Draft recovery retains the working text. A candidate may also be refused after deeper PDF verification; the draft still remains.

Save/reopen before editing another region. This version commits one region per exported PDF; it does not combine edits to multiple regions.

## Other supplied examples

Open `run/font-corpus/Word-Arial.pdf` or `Word-Calibri.pdf`. In the first line, replace `cafe calm. cafe calm.` with `ccfe calm. cafe calm.`. Save/reopen, then try `ccfe cclm. cafe calm.`. These are verified narrower mapped-character probes.

Word Consolas and the mixed-font first line in `run/position-corpus/Word-multiple-runs.pdf` remain restricted. ReportLab metric-rounding fixtures, visible whitespace mapped to a glyph, nearby graphics and ambiguous labels remain restricted. Do not interpret a clickable line as permission for every possible replacement.

For ordinary natural wrapping, open the earlier controlled samples in `run/samples/` or the partial-encoding case `run/font-corpus/J-partial-encoding.pdf`; their existing behavior is retained. Unsupported characters remain in the draft and cannot be saved.

## Manual review still needed

The automated checks exercised actual WPF controls/shared save paths, not hardware input or Open/Save As picker traversal. Please check physical click/caret placement, drag selection, sustained typing, Ctrl+Z/Ctrl+Y, clipboard between applications, four zooms, dialogs, source preservation and recovery on your interactive desktop. Intermittent clipboard failures are still tracked; a current pass does not establish a permanent fix.

Detailed scope, measured tests and limits are in the five accompanying handover reports. No Phase 4B work has begun.
''')
(R/'README.md').write_text('''# PDF Editor V2 — Phase 4A.1

Run Launch.ps1 or run/PdfEditorPrototype.exe (Windows x64, .NET 8 Windows Desktop runtime).
The default genuine Word letter supports fixed-origin equal/narrower substitutions such as Phase -> Phace.
No general paragraph reflow or multi-region commit. Unsupported input stays in the draft.

Full self-contained reports: ../PHASE_4A1_HANDOVER/.
Build: ./build.ps1. Keep the entire run directory and its licenses together.
Development tests and independent-reader tools are in tools/, evidence in evidence/.
Earlier phases are retained; Phase 4B has not started.
''',encoding='utf-8')
print('Wrote six handover documents')
