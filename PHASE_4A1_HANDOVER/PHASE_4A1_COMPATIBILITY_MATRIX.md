# Phase 4A.1 compatibility matrix

28 October 2026. Both binaries inspected identical bytes. E/L/V are counts of Editable/Limited/View Only regions, not document acceptance percentages. Activation does not guarantee every draft can export. Position models use fixed origins; natural models retain wrapping. Full observations/timings are in `phase4a1/evidence/position-matrix.json`.

| Source under run/ | Phase 4A E/L/V | Phase 4A.1 E/L/V | Actual edit evidence or restriction |
|---|---|---|---|
| corpus/01-letter.pdf | 5/0/0 | 5/0/0 | Natural-layout behavior retained; specific saves and negative cases in discovery/compatibility suites. |
| corpus/02-report.pdf | 4/0/0 | 4/0/0 | Natural-layout behavior retained; specific saves and negative cases in discovery/compatibility suites. |
| corpus/03-adjacent.pdf | 1/0/2 | 1/0/2 | Natural-layout behavior retained; specific saves and negative cases in discovery/compatibility suites. |
| corpus/04-two-columns.pdf | 0/0/10 | 0/0/10 | Remains restricted; exact font/transform/ownership reasons in JSON. No export claimed. |
| corpus/05-table.pdf | 0/0/6 | 0/0/6 | Remains restricted; exact font/transform/ownership reasons in JSON. No export claimed. |
| corpus/06-ambiguous.pdf | 0/2/0 | 0/2/0 | Remains restricted; exact font/transform/ownership reasons in JSON. No export claimed. |
| corpus/07-rotated.pdf | 0/0/1 | 0/0/1 | Remains restricted; exact font/transform/ownership reasons in JSON. No export claimed. |
| corpus/08-nonembedded.pdf | 0/0/1 | 0/0/1 | Remains restricted; exact font/transform/ownership reasons in JSON. No export claimed. |
| corpus/09-mupdf-letter.pdf | 3/0/0 | 3/0/0 | Natural-layout behavior retained; specific saves and negative cases in discovery/compatibility suites. |
| corpus/10-mupdf-subset.pdf | 0/0/3 | 0/0/3 | Remains restricted; exact font/transform/ownership reasons in JSON. No export claimed. |
| corpus/11-word-letter.pdf | 0/0/3 | 3/0/0 | Position title reconstruction, Phace, narrower Oflice, rediscovery/second save; other two lines activation measured. |
| corpus/12-image-overlap.pdf | 0/1/0 | 0/1/0 | Remains restricted; exact font/transform/ownership reasons in JSON. No export claimed. |
| corpus/13-shuffled-order.pdf | 1/0/0 | 1/0/0 | Natural-layout behavior retained; specific saves and negative cases in discovery/compatibility suites. |
| corpus/14-annotation.pdf | 0/0/1 | 0/0/1 | Remains restricted; exact font/transform/ownership reasons in JSON. No export claimed. |
| corpus/15-letter-spacing.pdf | 0/0/1 | 0/0/1 | Restricted: additional position metric-rounding guard; no release export claimed. |
| font-corpus/A-subset-existing.pdf | 1/0/1 | 1/0/1 | Natural-layout behavior retained; specific saves and negative cases in discovery/compatibility suites. |
| font-corpus/B-original-only.pdf | 1/0/1 | 1/0/1 | Natural-layout behavior retained; specific saves and negative cases in discovery/compatibility suites. |
| font-corpus/C-subset-bold.pdf | 1/0/1 | 1/0/1 | Natural-layout behavior retained; specific saves and negative cases in discovery/compatibility suites. |
| font-corpus/D-fragmented.pdf | 0/1/2 | 0/1/2 | Remains restricted; exact font/transform/ownership reasons in JSON. No export claimed. |
| font-corpus/E-character-spacing.pdf | 0/0/2 | 0/0/2 | Restricted: additional position metric-rounding guard; no release export claimed. |
| font-corpus/F-kerning.pdf | 0/0/2 | 0/0/2 | Restricted: additional position metric-rounding guard; no release export claimed. |
| font-corpus/G-duplicate-unicode.pdf | 1/0/1 | 1/0/1 | Natural-layout behavior retained; specific saves and negative cases in discovery/compatibility suites. |
| font-corpus/H-wrong-unicode.pdf | 0/0/2 | 0/0/2 | Remains restricted; exact font/transform/ownership reasons in JSON. No export claimed. |
| font-corpus/I-missing-unicode.pdf | 0/0/2 | 0/0/2 | Remains restricted; exact font/transform/ownership reasons in JSON. No export claimed. |
| font-corpus/J-partial-encoding.pdf | 1/0/1 | 1/0/1 | Phase 4A gain retained: existing mapped-character edits and longer natural wrapping; unmapped Z refused. |
| font-corpus/PowerPoint-Arial-subset.pdf | 0/0/2 | 0/2/0 | Graphics/background ownership restriction retained. |
| font-corpus/Word-Arial.pdf | 0/0/2 | 2/0/0 | Fixed-position first line: ccfe, then cclm; two independent verified saves. Other line activation only. |
| font-corpus/Word-Calibri.pdf | 0/0/2 | 2/0/0 | Fixed-position first line: ccfe, then cclm; two independent verified saves. Other line activation only. |
| font-corpus/Word-Consolas.pdf | 0/2/0 | 0/2/0 | Natural glyphs but separately owned space still blocks conservative ownership; not promoted. |
| position-corpus/adjacent-label.pdf | 0/0/2 | 0/0/2 | Adjacent label, intersecting graphic or restricted boundary: first region refused. |
| position-corpus/nearby-graphic.pdf | 0/0/1 | 0/0/1 | Adjacent label, intersecting graphic or restricted boundary: first region refused. |
| position-corpus/restricted-boundary.pdf | 0/0/1 | 0/0/1 | Adjacent label, intersecting graphic or restricted boundary: first region refused. |
| position-corpus/visible-whitespace.pdf | 0/0/1 | 0/0/1 | Visible glyph mapped to space; nonzero geometry remains protected. Refused. |
| position-corpus/Word-multiple-runs.pdf | 0/0/4 | 1/2/1 | Mixed-font first line remains ambiguous; no mixed-run merging. Other regions assessed individually. |

Saved and reopened outputs are tested separately in position-tests.json and the WPF position-control evidence. Position-aware edit eligibility is reassessed each generation; no synthetic ownership metadata is attached. More resource aliases can appear on later saves while pointing to the same unchanged font dictionary.

Equal character count is required but insufficient. Only mapped ASCII substitutions no wider than the original slot are planned; actual ink/extraction/candidate checks can still refuse. Missing cmap, wrong Unicode, missing encoding, unsupported transforms/pages and unrelated ownership checks remain active. No general Word support, mixed formatting, arbitrary kerning, longer positioned text or multi-region commit is claimed.
