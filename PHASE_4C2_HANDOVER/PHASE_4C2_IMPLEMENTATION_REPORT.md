# Phase 4C.2 implementation report

Completed 28 October 2026. The Windows x64 application is `phase4c2/run/PdfEditorPrototype.exe`; keep the complete run directory together. It requires the .NET 8 Windows Desktop runtime. The build is framework-dependent, with no Python dependency for users. Build from source using `phase4c2/build.ps1` and the .NET 8 SDK.

## Delivered behaviour

Eligible original-font positioned text can grow into multiple genuine PDF text runs inside a conservative available rectangle. Genuine Microsoft Word letter, Arial and Calibri sources demonstrate this. One exact logical draft underlies all soft rows. Wrapping adds neither newline characters nor history events. Multi-region/page drafts, document-wide undo/redo, source-bound recovery and atomic combined Save As remain operational.

## Layout and editing architecture

`Core/PositionLayout.cs` retains the original single-line planner as PlanSingle. Safe single-row edits retain their prior origin policy. Horizontal overflow or protected-content contact can invoke wrapping. The deterministic plan records each row's logical start, text, baseline, origins, relative positions and ink, plus the available area. A pure expanded-width source clone obtains alignment and measurements; it does not grant ownership. Final rows must satisfy the original real-area/protected-object checks. Source observations remain immutable.

`Core/Models.cs` delegates positioned hit testing to the plan. `App/PositionedInk.cs` displays original-font glyph runs, caret and selection per row. `App/PositionSelection.cs` maps rows to logical offsets and implements Up/Down/Home/End and shift variants with preferred X and soft-boundary affinity. WPF owns text, text selection and input; horizontal movement remains native. `SessionEditing.cs` finds inactive drafts through proposed row bounds, allowing a click on a newly created second row to reactivate its draft.

`Core/DocumentTransaction.cs` emits one real text object per planned row, preserving original font, colour, size and verified mapping. The first baseline stays original. Each later row resets X to the original anchor. Native spacing offsets are skipped for a one-character run because no inter-character offsets exist; its anchor/origin is still strictly verified. This edge-case fix also covers reconstruction and the legacy writer. Empty drafts retain source ownership without a replacement object.

## Combined verification and boundaries

All modified source identities are resolved against the immutable original before mutation. Intersecting changed envelopes block both drafts. One candidate contains all safe edits; it is reopened and checked before atomic save to a different filename. Unsupported/unsafe changes retain every draft and block the combined save. Fingerprint, revision, session and navigation guards reject stale or foreign responses.

Positioned target and unrelated geometry remain at 0.01 pt. Outside-region changed pixels must be zero above the existing per-channel difference threshold of 8. Existing natural-path tolerances remain unchanged. Glyph mapping, outlines, original font programs, protected whitespace and exact extraction remain verified. No tolerance was relaxed to obtain a pass.

The recalculation path is bounded to 512 logical characters and eight rows, with available height often tighter. Inferred leading is deliberately conservative. Positioned hard newlines and failed exact-space extraction remain blocked without modifying the draft. Reopening can expose independently justified emitted rows, with no whole-paragraph ownership guarantee. General reflow, moving neighbours, mixed-font reconstruction, cross-page flow, OCR, merge/split, forms, signatures, undo grouping and installers were not added.

Native PDFium remains pinned to 156.0.8076.0, SHA256 `bede3932ce96a2e1ed9a7e6cae71aec8914efd2907d37ab44b1b81f9c8a6d04e`. Existing third-party notices accompany runtime/run. Development Python readers are not shipped application dependencies. No new licensing conclusion is implied.

The preservation audit covers 3,689 pre-existing files and the separate 353-file Phase 1 manifest. Historical phase source/build/evidence/handovers remain unchanged. START_HERE is the sole intentional pre-existing repository-entry documentation update, recorded with before/after hashes. The new release manifest hashes source, build, tools and handovers. This phase stops for review; no next phase has started.
