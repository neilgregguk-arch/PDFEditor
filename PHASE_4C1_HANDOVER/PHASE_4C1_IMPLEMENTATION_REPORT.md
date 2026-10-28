# Phase 4C.1 implementation report

Delivered 28 October 2026. All implementation, building and tests took place in Codex. The separate `phase4c1/` source and runnable Windows x64 build extend Phase 4B. Prior releases, fixtures and evidence are preserved by a before/after hash audit. Phase 4C.2 has not started.

## Outcome and architecture

Supported position-aware Word lines now permit mapped-character insertion, deletion, range replacement with different lengths and complete line removal. Subsequent glyphs receive explicitly calculated origins. The line stays anchored at its original source x and baseline; it does not wrap, shrink its font or move unrelated objects. Unsafe spacing, unsupported glyphs, overflow, protected-content collision or failed candidate verification block the complete export while retaining every draft.

The two editing strategies remain distinct. Natural-layout paragraphs retain bounded wrapping and expansion. Existing equal-or-narrower substitutions retain fixed original origins. Other supported positioned changes use surviving source-pair spacing and original-font advances at edited joins.

The Phase 4B document session, chronological history, recovery, asynchronous worker, revision guards and atomic Save As are reused. Undo grouping is unchanged: one native text-change event records one history unit, with explicit control changes grouped as before. No word-based or time-based grouping has been added.

## Implementation map

- `Core/PositionLayout.cs`: immutable source observations, bounded character alignment, replacement/deletion classification, proposed origins and ink, single-line bounds and spacing rules.
- `Core/Models.cs`: `Layout.Positioned` pointer-free proposed geometry and proposed-origin hit testing.
- `Core/DocumentTransaction.cs`: consumes the complete per-region plan, writes explicit offsets, verifies proposed origins/ink and reports planning, candidate generation and reopen verification timing.
- `Core/PdfEngine.cs`: existing fixed-origin single-request path retained; spacing-recalculated positioned requests route through the document transaction.
- `Core/DocumentSession.cs`: retains source-based identity, including safe horizontal bound; working draft never becomes a synthetic source.
- `App/PositionedInk.cs`: source-font glyph presentation plus aligned visible caret and selection, using the same proposed origins as export.
- `App/PositionSelection.cs`: mapped click, drag, shift selection and word/line selection helpers. Logical text/selection and input remain with the existing RichTextBox.
- `App/EditorWindow.cs`, `App/SessionEditing.cs`: immediate editor width update, inactive drafts and source-clean page presentation, validation and source-bound recovery.
- `App/InsertionControlTests.cs`, `Checks/Program.cs`, `tools/test_insertion.py`: executable interaction, model and worker checks. Development independent readers are separate from application runtime.

## Source and draft model

`PositionedSource` retains original glyphs/origins/bounds, explicit offsets, verified original-font ink offsets, protected objects, coexisting nonpainting whitespace and the conservative page-margin horizontal limit. Original observations are never changed by planning. Native scratch objects measure verified glyph ink and are removed before the source is used. No native pointer survives in a session or cache observation.

`PositionedDraft` contains absolute proposed origins, PDFium N-1 float offsets, original surviving-character indices, character kinds, replacement-source indices, deleted original indices, per-glyph ink bounds, policy and ambiguity observation. Replacement attribution is deterministic, not a claim about original author intent. Only unchanged adjacent source pairs carry measured spacing forward.

The existing fixed-origin pathway remains available for same-count equal-or-narrower substitutions. Recalculated layouts are bounded to 512 source/draft characters, avoiding unbounded quadratic alignment on the input thread. A larger fixed-origin source is not newly prohibited solely by this recalculation limit. Unsupported or excessive drafts remain editable/recoverable within the inherited recovery size limit.

## Live interaction

The active original-font ink follows the proposal immediately; inactive regions retain their latest draft. Validation remains debounced by 300 ms and recovery by 350 ms. Input does not wait for a PDF candidate. Replies must match session instance, source hash and revision. Candidate verification does not replace the current ink presentation, so it does not introduce a new text-position jump.

Testing exposed a Calibri native-caret discrepancy of 1.271 pt after insertion. The supported positioned path now hides WPF's natural-spacing caret and highlight and paints them at the proposal. Mouse placement/drag use the same origin hit mapping; RichTextBox still owns text, offsets, keyboard commands and history. Unsupported drafts use the visible native fallback with a warning; their appearance is not a verified layout. The custom caret blinks, with its timer stopped for inactive/unloaded layers.

## Genuine output and integration

The transaction freshly resolves every region against original source hash/identity, checks all strategies together, creates text with each original font, sets explicit positions and removes only owned source objects. One complete candidate is saved, reopened and verified. Predicted glyph origins and ink are checked at 0.01 pt; untouched neighbours retain the same strict tolerance. Source programs, mappings/style/outlines, page properties and outside-area pixels are protected. Separate whitespace objects remain owned by the source and are never absorbed into line deletion.

Save stages beside a new destination, rechecks checksums/source and commits without overwrite. Failure retains all drafts; existing destinations and source cannot be replaced. Save retains the original working base and history, so reopen an output to start a freshly discovered generation. Recovery uses the private `phase4c1/sessions` directory and does not migrate older phase sessions.

## Build and delivery

Run `phase4c1/Launch.ps1` or `phase4c1/run/PdfEditorPrototype.exe`. Framework-dependent .NET 8 Windows Desktop x64 runtime is required. Build with `phase4c1/build.ps1`. The separate worker and unchanged PDFium 156.0.8076.0 DLL ship together; DLL SHA256 is `bede3932ce96a2e1ed9a7e6cae71aec8914efd2907d37ab44b1b81f9c8a6d04e`. Python/readers are development-only. No cloud dependency, installer or font substitution was added. Review the tests, spacing analysis, compatibility matrix, issues and manual guide alongside this report.
