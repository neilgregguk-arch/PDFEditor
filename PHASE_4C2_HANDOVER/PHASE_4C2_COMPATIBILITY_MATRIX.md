# Phase 4C.2 compatibility matrix

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
