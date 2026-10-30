# PDFEditor V2 — Phase 5.2.2

Corrective release for multi-region activation, current draft verification and character-specific refusal feedback. All PDF engine source is byte-identical to 5.2.1. Source identity, safe envelopes and export rules are unchanged.

```powershell
./phase5_2_2/Launch.ps1 -Pdf './phase5_2_2/run/original-paragraphs/Word-cafe-paragraph.pdf'
```

Windows x64, .NET 8 Windows Desktop runtime. Build with `./phase5_2_2/build.ps1`. Click original text or a bounded draft preview; use **Text area** above the page to return to either source region if previews overlap. Amber retains exact unsupported text and allows internal scrolling, using an explicitly labelled Segoe UI review font so empty subset glyphs are visible. Verified/original presentation restores the embedded source font; PDF export never substitutes a font. A shorter draft may still contain unmapped characters or hard breaks. Save As requires current complete verification.

See [user guide](../PHASE_5_2_2_HANDOVER/PHASE_5_2_2_USER_TEST_GUIDE.md), [root cause](../PHASE_5_2_2_HANDOVER/PHASE_5_2_2_ROOT_CAUSE_ANALYSIS.md), [tests](../PHASE_5_2_2_HANDOVER/PHASE_5_2_2_TEST_RESULTS.md), [visual review](../PHASE_5_2_2_HANDOVER/PHASE_5_2_2_VISUAL_AND_INTERACTION_REVIEW.md) and [evidence](evidence/README.md).

Manual acceptance, OS-scale/input/accessibility review and historical intermittent clipboard Win32 5 remain open. Stop after this phase; no Phase 5.3 or Repository Maintenance R1.
