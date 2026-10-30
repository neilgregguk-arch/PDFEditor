# R1 local development workspace audit

The full starting workspace contains 45,907 files / 2,365,115,376 bytes (2255.55 MiB), including tracked, ignored, untracked and .git. Ignored data alone is 1,231,942,507 bytes (1174.87 MiB). This is logical length, not allocated disk/cloud usage. The full per-file local inventory is private outside Git at `C:/Users/NGregg/AppData/Local/Temp/pdfeditor-r1-20261030/baseline-files.csv.gz`; public metadata contains summaries only.

## Large directories and classification

| Directory | Files | Logical bytes |
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

inventory/local-directory-classification.json classifies every local-only directory over1MiB (including nested cache directories). Source, fixtures and notices are essential; historical builds/evidence and all unknown/local-only outputs require preservation. SDK bin/obj/__pycache__ are reproducible candidates, not blanket deletion targets. Virtual environments are reproducible in principle but not restored/verified here; the recorded version drift requires preservation. Test-work can contain unique candidates/source copies/forensic failures, so it stays until purpose/backup/regeneration are established.

26,188 ignored/untracked files had no independently verified backup in the scan. This is not a claim that all are irreplaceable or globally unique: no external backup service was authenticated/audited, and packages may be restorable later. The43,149-byte untracked Word-two-rows-edited-manual-test.pdf is an explicit user document, not disposable. It remains excluded from staging and cleanup. Byte-identical Git-backed cache copies are distinguished from truly unverified local content in the private CSV.

Known external app state is measured separately, not included in workspace total: inventory/external-application-state.json records recovery under LOCALAPPDATA/PdfEditorPrototype and temporary application work under TEMP/PdfEditorPrototype. Metadata only was read; drafts were not inspected. Both are excluded from all cleanup targets, particularly live-session temp/recovery. This is not a global AppData/NuGet/SDK storage sweep.

## Concrete cleanup assessment

Only 2 current-phase executable host products / 303,616 logical bytes meet all current plan requirements: known SDK producer path/name, not tracked, matching validated rebuild, exact verified remote-Git backup, source/build identity unchanged. Remaining managed DLL/PDB/cache/test-work/venv/render/evidence files do not receive inferred deletion approval. A report of many possible reproducible bytes is not a safe removal list.

The script's Audit and DryRun modes and Clean -ApproveCleanup -WhatIf were exercised;18safety/refusal tests confirm candidates stay unchanged. No destructive cleanup was approved or executed. Before/after Audit snapshots can change from concurrent validation output; removedFiles/removedLogicalBytes remain0. SIZE_COMPARISON distinguishes maintenance growth from hypothetical savings. Actual post-approved-cleanup measurement/build validation remains pending because there was no approval.
