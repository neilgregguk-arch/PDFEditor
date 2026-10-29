# Phase 5.2.1 root cause analysis

Starting commit: e7f73115923e192e3dfe48fad2938bf0f3cfbb52. Investigation and testing took place in Codex against the genuine, byte-original Word cafe fixture. The clarification supplied the full brief; its replacement/append mode and the original screenshot image files were not supplied. The full brief was additionally exercised as a possible paste in both modes, without asserting it was the screenshot's exact workflow. These results reproduce the described failure classes, not an asserted pixel-identical reconstruction of the user's screenshots.

## Reproduced failures

The original paragraph has 109 characters in two owned rows. Controlled replacement with 30 repetitions of `cafe calm.` produces 329 characters; appending it produces 439. Both exceed the existing height allowance. The planner returns unsafe positioned proposals of five/seven rows. The old active and inactive painters accepted any non-null positioned proposal without requiring its layout to be safe, so they painted rejected rows over the protected reference.

At 70 repetitions, replacement/append lengths are 769/879. The existing 512-character position-recalculation limit correctly refuses a proposal. The old active fallback makes its RichTextBox as wide as the entire unwrapped string: right edges 6,285.8/7,165.4 DIP on a 793.8-DIP page. Page painting was not clipped. The inactive fallback instead caps width and assigns only 36 DIP height for a single logical line. Thus switching regions changes wrapping and clips the retained text.

All four baseline Save As attempts were refused and the original PDF hash remained unchanged. This is not evidence of an invalid PDF export. Baseline metrics/full WPF captures are retained under phase5_2_1/evidence/baseline-presentation-*.

| Hypothesis | Finding |
|---|---|
| A. Correct refusal with poor presentation | Confirmed: unchanged height/length gates refuse the controlled long drafts. |
| B. Incorrect active editor dimensions | Confirmed for the null-proposal fallback: width follows unwrapped text, not its safe presentation area. |
| C. Active/inactive inconsistency | Confirmed: distinct fallback width/height decisions; rejected positioned ink was also drawn in both modes. |
| D. Clipping/scrolling | Confirmed: no page clip permitted spill; fixed-height inactive fallback hid text without a usable correction surface. Valid positioned-caret scrolling itself was not the cause. |
| E. Incorrect paragraph ownership/envelope | Not supported by these reproductions. Actual source membership/font/rows remain verified. Thirteen `cafe calm.` repetitions (142 characters) fit; fourteen (153) cross the height threshold. No envelope expansion is justified. |
| F. Combination | Confirmed: unsafe ink painting plus the fallback dimensions/containment mismatch explain the two observed classes. |

## Geometry and state

Source horizontal anchor is approximately 72.024pt; safe right is 523.296pt. The existing safe bottom is 136.808pt, with source top approximately 72.041pt. Five proposed rows require 114pt, exceeding the roughly 64.767pt source allowance and reaching the next reference. That refusal remains correct. Original source baselines and font metrics are immutable; the correction never moves the next paragraph, shrinks the font, invents membership or consumes blank page space.

Focus loss alone preserves the logical string. Switching to another region invokes a different painter and clean-background composition; the old fallback's layout decisions then made the same string appear different/clipped. The correction uses the same retained-draft surface policy in both paths. Native scroll offset and ordered selection are retained for same-source/same-text re-entry.

Validation responses already carried source/session/revision guards. Navigation guards now additionally prevent a response for an earlier view from changing the newly opened view. Opening clears the old layout and disables Save As, including its hotkey. Presentation-only formatting no longer restarts validation or creates a dirty edit when logical text is unchanged.

## Development findings kept separate

The first corrective candidate measured an empty native character rectangle while the editor was collapsed, causing an infinite-width Open failure. Visual review caught it; measurement is now restricted to visible active editors and finite rectangles. Later review found that immediate screenshot capture could render the previous TextBlock frame even though the paired JSON recorded current verification correctly. Capture now waits for layout/render quiescence. These were development/harness corrections, not additional claims about the user's original failure.
