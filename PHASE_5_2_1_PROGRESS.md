# Phase 5.2.1 progress — INCOMPLETE

Starting SHA: e7f73115923e192e3dfe48fad2938bf0f3cfbb52 on main. Only untracked file: private phase5_1/run/paragraph-examples/Word-two-rows-edited-manual-test.pdf (preserve, never stage). Separate phase5_2_1 source/runtime/run/tools copied from tracked 5.2 files; earlier evidence not duplicated. Baseline created AFTER textual migration and retains exact original keys/hashes. No Core/discovery/safety expansion is planned. No new font/fixture assets required.

## Verified starting observations
Read full corrective brief. Exact pasted text, replacement/append mode and original screenshots are not available in this task; optional request received the brief again, no exact string. Reproduce both paths with explicit controlled lengths; do not claim screenshot pixel equivalence. Prior tests did not cover actual invalid fallback presentation.

Source review: when PositionLayout returns no Positioned proposal, active editor falls back to native RichTextBox with width based on complete unwrapped text, ColumnWidth=1000000, and natural foreground/caret restored. Inactive fallback uses a different capped width and height from line-count/unsafe layout, so may clip long drafts. These are hypotheses until real WPF reproduction. Shared source envelope/export checks must remain unchanged.

## Current state / exact next action
Add a WPF reproduction stage using the genuine Word cafe source, active/inactive screenshots and measured control widths/clip bounds. Run it against copied UNFIXED code before changing presentation. Record active fallback, logical text and worker refusal. Then implement one consistent bounded invalid-draft presentation with exact native text/selection and explicit pending/blocked status; preserve valid positioned ink/caret scrolling. Do not change layout tolerances or original ownership.

## Commands
Build: ./phase5_2_1/build.ps1
Python: .venv/Scripts/python.exe phase5_2_1/tools/<tool>.py
Current suites: test_engine, test_discovery, test_compatibility, test_position, test_insertion, test_document, test_wrap, test_roundtrip, test_original; paragraph_process, original_process; existing Checks and independent/frozen readers. Final handover requires six corrective reports, runnable build, actual WPF visual states, preservation audit, commit and push. No Phase 5.3.

## Unfinished
Reproduction, root cause confirmation, implementation, tests, visual review and release all incomplete. Copied run binary/README are not a completed 5.2.1 release.

## Reproduced and corrected presentation paths (validation incomplete)
Actual pre-fix WPF captures: replacement/append lengths 329/439 draw 5/7 unsafe proposed rows over protected text; 769/879 hit the 512-positioning limit and expose a native editor right edge 6285.8/7165.4 DIP on a 793.8-DIP page. Inactive fallback height is only 36 DIP. All four exports refused; source unchanged. Baseline captures retained under baseline-presentation-*.

Correction in App only: one bounded amber, scrollable native draft surface for locally invalid or worker-blocked drafts, shared active/inactive bounds/font/line policy; safe positioned PDF ink remains for local-safe pending/verified layouts. No Core/discovery/transaction/envelope/tolerance changes. Native invalid navigation/selection is no longer intercepted by PDF-position handlers. Page and surface clip bounds; Save As UI is enabled only for a current verified whole session. Late validation/save UI updates require source/session/revision AND navigation match. A test-only worker delivery gate covers real late responses. Invalid previews retain exact text and scroll state; status distinguishes retained/pending/verified.

Visual review of initial correction caught a collapsed editor's empty native character rectangle producing an infinite width on Open. Corrected by measuring only a visible active editor and checking finite coordinates. Earlier faulty fixed captures retained; final tests now assert no Open failure and exact inactive text/bounds. Checkpoint is not complete: expanded WPF matrix, full regression, independent PDFs, handover and publication remain.

Exact next action: build and execute expanded presentation matrix (all zooms/window sizes, input positions/typing, native invalid caret/selection, incremental bounds, safe save/reopen and controlled late worker responses). Inspect final screenshots and preserve any failures. Then existing worker/model/WPF/reader/frozen suites, six reports, manifest, commit/push.
