# Phase 4B open issues and limits

## User interaction

Historical clipboard error Win32 5 remains intermittent. Earlier runs in this phase failed the clipboard control case; later probes and the designated release run passed. No clipboard fix is claimed. Prior evidence sometimes reported a valid owner with holder PID zero/unknown; this does not establish the cause. Draft/history safeguards still apply when clipboard operations fail.

WPF test code exercises the actual controls, routed text composition, editing commands, shared region hit-testing and export paths. It does not send hardware mouse/keyboard input or manually operate Windows file pickers. Physical clicking, typing, IME, keyboard shortcuts and dialogs remain manual checks in the guide. The Word title's WPF caret has the inherited small sub-point approximation; exact PDF glyph position checks are separate. No new physical comfort assessment is claimed.

Inactive invalid drafts are application presentation, not certified PDF appearance. Expansion is not automatic content movement. A blocked area does not stop editing another area but prevents a complete Save As until corrected. Recovery identity mismatch can require inspection of preserved JSON; there is no orphan-draft editor. Save retains drafts against the original, so reopening an output is required to start a new source base.

## PDF scope

Eligibility remains deliberately narrow. No general Word reflow, positioned insertion/deletion, font substitution, subset rebuilding, OCR, forms, signatures, annotation editing, merging/splitting or cloud features were added. Rotated/clipped/complex/unsupported font runs remain gated. Broad mixed-document coverage is not established by the small fixture corpus. Tags, MCID/structure trees, accessibility, XMP, PDF/A conformance, complete annotation dictionaries and semantic reading order are not certified. Replacements can be appended in a different content-stream order despite identical visual geometry. Existing protected-document gates remain necessary.

Font aliases may accumulate, and unused dictionary entries can be pruned by PDFium; used embedded programs and mappings are verified. Existing documents without safely reusable mappings remain ineligible.

## Performance, persistence and packaging

History is bounded to 2,000 entries / 2,000,000 stored UTF-16 characters. Current draft text is never truncated. Recovery max is 16 MB; a larger draft remains in memory with previous on-disk recovery retained. Up to 128 modified regions per transaction are supported. Per-analysis cache and candidate retention are bounded (eight analyses; twelve candidate PDFs and twelve PNGs), but extracted fonts, observed region snapshots and total session memory have no comprehensive hard cap.

Clean-close temporary cleanup is best effort. Font locks or crashes can leave orphan work directories; no global crash-orphan collector is included. Separate instances can race on one recovery file, with no merge/lock. Native operations have the existing 30-second worker timeout, without in-flight native cancellation. Small-corpus performance is measured; large documents and prolonged production workloads are unqualified.

The delivered executable needs the .NET 8 Windows Desktop runtime on Windows x64. A self-contained switch exists in build.ps1 but that variant and clean-machine installation were not certified. No installer, deployment or production support claim is made. Independent reader tools are development-only and are not invoked for every normal user save; runtime save verification uses PDFium plus structural/glyph/pixel checks.

## Development failures retained

An early layer insertion before page-child construction caused a constructor exception; placement was corrected. Mixed source encodings produced arrow mojibake; new source files were normalized to UTF-8. An early destination-protection test incorrectly expected a pre-existing protected file not to exist; it now asserts byte preservation. An independent parser initially misclassified trailing target spaces as neighbours; target classification was corrected without loosening fidelity limits.

The unchanged old UI contract suite had 14/26 failures, including obsolete per-region undo, single-draft recovery, dirty-switch and bitmap assumptions plus intermittent clipboard behaviour. Raw files remain in `old-control-contracts/`. Active copies were adapted to the required document model while retaining substantive control, geometry and fidelity assertions. Intermediate active runs had 25/26 and 37/38 passes because of clipboard error 5; those are retained rather than erased. Frozen Phase 2 assertions against Phase 3 retain one known obsolete manifestless-view-only expectation (17/18). Consult the test report for the designated final evidence.

Stop at Phase 4B. Phase 4C requires review.
