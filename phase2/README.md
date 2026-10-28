# PDF Editor V2 - Phase 2 prototype

Launch **`run/PdfEditorPrototype.exe`**, or run `Launch.ps1`. This is a Windows x64 WPF prototype using a separate native-PDFium worker. The supplied build requires the **.NET 8 Windows Desktop runtime**; version 8.0.33 is installed on the test machine. It has no Python, PyMuPDF, web browser, server or network dependency at runtime. No production installer is included.

The default A sample opens automatically. Open the other files under `run/samples/` to try longer text, restricted space and font diagnostics. Click the existing paragraph itself and type on the page. Only the supplied hash-bound paragraph regions are editable. Other PDFs and saved outputs without an ownership manifest open as view-only documents.

The draft is separate from the original PDF. Saving removes the owned original text objects and reconstructs the region using its original embedded font. This is genuine region reconstruction, not universal native word editing or arbitrary reflow. Existing destinations and the original cannot be overwritten. Drafts are cached under `%LOCALAPPDATA%\PdfEditorPrototype\drafts` and retained after blocked saves. Undo history is in-memory per opened editing session, not persisted across reopening.

## Build

With the .NET 8 or newer SDK on Windows:

```powershell
& .\build.ps1
& .\Launch.ps1
```

`runtime/` supplies the pinned PDFium DLL, exact font asset and third-party notices. The delivered folder includes these prerequisites. If reconstructing assets from scratch, `tools/prepare_assets.py` is a development helper using the original Vera fixture font, fontTools and the pinned Windows `pypdfium2 5.14.0` wheel. It does not ship Python in the application. Preserve the exact font asset and sample manifests as a set; regenerating a font with different bytes invalidates old manifests. Build copies original sample PDFs only when initially missing.

`build.ps1 -Portable` can publish a self-contained .NET build, but that optional mode was not exercised in this phase. The tested and delivered executable uses the installed desktop runtime. Dependency restoration/building can use network access; running document operations does not.

## Verification

```powershell
# Development Python environment with pypdf, NumPy and Pillow; Poppler for independent visuals:
python -B tools/test_engine.py
python -B tools/verify_visuals.py
# Actual WPF control integration, with diagnostics isolated from ordinary recovery drafts:
.\run\PdfEditorPrototype.exe --ui-test --audit "C:\path\phase2-control-evidence"
```

The WPF test suite invokes actual controls/commands/routed input in a shown window. It is **not** physical mouse/keyboard automation. The host denied system clipboard access (Win32 5); the final control suite retains that failure. Windows UI automation also could not activate/capture the application correctly, so physical typing, mouse selection and file-dialog traversal remain manual verification items. Do not report all UI acceptance criteria as fully certified.

See the four reports in `../PHASE_2_HANDOVER/` for exact executed results, screenshots, known limits and a user walkthrough. `evidence/development/` retains earlier failing control checks and corrections. All Phase 1 files remain unchanged.
