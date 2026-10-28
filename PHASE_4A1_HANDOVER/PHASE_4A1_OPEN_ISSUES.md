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
