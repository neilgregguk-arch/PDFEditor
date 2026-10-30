# R1 measured size comparison

| Metric | Before | After maintenance audit checkpoint |
|---|---:|---:|
| After snapshot | baseline captured | PENDING final audit |

Final post-validation audit is pending; no cleanup measurement is invented.

Git's baseline count-objects and after count-objects are retained in the snapshot JSON. Baseline5packs/77,627KiB; no repack/history rewrite. Ordinary maintenance commits add small objects; removing paths cannot remove bytes retained in historical commits. Tracked build/dependency and evidence footprint by phase is in classification-summary.json; all historical content remains. Added bulk build/tests live under ignored .local-generated; their measured size is in after-summary.json when captured.

**Actual deletion savings:0bytes. Actual tracked historical paths removed:0. Approved archive migrations:0. Destructive cleanup runs:0.** Planned local cleanup is only 2 host files / 303,616 bytes (0.29 MiB); not performed, not physical allocated-disk savings. Broader 851,973,545 bytes (812.51 MiB) archive proposals and 434,806,976 bytes (414.66 MiB) duplicate-path bytes are hypothetical and overlap; never add them as achieved savings.

Future growth: source/docs are small relative to generated evidence and repeated native checkouts. The latest phase's measured footprint is in baseline/phases. Repeating that whole tree would add comparable logical working-copy bytes; Git compressed incremental growth is not predictable from that number. Future policy instead admits changed source, essential new fixtures, compact summaries/manifests and selected critical examples; full renders/builds are local or later-approved archives. Track actual size per phase and review large artifacts before committing.
