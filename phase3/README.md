# PDF Editor V2 - Phase 3

Local Windows WPF prototype with PDFium worker. Run `run/PdfEditorPrototype.exe` or `Launch.ps1`. Requires .NET 8 Windows Desktop Runtime x64; no Python or network service is required at runtime. The default letter has **no region manifest**. Earlier Phase 2 files remain in `../phase2/` unchanged.

Click a supported paragraph to use the existing inline editor. Save As always requires a new filename. Reopen that output to edit another region or make another edit. One changed region is committed per export. Working drafts remain available when validation fails.

The `run/corpus/` folder contains 15 fictional documents from ReportLab, MuPDF and Microsoft Word. The Word example, subset example, columns, table, annotation and spacing examples demonstrate conservative refusals; their presence does not imply editing support.

Build with `./build.ps1` using the installed .NET SDK. `-Portable` remains an unvalidated optional build mode. The normal delivered build is framework-dependent. Native/font dependency notices are in `runtime/` and `run/`. The application runtime does not include Python, MuPDF, ReportLab, Poppler or qpdf.

Development checks (project root, existing `.venv`):

```powershell
& .venv/Scripts/python.exe phase3/tools/run_regressions.py
& .venv/Scripts/python.exe phase3/tools/test_discovery.py
& .venv/Scripts/python.exe phase3/tools/verify_independent.py
& phase3/run/PdfEditorPrototype.exe --ui-test --audit C:/path/to/fresh-evidence
& phase3/run/PdfEditorPrototype.exe --discovery-ui-test --audit C:/path/to/other-fresh-evidence
```

`run_regressions.py` executes the original unmodified Phase 2 worker test class against both builds. Its old assertion that any manifestless PDF must be view-only deliberately fails on Phase 3; the retained raw result is 17/18, with that one behaviour superseded by discovery tests. The frozen Phase 2 build passes 18/18.

Regenerate development corpus with `tools/create_corpus.py`; Word export, when available, uses `tools/create_office_corpus.ps1`. This overwrites only the generated corpus files. Read `../PHASE_3_HANDOVER/` for the complete supported class, test evidence and limitations. Do not treat this as unrestricted PDF editing.
