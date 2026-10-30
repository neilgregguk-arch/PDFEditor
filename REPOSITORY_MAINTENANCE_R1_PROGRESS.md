# Repository Maintenance R1 — ready for review

Branch: `maintenance/R1`. Starting/main commit: `058cd3df42199c2c39af80519d3a14c0e009201b`.

No destructive workspace cleanup was approved or performed. No release/archive upload, historical artifact migration, history rewrite, main merge or Phase 5.3 work occurred. Ordinary checkpoint commits preserve the audit and implementation. The final commit SHA is reported in the delivery message.

## Verified checkpoints

1. Captured the baseline before repository changes. Full private local inventory remains outside Git in `C:/Users/NGregg/AppData/Local/Temp/pdfeditor-r1-20261030/`. Public baseline contains only the tracked inventory, hashes and aggregate local measurements.
2. Classified all 17,039 starting tracked paths, indexed evidence/critical failures, and prepared an unapproved archive manifest for 14,850 E/F paths (851,973,545 logical bytes). All remain in place.
3. Implemented narrow ignore rules, a 19-entry pinned offline runtime/font/notice cache, isolated current builds, redirected inherited validation and a conservative PowerShell cleanup script. Default Audit, DryRun and Clean-with-WhatIf/refusal checks passed without removal. The current plan is two verified executable-host duplicates / 303,616 logical bytes only.
4. Built and ran the latest accepted application without modifying PDF logic. Default PE metadata differs from the delivered reference. An explicit original informational-stamp attempt matches two hosts/native bytes but does not establish managed DLL/PDB bit equivalence; historical reference binaries are retained. The explicit-stamp host passed launch/PDF-inspection smoke testing.
5. Validation passed: 254 worker/model checks; 141 WPF checks; 110 independent PDF candidates and 117 paragraph groups; 18 frozen Phase 2 checks; 18 non-destructive cleanup safety checks; 14 ignore-boundary checks; 19 runtime/font/notice hashes; one host smoke check. An initial test-wrapper CLI argument issue was corrected before presentation launch; remaining suites resumed with unchanged application/test logic.
6. Preserved every starting tracked file except the intentional root `.gitignore` update. 28,783 pre-existing local non-build files are unchanged; 35 compiler/cache files were regenerated during builds. No pre-existing non-Git file is missing. The user's private 43,149-byte PDF remains unchanged, untracked and excluded from cleanup/staging. External recovery/live-temp state was measured by metadata only and is never a cleanup target.

## Measurements

Baseline: 45,907 files / 2,365,115,376 logical bytes including .git; 17,039 tracked files / 1,051,098,174 bytes.

Post-validation audit checkpoint: 48,074 files / 2,490,639,782 bytes. Growth: 125,524,406 bytes, including 119,321,672 bytes of new ignored staging. Tracked at that checkpoint: 17,086 paths / 1,054,374,637 bytes. Later report/inventory additions and Git bookkeeping are identified as additive, not hidden in a savings claim. The timestamped SIZE_COMPARISON and inventories contain the exact observed metrics.

Git .pack payload is unchanged at 79,218,973 bytes across five packs. Actual cleanup savings: **0 bytes**. Proposed cleanup and archive sizes are hypothetical, overlapping and unapproved. No historical pack shrinkage is claimed.

## Deliverables and remaining gate

All twelve required reports, repeatable audit/classification/build/cleanup/validation tools, machine-readable inventories and delivery hashes are complete. Licensing/font-fixture provenance, private backups, environment drift (Pillow 13.0.0 versus declared 12.3.0), historical managed-binary reproduction, the intermittent clipboard issue and archive approval remain documented limitations.

Before/after measurements and build/run verification following an actual approved cleanup remain conditional: cleanup was not approved. Use LOCAL_CLEANUP_GUIDE after separate explicit authorisation; do not remove -WhatIf on an agent's own initiative.

Final action: commit and push only maintenance/R1; verify its remote SHA and main still at the starting commit, then stop for review. Do not merge or begin Phase 5.3.

## Resume / reproduce

- Audit: `.venv/Scripts/python.exe REPOSITORY_MAINTENANCE_R1/tools/audit_workspace.py --out <new-external-private-folder> --label <new-label>`.
- Default non-removing check: `pwsh -NoProfile -File REPOSITORY_MAINTENANCE_R1/tools/Local-Cleanup.ps1`.
- Build: `pwsh -NoProfile -File REPOSITORY_MAINTENANCE_R1/tools/Build-Current.ps1`; use its new output with `tools/validate_r1.py --stage <output>`.
- Complete validation recipes, preservation proof and pending migration instructions are in the twelve reports and inventory/.
