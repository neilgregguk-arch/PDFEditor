# PDF Editor

An offline Windows PDF editing prototype built with .NET 8, WPF and an isolated PDFium worker. **The latest completed version is Phase 4C.2, in [phase4c2/](phase4c2/).** Earlier phases and their evidence are intentionally retained.

## Run the current application

Requires Windows x64 and the **.NET 8 Windows Desktop runtime**. Keep the complete `phase4c2/run/` directory together.

```powershell
./phase4c2/Launch.ps1
# Open the genuine Word sample used for insertion/deletion tests:
./phase4c2/Launch.ps1 -Pdf './phase4c2/run/corpus/11-word-letter.pdf'
```

Alternatively, launch `phase4c2/run/PdfEditorPrototype.exe`. The delivered build is framework-dependent, not an installer. Build from source with the .NET SDK:

```powershell
./phase4c2/build.ps1
```

## Current capabilities

- Automatic discovery of eligible original-font text regions.
- Bounded natural paragraph editing, controlled Word insertion/deletion and safe soft wrapping into genuine text runs.
- Multiple region/page drafts with document-wide undo/redo and source-bound recovery.
- Combined layout/collision validation and verified atomic Save As to a new filename.
- Proposed-position glyph, caret and selection presentation.

This is a constrained prototype. Positioned text wraps only inside conservatively available space, using the original font. Unsupported mappings, hard newlines, unsafe spacing/collisions and exact-extraction failures remain blocked with drafts retained. Reopened wrapped text may expose separate editable lines rather than a whole paragraph. Clipboard reliability and physical input/OS display-scale checks remain open. Development stops after Phase 4C.2 for review.

## Review and test

Start with the [Phase 4C.2 user guide](PHASE_4C2_HANDOVER/PHASE_4C2_USER_TEST_GUIDE.md), [implementation report](PHASE_4C2_HANDOVER/PHASE_4C2_IMPLEMENTATION_REPORT.md), [test results](PHASE_4C2_HANDOVER/PHASE_4C2_TEST_RESULTS.md), [spacing analysis](PHASE_4C2_HANDOVER/PHASE_4C2_WRAPPING_AND_SPACING_ANALYSIS.md), [compatibility matrix](PHASE_4C2_HANDOVER/PHASE_4C2_COMPATIBILITY_MATRIX.md) and [open issues](PHASE_4C2_HANDOVER/PHASE_4C2_OPEN_ISSUES.md).

The current [evidence index](phase4c2/evidence/README.md) identifies approved runs and retained development failures. The complete earlier source, fixtures, handovers and delivered builds are included. Generated virtual environments, bin/obj and temporary test-work caches are excluded.

The root [README.md](README.md) is the historical Phase 1 document and is intentionally unchanged because it is covered by frozen preservation manifests. Some historical reports contain workstation-specific absolute paths; use their repository-relative equivalents after cloning. Evidence that refers to excluded transient test-work paths may need regeneration; designated exported PDFs and reader reports are included.

## Dependencies and distribution notes

The application ships the pinned PDFium runtime and existing font/native dependency notices under each phase's runtime/run assets and licenses. Python tools (including research PDF libraries) are development-only; see the preserved reports and `requirements.txt` for their context. No new project-wide license has been assigned by this repository import. Review third-party notices before redistribution.

Git attributes preserve file bytes without automatic line-ending normalization so frozen SHA256 evidence can still be checked. Previous phase implementations remain unchanged. This entry guide is updated for Phase 4C.2; its before/after hashes are recorded separately from historical preservation.
