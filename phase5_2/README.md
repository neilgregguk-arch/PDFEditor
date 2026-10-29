# PDF Editor V2 — Phase 5.1

Reliable, bounded rediscovery of newly exported original-font paragraphs through embedded declarations checked against actual PDF text objects. Whole-paragraph editing survives two → three → one row generations in fresh processes.

## Run

Windows x64 with .NET 8 Windows Desktop runtime; keep the complete run directory together.

```powershell
./phase5_2/Launch.ps1 -Pdf './phase5_2/run/paragraph-examples/Word-two-rows.pdf'
# To begin from the genuine original Word fixture:
./phase5_2/Launch.ps1 -Pdf './phase5_2/run/corpus/11-word-letter.pdf'
```

Build with `./phase5_2/build.ps1` and the .NET 8 SDK. Python/Poppler are development-only. No production dependency was added; existing native/font notices remain in run/runtime.

Read [the user guide](../PHASE_5_1_HANDOVER/PHASE_5_1_USER_TEST_GUIDE.md), [ownership analysis](../PHASE_5_1_HANDOVER/PHASE_5_1_PARAGRAPH_OWNERSHIP_ANALYSIS.md), [results](../PHASE_5_1_HANDOVER/PHASE_5_1_ROUNDTRIP_TEST_RESULTS.md) and [evidence index](evidence/README.md).

The private declaration is untrusted input, not an authenticity certificate. Actual member text/font/positions/reading order, page identity, bounds and neighbouring content must agree. Ambiguous/corrupted groups are restricted. Legacy unmarked C2 paragraphs are not retroactively grouped. Original font/mapping, hard-break and exact-space restrictions remain, and the historical clipboard error is still open. No general Word paragraph discovery, document reflow or Phase 5.2 work is included.
