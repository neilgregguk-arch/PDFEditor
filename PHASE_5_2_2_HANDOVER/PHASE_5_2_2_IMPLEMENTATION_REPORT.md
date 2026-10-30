# Phase 5.2.2 implementation report

Isolated corrective release under phase5_2_2. Earlier accepted releases are preserved. Final commit SHA is reported in the completion message and `git log -1`; the source checkpoint was explicitly labelled incomplete. No Phase 5.3 or Repository Maintenance R1.

## Implementation

- App/EditorWindow.cs uses the source-bound resolved hit target for activation, including bounded retained surfaces. Blank clicks do not snap to unrelated text. Existing async guards remain. Audits include current per-region presentation state.
- App/SessionEditing.cs prioritises original observed identities and deterministically resolves expanded surfaces. Only current attributable worker rejection affects a fitting region. Global summary and Save As require complete current-session verification.
- App/PresentationState.cs implements unchanged, pending, verified, rejected and stale states with session/source/identity/exact-text/revision evidence. Text area offers explicit access to overlapping regions. Caret and selection are snapshotted before activation/focus events can overwrite them; selecting the current inactive area also activates it.
- App/DraftPresentation.cs derives amber from current restrictions/rejection, rather than historical Blocked alone. Bounded native scrollable drafts use an explicitly labelled Segoe UI review font to keep unsupported subset characters visible. Valid/original presentation restores the embedded original family; no PDF mapping/font rule changes. Diagnostics distinguish current hard breaks and scalar/mapping failures.
- Dedicated multi-region/recovery WPF tests exercise hit routing, overlap, current characters, delayed responses, global history, new-process recovery and corrected save/reopen/re-edit. Diagnostic point override exists only during tests and is null for normal input.

PDF engine Core source is byte-identical to 5.2.1. Font identity/mapping, source ownership, safe envelopes, row/512-character limits, protected whitespace/collision checks, recovery schema, atomic transactions, exact text extraction and reopened candidate verification are unchanged. Presentation bounds do not confer extra PDF ownership. A pending positioned preview is a proposal; focus never grants approval.

## Delivery and preservation

run/PdfEditorPrototype.exe, PdfWorker.exe, managed assemblies/configuration, pinned pdfium.dll, assets and fixture folders form the runnable Windows x64 build. Requires .NET 8 Windows Desktop runtime (framework-dependent). `./phase5_2_2/build.ps1` rebuilds it. Optional existing `-Portable` publishes self-contained; that is not the tested shipping configuration. No new native dependency; Segoe UI is the Windows UI review font only. No PDF font substitution. Native SHA256: bede3932ce96a2e1ed9a7e6cae71aec8914efd2907d37ab44b1b81f9c8a6d04e.

Starting preservation baseline covers 13,886 tracked paths. START_HERE.md is the sole intentional previous-path update. Phase 1's separate 353-file manifest is checked too. The user's untracked manual-test PDF under phase5_1 remains untouched, excluded from new phase copies and staging. See prior-phase-preservation.json, phase1-preservation.json and release-manifest.json. All final successes have portable source/destination hashes in portable-pdf-index.json.
