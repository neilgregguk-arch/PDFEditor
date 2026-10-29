# PDF Editor

An offline Windows PDF editing prototype built with .NET 8, WPF and an isolated PDFium worker. **The latest completed version is Phase 5.2.1, in [phase5_2_1/](phase5_2_1/).** Earlier phases and their evidence are intentionally retained.

## Run the current application

Requires Windows x64 and the **.NET 8 Windows Desktop runtime**. Keep the complete `phase5_2_1/run/` directory together.

```powershell
./phase5_2_1/Launch.ps1
# Open an original, previously unmarked multi-line Word paragraph:
./phase5_2_1/Launch.ps1 -Pdf './phase5_2_1/run/original-paragraphs/Word-cafe-paragraph.pdf'
```

Alternatively, launch `phase5_2_1/run/PdfEditorPrototype.exe`. The delivered build is framework-dependent, not an installer. Build from source with the .NET SDK:

```powershell
./phase5_2_1/build.ps1
```

## Current capabilities

- Bounded, scrollable retained-draft presentation with explicit pending/blocked/verified states and current-session Save As gating.
- Whole-paragraph discovery for selected original Word PDFs, using native and indexed structural proof.
- Automatic discovery of eligible original-font text regions.
- Bounded natural paragraph editing, controlled Word insertion/deletion and safe soft wrapping into genuine text runs.
- Multiple region/page drafts with document-wide undo/redo and source-bound recovery.
- Combined layout/collision validation and verified atomic Save As to a new filename.
- Proposed-position glyph, caret and selection presentation, including proposed-caret scrolling.
- Validated embedded paragraph identity for fresh-process whole-paragraph rediscovery and repeated save generations.

Rejected drafts now use a contained amber correction surface rather than painting unsafe PDF rows or extending across the page. This is a constrained prototype. Positioned text wraps only inside conservatively available space, using the original font. Unsupported mappings, hard newlines, unsafe spacing/collisions and exact-extraction failures remain blocked with drafts retained. Qualified original paragraphs activate as one logical region and gain validated identity on first export. Subsequent generations reopen as complete paragraphs. Legacy unmarked exports remain separate eligible/Limited lines. Private identity data is validated against actual content and is not an authenticity certificate. Clipboard reliability and physical input/OS display-scale checks remain open. Development stops after Phase 5.2.1 for review.

## Review and test

Start with the [Phase 5.2.1 user guide](PHASE_5_2_1_HANDOVER/PHASE_5_2_1_USER_TEST_GUIDE.md), [root cause](PHASE_5_2_1_HANDOVER/PHASE_5_2_1_ROOT_CAUSE_ANALYSIS.md), [implementation](PHASE_5_2_1_HANDOVER/PHASE_5_2_1_IMPLEMENTATION_REPORT.md), [test results](PHASE_5_2_1_HANDOVER/PHASE_5_2_1_TEST_RESULTS.md), [visual comparison](PHASE_5_2_1_HANDOVER/PHASE_5_2_1_VISUAL_COMPARISON.md) and [open issues](PHASE_5_2_1_HANDOVER/PHASE_5_2_1_OPEN_ISSUES.md).

The current [evidence index](phase5_2_1/evidence/README.md) identifies approved runs and retained development failures. The complete earlier source, fixtures, handovers and delivered builds are included. Generated virtual environments, bin/obj and temporary test-work caches are excluded.

The root [README.md](README.md) is the historical Phase 1 document and is intentionally unchanged because it is covered by frozen preservation manifests. Some historical reports contain workstation-specific absolute paths; use their repository-relative equivalents after cloning. Evidence that refers to excluded transient test-work paths may need regeneration; designated exported PDFs and reader reports are included.

## Dependencies and distribution notes

The application ships the pinned PDFium runtime and existing font/native dependency notices under each phase's runtime/run assets and licenses. Python tools (including research PDF libraries) are development-only; see the preserved reports and `requirements.txt` for their context. No new project-wide license has been assigned by this repository import. Review third-party notices before redistribution.

Git attributes preserve file bytes without automatic line-ending normalization so frozen SHA256 evidence can still be checked. Previous phase implementations remain unchanged. This entry guide is updated for Phase 5.2.1; its before/after hashes are recorded separately from historical preservation.
