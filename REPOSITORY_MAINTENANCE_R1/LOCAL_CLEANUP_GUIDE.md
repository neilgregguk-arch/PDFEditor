# Safe local cleanup guide

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
pwsh -NoProfile -File ./REPOSITORY_MAINTENANCE_R1/tools/Build-Current.ps1
# Use the R1_OUTPUT printed above; do not reuse/overwrite a prior stage.
.venv/Scripts/python.exe REPOSITORY_MAINTENANCE_R1/tools/validate_r1.py --stage <R1_OUTPUT>
dotnet run --project phase5_2_2/Checks/Checks.csproj -c Release -- <R1_OUTPUT>/evidence/model phase4c1/evidence/word-spacing-analysis.json phase5_2/evidence/development-generations.json phase5_2/evidence/original-source-observations.json
```

These launch the actual WPF app and verify Phase5.1/5.2/5.2.1/5.2.2 behaviour plus independent PDF export checks. Do not claim cleanup success if a rebuild/launch fails. Restore an exact accidentally removed *planned* host from its pinned Git backup via binary-safe tools or regenerate after verifying the recipe. No other user file is intended to be removed. No post-cleanup build claim is made by this R1 because cleanup was not approved.

For a fresh plan, run tools/audit_workspace.py to an external private folder, build to a new local stage, then tools/create_retention_plan.py with --local-inventory <new-name-files.csv.gz> and --build-manifest <stage>/build-manifest.json. The current planner is deliberately scoped to phase5_2_2 known products and the verified starting source inventory; later phases must explicitly review/update producer/backup/validation scope. Never add whole test-work, venv or render trees based only on their names. Keep the unique user PDF and all recovery data outside every plan.

Between phases: measure first, review the private unique-local list, retain critical failures and fixtures, keep large new outputs under .local-generated, use narrow ignore tests, propose approved archives separately, then request approval only for a concrete safe list. Historical sources/releases/evidence stay until migration is independently verified. No remote uploads or merge into main are part of local cleanup.
