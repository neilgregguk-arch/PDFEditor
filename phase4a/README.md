# PDF Editor V2 - Phase 4A

Run `run/PdfEditorPrototype.exe` or `Launch.ps1`. Requires .NET 8 Windows Desktop Runtime x64. The existing WPF editing interface is preserved. The default source is `run/font-corpus/J-partial-encoding.pdf`, which the frozen Phase 3 engine refuses but Phase 4A can edit using its existing mapped glyphs.

Click `cafe calm.` and try `face calm.` or a longer repetition of those words. Save As to a new file; reopen it to edit again. Adding `Z` is refused even though the embedded font contains it: this PDF has no verified existing encoding for that character. All input is retained. No font substitution, font extension or multi-region transaction is implemented.

The original Word example still cannot be activated: its font issue is now separated from its spacing and ownership restrictions. See the six reports in `../PHASE_4A_HANDOVER/` for the complete evidence and limitations.

Build with `./build.ps1`. The delivered build is framework-dependent; `-Portable` remains unvalidated. Production uses only the existing WPF/Core/PDFium worker/runtime. Python, MuPDF, pypdf, fontTools, ReportLab, Poppler and qpdf are development tools and are not shipped as runtime dependencies.

Development commands from the project root:

```powershell
& .venv/Scripts/python.exe phase4a/tools/run_regressions.py
& .venv/Scripts/python.exe phase4a/tools/test_engine.py
& .venv/Scripts/python.exe phase4a/tools/test_discovery.py
& .venv/Scripts/python.exe phase4a/tools/test_compatibility.py
& .venv/Scripts/python.exe phase4a/tools/compare_compatibility.py
& .venv/Scripts/python.exe phase4a/tools/verify_independent.py
& .venv/Scripts/python.exe phase4a/tools/investigate_fonts.py
& .venv/Scripts/python.exe phase4a/tools/api_lab.py
& .venv/Scripts/python.exe phase4a/tools/verify_api_lab.py
& phase4a/run/PdfEditorPrototype.exe --ui-test --discovery-ui-test --font-ui-test --clipboard-probe --audit C:/path/to/fresh-evidence
```

The API lab is experimental and bypasses product eligibility with known object mappings. Its files are not production-approved exports. Negative controls deliberately produce a missing or wrong glyph. Do not confuse successful API returns or matching extracted text with a verified product export.

Regenerate the new synthetic corpus with `tools/create_font_corpus.py`; optional installed Office generators are `tools/create_word_corpus.ps1` and `tools/create_powerpoint_corpus.ps1`. These overwrite only generated Phase 4A inputs. Earlier phases remain untouched. Native dependency notices and the original controlled font license remain in `runtime/` and `run/`; the additional Compatibility Sans test font license accompanies `run/font-corpus/`.
