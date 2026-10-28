# Phase 1 consolidated technical report

**Project:** PDF Editor V2 - new offline Windows PDF editor  
**Review date:** 27 October 2026  
**Scope:** analysis and handover of the completed feasibility laboratory. No source, test, original PDF or experimental result was changed. No Phase 2 feature was implemented.

## A. Executive Summary

**The project is technically viable for constrained editing of existing digital PDF text. A natural, direct-on-page editing experience is a reasonable next investigation, but has not been demonstrated. Reliable Word-like editing and reflow of arbitrary PDFs remain unproven.**

Phase 1 implemented a Python command-line laboratory with six synthetic original PDFs, thirteen genuinely edited candidates, three unchanged candidates representing refused operations, diagnostics, automated checks and saved render comparisons. The retained suite records **14 tests passing**. Some tests deliberately expect an unsafe edit or metadata preservation failure; this is not evidence that every candidate is suitable for users.

The most important findings are:

1. Existing text can genuinely change. Both a parsed PDF string-operand change and PDFium's existing-text-object mutation survived saving and reopening, with the replacement extractable and the old target absent. PyMuPDF removal/reinsertion also changes real content, through reconstruction rather than preservation of the original text object.
2. A successful API call and syntactically valid save do not establish fidelity. Longer replacement text collided with an adjacent label. A much smaller width change moved a following word by approximately **0.840 pt**.
3. Known-width spacing compensation corrected the bold example. A known complete paragraph could be reconstructed and wrapped in a declared box. Neither operation establishes general paragraph discovery or document reflow.
4. The italic example is weaker than its almost-clean raster diff suggests: read-only inspection during this handover found the following period moved approximately **1.443 pt left**. The saved diff reports only **one** outside-mask pixel in PDFium. Padded raster masks can conceal small neighbour movement; glyph geometry must also be checked.
5. Save integrity is configuration-sensitive. Default pikepdf saving reserialized XMP; disabling its metadata-version fix preserved the exact packet in this fixture. PDFium and PyMuPDF also changed font resource inventories while retaining the tested appearance.
6. No caret, inline input, keyboard navigation, live preview, persistent editable draft, collision preflight or undo/redo exists. The three refusal examples are explicit scripted cases, not a generic production eligibility system.

**Recommendation:** retain PDFium as the leading engine candidate and a native Windows .NET/WPF shell as the leading UI direction, with an isolated PDF worker and an application-owned interactive text model. Prove a small in-place editing slice before committing to a full editor. Keep draft editing permissive and preserve user input when safe PDF export is unavailable. The original text rectangle should inform layout, not automatically define a hard input limit.

**Biggest unresolved limitation:** translating an editable on-page text region back into original PDF glyphs, encodings, font resources and surrounding layout when the text changes length. UI work alone cannot recover absent paragraph semantics, missing font glyphs or a unique intended reflow.

There is sufficient evidence to **plan** Phase 2, with explicit experiments and review gates. There is insufficient evidence to promise unrestricted Word-like editing or to commit to a production architecture without further validation.

### Review method and evidence boundary

The handover inventoried and hashed **351 existing project artifacts**, excluding dependency environments and caches. It reviewed source/test scripts, all four reports, the README, dependency pins, retained logs, the evidence index, all **57 result JSON files**, PDFs and saved image comparisons. There are **22 PDFs**, **243 page-render/diff PNGs** and five additional review sheets.

Read-only checks during consolidation:

- Confirmed the harness SHA256 matches `results/summary.json` and the six originals match the persistent manifest.
- Confirmed all 32 before/after diagnostic PDF hashes match their actual files.
- Recomputed the stored thresholded metrics from all **81 before/after page pairs** across three renderers; no metric mismatch was found. This checks stored image consistency, not a new rendering run.
- Reopened all thirteen edited candidates, confirmed replacement text and old-target absence through MuPDF, and obtained no qpdf syntax warnings.
- Examined saved geometry to quantify the bold advance and italic punctuation movement.
- Verified all 117 file references in the existing HTML evidence index resolve.

The original test runners were **not rerun**, because they write experimental results and/or temporary experiment files. The 14-test result and clean-environment/offline execution claims below refer to retained Phase 1 evidence. The handover added read-only evidence checks, not new editing experiments. External technology/licensing research is carried forward from the Phase 1 sources checked on 27 October 2026; it was not refreshed during this consolidation.

No ZIP was necessary: this report communicates the important evidence and limits independently, and the companion index maps the original artifacts for deeper verification.

## B. Technology and Architecture Evaluation

### Tested technology snapshot

Recorded host: **Windows-11-10.0.26300-SP0**, Python **3.12.14**. These are retained run identifiers, not minimum supported versions. Individual edit/save operations took **10.193-76.413 ms** in the delivered run; total harness time was **36.79 s**, including rendering and evidence generation. This is not a controlled engine benchmark or an interactive latency measurement.

| Technology/version | What was actually exercised | Advantages | Disadvantages and offline/distribution implications |
|---|---|---|---|
| PDFium **156.0.8076.0**, pypdfium2 **5.14.0** | Rendering, extraction and one existing line-object text mutation using `FPDFText_SetText`, content regeneration and save | Demonstrated real object mutation; native engine suitable for local rendering; leading permissive-license candidate | Only one mutation scenario tested. Arbitrary glyph selection, subsets, shaping and explicit positions unproven. Raw handles require careful ownership; native binaries and dependency notices must be packaged. |
| PyMuPDF **2.0** | Fixture construction support, span/font/image diagnostics, rendering, text redaction and reinsertion, known-box layout | Broad convenient API; strong research/verification tool | Reconstruction can change reading order/resources. The complete current harness imports it, including the PDFium test path. AGPL/commercial licensing is a product decision, not resolved by choosing a different mutator. |
| pikepdf **10.17.0**, embedded qpdf **12.4.2** | Parsed `Tj`/`TJ` string edits, stream serialization, save policy and syntax checks | Direct controlled operand changes preserve tested resources; useful structural companion | No renderer, layout model or paragraph reflow. Custom encoding/advance logic required. Fixture-aware ASCII editing is not a generic API. |
| pypdf **6.10.0** | Third extraction check in retained tests | Independent semantic check; Python portability | Not used as the mutating engine; no rendering or interactive layout demonstrated. |
| ReportLab **4.4.9** | Synthetic PDFs and known-font width calculation | Reproducible controlled fixtures, known metrics | Easy fixtures share assumptions with the editor. Generation-time text layout is not recovery of arbitrary existing layout. |
| Poppler **26.07.0** (`pdftoppm`) | Independent 144 DPI rendering | Third visual comparison engine | Externally supplied tool on PATH, not included in Python requirements. Product redistribution and licensing would need separate consideration if shipped. |
| Pillow **12.3.0**, NumPy **2.3.5** | Synthetic images, reading/writing PNGs and raster differences | Local measurable comparisons | One resolution, threshold and rectangular masks do not prove geometry or print fidelity. |
| fontTools **4.67.0**; Bitstream Vera fixture font | Embedded subset cmap inspection for absent U+2603 | Concrete missing-glyph evidence; font license retained | Does not establish a general Unicode-to-PDF-code mapping or font replacement policy. |

