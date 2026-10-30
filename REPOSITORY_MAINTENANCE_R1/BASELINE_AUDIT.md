# R1 baseline audit

Measured 2026-10-30T11:33:10.088311+00:00 to 2026-10-30T11:34:35.662514+00:00, before repository changes. Base/main `058cd3df42199c2c39af80519d3a14c0e009201b`; initial branch main. Only untracked file: the user's `phase5_1/run/paragraph-examples/Word-two-rows-edited-manual-test.pdf` (43,149 bytes). No tracked changes. Development proceeds on maintenance/R1; no main merge.

| Scope | Files | Logical bytes |
|---|---:|---:|
| Tracked | 17,039 | 1,051,098,174 |
| Ignored | 28,817 | 1,231,942,507 |
| Untracked | 1 | 43,149 |
| Git metadata | 50 | 82,031,546 |
| Entire workspace including .git | 45,907 | 2,365,115,376 |

Git count-objects: 1 loose object / 1 KiB, 9,524 packed objects, 5 packs / 77,627 KiB (79,490,048 bytes as Git's KiB report), no garbage. These are Git's aggregate pack/index accounting; exact file metadata is included in the full local inventory. Git administrative files total 82,031,546 bytes. No GC/repack/history rewrite was performed. No tracked Git LFS files or LFS attribute filters. Remote main matched base; remote tags and GitHub Releases were empty. Public read-only GitHub REST releases query succeeded; gh CLI was unauthenticated, Git transport uses existing credentials. No release upload/storage change.

Duplicate tracked logical path bytes: **434,806,976**, 1,394 groups. Unique content bytes across the current tracked tree: 616,291,198. These are checked-out logical duplication measures, not independent Git object storage or promised disk savings. Git already deduplicates identical blob content and compresses packs. No pack savings are claimed from removing duplicate paths.

## By phase

| Phase | Tracked files | Logical bytes | Generated evidence bytes |
|---|---:|---:|---:|
| phase2 | 173 | 24,954,377 | 1,645,981 |
| phase3 | 252 | 28,919,343 | 12,605,419 |
| phase4a | 441 | 35,496,499 | 18,841,986 |
| phase4a1 | 588 | 55,501,458 | 38,608,101 |
| phase4b | 767 | 41,355,745 | 24,158,518 |
| phase4c1 | 1,061 | 62,193,576 | 44,771,112 |
| phase4c2 | 1,758 | 95,491,117 | 77,781,635 |
| phase5_1 | 3,212 | 207,901,772 | 189,719,704 |
| phase5_2 | 2,190 | 152,353,883 | 133,786,124 |
| phase5_2_1 | 3,011 | 159,851,091 | 141,130,225 |
| phase5_2_2 | 3,146 | 177,895,738 | 159,062,894 |

Root files/handovers appear separately in classification-summary.json. Nested directories below overlap; do not sum parent/child rows.

| Large directory | Files | Logical bytes |
|---|---:|---:|
| `.venv-clean` | 6,604 | 323,417,529 |
| `.venv` | 4,152 | 221,367,538 |
| `phase5_1/evidence` | 3,014 | 189,719,704 |
| `phase5_1/test-work` | 3,873 | 175,867,926 |
| `phase5_2_2/evidence` | 2,903 | 159,062,894 |
| `phase5_2_1/evidence` | 2,774 | 141,130,225 |
| `phase5_2/evidence` | 1,960 | 133,786,124 |
| `phase5_2/test-work` | 2,561 | 92,782,120 |
| `.git` | 50 | 82,031,546 |
| `phase4c2/evidence` | 1,571 | 77,781,635 |
| `phase4c2/test-work` | 1,841 | 72,894,402 |
| `phase5_2_2/test-work` | 1,819 | 67,864,579 |
| `phase5_2_1/test-work` | 1,627 | 59,930,668 |
| `phase4a1/test-work` | 1,496 | 51,351,491 |
| `phase4c1/test-work` | 1,205 | 46,487,037 |
| `phase4c1/evidence` | 889 | 44,771,112 |
| `phase4a1/evidence` | 442 | 38,608,101 |
| `phase4a/test-work` | 884 | 29,235,502 |
| `phase4b/test-work` | 834 | 28,514,739 |
| `phase5_1/evidence/document-poppler` | 1,004 | 26,261,446 |

| Largest file | Logical bytes | State |
|---|---:|---|
| `.git/objects/pack/pack-85d6c794e21f42a05bbb77d1573bf394f61aff68.pack` | 44,267,533 | git-metadata |
| `.git/objects/pack/pack-8be5fce035a0fa16be18d385487dd1a31f700f2f.pack` | 27,519,402 | git-metadata |
| `.venv/Lib/site-packages/pymupdf/mupdfcpp64.dll` | 26,321,408 | ignored |
| `.venv-clean/Lib/site-packages/pymupdf/mupdfcpp64.dll` | 26,321,408 | ignored |
| `phase5_1/evidence/verified-export-records.json` | 24,974,225 | tracked |
| `.venv-clean/Lib/site-packages/numpy.libs/libscipy_openblas64_-9e3e5a4229c1ca39f10dc82bba9e2b2b.dll` | 20,403,712 | ignored |
| `.venv/Lib/site-packages/onnxruntime/capi/onnxruntime_pybind11_state.pyd` | 19,997,496 | ignored |
| `.venv-clean/Lib/site-packages/onnxruntime/capi/onnxruntime_pybind11_state.pyd` | 19,997,496 | ignored |
| `.venv/Lib/site-packages/onnxruntime/capi/onnxruntime.dll` | 19,288,376 | ignored |
| `.venv-clean/Lib/site-packages/onnxruntime/capi/onnxruntime.dll` | 19,288,376 | ignored |
| `phase5_2_2/evidence/verified-export-records.json` | 17,157,405 | tracked |
| `phase5_2_1/evidence/verified-export-records.json` | 14,770,507 | tracked |
| `.venv/Lib/site-packages/pymupdf/_mupdf.pyd` | 13,037,056 | ignored |
| `.venv-clean/Lib/site-packages/pymupdf/_mupdf.pyd` | 13,037,056 | ignored |
| `phase5_2/evidence/verified-export-records.json` | 10,466,085 | tracked |

## Repeatability and limitations

Run `.venv/Scripts/python.exe REPOSITORY_MAINTENANCE_R1/tools/audit_workspace.py --root . --out <external-private-folder> --label <name>`. It scans tracked/untracked/ignored files and .git, hashes non-Git-admin content, records categories/directories/SHA256 duplicates, and verifies tracked working bytes against remote-main Git blobs. It never removes files. A fresh audit needs the current remote-main commit available locally. Baseline schema1 was captured before edits; the improved repeatable script schema2 verifies changed working blobs as well.

Public compact baseline: inventory/baseline-summary.json and baseline-tracked.csv.gz. Full local path/hash inventory and all-workspace duplicates remain private outside Git in `C:/Users/NGregg/AppData/Local/Temp/pdfeditor-r1-20261030/`. The scan had zero read errors and no skipped junction/symlink paths. Counts are logical lengths, not allocated filesystem blocks or cloud storage. OneDrive path membership is not verified off-machine backup. The scan is time-bounded, not a volume snapshot. It covers this checkout; known external application state is documented separately, not added to workspace totals.
