# Phase 4C.1 compatibility matrix

The matrix describes executed local fixtures, not arbitrary PDFs with the same producer/font name. Every newly allowed character must have a verified original PDF mapping; no font program is rebuilt or replaced.

| Source / feature | Phase 4B | Phase 4C.1 evidence |
|---|---|---|
| Genuine Word letter, three Arial lines | Same-count equal/narrower substitutions | Preserved, plus start/middle/end insertion, multiple insertions, deletion/range replacement, empty title and second generation |
| Word-Arial `cafe calm. cafe calm.` | Fixed-origin substitutions; narrower-gap extraction failure possible | Insert ` cafe`, remove word/characters, different-length replacement; verified outputs preserve source font and surviving pair spacing |
| Word-Calibri same sample | Fixed-origin substitutions | Same insertion/deletion/replacement cases verified; visible caret/selection corrected for measured native drift |
| Natural Prototype paragraphs | Bounded wrapping/expansion | Existing engine/discovery/font tests remain passing; combined natural + Word edits on different pages pass |
| Same-count wider mapped replacement | Refused | Recalculated single-line path allowed only if spacing/ink/bounds and complete export verify; tested letter `...letWer` |
| Fixed-origin equal/narrower replacement | Supported under existing gates | Same fixed origins and original-font checks retained |
| New f/f/f overlap | Refused by old count rule | Refused by new ink-overlap rule; draft retained |
| Double-space insertion with extraction collapse | Refused by old count rule | Saved text mismatch blocks output; draft retained |
| Unsupported snowman / unmapped punctuation | Refused | Refused; other drafts remain editable, complete export blocked |
| Horizontal overflow or protected graphic ahead | Refused by old count rule | Eligible source activates, but expanding draft is refused without wrapping or moving graphics |
| Positioned newline / paragraph reflow | Refused | Still refused; natural paragraph wrapping is a separate strategy |
| Word-multiple-runs mixed-font line | Ambiguous/restricted | Remains restricted; no run merging |
| Word Consolas / PowerPoint protected cases | Existing ownership/graphic restrictions | Not newly promoted; no expanded compatibility claim |
| ReportLab artificial character spacing / kerning metric mismatch | Metric gate refused | Gate retained; no 0.01 pt relaxation |
| Visible or nonzero separately owned whitespace | Protected/restricted | Still protected; only verified nonpainting zero-extent coexistence exception retained |
| Signatures, encryption, forms/annotations, unsupported transforms/clipping | Existing safety gates | Unchanged; no authoring support added |

The final tests include source-hash and identity rejection, destination protection, worker restart, chronological multi-region history, recovery across distinct exited processes, combined output and second-generation rediscovery. A source may expose several eligible lines while still containing unsupported regions. Reopening a fully deleted line cannot recreate its former region: it has genuinely been removed; other surviving regions remain discoverable.

Spacing recalculation supports up to 512 original/draft characters per positioned line. Existing fixed-origin substitutions retain their prior path. Combined export retains the Phase 4B maximum of 128 modified regions. The same-source session base remains original after Save As; reopen the output for a new generation. See the test report for exact counts and the issues report for semantic PDF, recovery and packaging limits.
