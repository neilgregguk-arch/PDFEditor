# PDF Editor

An offline Windows PDF editing prototype built with .NET 8, WPF and an isolated PDFium worker. **The latest completed version is Phase 4C.1, in [phase4c1/](phase4c1/).** Earlier phases and their evidence are intentionally retained.

## Run the current application

Requires Windows x64 and the **.NET 8 Windows Desktop runtime**. Keep the complete `phase4c1/run/` directory together.

```powershell
./phase4c1/Launch.ps1
# Open the genuine Word sample used for insertion/deletion tests:
./phase4c1/Launch.ps1 -Pdf './phase4c1/run/corpus/11-word-letter.pdf'
```

Alternatively, launch `phase4c1/run/PdfEditorPrototype.exe`. The delivered build is framework-dependent, not an installer. Build from source with the .NET SDK:

```powershell
./phase4c1/build.ps1
```

## Current capabilities

- Automatic discovery of eligible original-font text regions.
- Bounded natural paragraph editing and controlled single-line Word character insertion/deletion.
- Multiple region/page drafts with document-wide undo/redo and source-bound recovery.
- Combined layout/collision validation and verified atomic Save As to a new filename.
- Proposed-position glyph, caret and selection presentation.

This is a constrained prototype. Unsupported fonts/glyph mappings, unsafe spacing, collisions and positioned wrapping remain blocked. Clipboard reliability remains an open issue. Physical input and OS display scales beyond the measured workstation configuration still need manual testing. No Phase 4C.2 work has been started.

## Review and test

Start with the [Phase 4C.1 user guide](PHASE_4C1_HANDOVER/PHASE_4C1_USER_TEST_GUIDE.md), [implementation report](PHASE_4C1_HANDOVER/PHASE_4C1_IMPLEMENTATION_REPORT.md), [test results](PHASE_4C1_HANDOVER/PHASE_4C1_TEST_RESULTS.md), [spacing analysis](PHASE_4C1_HANDOVER/PHASE_4C1_WORD_SPACING_ANALYSIS.md), [compatibility matrix](PHASE_4C1_HANDOVER/PHASE_4C1_COMPATIBILITY_MATRIX.md) and [open issues](PHASE_4C1_HANDOVER/PHASE_4C1_OPEN_ISSUES.md).

The current [evidence index](phase4c1/evidence/README.md) identifies approved runs and retained development failures. The complete earlier source, fixtures, handovers and delivered builds are included. Generated virtual environments, bin/obj and temporary test-work caches are excluded.

The root [README.md](README.md) is the historical Phase 1 document and is intentionally unchanged because it is covered by frozen preservation manifests. Some historical reports contain workstation-specific absolute paths; use their repository-relative equivalents after cloning. Evidence that refers to excluded transient test-work paths may need regeneration; designated exported PDFs and reader reports are included.

## Dependencies and distribution notes

The application ships the pinned PDFium runtime and existing font/native dependency notices under each phase's runtime/run assets and licenses. Python tools (including research PDF libraries) are development-only; see the preserved reports and `requirements.txt` for their context. No new project-wide license has been assigned by this repository import. Review third-party notices before redistribution.

Git attributes preserve file bytes without automatic line-ending normalization so frozen SHA256 evidence can still be checked. No previous implementation file was changed for the repository import; only Git configuration and this entry guide were added.