`requirements.txt` pins the complete selected dependency closure, including PyMuPDF layout/ML dependencies. Their installation is not evidence that OCR, ML layout inference or advanced paragraph reconstruction was exercised. No such feature is present in the experiment paths.

### Researched technologies and licensing

These are recorded Phase 1 research findings, not locally tested SDK behaviour or a final legal determination.

| Candidate | Recorded license/distribution position | Architectural relevance and qualification |
|---|---|---|
| PDFium/pypdfium2 | PDFium BSD-style; wrapper Apache-2.0/BSD-3-Clause; dependency notices depend on the exact native build | Plausible open- or closed-source path with license compliance. Current Python inspector is not yet independent of PyMuPDF. |
| MuPDF/PyMuPDF | AGPL or commercial | Consider an AGPL-compatible application or appropriate commercial agreement. A worker/sidecar is not assumed to remove copyleft obligations. |
| qpdf / pikepdf | Apache-2.0 / MPL-2.0 | qpdf is a native structural option. pikepdf has file-level copyleft obligations; do not conflate them with AGPL or ignore covered-source requirements. |
| pypdf | BSD-3-Clause | Useful development/verification tool; not the selected editing core. |
| iText (.NET/Java; not installed) | AGPL/commercial | Broad document processing and low-level access researched; no local fidelity or reflow results. |
| PDFsharp/MigraDoc (not installed) | Phase 1 research records AGPL/commercial for 6.5.0+ and 7.0 preview 2+, rather than older MIT assumptions | .NET integration/generation is attractive, but existing-text editing was not tested. Version-specific licensing must be rechecked at selection time. |
| Apryse (not installed) | Commercial terms/modules/offline distribution require evaluation | Vendor content-editing/reflow claims are a possible fallback, not demonstrated project capability. No purchase or paid API was used. |
| Bitstream Vera font | Redistribution license retained in `assets/bitstream-vera-license.txt` | Applies to this supplied fixture font, not arbitrary fonts extracted from customer PDFs. |

