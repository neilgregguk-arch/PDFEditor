# Phase 5.1 compatibility matrix

| Actual fixture / behaviour | Phase 4C.2 | Phase 5.1 |
|---|---|---|
| Genuine Word letter, fitting single row | Verified original-font editing | Retained; eligible bounded exports can carry one-row identity |
| Genuine Word third paragraph, new two-row export | Wrapped output, independent rows on reopen | Complete logical group in a fresh process |
| Consecutive two → three → one generations | No whole-paragraph relationship | Verified stable ID, new source bindings and exact row removal |
| Word Arial / Calibri | Verified wrapping, limited paragraph rediscovery | Repeated whole-group generations; inherited font/caret policies retained |
| Legacy unmarked C2 wrapped PDF | Independent eligible/Limited lines | Same conservative classifications; no retroactive grouping |
| General original Word multi-line layout | Ambiguous cases restricted | No new generic heuristic promotion |
| Natural paragraphs | Bounded existing discovery/editing | Retained; not converted into arbitrary editor-marked Word groups |
| Reopened group + other Word + natural on another page | Could not restore whole group | History, recovery and combined export verified |
| Two groups whose expansions collide | Combined collision protection | Same refusal, both full drafts retained |
| Long word ending in a one-character row | Verified C2 export | Verified export and validated member set |
| Whole paragraph deletion | Text removal | All members removed, no invisible ownership tombstone |
| External save retaining consistent marks | No group mechanism | pikepdf save/re-edit verified; not a guarantee for every editor |
| Changed/missing/duplicate/conflicting members | Independent-line fallback | Marked group restricted; no new proximity recovery |
| Stripped private marks | Not applicable | Legacy classifications; whole group no longer promised |
| Repeated spaces / positioned hard breaks | Exact-extraction/newline restrictions | Exact draft/recovery retained; demonstrated unsafe exports still refused |
| Unsupported glyphs/fonts, mixed styles, transforms | Restricted | Existing restrictions retained; metadata cannot override them |
| Unsupported existing accessibility scope | No round-trip mechanism | Refused rather than stripped or fabricated |
| Clipboard Win32 error 5 | Historical intermittent issue | Still fails in this session on both versions |

Genuine inputs remain the existing `run/corpus/11-word-letter.pdf` and `run/font-corpus/Word-Arial.pdf` / `Word-Calibri.pdf`. Read-only copies of certified outputs are supplied under `run/paragraph-examples/`; their manifest identifies the originating evidence and SHA256. The 32-group performance page and adversarial files are explicitly derived development fixtures, not simplified substitutes for the genuine Word acceptance cases.

Support applies to the demonstrated bounded ASCII/original-font model. No font substitution, subset rebuilding, OCR, mixed-font reconstruction or cross-page paragraph flow was introduced. Structure preservation does not constitute PDF/UA or arbitrary-editor compatibility certification.
