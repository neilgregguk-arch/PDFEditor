# Phase 5.2.2 open issues

- Manual acceptance remains required: repeat the original two-region sequence, original/expanded clicks, Text area access, safe shortening and keyboard/caret/selection operations on the user's actual Windows setup. Automated WPF and any SendInput review are labelled separately.
- Historical intermittent clipboard Win32 5 is not claimed fixed. Actual platform clipboard tests are separate from deterministic shared-paste tests; inspect the current probe and inherited suite result.
- Exact original clipboard payload and physical click coordinates were unavailable. No claim that every original user action was reproduced. A limited automated Windows click/input spot-check is recorded separately; UIA can name an anonymous readonly document despite native editor keyboard focus, so accessibility certification remains open. The genuine fixture and explicit multi-region/character cases were exercised.
- Word subset U+0075 has a cmap entry but zero advance/no contours and lacks verified PDF encoding. No substitute font/mapping invented. Hard breaks, tabs, NBSP, unmapped glyphs, 512-character recalculation, row limits and safe-envelope refusals remain existing restrictions. Existing CRLF/CR-to-LF logical representation is explicit; no character/break is dropped for approval.
- An incomplete combined worker call leaves a fitting candidate pending, with a global failure reason. It does not establish which region is invalid, and cannot approve export. Recovery restores text/history, not approval.
- Expanded UI overlap is resolved by original source priority plus explicit Text area access. It does not enlarge PDF ownership or move protected neighbours.
- Frozen Phase 3 engine retains its historical one-expectation mismatch (17/18). Earlier evidence and tests are preserved. Multi-monitor/DPI/high-contrast/accessibility/third-party PDF coverage needs separate review.
- Windows x64/.NET 8 Desktop runtime is required for this supplied framework-dependent configuration. No Phase 5.3 or Repository Maintenance R1 work is included.

All observed failures and their disposition are recorded in the progress and final results, rather than silently weakening fidelity checks. Stop for Phase 5.2.2 manual acceptance.
