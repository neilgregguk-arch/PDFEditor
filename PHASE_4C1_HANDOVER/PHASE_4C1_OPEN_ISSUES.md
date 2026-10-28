# Phase 4C.1 open issues

## Deliberate safety limits

This is controlled single-line editing, not Word paragraph reflow. Positioned newlines/wrapping remain blocked. Original-font character eligibility, transforms, paint, clipping and ownership gates are unchanged. Only mappings actually verified in each PDF can be inserted. Natural paragraphs retain their separate bounded wrapping model. No font substitution, subset rebuilding, moving unrelated objects, OCR, merging/splitting, forms, annotations, signatures, AI or cloud functionality was added.

Spacing at edited joins uses verified advances with zero borrowed original residual. It is not a new kerning engine. Original pair residuals are retained only for surviving adjacent characters. Repeated-symbol alignment is deterministic and conservative, without author-intent reconstruction. A conceptual replacement may be classified differently from a user's typing history. Classification does not authorize extra spacing changes.

New `fff` ink overlap and double-space extraction collapse are concrete refused cases. Other pairs can also fail strict reconstruction/extraction even when local planning initially passes. Every draft remains available; a failed candidate blocks the complete transaction. An entire line can be removed safely in tested fixtures, but an empty region is absent on later rediscovery.

## Presentation and interaction

Calibri exposed a 1.271 pt difference between WPF natural-spacing caret and positioned glyphs. Supported positioned drafts now show a custom proposed-position caret/highlight and map mouse selection accordingly. Hidden native geometry is still recorded; it is not claimed fixed internally. Invalid drafts fall back to native presentation with warnings and may scroll or wrap temporarily. They are not a verified PDF layout.

Actual controls/shared click and drag methods, routed input/commands and saved output were tested. No hardware mouse/keyboard or native Windows file-picker automation took place. Four zooms were measured at the actual 96 DPI / 100% Windows display scale. 125%, 150%, 200% OS scaling, IME, accessibility tools, touch, high contrast and complex bidirectional/shaped scripts are not certified. Manual checks are in the guide. WPF control tests do not establish new physical comfort feedback.

The intermittent clipboard Win32 5 defect remains open. This phase does not attempt a clipboard fix. Passing release copy/cut/paste checks and five successful probes do not prove reliability. Earlier phase failures remain preserved. Undo grouping is unchanged by request.

## Document integrity and persistence

Untouched visual/glyph/font checks are strict, but full tag trees/MCID semantics, accessibility, logical reading order, XMP, PDF/A, complete annotation dictionaries and signature preservation are not certified. Replacement stream order can differ from visual reading order. Font resource aliases may accumulate; unused resource entries can be pruned. Used font programs and mapping/width rules are independently checked.

Recovery is private to Phase 4C.1, hash-keyed and atomically replaced. Earlier phase sessions are preserved rather than migrated. A changed source is a new session. History remains bounded to 2,000 entries / 2,000,000 UTF-16 before+after characters. Recovery is limited to 16 MB; oversize drafts stay in memory and the prior file survives. Multiple app instances have no recovery merge or locking; do not edit the same source concurrently. Incompatible snapshots can require technical inspection of retained JSON; no orphan-draft UI is added.

The application retains the original source binding and drafts/history after Save As; it does not automatically rebase or mark drafts clean. Source and existing destinations cannot be overwritten. Atomic stage/move failure is tested, but crash/power-loss durability and unusual network-filesystem semantics are not certified.

## Performance and packaging

Recalculated alignment is bounded at 512 source/draft characters; fixed-origin substitutions retain the earlier pathway. Native work retains the 30-second worker timeout and revision/session guards, with no in-flight native cancellation. Analysis cache and candidate retention remain eight observed pages and twelve candidate PDFs/twelve PNGs per work directory. Total session/font memory is not hard capped; clean-close cleanup is best effort and crashes can leave orphan directories.

Measured timings cover small local fixtures and programmatic WPF handlers, not large documents or keyboard-to-screen latency. Framework-dependent .NET 8 Windows Desktop x64 is the delivered build. No self-contained clean-machine or installer certification was performed. Development independent readers are not runtime dependencies; normal Save As uses the built-in worker's PDFium structural/glyph/outline/pixel verification.

## Retained failures and corrections

The first insertion test expected every proposed example to pass: the `fff` and double-space cases exposed genuine safety limits and are now explicit negative controls. The passing within-word/multi-insertion cases use other safely mapped letters; no numeric threshold was relaxed. Initial independent glyph sorting incorrectly included protected F2 spaces inside expanded titles; they are now tracked separately and still strictly preserved.

Old positioned tests expected longer, shorter and wider replacements to fail; original results are retained and those three expectations intentionally changed. An initial discovery test found a verification-envelope compatibility break after routing all positioned single requests through combined output; the original fixed-origin single-request path is retained, restoring the old contract. Parallel test work-folder names collided at equal Windows timestamps; UUID work directories fixed the harness collision. A Word-analysis JSON serialization error from reusing a raw-byte variable was corrected.

Early WPF insertion tests assumed reopening an existing source reset its session. It correctly restored prior drafts; tests now explicitly restore the original text before isolated editing assertions. Native Calibri caret failure is retained in development evidence and led to the aligned visual layer. Selection screenshots now wait for rendering after changing selection; this is a capture correction, not a geometry tolerance change. Consult the test report for designated release evidence and all retained failures.

Stop at Phase 4C.1. Phase 4C.2 requires review.
