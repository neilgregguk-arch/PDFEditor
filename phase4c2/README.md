# PDF Editor V2 — Phase 4C.2

Controlled soft wrapping for eligible original-font positioned Word text, with shared live/export geometry, multi-region drafts and strict combined verification.

## Run

Windows x64 with .NET 8 Windows Desktop runtime. Keep all of `run/` together.

```powershell
./phase4c2/Launch.ps1 -Pdf './phase4c2/run/corpus/11-word-letter.pdf'
```

Framework-dependent build: `./phase4c2/build.ps1` with the .NET 8 SDK. No Python is required to run the app. Python and the root requirements are for development verification only. The pinned PDFium runtime and third-party notices are retained under runtime/run.

Start with [the user guide](../PHASE_4C2_HANDOVER/PHASE_4C2_USER_TEST_GUIDE.md), [implementation report](../PHASE_4C2_HANDOVER/PHASE_4C2_IMPLEMENTATION_REPORT.md) and [evidence index](evidence/README.md).

Soft wrapping preserves the exact draft and original font; it stays inside conservative available space. It does not move neighbours or continue onto another page. Positioned hard breaks and unsafe/unmapped characters remain blocked. Some adjacent-space drafts fail exact PDF extraction and remain unsaved. Reopening can expose eligible emitted lines separately; whole-paragraph ownership is not inferred. Clipboard reliability and physical input/display-scale checks remain open. No work beyond Phase 4C.2 is included.
