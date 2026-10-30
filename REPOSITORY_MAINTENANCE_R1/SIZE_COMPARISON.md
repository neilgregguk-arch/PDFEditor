# R1 measured size comparison

| Metric | Before | After maintenance audit checkpoint |
|---|---:|---:|
| Tracked paths at snapshot | 17,039 | 17,086 |
| Tracked logical bytes | 1,051,098,174 | 1,054,374,637 |
| Entire workspace files | 45,907 | 48,074 |
| Entire workspace logical bytes | 2,365,115,376 | 2,490,639,782 |
| Git metadata logical bytes | 82,031,546 | 84,951,711 |
| Tracked duplicate logical bytes | 434,806,976 | 434,833,408 |
| Historical phase evidence directories | 849,646,616 | 849,646,616 |
| SDK project bin/obj directories | 30,972,930 | 30,976,756 |
| New .local-generated staging | 0 | 119,321,672 |
| Actual Git .pack payload bytes | 79218973 | 79218973 |

After snapshot: 2026-10-30T12:11:04.973259+00:00 to 2026-10-30T12:12:32.324489+00:00. Actual workspace logical growth at that checkpoint: 125,524,406 bytes. This includes validation/dependency staging and the then-existing R1 metadata. Later copying this summary, report updates and normal commit bookkeeping can change live bytes; it is a timestamped measurement, not a perpetual size claim.

Git's baseline count-objects and after count-objects are retained in the snapshot JSON. Baseline5packs/77,627KiB; no repack/history rewrite. Ordinary maintenance commits add small objects; removing paths cannot remove bytes retained in historical commits. Tracked build/dependency and evidence footprint by phase is in classification-summary.json; all historical content remains. Added bulk build/tests live under ignored .local-generated; their measured size is in after-summary.json when captured.

**Actual deletion savings:0bytes. Actual tracked historical paths removed:0. Approved archive migrations:0. Destructive cleanup runs:0.** Planned local cleanup is only 2 host files / 303,616 bytes (0.29 MiB); not performed, not physical allocated-disk savings. Broader 851,973,545 bytes (812.51 MiB) archive proposals and 434,806,976 bytes (414.66 MiB) duplicate-path bytes are hypothetical and overlap; never add them as achieved savings.

Future growth: source/docs are small relative to generated evidence and repeated native checkouts. The latest phase's measured footprint is in baseline/phases. Repeating that whole tree would add comparable logical working-copy bytes; Git compressed incremental growth is not predictable from that number. Future policy instead admits changed source, essential new fixtures, compact summaries/manifests and selected critical examples; full renders/builds are local or later-approved archives. Advisory future target: at most 5 MiB of new tracked source/docs/compact evidence per phase, plus separately justified essential fixture growth. This is a planning budget, not claimed savings or an automatic permission gate overriding a user brief. A comparable full local validation can still generate roughly 0.1–0.25 GB of ignored data; this R1 measured 119,321,672 bytes in its .local-generated root. Native/release/archive sizes and test matrices vary. Track actual size per phase and review large artifacts before committing.
