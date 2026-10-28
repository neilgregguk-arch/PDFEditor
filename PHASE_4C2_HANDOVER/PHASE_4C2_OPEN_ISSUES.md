# Phase 4C.2 open issues

## Deliberate boundaries

- Whole wrapped paragraphs are not reliably rediscovered as one region. Saved rows are separate genuine PDF objects. Existing rules can justify an individual emitted line; short rows may remain Limited because separately owned Word whitespace cannot be claimed. No ownership tags/sidecar were added.
- Positioned hard newlines remain unsupported and block combined export while retaining the exact draft and recovery. Soft wrapping never inserts a hard break.
- Some adjacent-space drafts fail exact native extraction. They remain unsaved and unchanged; no trimming/normalisation workaround is used.
- Available area and leading are conservative inferences. Demonstrated 12 pt text uses 24 pt leading, not recovered Word paragraph formatting. Plausible edits can be refused. Neighbours never move and text never flows across pages.
- Recalculation is bounded to 512 characters/eight rows, often constrained further by height. Mixed fonts, unsupported mappings/transforms/styles, unsafe joins and ambiguous ownership retain prior restrictions.

## Physical interaction and accessibility

WPF tests cover routed text events, commands/shared hit mapping, four app zooms and 96-DPI capture. They do not certify physical keyboard/mouse, native file pickers, IME, touch, screen readers, high contrast or multiple OS display scales. The positioned visual layer overlays WPF's logical surface; assistive-technology behaviour needs dedicated review. Native text events are queued, so automated assertions wait for dispatcher processing.

The historical intermittent clipboard Win32 error 5 remains open. A passing probe is local evidence, not a reliability fix. Undo still records ordinary edit events without grouping improvement, as requested.

## Operational limits

Performance measurements use small local corpus documents. Large PDFs, many changed regions, damaged files, memory pressure and prolonged sessions need broader coverage. Existing limits remain: 128 changed regions per transaction; bounded history (2,000 entries/2 million history characters), 16 MB recovery protection, source fingerprint/revision rejection, cache and candidate retention caps, 30-second worker timeout. No new native-operation cancellation is claimed. Recovery contains source-bound text under the user's local application data.

Retained failed control runs are development evidence; final-controls-approved is authoritative. Early collision outputs referencing a replaced source are diagnostic, with the original fixture archived. Strict reader reports identify certified files. Historical JSON may contain workstation-specific/transient paths; retained exports/fixtures are usable after cloning, and checks can be regenerated. No installer or broad production readiness is claimed.

The frozen Phase 2-on-Phase 3 obsolete view-only expectation remains documented. The protected-graphic policy now permits safe wrapping. Neither is concealed by loosening thresholds. Development stops at Phase 4C.2 pending review.
