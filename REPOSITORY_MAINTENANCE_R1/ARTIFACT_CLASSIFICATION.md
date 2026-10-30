# R1 artifact classification

All 17,039 starting tracked paths are classified in inventory/artifact-classification.csv.gz, with SHA256, Git blob, logical size, proposed tier and current disposition. No existing artifact is removed. Initial heuristic unknowns were five historical root/build logs; they are retained as F, not discarded as caches.

| Class | Files | Bytes |
|---|---:|---:|
| A | 789 | 4,416,770 |
| B | 90 | 561,956 |
| F | 14,718 | 842,530,514 |
| D | 429 | 173,454,667 |
| C | 881 | 20,691,236 |
| E | 132 | 9,443,031 |

- A — Essential source: C#, projects, test implementations, build/configuration and dependency requirements. Keep in Git; never clean source or generated .cs using the cleanup tool.
- B — Essential documentation: handovers, architecture/decisions, test methodology, open issues. Keep in Git.
- C — Essential fixtures: regression PDFs, fixture definitions, source example data. Keep necessary fixtures in Git; redistribution rights need separate review.
- D — Third-party dependencies: pinned native programs/fonts and every licence/attribution notice. Existing historical copies stay. Future restorations use a hash-pinned canonical cache; notices accompany distributions.
- E — Release/reference binaries: retain each historical release/reference until provenance, reproducibility and an authorised versioned destination are verified. Managed/PDB byte equivalence is not established, so none are deleted.
- F — Generated evidence: preserve authoritative results, important failures, unique forensic records and independently verified examples. Tier 2 archive proposals require semantic review and verified destinations. Current tracked copies stay intact.
- G — Disposable intermediates: no starting tracked files were classified G. Ignored SDK caches/build outputs may be reproducible, but that is not deletion permission. Unique local files remain protected until assessed.

Directory-level local essential/reproducible/preservation classifications are in inventory/local-directory-classification.json and LOCAL_WORKSPACE_AUDIT.md. A directory label never authorises deleting its entire tree. Proposed archive manifest includes 14,850 E/F paths / 851,973,545 bytes (812.51 MiB); every row is **unapproved, destination unverified, retain in place**. A candidate is not a completed migration. Full preserved evidence remains available while the minimum-record index is reviewed.
