"""Render compact human review documents from measured R1 inventories."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];R=ROOT/'REPOSITORY_MAINTENANCE_R1';I=R/'inventory'
def load(n):return json.loads((I/n).read_text(encoding='utf-8'))
def write(n,t):(R/n).write_text(t.strip()+'\n',encoding='utf-8',newline='\n')
def size(v):return f'{v:,} bytes ({v/1048576:.2f} MiB)'
b=load('baseline-summary.json');c=load('classification-summary.json');plan=load('local-cleanup-plan.json');v=load('validation-summary.json');safety=load('cleanup-safety-tests.json');a=load('after-summary.json') if (I/'after-summary.json').exists() else None
table='\n'.join(f"| {k} | {d['files']:,} | {d['bytes']:,} |" for k,d in c['categories'].items())
phases='\n'.join(f"| {p} | {d['files']:,} | {d['bytes']:,} | {d['evidenceBytes']:,} |" for p,d in sorted(c['phases'].items()) if p.startswith('phase'))
largest='\n'.join(f"| `{x['path']}` | {x['files']:,} | {x['bytes']:,} |" for x in b['artifactDirectories'][:20])
largeFiles='\n'.join(f"| `{x['path']}` | {x['bytes']:,} | {x['status']} |" for x in b['largestFiles'][:15])
write('BASELINE_AUDIT.md',f'''# R1 baseline audit

Measured {b['startedUtc']} to {b['finishedUtc']}, before repository changes. Base/main `058cd3df42199c2c39af80519d3a14c0e009201b`; initial branch main. Only untracked file: the user's `phase5_1/run/paragraph-examples/Word-two-rows-edited-manual-test.pdf` (43,149 bytes). No tracked changes. Development proceeds on maintenance/R1; no main merge.

| Scope | Files | Logical bytes |
|---|---:|---:|
| Tracked | {b['statusTotals']['tracked']['files']:,} | {b['statusTotals']['tracked']['bytes']:,} |
| Ignored | {b['statusTotals']['ignored']['files']:,} | {b['statusTotals']['ignored']['bytes']:,} |
| Untracked | 1 | 43,149 |
| Git metadata | {b['statusTotals']['git-metadata']['files']} | {b['statusTotals']['git-metadata']['bytes']:,} |
| Entire workspace including .git | {b['files']:,} | {b['logicalBytes']:,} |

Git count-objects: 1 loose object / 1 KiB, 9,524 packed objects, 5 packs / 77,627 KiB (79,490,048 bytes as Git's KiB report), no garbage. These are Git's aggregate pack/index accounting; exact file metadata is included in the full local inventory. Git administrative files total 82,031,546 bytes. No GC/repack/history rewrite was performed. No tracked Git LFS files or LFS attribute filters. Remote main matched base; remote tags and GitHub Releases were empty. Public read-only GitHub REST releases query succeeded; gh CLI was unauthenticated, Git transport uses existing credentials. No release upload/storage change.

Duplicate tracked logical path bytes: **{b['trackedDuplicateBytes']:,}**, {b['trackedDuplicateGroups']:,} groups. Unique content bytes across the current tracked tree: {b['trackedUniqueContentBytes']:,}. These are checked-out logical duplication measures, not independent Git object storage or promised disk savings. Git already deduplicates identical blob content and compresses packs. No pack savings are claimed from removing duplicate paths.

## By phase

| Phase | Tracked files | Logical bytes | Generated evidence bytes |
|---|---:|---:|---:|
{phases}

Root files/handovers appear separately in classification-summary.json. Nested directories below overlap; do not sum parent/child rows.

| Large directory | Files | Logical bytes |
|---|---:|---:|
{largest}

| Largest file | Logical bytes | State |
|---|---:|---|
{largeFiles}

## Repeatability and limitations

Run `.venv/Scripts/python.exe REPOSITORY_MAINTENANCE_R1/tools/audit_workspace.py --root . --out <external-private-folder> --label <name>`. It scans tracked/untracked/ignored files and .git, hashes non-Git-admin content, records categories/directories/SHA256 duplicates, and verifies tracked working bytes against remote-main Git blobs. It never removes files. A fresh audit needs the current remote-main commit available locally. Baseline schema1 was captured before edits; the improved repeatable script schema2 verifies changed working blobs as well.

Public compact baseline: inventory/baseline-summary.json and baseline-tracked.csv.gz. Full local path/hash inventory and all-workspace duplicates remain private outside Git in `C:/Users/NGregg/AppData/Local/Temp/pdfeditor-r1-20261030/`. The scan had zero read errors and no skipped junction/symlink paths. Counts are logical lengths, not allocated filesystem blocks or cloud storage. OneDrive path membership is not verified off-machine backup. The scan is time-bounded, not a volume snapshot. It covers this checkout; known external application state is documented separately, not added to workspace totals.
''')
write('ARTIFACT_CLASSIFICATION.md',f'''# R1 artifact classification

All {b['statusTotals']['tracked']['files']:,} starting tracked paths are classified in inventory/artifact-classification.csv.gz, with SHA256, Git blob, logical size, proposed tier and current disposition. No existing artifact is removed. Initial heuristic unknowns were five historical root/build logs; they are retained as F, not discarded as caches.

| Class | Files | Bytes |
|---|---:|---:|
{table}

- A — Essential source: C#, projects, test implementations, build/configuration and dependency requirements. Keep in Git; never clean source or generated .cs using the cleanup tool.
- B — Essential documentation: handovers, architecture/decisions, test methodology, open issues. Keep in Git.
- C — Essential fixtures: regression PDFs, fixture definitions, source example data. Keep necessary fixtures in Git; redistribution rights need separate review.
- D — Third-party dependencies: pinned native programs/fonts and every licence/attribution notice. Existing historical copies stay. Future restorations use a hash-pinned canonical cache; notices accompany distributions.
- E — Release/reference binaries: retain each historical release/reference until provenance, reproducibility and an authorised versioned destination are verified. Managed/PDB byte equivalence is not established, so none are deleted.
- F — Generated evidence: preserve authoritative results, important failures, unique forensic records and independently verified examples. Tier 2 archive proposals require semantic review and verified destinations. Current tracked copies stay intact.
- G — Disposable intermediates: no starting tracked files were classified G. Ignored SDK caches/build outputs may be reproducible, but that is not deletion permission. Unique local files remain protected until assessed.

Directory-level local essential/reproducible/preservation classifications are in inventory/local-directory-classification.json and LOCAL_WORKSPACE_AUDIT.md. A directory label never authorises deleting its entire tree. Proposed archive manifest includes {c['archiveCandidates']:,} E/F paths / {size(c['archiveCandidateBytes'])}; every row is **unapproved, destination unverified, retain in place**. A candidate is not a completed migration. Full preserved evidence remains available while the minimum-record index is reviewed.
''')
write('RETENTION_POLICY.md',r'''# R1 retention policy

Tier 1 — Source repository: source/configuration/test recipes, essential fixtures, all licence/attribution notices, human summaries/decisions/open issues, exact source/native/output manifests and hashes, and representative critical failure evidence with reproduction context. A SHA without retrievable bytes is not a backup. Keep failed outcomes visible and describe limits honestly.

Tier 2 — Approved versioned archive: full final distributables, large complete reader outputs, representative raster comparisons and historical binary/forensic datasets. Before moving a path, record immutable archive version/location, SHA256/size, source/build/SDK/native provenance, retrieval instructions, and a separately verified download/hash/reopen or relevant test. Obtain explicit approval for release uploads/external storage changes. Keep current tracked copies until all checks pass. This R1 performs no uploads or migrations; no archive destination exists yet.

Tier 3 — Local generated: bin/obj caches, disposable test workspaces, intermediate renders and release staging with proven regeneration. Put future bulk output under .local-generated/ or artifacts/staging/, not phase evidence/run/runtime paths. Never treat “ignored”, “untracked” or “generated-looking” as evidence of disposability. Preserve user documents, credentials, source, fixtures, recovery and unique evidence. Review unexpected files even inside a cache directory.

inventory/evidence-retention-index.json lists per-phase summaries/handovers, authoritative root records, critical failure references and footprint. This is a conservative minimum-review index, not approval to discard everything absent from it. Preserve the original baseline presentation failure in Phase 5.2.1, the Phase 5.2.2 activation/u-glyph baseline and development failures, original-font mapping observations, source identity/recovery findings, historical clipboard failures and known frozen expectation mismatch. Existing full records remain in Git while choosing representative Tier 1 and larger Tier 2 datasets.

For a future phase, budget changed source + new essential fixture bytes + compact human/JSON summary and a small representative failure/example set in Git. Keep detailed generated observations/renders locally until an approved archive exists. Record actual sizes before/after; do not estimate Git pack growth from path duplication. Archive plans and future storage budgets are distinct from achieved savings.
''')
write('DEPENDENCY_STRATEGY.md',r'''# R1 dependency strategy

23 tracked PDFium DLL paths have the identical SHA256 bede3932ce96a2e1ed9a7e6cae71aec8914efd2907d37ab44b1b81f9c8a6d04e (7,397,168 bytes each). Their extra logical copies are 162,737,696 bytes, but Git stores identical blobs once: that is not a Git object savings claim. The application's existing provenance names PDFium156.0.8076.0 / pypdfium2 5.14.0 Windows x64. The different DLL under .venv-clean is SHA25669f1e860f6742fbaafcc4db80e785eec9a4ee0da36ea6d1dc0867ea0f18baea6 /7,381,504bytes. It is an environment asset, not a permitted runtime substitute.

inventory/runtime-asset-families.json groups other copied managed/font/notice assets by exact hash, including differences that must not be silently consolidated. inventory/pinned-runtime.json pins19 exact runtime/font/notice files to the verified starting commit and Git blobs, with size and SHA256. Restore-PinnedRuntime.ps1 materialises them into one ignored .local-generated/dependencies/version-hash cache, validates hashes on every use, refuses mismatched cache content and verifies the blob against its source commit/path. It uses binary-safe local Git stdout, no guessed or unverified download URL. A shallow checkout missing those objects must fetch the documented commit before retrying. Historical run/runtime copies and source manifests are unchanged.

Build-Current.ps1 publishes current accepted source into a new ignored output directory, copies only pinned dependency entries and tracked fixture paths (never unknown local files), and records SDK/source hashes/product hashes. Fonts/notices remain with the build. The original phase build scripts still exist and still build their original layouts; they are not silently redirected or upgraded. The new wrapper is opt-in infrastructure for future phases.

Default rebuild informational version records the maintenance commit, whereas the delivered reference records376e2de7ffe54c71fd38c2249cebb15782667ba6. An explicit historical stamp attempt reproduced the two .exe hosts and pinned native bytes, but managed DLL/PDB byte equivalence was not established. Do not replace/drop historical reference binaries based on functional tests alone. The explicit-stamp host also passed a separate launch/PDF-inspection smoke check; full feature suites ran on the default rebuilt, source-identical application. Future releases should capture SDK/OS/RID, source content and dirty state, informational stamp, complete MSBuild settings, dependency/wheel provenance, output hashes and verification recipe. Do not advertise bit-reproducible historical releases until measured.

No LFS migration, new native version, online binary download, release upload, branch/tag deletion or Git history rewrite occurred. Versioned release/archive storage remains a separately approved follow-up. Native and third-party notice completeness needs the later licensing audit described in the risk register.
''')
write('REPOSITORY_STRUCTURE_PROPOSAL.md',r'''# Gradual repository structure proposal

No historical source directory is migrated in R1. Frozen manifests and tests refer to exact phase paths, and some source/reference builds cannot yet be reproduced byte-for-byte. Keeping these references now is safer than an uncontrolled rename/delete operation.

Proposed future layout after explicit adoption: src/PdfEditor for current application/worker/core, tests/fixtures for approved shared regression inputs, docs/phases for handovers, dependency lock metadata in source, artifacts/staging and .local-generated for ignored bulk builds/tests, and approved immutable releases/evidence archives externally. Git commits identify old implementation states; tags can be added later with a documented policy, but none are created/deleted here.

Transition steps: (1) retain this branch's audit/policies and use the safe output wrapper; (2) in a separately scoped development phase move only the current source to a shared location and adapt tests with before/after fidelity proof; (3) keep earlier phase sources/builds until recipes and verified archive retrieval preserve their role; (4) replace repeated native-file checkouts only after every historical build/manifest consumer is migrated; (5) reduce current-tree artifact paths only after approved archive verification. Ordinary commits preserve history; no force push/rewrite.

Do not copy complete phase run/runtime/evidence directories into each new phase. A phase brief explicitly requiring isolation can still isolate changed source, but must define a size/retention plan rather than cloning historical bulky evidence. Existing user instructions take priority; do not infer permission to discard older releases from this proposal.
''')
write('IMPLEMENTATION_REPORT.md',r'''# R1 implementation report

Work is on maintenance/R1, based on058cd3df42199c2c39af80519d3a14c0e009201b. Main is not merged. Final commit is reported in the delivery message; checkpoints are ordinary maintenance commits. No Phase 5.3 or PDF editing/discovery/font/transaction logic changes.

Implemented: repeatable tracked/local SHA256 storage audit; complete A–G classification and unapproved archive manifest; phase evidence retention index; narrow root ignore rules; offline pinned runtime cache; isolated opt-in current build with source/native/product identity manifests; redirected inherited validation; conservative PowerShell cleanup preflight and executor; non-destructive safety tests; licensing/environment/unique-local risk inventory; twelve human reports plus progress.

The sole deliberate pre-existing tracked-path change is .gitignore. Its rules ignore new bin/obj, caches, named staging and phase test-work outputs; they do not untrack or remove already committed artifacts. No global PDF/PNG/JSON/log ignore is added, and 14 boundary tests keep fixtures/source/licences/final evidence eligible. Existing source, fixtures, run/runtime binaries, handovers, licences, evidence and the user's untracked manual PDF are preserved. Old phase manifests remain byte-identical and ordinary build entry points are retained. Historical whole-repository preservation scripts may intentionally reject the new root .gitignore hash; run those assertions at their recorded original commit. R1 separately records .gitignore as its sole authorised pre-existing tracked exception, without editing old verifiers or weakening PDF tests. The new wrapper publishes into .local-generated rather than overwriting a delivered run directory. Compiler bin/obj products may be regenerated as part of an authorised build; no maintenance deletion was performed.

Local-Cleanup.ps1 defaults to Audit. DryRun enumerates each exact proposed file. Clean requires -ApproveCleanup, validates the workspace, build/source hashes, allowlist, file size/hash, actual Git backup bytes and non-reparse ancestry, preflights all candidates, then uses file-by-file literal-path removal through ShouldProcess. No recursive removal, git clean or tracked-file deletion. Only two SDK executable-host duplicates currently qualify; all broader environments/test workspaces/unique outputs remain outside the plan. Clean was tested only with -WhatIf, never destructively.

Actual deletion savings are zero. Documentation and validation introduce measured new local data. Duplicate logical bytes, proposed migration bytes and future avoided growth are not achieved savings. No GitHub Releases, archive uploads or other remote storage changes. Push this completed branch only; stop for review and separate approval of any future cleanup/migration.
''')
ctrl=sum(x['tests'] for x in v['controls']);ctrlfail=sum(x['failures'] for x in v['controls'])
write('VALIDATION_RESULTS.md',f'''# R1 validation results

Latest accepted Phase 5.2.2 source rebuilt with Build-Current.ps1 into .local-generated/R1-validation/run. No application source was edited. Actual WPF executables launched and closed across the suites; inventory/rebuilt-application-wpf.png is a genuine rendered-control capture. Programmatic WPF testing is not human mouse/keyboard/DPI/accessibility certification.

| Check | Result |
|---|---|
| Current engine/discovery/compatibility/position/insertion/document/wrap workers |151/151 |
| Phase 5.1 paragraph worker round trips |37/37 |
| Phase 5.2 original Word workers |31/31 |
| Session/layout models |35/35 |
| Phase 5.2.2 multi-region WPF including separate recovery process |29/29 |
| Phase 5.2.1 presentation WPF |27/27 |
| Marked paragraph new-process WPF |16/16 |
| Original Word new-process WPF |12/12 |
| Inherited WPF controls |{ctrl-ctrlfail}/{ctrl} |
| Independent combined PDF candidates |{v['independent']['candidates']} passing |
| Independent paragraph structure |{v['independent']['paragraphGroups']} groups passing |
| Frozen Phase 2 original source/binary |18/18 |
| Cleanup audit/dry-run/refusal/WhatIf safety |{safety['tests']}/{safety['tests']}, no removal |
| Ignore boundary rules |14/14 |
| Pinned runtime/font/notices |19/19 SHA256 matched |
| Explicit historical-stamp host launch/inspect smoke |1/1; no source mutation |

Compact details: inventory/validation-summary.json, validated-build-identity.json, build-reproduction.json, frozen-phase2-validation.json, cleanup-safety-tests.json, ignore-rule-tests.json. Full generated logs/PDFs/JSON/renders remain in the ignored stage, not duplicated into Git. Archived older source/evidence hashes are checked against baseline; the compatibility suite also invokes a frozen Phase 3 worker. Full historical suites were not all repeated: maintenance changes no application logic, and no historical binary/evidence was removed. The prior frozen Phase 3 expectation mismatch and historical intermittent clipboard Win32 5 remain open; a passing current probe does not establish a fix.

One harness attempt failed before presentation launch because wrapper CLI arguments were interpreted as an optional reproduction filename. Clearing inherited sys.argv fixed invocation; completed worker/multi-region results were reused and the remaining suites resumed. Only path/argument bindings change in memory, not inherited test or application logic. Recipes record source test hashes.

Reproduce: run Build-Current.ps1 with a new output folder; `.venv/Scripts/python.exe REPOSITORY_MAINTENANCE_R1/tools/validate_r1.py --stage <output>` (add --resume only for the same unchanged build), and run the model command recorded in LOCAL_CLEANUP_GUIDE. Frozen smoke: tools/validate_frozen_phase2.py. Safety: tools/test_cleanup_safety.py. Ignore: tools/test_ignore_rules.py. Independent readers use pypdf, pikepdf, MuPDF, fontTools and Poppler; no PyMuPDF is added to the shipped application.

**No approved destructive cleanup occurred.** These establish build/run after maintenance, not after an unperformed cleanup. After any separately approved real cleanup, rebuild and rerun critical checks using a fresh stage before declaring cleanup successful. A live junction test was not created; ancestor rejection is implemented and inspected. Clean is deliberately file-by-file, not an atomic directory transaction.
''')
def directoryBytes(snapshot,pattern):return sum(d['bytes'] for d in snapshot['artifactDirectories'] if __import__('re').match(pattern,d['path']))
gitStorage=load('git-storage-detail.json') if (I/'git-storage-detail.json').exists() else None
if a:
 afterTracked=a['statusTotals']['tracked'];comparison=f'''| Tracked paths at snapshot | {b['statusTotals']['tracked']['files']:,} | {afterTracked['files']:,} |
| Tracked logical bytes | {b['statusTotals']['tracked']['bytes']:,} | {afterTracked['bytes']:,} |
| Entire workspace files | {b['files']:,} | {a['files']:,} |
| Entire workspace logical bytes | {b['logicalBytes']:,} | {a['logicalBytes']:,} |
| Git metadata logical bytes | {b['statusTotals']['git-metadata']['bytes']:,} | {a['statusTotals']['git-metadata']['bytes']:,} |
| Tracked duplicate logical bytes | {b['trackedDuplicateBytes']:,} | {a['trackedDuplicateBytes']:,} |
| Historical phase evidence directories | {directoryBytes(b,r'^phase[^/]+/evidence$'):,} | {directoryBytes(a,r'^phase[^/]+/evidence$'):,} |
| SDK project bin/obj directories | {directoryBytes(b,r'^phase[^/]+/(App|Core|Worker|Checks)/(bin|obj)$'):,} | {directoryBytes(a,r'^phase[^/]+/(App|Core|Worker|Checks)/(bin|obj)$'):,} |
| New .local-generated staging | 0 | {next((r['bytes'] for r in a['phases'] if r['path']=='.local-generated'),0):,} |
| Actual Git .pack payload bytes | {gitStorage['before']['packPayloadBytes'] if gitStorage else 'See inventory'} | {gitStorage['afterCheckpoint']['packPayloadBytes'] if gitStorage else 'See inventory'} |''';afterNote=f"After snapshot: {a['startedUtc']} to {a['finishedUtc']}. Actual workspace logical growth at that checkpoint: {a['logicalBytes']-b['logicalBytes']:,} bytes. This includes validation/dependency staging and the then-existing R1 metadata. Later copying this summary, report updates and normal commit bookkeeping can change live bytes; it is a timestamped measurement, not a perpetual size claim."
else:comparison='| After snapshot | baseline captured | PENDING final audit |';afterNote='Final post-validation audit is pending; no cleanup measurement is invented.'
write('SIZE_COMPARISON.md',f'''# R1 measured size comparison

| Metric | Before | After maintenance audit checkpoint |
|---|---:|---:|
{comparison}

{afterNote}

Git's baseline count-objects and after count-objects are retained in the snapshot JSON. Baseline5packs/77,627KiB; no repack/history rewrite. Ordinary maintenance commits add small objects; removing paths cannot remove bytes retained in historical commits. Tracked build/dependency and evidence footprint by phase is in classification-summary.json; all historical content remains. Added bulk build/tests live under ignored .local-generated; their measured size is in after-summary.json when captured.

**Actual deletion savings:0bytes. Actual tracked historical paths removed:0. Approved archive migrations:0. Destructive cleanup runs:0.** Planned local cleanup is only {len(plan['files'])} host files / {size(plan['estimatedLogicalSavingsBytes'])}; not performed, not physical allocated-disk savings. Broader {size(c['archiveCandidateBytes'])} archive proposals and {size(b['trackedDuplicateBytes'])} duplicate-path bytes are hypothetical and overlap; never add them as achieved savings.

Future growth: source/docs are small relative to generated evidence and repeated native checkouts. The latest phase's measured footprint is in baseline/phases. Repeating that whole tree would add comparable logical working-copy bytes; Git compressed incremental growth is not predictable from that number. Future policy instead admits changed source, essential new fixtures, compact summaries/manifests and selected critical examples; full renders/builds are local or later-approved archives. Advisory future target: at most 5 MiB of new tracked source/docs/compact evidence per phase, plus separately justified essential fixture growth. This is a planning budget, not claimed savings or an automatic permission gate overriding a user brief. A comparable full local validation can still generate roughly 0.1–0.25 GB of ignored data; this R1 measured 119,321,672 bytes in its .local-generated root. Native/release/archive sizes and test matrices vary. Track actual size per phase and review large artifacts before committing.
''')
write('OPEN_ISSUES_AND_LICENSE_RISKS.md',r'''# R1 open issues and licence risk register

| Risk | Finding and next action |
|---|---|
| Project-wide licence | No root project licence declaration found; do not assign MIT/GPL/another licence without the owner's decision. A public repository alone is not a documented redistribution grant. Seek a later licensing audit. |
| Proprietary embedded subsets | Word-Arial.pdf and Word-Calibri.pdf contain embedded ArialMT/Calibri subsets (technical fsType8). Embedding metadata is not independent permission to redistribute fixture/font programs. Record fixture authorship/source and applicable font terms with qualified review; keep current material intact pending review. |
| Fixtures and user data | Essential regression PDFs/source examples need provenance and redistribution review. The user's untracked manual PDF has no verified backup in this audit, remains private/untracked and must not enter releases/cleanup. No files removed to conceal concerns. |
| Native notices |19 pinned runtime/font/notice files are retained/restored together, including PDFium/component notices and renamed Bitstream Vera-derived font notice. Confirm notice completeness for the exact historical wheel/native build, not a newer upstream licence. |
| Development Python | Local metadata identifies PyMuPDF2.0 as AGPL/commercial; review development/distribution and generated-artifact obligations separately from the WPF application. PyMuPDF is development-only in this project. The [official licensing page](https://pymupdf.io/licensing) and [official FAQ](https://pymupdf.readthedocs.io/en/latest/faq/index.html) describe its licensing routes; no legal-compliance conclusion is made here. pikepdf/MPL and other package terms are listed in development-license-metadata.json for review. |
| Environment drift | Installed Pillow13.0.0 differs from requirements.txt12.3.0. Actual package versions are captured without credential URLs. Both environments stay; no dependency downgrade/upgrade or environment recreation was attempted. |
| Historical reproducibility | Managed DLL/PDB bit equivalence unproven even with original informational stamp; keep historical binaries. Native SHA and2host executables match; default build passes functional tests. |
| Archive storage | No approved versioned destination or release assets exists. All14,850E/F candidate paths remain in place. Independent upload/download verification and user authorisation are required before migration. |
| Local-only state | Many ignored files have no verified independent backup. Some are reproducible in principle, others may be unique evidence. Recovery/live temp outside checkout is excluded from cleanup. OneDrive path membership does not prove backup. |
| Existing platform limits | Clipboard Win32 5 intermittency, user manual/DPI/accessibility acceptance and historical frozen Phase 3 expectation mismatch remain open. R1 fixes none of these application behaviours. |

This register flags issues for a later legal/licensing/provenance audit; it does not silently resolve them, remove evidence, upload archives or choose a new project licence. No Phase 5.3 work.
''')
write('FUTURE_CODEX_DEVELOPMENT_RULES.md',r'''# Future PDFEditor development rules

1. Read current handover/open issues and record starting Git status/commit. Preserve user/untracked/recovery files. Follow the user's explicit phase scope.
2. Do not copy whole prior run/runtime/evidence trees into a new phase. Prefer changed source on shared current code after an explicitly scoped transition; keep historical source until the migration is proven.
3. Use the version/hash-pinned dependency manifest/cache. Never silently upgrade PDFium, replace historical bytes or drop licence notices. Record SDK/source/build/output provenance.
4. Put bulk generated builds, logs, PDF candidates, renders and test workspaces under ignored .local-generated/ or artifacts/staging/. Retain only essential fixtures, compact summaries/manifests/recipes and critical representative evidence in Git.
5. Do not overwrite frozen phase source, fixtures, evidence or releases. Test path overrides must only redirect outputs; no behaviour changes to make maintenance tests pass.
6. Keep meaningful failure evidence and exact limitations. A passing model test is not physical input proof. Never weaken PDF fidelity/export gates for storage convenience.
7. Record before/after tracked, workspace, build/evidence and Git object sizes. Distinguish logical duplicates, archived proposals and actual achieved savings; do not claim historical pack shrinkage without measurement.
8. No automatic archive upload or irreversible migration. Get explicit approval for remote storage changes and verify immutable retrieval/hash/test before removing current copies.
9. Local cleanup defaults to Audit, then DryRun. Real cleanup needs explicit user approval, a fresh reviewed per-file plan, current source/build/hash checks and post-cleanup build/run validation. Never git clean -fdx, delete by unknown Git status, or recursively sweep a directory.
10. Follow the requested branch/delivery gate; maintenance work is not automatic permission to merge main or start Phase 5.3. Retain progress/checkpoints and stop for review when required.
''')
write('LOCAL_WORKSPACE_AUDIT.md',f'''# R1 local development workspace audit

The full starting workspace contains {b['files']:,} files / {size(b['logicalBytes'])}, including tracked, ignored, untracked and .git. Ignored data alone is {size(b['statusTotals']['ignored']['bytes'])}. This is logical length, not allocated disk/cloud usage. The full per-file local inventory is private outside Git at `C:/Users/NGregg/AppData/Local/Temp/pdfeditor-r1-20261030/baseline-files.csv.gz`; public metadata contains summaries only.

## Large directories and classification

| Directory | Files | Logical bytes |
|---|---:|---:|
{largest}

inventory/directory-retention.json classifies all identified large directories and named build/cache/test-work roots; inventory/local-directory-classification.json additionally classifies local-only directories over 1 MiB (including nested cache directories). Source, fixtures and notices are essential; historical builds/evidence and all unknown/local-only outputs require preservation. SDK bin/obj/__pycache__ are reproducible candidates, not blanket deletion targets. Virtual environments are reproducible in principle but not restored/verified here; the recorded version drift requires preservation. Test-work can contain unique candidates/source copies/forensic failures, so it stays until purpose/backup/regeneration are established.

{b['localWithoutVerifiedBackupFiles']:,} ignored/untracked files had no independently verified backup in the scan. This is not a claim that all are irreplaceable or globally unique: no external backup service was authenticated/audited, and packages may be restorable later. The 43,149-byte untracked Word-two-rows-edited-manual-test.pdf is an explicit user document, not disposable. It remains excluded from staging and cleanup. Byte-identical Git-backed cache copies are distinguished from truly unverified local content in the private CSV.

Known external app state is measured separately, not included in workspace total: inventory/external-application-state.json records recovery under LOCALAPPDATA/PdfEditorPrototype and temporary application work under TEMP/PdfEditorPrototype. Metadata only was read; drafts were not inspected. Both are excluded from all cleanup targets, particularly live-session temp/recovery. This is not a global AppData/NuGet/SDK storage sweep.

## Concrete cleanup assessment

Only {len(plan['files'])} current-phase executable host products / {plan['estimatedLogicalSavingsBytes']:,} logical bytes meet all current plan requirements: known SDK producer path/name, not tracked, matching validated rebuild, exact verified remote-Git backup, source/build identity unchanged. Remaining managed DLL/PDB/cache/test-work/venv/render/evidence files do not receive inferred deletion approval. A report of many possible reproducible bytes is not a safe removal list.

The script's Audit and DryRun modes and Clean -ApproveCleanup -WhatIf were exercised;18 safety/refusal tests confirm candidates stay unchanged. No destructive cleanup was approved or executed. Before/after Audit snapshots can change from concurrent validation output; removedFiles/removedLogicalBytes remain0. SIZE_COMPARISON distinguishes maintenance growth from hypothetical savings. Actual post-approved-cleanup measurement/build validation remains pending because there was no approval.
''')
write('LOCAL_CLEANUP_GUIDE.md',r'''# Safe local cleanup guide

Requires PowerShell7 (`pwsh`), the existing Git checkout, and the current reviewed plan/build manifest. This R1 does **not** approve running destructive cleanup. No real cleanup was executed. Default Audit is safe to repeat.

```powershell
pwsh -NoProfile -File ./REPOSITORY_MAINTENANCE_R1/tools/Local-Cleanup.ps1
pwsh -NoProfile -File ./REPOSITORY_MAINTENANCE_R1/tools/Local-Cleanup.ps1 -Mode DryRun
```

DryRun prints every exact proposed path/byte count and estimated logical savings. Audit performs identical preflight without removal. Both measure workspace before/after; concurrent build/test output may change totals independently of cleanup. No source/fixture/user documents/credentials/recovery/evidence/historical run/runtime path is eligible. The current plan has only2known executable-host duplicates/303,616logicalbytes; no directory sweep or environment purge is implied.

Before any real run: inspect inventory/local-cleanup-plan.json and private local inventory; close builds/test processes, preserve user documents/recovery and obtain explicit human approval for the exact reviewed file list. A script flag alone is not prior authorisation for an agent. Do not widen paths or use Git clean. Use this non-removing rehearsal if desired:

```powershell
pwsh -NoProfile -File ./REPOSITORY_MAINTENANCE_R1/tools/Local-Cleanup.ps1 -Mode Clean -ApproveCleanup -WhatIf
```

Only after separate explicit approval, the same command **without -WhatIf** opts into file-by-file deletion. It refuses changed source/build/file hashes, wrong workspace, tracked/unknown paths, invalid backup bytes, traversal and reparse ancestors. It preflights all files first and rechecks immediately before each literal-path removal. It does not recurse, remove directories or follow junctions. A mid-run error stops further removal and reports before/after plus completed removal count; this is not an atomic transaction. Empty directories can remain intentionally. Source or SDK changes require a fresh build/audit/plan, not bypassing the guard.

After an approved cleanup, save the before/after object, build into a new ignored directory and rerun critical checks:

```powershell
$r1Output='.local-generated/cleanup-verification-'+(Get-Date -Format 'yyyyMMdd-HHmmss')
pwsh -NoProfile -File ./REPOSITORY_MAINTENANCE_R1/tools/Build-Current.ps1 -OutputRelative $r1Output
.venv/Scripts/python.exe REPOSITORY_MAINTENANCE_R1/tools/validate_r1.py --stage $r1Output
dotnet run --project phase5_2_2/Checks/Checks.csproj -c Release -- "$r1Output/evidence/model" phase4c1/evidence/word-spacing-analysis.json phase5_2/evidence/development-generations.json phase5_2/evidence/original-source-observations.json
```

These launch the actual WPF app and verify Phase 5.1/5.2/5.2.1/5.2.2 behaviour plus independent PDF export checks. Do not claim cleanup success if a rebuild/launch fails. Restore an exact accidentally removed *planned* host from its pinned Git backup via binary-safe tools or regenerate after verifying the recipe. No other user file is intended to be removed. No post-cleanup build claim is made by this R1 because cleanup was not approved.

For a fresh plan, run tools/audit_workspace.py to an external private folder, build to a new local stage, then tools/create_retention_plan.py with --local-inventory <new-name-files.csv.gz> and --build-manifest <stage>/build-manifest.json. The current planner is deliberately scoped to phase5_2_2 known products and the verified starting source inventory; later phases must explicitly review/update producer/backup/validation scope. Never add whole test-work, venv or render trees based only on their names. Keep the unique user PDF and all recovery data outside every plan.

Between phases: measure first, review the private unique-local list, retain critical failures and fixtures, keep large new outputs under .local-generated, use narrow ignore tests, propose approved archives separately, then request approval only for a concrete safe list. Historical sources/releases/evidence stay until migration is independently verified. No remote uploads or merge into main are part of local cleanup.
''')
print('Wrote twelve R1 review reports; after snapshot present:',bool(a))
