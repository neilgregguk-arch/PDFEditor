# Phase 5.2.1 implementation report

The correction is isolated under phase5_2_1. All twelve Core C# files are byte-identical to Phase 5.2, recorded in evidence/unchanged-core-policy.json. Discovery scope, row observations, font mapping, layout limits, safe envelopes, source identities, PDF transactions and visual-fidelity tolerances are unchanged. Earlier accepted releases and private manual output remain preserved.

## Presentation policy

`App/DraftPresentation.cs` defines one policy used by active editing and inactive drafts. Local-safe pending/verified positioned text retains the established proposed-PDF glyph/caret layer. A locally unsafe or worker-blocked draft instead uses a bounded amber native RichTextBox with wrapping and internal vertical scrolling. Its full logical text remains available for selection/correction. The status and tooltip explicitly say this is retained text, not a proposed PDF layout.

The retained surface stays within source limits and is narrowed against protected objects. Its top lies within observed source ink; it does not infer new ownership. Protected graphics can further reduce its width. Font size remains the original size; the native retained preview's line spacing is a reading aid, not PDF geometry. Unsupported characters may use normal WPF display fallback in this explicitly rejected preview; this never grants font substitution or export rights.

`EditorWindow.cs` clips the page, configures the active surface, resets layout on Open and exposes meaningful pending/blocked feedback. Save As and its picker/hotkey remain unavailable until the current complete session verifies. Export still runs the unchanged source-bound transaction and reopened-candidate checks. A failed output operation retains text, clears approval and revalidates; it does not permanently classify a previously fitting layout as geometrically invalid.

`SessionEditing.cs` uses the same bounds/style for inactive retained drafts and records source/identity/text-bound viewport state. Re-entry restores the ordered selection. Source changes cannot inherit a viewport from another session. `PositionSelection.cs` delegates retained-draft caret/navigation/selection to native WPF, while preserving the accepted proposed-position handlers and hidden-native-caret suppression for valid positioned previews.

Async completion requires matching session object, revision, source hash and navigation generation. The current view is refreshed from current session state, not an old captured region. Same-logical-text formatting events do not create history/verification changes. The existing character-by-character undo policy remains.

## Testing and runtime

`PresentationControlTests.cs` and tools/presentation_process.py exercise real WPF controls and screenshots, including a controlled delivery gate in WorkerClient for actual late worker responses. The gate is internal test instrumentation and is unset during normal use. It does not alter worker protocol or PDF processing. No physical input certification is claimed.

Run `phase5_2_1/run/PdfEditorPrototype.exe` or Launch.ps1 with the cafe path. Windows x64 and .NET 8 Windows Desktop runtime are required. build.ps1 publishes the framework-dependent app and worker with supporting files. PDFium remains pinned to SHA256 bede3932ce96a2e1ed9a7e6cae71aec8914efd2907d37ab44b1b81f9c8a6d04e. No new production dependency, font asset, installer, cloud feature, modal editor, general reflow or Phase 5.3 work was introduced.