Original primary-source pointers: [PDFium editing API](https://pdfium.googlesource.com/pdfium/+/refs/heads/main/public/fpdf_edit.h), [PDFium license](https://pdfium.googlesource.com/pdfium/+/refs/heads/main/LICENSE), [pypdfium2 licensing](https://pypdfium2.readthedocs.io/en/stable/readme.html#licensing), [MuPDF/PyMuPDF licensing](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright), [qpdf scope](https://qpdf.readthedocs.io/en/stable/overview.html), [qpdf license](https://github.com/qpdf/qpdf/blob/main/LICENSE.txt), [pikepdf license](https://github.com/pikepdf/pikepdf/blob/main/LICENSE.txt), [pypdf license](https://github.com/py-pdf/pypdf/blob/main/LICENSE), [iText licensing](https://itextpdf.com/how-buy/AGPLv3-license), [PDFsharp licensing](https://docs.pdfsharp.net/General/License/License.html), and [Apryse content-editing description](https://support.apryse.com/support/solutions/articles/35000251231-content-editing).

### Shell alternatives

| Option | Why consider it | Why it was not established in Phase 1 |
|---|---|---|
| Native .NET/WPF shell plus native worker | Windows priority; native input, files and accessibility; separates UI text editing from PDF processing | No shell, text-input experiment, worker binary, IPC or installer exists. Recommendation only. |
| Tauri 2 shell plus separate engine | Web UI and possible future portability; sidecar architecture | Rust/JS/native integration and page-coordinate synchronization remain. Offline WebView2 installation must be planned; no local Tauri build or comparison exists. |
| Python desktop shell | Reuses tested bindings and shortens a research spike | No UI framework was selected/tested. Runtime packaging/startup and PyMuPDF distribution questions remain. |
| Commercial SDK plus native shell | May reduce implementation effort for difficult editing | Costs, SDK behaviour and fully offline delivery untested. |

The WPF preference reflects project fit, not a performance win measured against Tauri. [WPF documentation](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/overview/), [Tauri sidecars](https://v2.tauri.app/develop/sidecar/) and [Tauri Windows installation](https://tauri.app/distribute/windows-installer/) were the original architecture sources. All tested document operations were local. First-time dependency installation used package downloads; a disconnected application installer was not built or validated.

## C. Experiment Results

### Interpretation of status and measurements

- **Pass** means the stated narrow fixture objective was met, with qualifications explicitly recorded.
- **Partial pass** means a real change or safety finding was demonstrated but the broader fidelity/editing objective was not met.
- **Fail** means the intended safe visible edit failed, even if text extraction and PDF syntax checks passed.
- **Not tested** means no executable demonstration exists for that capability.

Refusal cases are passes for documenting safe non-modification, **not successful edits**. They copy a known original and record a known reason; they do not invoke a reusable general eligibility planner. No meaningful real-world acceptance percentage can be inferred from this corpus.

The three renderer counts below are **MuPDF / PDFium / Poppler** pixels changed outside the declared original edit mask. Masks use 2 pixels per PDF point at **144 DPI**, threshold **maximum RGB-channel difference > 8**, and nominal **3-pixel padding**, with the exclusive slice endpoint allowing the terminal extra pixel. Reflow uses a larger declared paragraph region. Counts are summed over pages; all changes reported here are on page one. All second-page render comparisons have zero change and maximum channel delta zero.

### Experiment 1 - Basic replacement

**Objective and expected outcome:** replace `blue` with `glue` in a multi-paragraph two-page digital PDF, preserve original font/size/colour/start position and unrelated content, and reopen a genuinely changed file. Source: `output/pdf/originals/basic.pdf`.

| Candidate (under `output/pdf/edited/`) | Implementation approach | Actual outcome and metrics | Status / errors / established cause | Limitation and lesson |
|---|---|---|---|---|
| `e1_operand.pdf` | Parse page instructions with pikepdf; replace a unique ASCII string operand; save a new stream | Both extraction engines find `glue`, not `blue`; targeted old bytes absent from parsed operands. Outside pixels **0 / 0 / 0**. Exact tested font inventory retained | **Pass**, controlled fixture. No retained API/syntax error | Unique known single-byte occurrence only; no generic mapping from clicked glyphs to operators. Direct content change is possible. |
| `e1_pdfium.pdf` | Find a page text object containing `blue`; replace the object's complete text with `FPDFText_SetText`; regenerate/save | Same semantic and raster result: **0 / 0 / 0**. Font inventory comparison false | **Pass for appearance/content; partial for exact resource preservation.** No syntax error. Page resource inventory is regenerated | Demonstrates one complete line-object mutation, not arbitrary caret-level surgery. PDFium is not render-only. |
| `e1_remove_reinsert.pdf` | Locate word rectangle/baseline; text-only redaction with images/graphics preserved; insert text in Helvetica | Old content removed; replacement saved; outside pixels **0 / 0 / 0**. Added `helv` resource and changed extraction order | **Pass for this appearance; partial for original-object/resource identity.** No syntax error | Reconstruction can be visually faithful without preserving original structure or reading order. Must be labelled accurately. |

All three retain Helvetica **12 pt**, packed RGB colour **1720435**, and target start/baseline **(182.059967, 112.0) pt** in saved diagnostics. The original and operand-edited word boxes are exactly equal in the handover reopening: **[182.059967, 99.099998, 204.739960, 115.587997] pt**. Font names here are unembedded Base-14 fonts; across-machine substitution is not settled by these local renders.

The first-page original font list contains Helvetica, Helvetica-Bold and an unused Courier resource. PDFium's rewritten list has Helvetica-Bold/Helvetica with regenerated resource names; Courier remains on the unchanged second page where used. PyMuPDF's new list adds another Helvetica resource. The false inventory flags are not evidence that visible text lost its required font.

### Experiment 2 - Longer text, overflow and owned-box wrapping

**Objective and expected outcome:** replace `brief note` with `a substantially longer replacement phrase which needs several lines`, investigate overflow/wrapping and determine whether surrounding elements remain safe. Source: `output/pdf/originals/expansion.pdf`, containing a fixed neighbouring label and content below.

| Candidate | Implementation approach | Actual outcome and metrics | Status / errors / cause | Limitation and lesson |
|---|---|---|---|---|
| `e2_overflow.pdf` | Direct string operand substitution at original size/position | New phrase genuinely saved on one line, colliding with `NEIGHBOUR - DO NOT MOVE`; outside pixels **5356 / 5829 / 5350** | **Fail for safe expansion.** No API/syntax error. Longer glyph advance extends the same line without layout | Valid PDF/text extraction is insufficient. No automatic collision detector or reflow is implied. |
| `e2_controlled_reflow.pdf` | Remove the entire known sentence `A brief note ends here.`; insert its full replacement into explicit **[50,95,355,150] pt** box | Two 12 pt lines fit. Outside pixels **0 / 0 / 0** with comparison region **[49,94,356,151] pt**. Font inventory changes; paragraph origin intentionally moves | **Partial pass:** bounded reconstruction demonstrated; arbitrary paragraph reflow not tested. No fit/API error | The box is **305 x 55 pt**, supplied by the experiment, not inferred. Neighbour stays fixed. Known ownership and available space make wrapping tractable. |
| `e2_rejected_expansion.pdf` | Script records known width condition and copies input unchanged | Original phrase width **50.028 pt**, replacement **362.148 pt**; candidate byte-identical; all pixels unchanged | **Pass for the scripted refusal demonstration; editing not tested in this case.** No exception | Does not justify rejecting a user's draft at the old box boundary. Export eligibility and interactive input should be separate. |

The original red reference outline is **310 x 55 pt**, while insertion uses a slightly narrower **305 x 55 pt** box; these are different intentional constants. Saved wrapped lines have boxes approximately **[50,95.000023,353.467957,111.488022]** and **[50,112.724571,176.719971,129.212570] pt**. They fit the declared insertion area. The phrase is mechanically assembled as `A a substantially ...`; no linguistic editing quality was tested. There is no demonstration of shifting downstream content or adding pages.

### Experiment 3 - Complex formatting and neighbours

**Objective and expected outcome:** edit individual elements while retaining style and protecting nearby content. Source: `output/pdf/originals/complex.pdf`, two pages with blue Helvetica-Bold **15 pt**, red Times-Italic **13 pt**, green Courier **10 pt**, purple subset Vera **14 pt**, ruled table, images, annotation and link.

| Candidate | Approach and expected result | Actual outcome / outside pixels | Status / errors / root cause | Limitation and lesson |
|---|---|---|---|---|
| `e3_bold.pdf` | `BOLD` -> `GOLD`, same text operand/font/start; expected isolated correction | Replacement genuine and style retained, but `heading` moves about **+0.840004 pt**. **1204 / 1474 / 1222** | **Partial pass:** semantic edit passes; neighbour preservation fails. No API error. New word advance is larger | Keeping font and starting point does not keep subsequent glyph positions. |
| `e3_bold_compensated.pdf` | Split known string into `TJ` pieces and compensate known Helvetica-Bold advance | Outside pixels **0 / 0 / 0**. Following word residual shift about **0.00000763 pt** on handover reopening | **Pass for this fixture.** No syntax error. Explicit spacing offsets the changed advance | Hard-coded 15 pt font metrics, not generic kerning/shaping. Word is still wider; available trailing space is reduced. |
| `e3_italic.pdf` | `elegant` -> `refined` in Times-Italic; expected local style-preserving correction | Style/anchor retained; **0 / 1 / 0**. Handover reopening confirms period moves **-1.442993 pt** | **Partial pass.** No API error. Uncompensated shorter word advances the following period less | Exact raster-edge behaviour remains renderer-dependent; small padded-mask diffs do not prove stable surrounding glyphs. |
| `e3_table.pdf` | `125.00` -> `175.00`, existing numeric operand | **0 / 0 / 0**; table rules, other cells and nearby image unaffected in the measured views; resources retained | **Pass**, narrow equal-width numeric change. No error | No table model, cell resizing or long-cell reflow was implemented. |
| `e3_subset.pdf` | `cafe` -> `face`, reordering existing encoded ASCII glyphs | **0 / 0 / 0**; same embedded font program, same word width/start; Vera **14 pt** retained | **Pass**, existing-glyph subset case. No error | Does not prove insertion of new glyphs, a general Unicode encoding path or use of a full replacement font. |
| `e3_rejected_glyph.pdf` | Inspect embedded subset cmap for U+2603; retain original candidate | No cmap contains requested snowman; byte-identical candidate; all pixels unchanged | **Pass for scripted missing-glyph refusal; actual missing-glyph insertion not tested.** No engine failure attempted | Glyph absence is concrete. A reusable safe font fallback/extension strategy remains unimplemented. |

Bold target width grows from **42.495003 pt** to **43.335007 pt**; both versions start at **(50,102) pt**. Compensation preserves the next word, not the replacement's width. In the italic case the target width shrinks by **1.442993 pt**; period boxes move from **[196.224030,124.637001,199.474030,140.509995]** to **[194.781036,124.637001,198.031036,140.509995] pt**. This explains a real neighbour movement that the earlier report left less resolved. It does not establish why the thresholded edge count differs across renderers.

### Experiment 4 - Saving and integrity

**Objective and expected outcome:** preserve untouched content, page count/boxes, images, fonts, annotations, metadata and supported structure while editing a table value. Source: `output/pdf/originals/integrity.pdf`, two pages, nonempty XMP, two bookmarks, note/link, embedded subset font, and cropped/rotated control page.

| Candidate | Approach | Actual outcome / metrics | Status / error / cause | Lesson |
|---|---|---|---|---|
| `e4_integrity.pdf` | `125.00` -> `175.00`; pikepdf save with `fix_metadata_version=False` | All **9** reported integrity flags true; outside pixels **0 / 0 / 0**; untouched page identical | **Pass within tested properties.** No syntax warnings | Explicit save policy matters; this does not certify all PDF structures. |
| `e4_default_metadata.pdf` | Same edit, default `fix_metadata_version=True` | **8/9** flags true; `xml_metadata` false. Outside pixels **0 / 0 / 0**. XMP string changes from **308** to **367** characters; original description retained | **Partial pass:** visual/content success, exact-XMP preservation failure. No corruption/API exception. Packet reserialization is established | Distinguish metadata serialization changes from user-field loss. A visual check cannot detect this difference. |

The measured properties and their limits are detailed in F. The cropped control retains MediaBox **[0,0,612,792] pt**, CropBox **[20,20,592,772] pt**, rotation **90 degrees**, and displayed page rectangle **[0,0,752,572] pt**. Image digests/locations and embedded font program hashes match. Nonempty fixtures avoid treating empty annotations/XMP/bookmarks as meaningful preservation tests.

### Experiment 5 - Document diagnostics and scan distinction

**Objective and expected outcome:** report extractability, span geometry/style, embedded fonts, image locations, page sizes and possible editing limits; distinguish text and raster content without claiming OCR.

The diagnostic CLI and **57 JSON outputs** contain document/page counts, boxes, rotations, extracted text, spans/directions/baselines/styles, font resources/encoding/type/subset/program hashes, images, annotation/link data, metadata/bookmarks, limitations and comparison results. Not all 57 are diagnostic documents: they include summary, tests and per-experiment metrics.

| Case | Approach / expected outcome | Actual outcome / metrics | Status / error / cause | Limitation and lesson |
|---|---|---|---|---|
| Digital samples (`basic`, `expansion`, `complex`, `integrity`) | Extract spans/fonts/pages and flag limitations | All pages contain digital text and are labelled `digital-text`; CLI output parses as JSON | **Pass for controlled diagnostics.** No final retained error | Extracted spans are not original authoring paragraphs or stable edit handles. |
| `e5_mixed_edit.pdf`, source `mixed.pdf` | Identify large raster plus caption; edit only digital `blue` -> `glue` | `mixed-or-OCR-candidate`; image digest/location unchanged; outside pixels **0 / 0 / 0** | **Pass**, digital-caption edit. No error | Raster letters were not edited. Classifier does not distinguish mixed visible caption from hidden OCR text. |
| `e5_scan_no_edit.pdf`, source `scanned.pdf` | Detect no text and page-sized raster; avoid native-text mutation | `scan-candidate`, no extractable text; byte-identical candidate | **Pass for classification/scripted non-edit; OCR editing not tested.** No exception | Scanned appearance is pixels, not editable native text. |

### Retained tests, errors and performance interpretation

`results/tests.json` reports **14 run, successful=true, zero failures/errors/skips**. Both retained test logs report 14 passing tests in **0.740 s**. Tests cover original hashes, semantic replacement, pypdf extraction, core integrity with an explicit expected XMP exception, unchanged pages, nine selected visually safe cases, expected overflow/advance changes, style/anchor equality, operand-edit font programs, nonempty integrity features, unchanged refusal copies, known-box wrapping, scan heuristics, overlay control and word counts.

The suite does **not** assert that the italic neighbour stays fixed, nor test it as one of the nine zero-outside cases. Some assertions consume previously saved flags rather than recomputing every render/resource check. Unchanged word counts do not establish reading order, accessibility or glyph position. Thus the passing suite and partial/failing candidates are consistent.

No unexpected API exception is present in the retained final run log. Intermediate development exceptions are not retained as a complete history, so this report does not reconstruct an error chronology. The important final failures are visual isolation, resource-identity changes and exact-XMP serialization, not inability to write a file.

The **36.79 s** total and **10.193-76.413 ms** edit/save range include different documents, libraries and caches. They exclude interactive input performance, controlled repeated benchmarking, peak memory, hostile inputs and large files. Clean dependency installation and a Python socket-blocked run are recorded; no offline installer, native-process network isolation or VM installation test exists.

## D. Existing PDF Text Editing

### 1. Identifying existing text objects

Demonstrated: MuPDF extracts spans/rectangles, styles, baseline origins and directions. The harness searches a known word and chooses a containing span. PDFium enumerates text page objects and identifies the line containing `blue`.

Unproven: a stable bidirectional map between a mouse-selected logical character and the correct encoded PDF instruction/glyph, especially across `TJ` arrays, per-glyph positioning, nested/shared forms, ligatures, missing ToUnicode, reordered content or multiple matching strings. The operand editor counts one matching encoded occurrence; it is not a hit-testing or selection system.

### 2. Editing existing words

Demonstrated: unique ASCII operand replacement and a PDFium line-object update produce genuine saved changes. The embedded subset example reuses available glyphs. Reconstruction through removal/reinsertion is a different working mechanism.

Unproven: unrestricted replacement strings, repeated matches, arbitrary encodings, new glyphs, complex scripts or general mixed-style span splitting. Physical-removal evidence here is not a secure-redaction audit of all revisions, attachments and hidden resources.

### 3. Fonts, positioning, styling and spacing

Demonstrated: reopened target font name, nominal size, packed RGB colour and start/baseline match on the twelve non-reflow edited cases. Program hashes match for embedded fonts in operand edits. This is target-start preservation, not all-glyph position preservation. Bold and italic neighbours move when advances differ. Hard-coded `TJ` compensation corrects the bold fixture.

Unproven: recovering a missing original font, licensing its reuse/embedding, adding glyphs to subsets, exact rendering across machines, character/word spacing and kerning under arbitrary transforms. Colour/size extraction alone is not a complete text rendering state.

### 4. Whole sentences or paragraphs

Demonstrated: PDFium resets one whole line object containing the changed word; a known complete sentence is removed and its replacement wrapped into two lines in an explicitly owned region.

Unproven: treating arbitrary lines as a coherent authoring paragraph, preserving mixed-style runs while reflowing, moving downstream objects or flowing across pages. PDF layout may lack a recoverable semantic ownership model. Tags, where present, do not universally supply original authoring layout.

### 5-7. Longer replacements, overflow, wrapping and reflow

Naive content replacement does not cause automatic layout. The expansion example proves collision. One original phrase is **50.028 pt** wide, but replacement is **362.148 pt** wide. That mismatch is not itself proof that editing must be rejected: the full paragraph region may be wider and have room for another line.

Known-box layout proves wrapping under supplied ownership, font and space assumptions. Expanding into adjacent blank space is a potential policy requiring collision/ownership analysis; it is not implemented. General paragraph/document reflow remains technically constrained by absent semantics and unavailable font/shaping data. Shrinking text or silently substituting fonts was not validated and should not become a hidden fallback.

### 8. Protecting surrounding content

Demonstrated: per-renderer raster comparisons, selected resource checks and untouched-page comparisons detect several changes. Zero outside pixels is meaningful at the tested threshold/resolution, but masks can contain a moved neighbour: the italic punctuation case establishes this limit. A production verifier needs glyph geometry, logical content and resource invariants as well as renders.

Not demonstrated: generic pre-edit collision detection, arbitrary clipping/shared-object protection, signed/encrypted/form/tagged-file policies or complete rollback under failed saves.

### 9. Genuine saved content versus overlays

The thirteen edited candidates reopen as changed PDFs. MuPDF/PDFium extraction and parsed operands verify targeted original text removal; retained tests add pypdf. The overlay negative control paints over `blue` and inserts `glue`, yet still extracts both: it does not meet the removal criterion.

A transient interactive text layer is nevertheless a sensible UI mechanism. It can provide caret/input/preview while the draft is being edited. It becomes a false editing claim only if exported output merely covers old content, or the UI presents an uncommitted visual draft as a verified saved PDF. The user must be able to distinguish draft appearance, engine preview and saved/reopened result.

## E. In-Place Text Editing Feasibility

**No interactive capability in the following table was implemented in Phase 1.** Categories assess the next technical investigation, not existing features.

| Desired capability | Classification | Basis and remaining work |
|---|---|---|
| Click an existing text region and place a caret | **Feasible but untested** for eligible simple text | Extracted bounds/object data exist; need screen-to-page transform, glyph hit-testing, logical offsets and caret metrics. Ambiguous mappings remain constrained. |
| Edit directly on the page rather than in a modal | **Feasible but untested** | A focused native text surface aligned to the selected page region can hold a draft. Font metrics, clipping, zoom and background compositing need proof. |
| Keyboard selection, deletion, insertion and navigation | **Feasible but untested** for the initial simple-text class | Reuse native text-input behaviour and maintain logical offsets. Mapping selections across PDF runs, IME, ligatures and bidi requires additional investigation. |
| Show typed changes instantly | **Feasible but untested** | Paint the working text locally; asynchronously request engine layout/preview. Recorded save times are not live-preview latency evidence. |
| Wrap naturally within an owned region | **Technically constrained** | Static known-box wrapping succeeded, but interactive rich-text wrapping was not built. Need explicit ownership, shaping, metrics and height limits. |
| Expand the editing region where space permits | **Requires further investigation** | Need available-space analysis, exclusion geometry and ownership policy. Arbitrary downstream movement is a separate unsolved feature. |
| Detect collisions with neighbouring content | **Requires further investigation** | Overflow was observed after editing; no generic preflight collision detector exists. Glyphs, vectors, raster regions, clipping and transforms must be considered. |
| Warn about overflow without discarding input | **Feasible but untested** | Keep text and pending layout in a draft model; warn or block export rather than rejecting keystrokes or resetting text. |
| Maintain editable working state independently of PDF output | **Feasible but untested** | Immutable source plus logical text runs, original mappings, selection, layout intent, history and draft revision. Current batch scripts have no persistent interactive session. |
| Undo and redo | **Feasible but untested** | Command history or state snapshots over the draft model, with deterministic engine regeneration. No implementation exists. |

### Recommended interaction and engine boundary

Use a dedicated interactive text layer with its own working state. For the first spike, select one eligible horizontal region, preserve its original font/style and seed a native text editor from its logical text. Enter editing by clicking the region; keep the caret and selection on the document. Do not open a replacement modal as the primary path.

Store the source region's baseline, glyph/object references, original run styles and bounds separately from draft text and candidate layout bounds. Let the user continue typing beyond the old word/line width. Wrap within an explicitly selected/owned paragraph area; if more space is needed, show the proposed new extent and any collision warning. Where ownership or font mapping is unsafe, preserve the draft and explain that committing/exporting it requires a supported layout choice. This is a recommended design, not a demonstrated solution for arbitrary PDFs.

The interaction layer should send a revisioned `plan_edit` request with session/source fingerprint, selected region identity, logical text/runs, intended boundaries and layout mode. The worker returns eligibility, glyph/font issues, proposed line geometry, collision locations and a candidate preview or a structured reason it cannot produce one safely. Ignore stale responses from older draft revisions; avoid blocking text input on rendering/saving.

On commit, the engine chooses a supported original-object/operand change or explicit region reconstruction, creates a new candidate PDF, reopens it and reports verification. A UI-only draft must not be reported as committed content. Distinguish **draft valid for editing**, **candidate layout has warnings**, **engine commit supported**, and **saved output verified**.

This approach can avoid the old modal/box-rejection experience without pretending PDF constraints disappear. It preserves user effort while placing safety checks at layout/commit/export boundaries. How accurately the interactive layer can match original font shaping and page compositing remains a key Phase 2 experiment.

## F. PDF Fidelity and Saving

| Property | Evidence and verification method | Conclusion and boundary |
|---|---|---|
| Original files | Persistent SHA256 manifest, recorded before/after hashes, current read-only rehash | Six originals unchanged. Failure-injected transactional saving not tested. |
| Content outside edited region | 144 DPI same-engine before/after pixels; all 81 page comparisons reconciled during handover | Good isolation in selected cases. Expansion/bold fail; italic geometry also moves despite tiny outside count. One resolution/threshold cannot certify universal fidelity. |
| Untouched pages | Full second-page comparisons, all three engines; recorded max channel delta zero | Pixel-identical in this corpus, including cropped/rotated control. This does not mean identical file bytes or all object identities. |
| Target style and anchor | Twelve non-reflow before/after font/size/colour/start comparisons | Match on those cases. Reflow intentionally changes layout; neighbouring glyph positions need independent checks. |
| Font resources/programs | Ordered lists of base font names plus embedded-program SHA256 | All operand-edit inventories match. PDFium/reinsertion/reflow inventories differ. The flag does not compare every font dictionary property or establish licensing rights. |
| Images | Bounding boxes and decoded-image digests from MuPDF; render checks | Match in retained cases. Encoded image stream byte identity and full colour-management fidelity not certified. |
| Page count/dimensions | Page count, MediaBox, CropBox, displayed rectangle, rotation | Match in every recorded candidate, including unchanged copies. Other page-box semantics were not comprehensively tested. |
| Annotations | Extracted type, rectangle and info; rendered appearances | Match for supplied text notes. Not a comprehensive check of every annotation dictionary/action/appearance stream. |
| Links | Extracted link properties ignoring xref numbers | Match for fixture links. Not all possible actions/destinations were exercised. |
| Metadata | Document info dictionary and exact extracted XMP string | Info matches. Default pikepdf changes XMP serialization; explicit setting preserves it here. Description retained in both. |
| Bookmarks/structure | `get_toc()` values, syntax warnings, multiple-library reopen | Two basic bookmark entries preserved; no syntax warning in edited files. This is not full document-structure equivalence or PDF conformance certification. |
| Untargeted text | Retained word multiset checks plus saved extraction | Other words survive. Counts can miss order, position, logical role and accessibility changes. |

There is no retained evidence of unreadable/corrupt output PDFs in the tested cases. There is clear evidence of **valid but visually unsafe** output, changed resource inventories, changed extraction order and XMP serialization differences. Those distinctions reconcile “save succeeded” with partial/failing results.

Not certified: forms/widgets, signatures, encrypted permissions, shared/nested forms, tagged accessibility, attachments/portfolios, incremental revision history, PDF/A, transparency/clipping, arbitrary transformations, print fidelity or all colour spaces. Saving to a distinct filename does not preserve a digital signature's validity. These require explicit eligibility and testing before a user promise is made.

## G. Scanned PDF and OCR Findings

The diagnostic heuristic labels a page:

- `digital-text` if nonempty extracted text exists without the large-image condition;
- `scan-candidate` if no extractable text exists and summed image area exceeds **80%** of page area;
- `mixed-or-OCR-candidate` if text exists and summed image area exceeds **80%**;
- `no-text-no-image` otherwise, although that label can also cover outline/vector text or small-image pages and should not be treated as a precise semantic classification.

Area is the **sum of image rectangles**, not their union or actual visible coverage. It can double-count overlaps and ignore clipping. A large decorative background can resemble a scan, and invisible OCR text can resemble a digital caption to this classifier. Real documents should be described page by page rather than forced into a single provenance label.

The synthetic scan contains only raster text. The mixed sample adds a genuine digital caption; only that caption was edited. No OCR engine, recognition-quality benchmark, OCR text-layer mutation, visible scan-text replacement, background reconstruction or OCR verification workflow was tested. Installed layout/ML-related dependencies do not change this conclusion.

OCR recognition can identify words but does not recover original fonts or remove visible letters from an image. Editing only an OCR text layer can alter copy/search behaviour while leaving the visible scan unchanged. Scanned content is a separate future editing problem, not an extension already proved by digital text replacement.

## H. Known Problems and Risks

Severity reflects impact on the intended experience, not how often the small corpus encountered it. Confidence refers to the proposed direction; untested mitigations are not guaranteed fixes.

| Problem / severity | User impact and established or suspected cause | Possible response / confidence | Could block intended experience? |
|---|---|---|---|
| Missing paragraph ownership/authoring semantics - **Critical** | Natural reflow may move the wrong material; PDF text can be independently positioned without recoverable paragraph intent | Explicitly owned regions and constrained reconstruction; **high** confidence for known layouts, **low** for universal recovery | **Yes**, for unrestricted Word-like editing; cannot be solved by UI alone. |
| Selection-to-glyph/operator mapping - **Critical** | A caret may target wrong content or a replacement may affect shared/repeated objects; Phase 1 uses known unique matches | Stable glyph/run/object mapping, encoding round trips and shared-resource policy; **medium**, untested broadly | **Yes**, for dependable arbitrary selection. |
| Font availability/subsets/shaping - **Critical** | Missing glyphs, changed appearance, invisible output or wrong character mapping | Verify glyphs/encoding, original font rights, controlled fallback with explicit intent; **medium** for simple cases, **low** for universal fidelity | **Yes**, when required font/glyph information is absent. |
| Expanded text and collisions - **High** | New text overlaps neighbours; no implicit layout follows operand mutation | Draft retention, bounded wrapping, expansion analysis, collision checks and explicit commit modes; **medium** | **Yes**, for unconstrained reflow; limited regions remain plausible. |
| Changed text advance - **High** | Surrounding words/punctuation move despite same font/start; demonstrated at +0.840/-1.443 pt | Per-glyph geometry and correct spacing/shaping; **high** for known simple metrics, **medium** generally | Can block fidelity until addressed; not inherently a UI problem. |
| No interactive layer - **High validation gap** | Natural caret/keyboard/instant preview experience has no evidence | Minimal native on-page text-input spike; **medium-high** for basic input, **medium** for exact PDF alignment | Not a demonstrated blocker, but core usability remains unproved. |
| Draft and export conflation - **High product risk** | Repeating old hard box rejection could discard user input or make typing frustrating | Separate draft state/warnings from commit/export; **high** design confidence, implementation untested | Avoidable UI/state failure; does not solve underlying layout limits. |
| Raster metric blind spots - **High** | Padded masks/threshold can hide shifted punctuation; zero outside count can overstate fidelity | Add glyph-neighbour invariants, multiple resolutions and independent renders; **high** | Can invalidate acceptance claims if ignored. |
| Shared forms, clipping, transformed/fragmented text - **High, untested** | Apparently local changes may affect repeated content, break placement or rendering | Dedicated fixtures, structure inspection and deterministic unsupported handling; **medium** | Possibly; no evidence establishes coverage. |
| Resource inventory/reading-order changes - **Medium-High** | Looks correct but changes extraction/accessibility/resource identity | Compare required font programs/logical order; use original-object path where supported; **medium** | Can block strict preservation and accessible output promises. |
| Save metadata defaults - **Medium** | XMP changes unnoticed by visual review | Explicit save policy and metadata checks; **high** for the observed setting | Not a general blocker; exact preservation must be deliberate. |
| Corruption/recovery and special structures - **High, untested** | Lost edits, damaged destinations or invalid signatures/forms on failure | Read-only source, temporary candidate, reopen/verify, atomic destination commit, recovery/failure tests; **medium**, not implemented | Blocks production readiness until validated. |
| Distribution/license composition - **High** | A purported closed-source pipeline still imports AGPL PyMuPDF; native/font notices required | Choose application license or suitable commercial rights; remove inappropriate runtime dependencies if needed; **medium** until reviewed | Can block the intended distribution model. |
| Offline packaging/security/performance - **High validation gap** | Missing DLL/runtime, network dependency, worker crash/hang, slow large documents | Clean offline VM, native worker limits/updates, cancellation and measured workloads; **medium** | Can block reliable Windows delivery, not shown by the tiny corpus. |
| Scan/OCR misclassification - **Medium-High** | User clicks raster letters expecting native text editing | Page-level content analysis and clear unsupported/OCR state; **high** for basic distinction, **low** for universal provenance | Blocks the same editing promise for scanned text; separate work required. |

### Reconciliation of earlier statements

1. **“14 tests pass” versus unsafe candidates:** tests intentionally check known failures; nine selected cases get the zero-outside assertion. No contradiction once success criteria are scoped.
2. **“Font preserved” versus false inventory flags:** target style/program can survive while resources are reordered, renamed, added or unused entries removed. Neither visual font equality nor inventory equality alone proves all font semantics.
3. **“Reflow works” versus no automatic paragraph reflow:** wrapping is known-box sentence reconstruction. Generic paragraph inference and downstream layout are not implemented.
4. **“Refusal implemented” versus no eligibility engine:** specific copied refusal cases demonstrate reasons and non-modification, not automatic handling of arbitrary edits.
5. **“Only one outside pixel” versus unchanged neighbours:** handover geometry inspection confirms italic punctuation movement. Its cause is narrower replacement advance; the renderer-specific edge count remains a separate detail.
6. **“Offline validated” versus no offline installer:** socket-refusal execution and clean Python dependency/test evidence support exercised local paths. They do not sandbox native processes or prove packaging on a disconnected VM.
7. **“Adopt native PDFium/WPF” versus a Python-only laboratory:** the recommendation is a direction for the next proof, not an implemented or benchmarked architecture.

## I. Recommended Architecture

**Proposed, not implemented:** Windows .NET/WPF interaction shell, dedicated text-editing model/layer, isolated local PDF worker, PDFium as primary candidate, optional qpdf structural support, independent development validation. Keep technology adapters replaceable until mapping, shaping and save behaviour are proven.

```text
Windows document surface (.NET/WPF candidate)
  Page tiles + zoom/scroll transforms + native keyboard/IME input
                  |
                  v
Interactive text layer / draft session
  Logical text runs, caret/selection, original glyph mappings
  Draft boundaries, pending layout, warnings, undo/redo
                  |
          revisioned local commands
                  v
Isolated PDF worker (PDFium candidate; qpdf when useful)
  Inspect/map -> plan layout -> check glyphs/collisions
  Mutate original content OR reconstruct an explicit region
                  |
                  v
New temporary PDF -> reopen -> semantic/resource/visual checks
                  |
          verified Save As / export commit
                  v
New destination file; immutable source remains available

Independent reference renderers/checks: development evidence
Recovery: retain draft/history and last verified candidate
```

| Responsibility | Proposed owner / contract |
|---|---|
| PDF rendering | Worker uses PDFium, supplies page tiles/geometry keyed by document revision and zoom. UI caches/displays and cancels stale work. |
| Text extraction/analysis | Worker identifies objects/glyphs/fonts/rendering state; returns stable logical mappings and limitations, not merely text strings. A production-only path without PyMuPDF must still be proved if required by licensing. |
| Interactive editing | UI draft layer owns input, selection, local feedback, history and pending text. It does not perform blocking save/render work per keystroke. |
| Layout and collision planning | Worker/application layout adapter returns proposed line/glyph boxes and exclusions. UI presents warnings and preserves unsaved text. |
| Document modification | Worker chooses supported original-object/operand mutation or explicit reconstruction. It reports what changed and any substitution. |
| Save/export | Candidate written to a new temporary file, independently reopened/verified, then committed to a new destination. Export errors do not discard the draft. |
| Validation/recovery | Track immutable source hash, session/draft revisions and last verified state. Keep structured errors; discard stale worker results. Failure-injected atomic saving and recovery are future tests. |

Commands should include `inspect`, `plan_edit`, `preview_edit`, `commit_candidate` and `save_as`, with source/session/revision identifiers and structured error results. A returned bitmap or successful mutation API is not sufficient to declare commit success. Use local IPC; large images should use efficient buffers/files rather than large JSON base64 strings.

The original pypdfium2 guidance says PDFium calls must not run concurrently across threads; serialize calls in a worker and use separate processes for parallel rendering if needed. Process separation also limits UI exposure to crashes and long-running document work, but is not a substitute for security review or a licensing workaround. No such worker boundary exists in the current scripts.

All document processing, fonts and draft state should remain local. Bundle only required production components with reviewed notices and native runtime dependencies. For Tauri, offline WebView2 packaging is an additional consideration. The shell choice should remain provisional until the in-place input spike demonstrates caret alignment, font matching, keyboard behaviour and responsive previews.

## J. Phase 2 Recommendations

### Narrow objective

**Prove one direct-on-page editable text region, with genuine verified PDF commit and retained draft on overflow or failure.** This is more directly aligned with the user's usability goal than another batch-only replacement milestone. It refines the previous CLI-first proposal; no old report is modified and no implementation has begun.

### Proposed implementation scope

1. Build a minimal local Windows document surface showing one eligible horizontal digital-text region. Clicking places a caret at a mapped character. Use native text input for selection, typing, deletion and navigation; no modal as the primary editor.
2. Introduce a logical draft model independent of the PDF: original region/run mapping, editable text, selection, layout boundaries, revision and undo/redo. Preserve input on every warning/error.
3. Prove two explicitly named commit modes: a simple original-object correction where mapping/glyphs/advance are supported, and complete **owned-region reconstruction** for a plain-text paragraph. Do not silently switch mechanisms or substitute fonts.
4. Demonstrate bounded natural wrapping. Start with an owned region known to have vertical space. Separately test region expansion into a deliberately empty area versus a neighbouring object; show preview/warnings and preserve the draft when expansion is unsafe.
5. Produce candidate PDFs through the selected engine path, reopen independently, check removal/replacement and geometry/resources, then Save As. Keep the immutable source and last verified state intact.
6. Decide licensing composition and exercise a minimal offline Windows packaging check. PDFium-first inspection/mutation should not silently depend on an incompatible runtime component.

These are proposed experiments, not a guarantee PDFium alone supplies all layout/reconstruction functions. Engine/layout-adapter dependency choices must be justified with the subset-font and glyph-mapping tests.

### Deliberate exclusions

Exclude a finished editor, toolbar/ribbon design, document management, cloud services, full formatting controls, arbitrary rich-text paragraphs, automatic multipage/document reflow, moving unrelated content automatically, scan/OCR editing, font recovery from missing data, forms/signature editing, accessibility conformance claims and universal file support. Unsupported files may remain viewable; do not imply their text can be safely committed. IME/bidi/complex scripts should be explicitly unsupported in the first English/ASCII editing proof, while using an input architecture that can be extended later.

### Acceptance criteria and required tests

| Area | Required proof before expanding scope |
|---|---|
| Direct interaction | Click beginning/middle/end and inter-glyph positions at two zoom levels; correct caret and selection. Test typing, Backspace/Delete, arrows, Home/End, Shift-selection, paste and focus transitions. |
| Draft retention | Type beyond the original word/line width; no keystroke rejection based solely on the old rectangle. Unsafe layout produces visible state/warning; draft survives warning, failed commit, cancellation and worker restart. |
| Owned-region wrapping | Longer text forms expected lines within an explicit region, with fonts/styles and bounds verified. Expansion into free space is distinguished from collision; neither silently moves unrelated objects. |
| Instant feedback | Local typed text appears without blocking on PDF generation. Instrument input-to-paint and worker-preview latency; report actual measurements/hardware. No achieved latency target is inherited from Phase 1's edit/save timings. |
| Genuine commit | At least two independent extractors confirm replacement and targeted-old-content removal after reopen; overlay-only control fails. Verify logical text order as well as word counts. |
| Neighbour fidelity | Check unaffected glyph positions, not just padded raster masks. Reproduce and address bold +0.840 pt and italic -1.443 pt shifts; test explicit character/word spacing and unequal-width replacements. |
| Render/resource fidelity | Two independent renderers at two resolutions, declared regions, explained differences only. Preserve required font programs/images, annotations, boxes, links and supported metadata/bookmarks. |
| Font/encoding eligibility | Include subset available-glyph and missing-glyph cases, fragmented `TJ`, repeated text, non-identity encoding and missing mappings. Refuse unsupported commit while retaining draft; no silent font substitution. |
| History | Undo/redo typing, deletion, paste, wrapping and accepted layout changes; regenerate equivalent candidates deterministically. |
| Save/recovery | Locked destination, failed write and worker failure leave the source unchanged and no incomplete file presented as verified. Keep user text available for recovery. |
| Corpus | Reuse all Phase 1 artifacts, add targeted adversarial fixtures and a small initial set from at least three independent producers. Record provenance and each acceptance/refusal. The earlier 30-document corpus remains a broader robustness gate, not a prerequisite to demonstrating one input interaction. |
| Offline/distribution | Minimal x64 Windows run on a clean disconnected VM with required native/runtime dependencies and license inventory. No online document/font service. |

### Dependencies, risks and review decision

Dependencies are a stable extraction-to-edit mapping, usable original font metrics/programs, an interactive text-layout/input surface, explicit paragraph ownership, collision/exclusion geometry, a verified engine commit adapter and source-safe persistence. Missing glyphs, shared resources, mixed encodings, clipped/transformed content and mismatch between UI/PDF shaping are the main technical risks.

The first review should examine one end-to-end interaction: **click -> type a longer replacement -> wrap or warn without losing input -> undo/redo -> commit supported layout -> reopen verified PDF**. Report both accepted and unsupported cases without counting refusals as edits. Stop and reconsider the layout/engine/SDK choice if simple region ownership or correct glyph encoding cannot be achieved; do not conceal the gap behind a polished interface.

**Planning decision:** sufficient evidence exists to authorize designing that tightly scoped proof. It does not yet justify product-level reliability promises, arbitrary paragraph reflow, a full Windows editor or automatic continuation beyond the next review gate. All implementation remains future Codex work after a subsequent development instruction.
