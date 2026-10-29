# Phase 5.1 round-trip test results

Executed in Codex on Windows x64, 29 October 2026. Source start was `d864fbf265db32127a34e5862b30b4c72717caa9`, clean. Exact commands are in the user guide. Evidence paths below are relative to `phase5_1/evidence/`.

| Suite | Actual result | Evidence |
|---|---:|---|
| Active engine/discovery/compatibility/position/insertion/document/wrap | 151/151 | seven *-tests.json files |
| Dedicated paragraph generations/adversaries | 37/37 | roundtrip-tests.json |
| Separate WPF-process paragraph controls | 16/16 | paragraph-controls.json |
| Session/layout models | 29/29 | model/model-tests.json |
| Reopened repeated-space restriction | Pass; draft exact, export refused | paragraph-space-restriction.json |
| Inherited WPF controls, final build | 56/57 | controls-shipping/ |
| Same WPF suites, untouched C2 build | 56/57, same clipboard failure | frozen-c2-controls/ |
| Clipboard/basic-suite retry | 10/11, same failure | controls-basic-retry/ |
| Frozen C2 worker suites | 151/151 | frozen-phase4c2/ |
| Frozen C2 model | 22/22 | frozen-c2-model/model-tests.json |
| Current combined exports, independent readers | 206/206 | wrap-independent-verification.json |
| Current embedded/semantic structures | 206/206; 287 group instances | paragraph-structure-verification.json |
| Fixed-position / legacy independent exports | 11/11 and 21/21 | position-independent-verification.json; independent-verification.json |
| Frozen C2 combined independent exports | 73/73 | frozen-c2-readers/wrap-independent-verification.json |

The failing inherited check is native-copy-cut-paste-undo-redo: Win32 error 5, valid owner window, no identified clipboard holder. It also fails in untouched C2 and on retry; clipboard probes likewise fail in this desktop session. It is retained as the historical intermittent defect/environment limitation, not marked pass or claimed fixed. The new paragraph controls do not use the system clipboard.

## What the generations prove

The actual Word third paragraph passes two rows → three rows → one row through fresh native workers and again through separately exited WPF applications. The same embedded ID is retained while each new file establishes a new source hash and source object observations. Word Arial and Calibri pass three editing generations. Exact row/member counts, original fonts and complete logical text are asserted. Deleting the whole paragraph removes its text members with no invisible tombstone.

Six WPF processes use fresh isolated stores for generations; separate stages intentionally share a store to test recovery. Every row activates the same group. Checks cover all logical caret offsets at four app zooms, viewport containment, visible caret alignment at 0.01 pt, Up/Down/Home/End/shift, mapped multi-row drag, Backspace/Delete at soft boundaries, endpoint routed input, undo/redo after rewrapping, switching regions, three drafts across two pages, exited-process recovery and combined export. These are actual WPF commands/routed events/shared hit handlers, not physical keyboard/mouse or file-picker automation. Capture DPI is 96; app zoom does not certify OS display scales.

Adversarial cases include unmarked nearby matching lines, missing/duplicated members, external text/position changes, conflicting IDs including cross-page reuse, unknown schema/keys, broken/duplicate-key JSON, oversized/null/excessive member payloads, fractional row indices, wrong page/font/map/envelope claims, altered accessibility semantics and separately owned whitespace in a row gap. Later unsupported glyphs, hard breaks, vertical growth, source changes and failed Save As are refused. Two marked groups export safely alone and collide when combined; both drafts are retained.

## Independent checks and reader corrections

MuPDF text-drawing traces, fontTools cmap/glyph IDs/metrics, pypdf object structures, qpdf syntax through pikepdf and Poppler at 72/144 DPI check exact text, all modified regions, original programs/used mapping rules, origins/baselines, page properties, untouched glyphs/whitespace and zero outside-region changed pixels above threshold 8. Source/destination hashes are checked. Trace spans retain a separately owned Word F2 space that rawdict could merge into the edited span after reading order was preserved. No actual character is dropped or normalised; those spaces remain in untouched-object and raw-byte checks.

Independent structure checks inspect balanced custom marks, complete row indices, identical payloads, exact trace text and origins, absence of application-added accessibility semantics, existing semantic sequence equality and unchanged structure graphs/page StructParents. Coverage assertions require expected paragraph IDs to be encountered, so a vacuous zero-group scan cannot pass. A pypdf ContentStream truthiness guard initially skipped operations; it was corrected to an explicit `is not None` check, also strengthening the inherited font-rule reader. Frozen outputs are checked with their original engine/identity scheme. Historical prototype snapshots are matched back to actual source facts at the same tolerances; they are not trusted by an old opaque identity alone.

## Performance

The final 32-group fixture is a development-only untagged page derived from the existing fictional Word title TJ/font resources, not an untouched Word export. Size is 595.32 × 3400 pt. Two complete marked-save generations succeed. Cold rediscovery including render: 3174.17 ms; paragraph validation: 152.03 ms, excluding earlier font analysis. Warm median: 246.44 ms. Saves: 3190.10 and 4058.53 ms; generation/planning/reopen stages are recorded. Twenty repeated inspections show handle growth 0, RSS growth 112,721,920 bytes and worker exit. The same-file C2/current engine comparison is in paragraph-performance.json.

Fresh-process group activation (including Open and dispatcher work) ranges 203.49–306.40 ms in this run. Recovery store example: 316,970 bytes. Local input/layout timing and 30 wrap/unwrap operations are retained in controls-shipping/wrap-control-tests.json and wrap-performance.json. Measurements were under local/concurrent test load and do not certify large-document latency. Existing 30-second worker timeout, stale-response protections and cache/candidate caps remain.

## Retained failures and qualifications

Development caught content-stream append/reorder mistakes, a 32,767-byte string truncation, inaccurate guessed space extents, bitmap differences from reconstructing quantized claims instead of exact observations, and the one-character final-row edge case. The final writer inserts at the live source anchor, stores compact observed boxes under a 28,000-byte cap and reconstructs from exact observations. No geometry or bitmap tolerance was widened.

Two initial adversarial fixture errors were corrected: scalar pikepdf operands needed instruction replacement, and a whitespace obstacle was initially outside the horizontal edit area. One WPF test read an uninitialised cached layout rather than the source plan; corrected coverage uses the shared plan. Windows reused a PID, so fresh-process proof now pairs PID with OS creation time and isolated stores. Frozen-run output redirection and the reader's mixed-version fingerprint selection were corrected without touching old releases. Visual QA also exposed hidden native-caret panning at high zoom; the page now follows the proposed caret, with viewport containment tested at four zooms. Display strings were restored to correct UTF-8 after a development encoding mistake. Raw attempts are retained under development and timestamped control folders.

Earlier frozen suites also pass their previous counts: Phase 1 14/14, Phase 2 18/18, Phase 4A 18/18, Phase 4A.1 18/18, Phase 3 discovery 22/22, Phase 4A compatibility 23/23, Phase 4B document 17/17/position 20/20 and C1 insertion 30/30/document 17/17/position 20/20. The original Phase 2 suite against Phase 3 remains 17/18 because of the obsolete manifestless-view-only expectation. The C2 line-only rediscovery assertion is intentionally replaced by whole-declaration rediscovery; its earlier failure is retained and the original assertion still passes against frozen C2. Visual QA and byte-preservation audits are indexed separately.
