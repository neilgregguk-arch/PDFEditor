# Phase 5.2 test results

Executed in Codex on Windows x64, 29 October 2026. The final engine/worker/native hashes remain identical to the fully tested binaries. The final app changes only its phase caption and passes an additional 3/3 original WPF smoke checks with independently verified export. Evidence paths below are under phase5_2/evidence; commands are in the user guide.

| Suite | Actual result | Evidence |
|---|---:|---|
| Current engine/discovery/compatibility/position/insertion/document/wrap | 151/151 | seven *-tests.json files |
| Existing Phase 5.1 roundtrip/adversaries | 37/37 | roundtrip-tests.json |
| New original/authentic/adversarial/mixed worker checks | 31/31 | original-tests.json |
| Session/layout/identity models | 35/35 | model/model-tests.json |
| Existing six exited WPF paragraph processes | 16/16 | paragraph-controls.json |
| New five exited WPF original/recovery processes | 12/12 | original-controls.json |
| Inherited WPF full run | 55/57 initially | controls-shipping/ |
| Current basic-suite retry | 10/11 | basic-retry-phase5_2-*/ |
| Untouched 5.1 basic suite | 10/11, same clipboard failure | basic-retry-phase5_1-*/ |
| Combined exports, independent readers | 119/119 | wrap-independent-verification.json |
| Combined marked/semantic structures | 119/119; 124 group instances | paragraph-structure-verification.json |
| Position / legacy independent outputs | 11/11 and 21/21 | position-independent-verification.json; independent-verification.json |
| Frozen C2 worker suites | 151/151 | frozen-phase4c2/ |
| Frozen C2 combined independent exports | 52/52 | frozen-c2-readers/ |
| Historical Phase 1 | 14/14 | frozen-phase1-tests.log |

The first full WPF run had the known clipboard Win32 5 failure and a transient unsupported-glyph diagnostic assertion under concurrent load; its exact snowman draft remained present. Retrying the basic suite passes that assertion: 10/11 on both current and untouched 5.1, each failing only clipboard. The other 46 inherited checks pass. Latest individual suites account for 56/57, but this is not represented as one clean 57-check run. No clipboard or unrelated diagnostic defect is claimed fixed.

Other frozen runs pass previous counts: Phase 2 18/18; Phase 4A and 4A.1 engine 18/18 each; Phase 3 discovery 22/22; Phase 4A compatibility 23/23; Phase 4B document 17/17 and position 20/20; C1 insertion 30/30, document 17/17 and position 20/20. The original Phase 2 suite against Phase 3 remains 17/18 because of the historical manifestless-view-only expectation; it is retained, not a new current-engine failure.

## New acceptance and negative coverage

Five authentic originals have independent producer, text, font and metadata checks. Cafe and letter qualify as complete two-row groups. Calm and longer multiline retain bitmap restrictions; nearby short separate paragraphs are not merged. Exact member strings, including explicit spaces, equal MuPDF drawing traces. Source bytes are never preprocessed to manufacture a positive. Three fresh-worker editing generations preserve original fonts and establish/retain complete declarations. Original-boundary insertion/deletion/replacement pass; unsupported characters, hard breaks and height overflow are refused.

Negatives cover missing/changed structure, heading/table/list/header/footer roles, wrong backlinks/K/StructParents, duplicate/swapped parent associations, ActualText, duplicate native MCID scopes, interleaved whitespace, ambiguous separators, column/label geometry, reversed reading order, rotated/clipped rows, mixed font size, protected graphics and unsupported xref-stream-only syntax. Inherited suites retain their table/column/mixed-font/unsupported-mapping cases.

A derived four-page document contains an original group, a genuinely saved marked group, a natural paragraph and another-page edit. Four changes save atomically. New separate WPF processes test every original row, all caret offsets at four zooms, Up/Down/Home/End/shift, mapped drag, boundary Backspace/Delete, selected replacement, three save generations, inactive drafts, global history, exited-process recovery of all four drafts and unsafe/no-subset export. Existing source/revision/conflict/failed-Save-As tests pass. These are actual WPF controls/commands/routed events/shared hit handlers at 96 DPI, not physical input/dialog automation or OS-scale certification.

## Independent fidelity and visual review

MuPDF traces, pypdf, pikepdf/qpdf syntax, fontTools mapping/outlines/metrics and Poppler at 72/144 DPI verify complete logical text, used font rules/programs, glyph origins/baselines, untouched content/whitespace, page properties and zero changed pixels outside authorised areas above channel threshold 8. Geometry remains 0.01pt. Structure checks cover complete private groups, exact row sets/payloads, original semantic sequences, StructTreeRoot/MarkInfo/Lang and page StructParents. Coverage assertions prevent zero-group/vacuous passes. Frozen engine records remain separate; untouched 5.1 comparison exports are excluded from current-engine identity validation.

Rendered PDF and WPF contacts were inspected: original source geometry is retained before editing, edited rows use established conservative leading, references stay fixed and shortened output leaves no old row. WPF captures show editing/validation state; successful exports are proven by result JSON. portable-pdf-index.json maps all 174 independently checked source/destination paths to retained files. Temporary font/candidate/cache paths in raw logs are non-authoritative and regenerable.

## Performance

One authentic two-row source: cold inspection including render 462.00ms; grouping/raw proof 73.34ms; median of 20 warm inspections 39.37ms. Candidate total 374.17ms (planning 131.34, generation 21.75, reopen verification 186.61). RSS delta 24,461,312 bytes; handle delta 0; worker exited. Original WPF row activation took 263.08 and 188.36ms including Open/dispatcher work. original-performance.json includes a same-authentic-source 5.1/current comparison.

Four-page cold inspections: 489.69, 209.60, 129.64 and 131.37ms. Its separate 20-inspection sample records RSS delta 60,346,368 bytes and handle delta 0, followed by worker exit. Existing wrap controls record median local calculation 0.247ms across 30 input/wrap operations, with zero immediate worker requests. See original-page-performance.json and controls-shipping/wrap-control-tests.json. These local/concurrent samples do not certify large-document performance. RSS changes are specific samples, not whole Codex-session measurements or proof of a leak. No broad memory refactor was performed.

## Retained failures and corrections

Progress/investigation records retain initial Word author-property COM failures, the unavailable GetRawType native export, absent-attribute interpretation, hybrid free-placeholder/object-stream handling and revision-precedence corrections. New tests initially and correctly refused a too-tall 14-repeat draft, a replacement accidentally containing adjacent spaces, and relocation of a page-0 declaration to page 1. The mixed fixture now establishes its page-1 declaration through a genuine verified save. An overbroad whitespace exemption failed the existing protected-whitespace case; narrowing it to the actual shared paragraph scope restores 37/37. Raw failures remain visible. No tolerance, source fixture history or failed expectation was hidden to force success.
