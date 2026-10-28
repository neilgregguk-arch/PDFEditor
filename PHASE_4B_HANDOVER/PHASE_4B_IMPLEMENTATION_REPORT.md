# Phase 4B implementation report

Delivered 28 October 2026. This local Windows prototype extends Phase 4A.1 in a separate `phase4b/` directory. Earlier source, builds, fixtures and handovers are preserved; preservation hashes are in `phase4b/evidence/`. Phase 4C has not started.

## Working application

Launch `phase4b/Launch.ps1` or `phase4b/run/PdfEditorPrototype.exe`. The default two-page fictional document has three editable natural paragraphs on page one and two on page two. This release is a framework-dependent .NET 8 WPF Windows x64 build, with a separate PDF worker and the existing pinned PDFium binary. Python, ReportLab, MuPDF, pypdf, pikepdf and Poppler are development verification dependencies, not application runtime dependencies. No network service is used.

## Architecture and implementation map

- `Core/DocumentSession.cs`: source-bound working state, region snapshots, chronology, validation, bounded history and atomic recovery.
- `Core/DocumentTransaction.cs`: fresh source discovery, combined planning, one candidate save, reopen verification and protected final commit.
- `Core/PdfEngine.cs`: original discovery/eligibility and clean draft backgrounds, removing source text objects from temporary page renders.
- `App/SessionEditing.cs`: inactive draft presentation, global undo/redo commands, selection persistence, document summary, export audit and work cleanup.
- `App/EditorWindow.cs`: source/session navigation, asynchronous validation, Save As and recovery integration.
- `App/WorkerClient.cs`: isolated worker requests, existing timeout/restart and serialized access; no UI-owned native PDF handles.
- `App/SessionControlTests.cs`, `App/ProcessRecoveryTests.cs`, `Checks/`: executable tests of actual controls, separate-process recovery and session invariants.

A session stores source path and immutable SHA256, current page/page count and observed dimensions, active key, original editable regions, font/glyph strategy information, drafts, caret/selection offsets, validation messages, revision, last verified revision and global history. A region fingerprint includes source hash, page, original object references/text, font hash/style, layout geometry and explicit positioning data. Temporary extracted font-file paths are excluded. Identical-byte source copies can rebind a recovered path, but edits remain bound to the same source bytes.

Preview and export always resolve identities against the original source. They never use indices from a previous generated candidate as authority. A changed or incompatible identity retains its original snapshot and draft in the session and blocks export.

## User-visible behaviour

Multiple regions and pages retain independent text without intermediate saving or switching prompts. The active original-font editor remains in place; inactive drafts are transparent application-owned text over a source-clean render. Original graphics remain in the render. This temporary presentation is explicitly a working draft, with a small document summary showing changed areas, attention and readiness. Invalid text stays visible and editable. Zoom uses page coordinates and does not discard text.

The clean background removes all modified source text on that page plus the currently selected text, avoiding duplicate original text underneath drafts. Final files use genuine PDF text-object replacement, without white cover rectangles.

Undo/redo follows one chronological document stack and activates the affected region/page. Native RichTextBox undo is disabled. Ctrl+Z, Ctrl+Y and toolbar commands route to this stack. Source selection and programmatic restoration do not produce text-history entries.

Validation is debounced by 300 ms; persistence by 350 ms. Input performs local text/layout work, then the worker validates the complete modified set asynchronously. Responses must match the session instance, source hash and revision. An old response cannot mark an unrelated session verified even when its revision counter matches. Save captures a complete request; a successfully saved older snapshot does not mark subsequent working text saved.

## Export and retained working base

Every modified area participates, including blocked drafts. The worker rejects an unsafe set rather than silently saving its valid subset. It loads one source, plans all changes, removes the union of original objects, applies each region's existing strategy, generates changed page content and saves one temporary PDF. Reopen checks cover every changed region, untouched objects/pages, fonts and outside-area pixels. Only then is a checksummed file staged beside the selected new destination and moved without overwrite. Source and existing destinations are protected. Temporary candidate cleanup is advisory and cannot turn a committed save into a reported failure.

Save As retains the original source binding, working text and history. It does not reset the session to the exported file or mark drafts clean. Reopen an exported PDF to start a newly discovered session; second-generation tests exercise this path. Export audit JSON records the captured changes and verification result.

## Boundaries and review

Natural wrapping retains previous region/font restrictions. Position-aware text retains same-count, equal-or-narrower substitutions and original glyph positions; insertion, deletion and reflow remain blocked. Mixed edits preserve each strategy separately. See the validation report for tolerances and the issues report for remaining limits. Review the test report and manual guide before wider use. This remains a constrained prototype, without installer or broad PDF compatibility certification.
