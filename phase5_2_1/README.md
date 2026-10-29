# PDFEditor V2 — Phase 5.2.1

Corrects retained long-draft presentation without expanding PDF ownership, available space or export rights. Invalid text stays in one bounded amber scrollable surface; safe positioned previews retain original-font PDF geometry. Current whole-session verification controls Save As.

```powershell
./phase5_2_1/Launch.ps1 -Pdf './phase5_2_1/run/original-paragraphs/Word-cafe-paragraph.pdf'
```

Windows x64/.NET 8 Windows Desktop runtime. Build with ./phase5_2_1/build.ps1. See the [user guide](../PHASE_5_2_1_HANDOVER/PHASE_5_2_1_USER_TEST_GUIDE.md), [root cause](../PHASE_5_2_1_HANDOVER/PHASE_5_2_1_ROOT_CAUSE_ANALYSIS.md), [tests](../PHASE_5_2_1_HANDOVER/PHASE_5_2_1_TEST_RESULTS.md), [visual comparison](../PHASE_5_2_1_HANDOVER/PHASE_5_2_1_VISUAL_COMPARISON.md) and [evidence index](evidence/README.md).

Core source is byte-identical to 5.2. Clipboard Win32 5 and physical input/OS-scale/accessibility testing remain open. Earlier releases/private manual PDF are preserved. No Phase 5.3.
