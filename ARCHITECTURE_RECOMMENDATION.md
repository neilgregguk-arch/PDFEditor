# Architecture recommendation

## Recommended direction

Use a **native Windows .NET/WPF shell with a separate native PDF worker**, with PDFium as the primary candidate for rendering, extraction and constrained text-object mutation. Use qpdf where structural checks or controlled resource/stream work warrant it. Keep the shell replaceable and the editing policy independent of both engines.

This is an evidence-based direction, not a completed architecture validation: Phase 1 demonstrated the native engines through Python bindings. No WPF shell, C++ worker, IPC protocol or Windows installer has been implemented or benchmarked. A production-only path without PyMuPDF remains a Phase 2 acceptance requirement if closed-source distribution is retained.

The largest technical risk is the edit model, not the choice of window toolkit. Our samples show that a clean save can still overflow, a different word width can shift neighbours, and font resources can change without visible damage. Architecture must make eligibility, preview and post-save checks first-class operations.

## Options considered

| Option | Strengths | Costs and risks | Decision |
|---|---|---|---|
| Tauri 2 shell + separate worker | Cross-platform shell potential, web UI familiarity, explicit sidecar support | Rust/JS/native tooling, coordinate/zoom synchronization, IPC permissions, WebView2 dependency and offline installer planning. Does not solve PDF layout. | Viable second choice if cross-platform delivery becomes a real requirement. |
| Native Windows WPF/.NET + native worker | Fits Windows priority, native file/keyboard/accessibility integration, no browser-runtime requirement for the shell, established UI model | Windows-only shell; native ABI/lifetime and IPC work remain. Self-contained .NET/native dependencies increase package size. | **Preferred Windows direction.** |
| Python desktop shell + current harness | Fastest continuation of research; Python bindings already work | Interpreter/native-DLL packaging, startup/AV behaviour and UI stack selection untested. Current harness depends on AGPL PyMuPDF. | Keep for engineering tools rather than committing the product to it now. |
| Commercial SDK in a native shell | May reduce content-edit/reflow implementation burden | Licensing/module costs and vendor dependency; offline/distribution terms and real fidelity unverified | Contingency if the product must promise more than conservative text correction. |

[Microsoft's WPF overview](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/overview/) confirms WPF's Windows scope and .NET UI model. Tauri's [sidecar documentation](https://v2.tauri.app/develop/sidecar/) supports external workers; its [Windows installer documentation](https://tauri.app/distribute/windows-installer/) provides offline/fixed WebView2 options. A default download-bootstrapper installer would not meet a strict offline-install requirement. These are researched properties, not locally measured packaging results.

## Engine contract and edit model

The shell should send versioned local commands such as `inspect`, `render`, `plan_edit`, `preview_edit`, `save_as` and `verify_saved`. A document session and source fingerprint prevent stale selection handles. Selection refers to glyph/object identity plus geometry, rather than only a matching string. Maintain page/object/font references and text rendering state, including encoding, transformation, character/word spacing and visibility.

An edit plan must name its mechanism and outcome:

- **Direct text-object/operand change:** eligible glyph mapping, original font resources and controlled advance/geometry.
- **Region reconstruction:** explicitly owned text region, available fonts/shaping and an approved bounding area; requires distinct user-visible semantics.
- **Unsupported/refused:** reason such as missing glyphs, ambiguous shared object, unsafe overlap, scanned content or unsupported encoding.

The first production prototype should accept only horizontal simple digital text where mapping and fit are provable. Do not expose the fixture-specific ASCII replacement function as a generic backend. PDFium object mutation is the primary candidate, but its handling of kerning/position arrays and subsets requires tests beyond the single line demonstrated. qpdf's parser is useful when controlled operand rewriting is necessary; it is not the missing layout engine.

## Process, save and integrity boundaries

Run PDF processing outside the UI process. Serialize PDFium calls within a worker; for concurrent render work use separate processes, not simultaneous calls on threads. [pypdfium2's API guidance](https://pypdfium2.readthedocs.io/en/stable/python_api.html#incompatibility-with-threading) documents this restriction. Pass file paths and versioned JSON messages over local pipes; stream or share rendered image buffers rather than base64-encoding large page images into JSON.

Keep the source read-only. Edit a working session, save a new temporary candidate, reopen independently, validate semantics/resources/geometry, then commit to the requested new destination. Use atomic rename within the destination volume after successful validation, handle locked files and disk-full failures, and never silently fall back to overwriting the source. A worker crash leaves the original intact. These are proposed product safeguards; Phase 1 proves source preservation through separate outputs and hash checks, not crash-safe transactional saves.

Preview the actual saved/reopened candidate rather than only a canvas overlay. Distinguish font/resource substitution from ordinary text changes. Retain a command history for undo and rebuild from the immutable source when needed. Detect signatures, encryption permissions, forms and unsupported structures before edits; do not imply ordinary Save As preserves signature validity.

## Offline operation, performance and maintenance

All document operations should run locally with no remote parsing, fonts, telemetry dependency or paid API. Bundle required engines/runtimes and font notices in the eventual installer, and test installation on a clean offline Windows VM. Choose x64 first; ARM64 is a separate build/validation target. Ship security updates to native engines and audit DLL loading paths.

Render visible pages/tiles on demand, cancel stale requests, cache by document revision/page/zoom and cap memory. Keep interactive selection separate from expensive verification. Phase 1 measured only tiny documents; it does not establish UI latency, startup, memory or large-file performance targets.

Pin native engine builds, isolate adapters behind the worker contract, retain this corpus, and add independently generated documents. Re-run semantics and visual isolation checks when engine versions change. For a proprietary path, use PDFium/qpdf in shipped code and keep appropriately licensed independent reference tooling in development; do not assume today's PyMuPDF-dependent inspector is suitable for redistribution.

## Architectural review gate

Proceed with this direction only after a hardened CLI demonstrates robust selection-to-object mapping, missing-glyph refusal, collision/advance handling, source-safe saves, and the intended licensing composition. Review the shell decision after those tests and a packaging spike. No complete graphical editor is justified by this corpus alone. [The Phase 2 proposal](PHASE_2_PROPOSAL.md) defines that gate; it has not been started.
