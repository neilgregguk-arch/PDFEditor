# PDF Editor V2 — Phase 4B

Local Windows x64 WPF prototype: multiple source-bound text drafts, chronological document undo/redo, recovery and one verified atomic Save As. Natural and narrowly constrained position-aware editing retain separate fidelity rules.

Run `./Launch.ps1` or `run/PdfEditorPrototype.exe`. Requires .NET 8 Windows Desktop runtime. The default fictional two-page document supports multiple natural edits. Build with `./build.ps1` (.NET SDK required); the delivered framework-dependent build is under `run/`.

Read `../PHASE_4B_HANDOVER/PHASE_4B_USER_TEST_GUIDE.md` first. Architecture, tests, recovery, validation and limitations are in that handover directory. Approved evidence is indexed in `evidence/README.md`. Previous phases are preserved. No installer, cloud dependency or Phase 4C work is included.

Save As requires a new destination. It retains the original source binding and working drafts/history. Reopen an output PDF for a fresh session. Unsupported glyphs, positional insertion and combined collisions block the whole export without discarding drafts. Clipboard error 5 remains intermittent; physical input remains a manual evaluation item.
