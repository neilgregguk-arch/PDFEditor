# Future PDFEditor development rules

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
