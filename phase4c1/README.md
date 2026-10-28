# PDF Editor V2 - Phase 4C.1

Windows x64 .NET 8 WPF prototype with controlled original-font character insertion/deletion in eligible positioned Word lines. Natural paragraph wrapping, multi-region sessions, document chronology, recovery and one verified atomic Save As are retained. No positioned wrapping or Phase 4C.2 work.

Run `./Launch.ps1` or `run/PdfEditorPrototype.exe`; open `run/corpus/11-word-letter.pdf` for the insertion demo. Requires .NET 8 Windows Desktop runtime. Build with `./build.ps1` (.NET SDK required). Keep App/Worker/native DLL/assets together. Python and independent PDF readers are development tools only.

Read `../PHASE_4C1_HANDOVER/PHASE_4C1_USER_TEST_GUIDE.md`. All six reports and `evidence/README.md` describe executed checks and restrictions. Drafts are never silently discarded; unsupported glyphs, unsafe spacing, horizontal overflow and failed complete verification prevent all export. Save requires a new filename and retains the original session base/history.

The visible positioned caret/selection uses proposed glyph geometry; the underlying native Calibri spacing discrepancy is recorded. Hardware input and non-100% OS display scales need manual testing. The intermittent clipboard issue remains open. Prior phases and their recovery are preserved.
