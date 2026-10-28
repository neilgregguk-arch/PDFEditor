# Phase 4B history and recovery

## One chronology

Each text-change event records region key, complete before/after text and caret offsets. An A, B, C edit sequence undoes C, B, A and redoes A, B, C, even when another region is active. Navigation opens the affected source page and restores its draft and caret. Ordinary selection changes only update caret/selection state. Programmatic restoration suppresses text recording. New input after undo removes the redo tail. Native RichTextBox undo is disabled to avoid contradictory stacks; toolbar and routed undo/redo commands share document history.

There is no time-based word grouping: one native text-change event is one history unit, and an explicit control BeginChange/EndChange can group an operation. This can produce finer undo steps than a word processor. History is bounded to 2,000 entries and 2,000,000 UTF-16 characters across before/after strings. Old entries are evicted first. Full current draft text remains intact when history is evicted, with an eviction count recorded. Restoring history never reconstructs current text by truncating it.

## Recovery storage

Normal sessions are stored under `%LocalAppData%/PdfEditorPrototype/phase4b/sessions/<source-SHA256>.session.json`. Schema version 1 includes source identity, page observations, region original snapshots and fingerprints, strategies/font/glyph information, working text, caret/selection, revision, validation and history including redo tail. This is private local prototype data, not data embedded into the PDF.

Writes serialize to a temporary file, flush it, then replace the session file atomically. Switching documents and clean closure persist immediately; text changes use a 350 ms debounce. A power loss before a scheduled write can lose that short interval. Recovery files are limited to 16,000,000 bytes. Oversize serialization leaves the previous recovery file and complete in-memory draft intact and reports the failure; larger work is not guaranteed recoverable until reduced or exported.

Restore checks schema, matching source hash, region source identity, cursor/entry bounds, history character budget and before/after consistency by traversing history in both directions. Verified revision is reset. Fresh source discovery must confirm restored regions before they can be trusted for export. Compatible observations refresh transient font paths. Incompatible identities retain the original snapshot and draft as blocked; they are never rebased onto guessed object indices.

Malformed/partial/contradictory files are rejected; the UI preserves invalid data with an `.invalid-<GUID>` name. Changed source bytes get a separate hash-keyed session when explicitly reopened, leaving old recovery untouched. A changed original cannot silently receive stale drafts. A same-byte copy is eligible for the same source-bound recovery after fresh checks. Older phases' single-region recovery files are not migrated or altered.

## Executed evidence

`evidence/model/model-tests.json`: 11 passing invariants, including chronology, redo branching, no selection entries, session/revision/hash response rejection, both history limits, atomic recovery with redo, changed-source refusal, malformed and corrupt history retention, oversize recovery and identity mismatch retention.

`evidence/process-recovery.json`: three edited regions across two pages persisted in one app process; that process exited. A different PID reopened the original with an isolated shared recovery store, restored all three drafts, undid/redid and saved all three in one output. The source hash remained unchanged. This is separate-process recovery, not merely a same-window serialization test. `final-release-controls/session-control-tests.json` additionally tests control restoration and explicitly changed-source reopening.

## Limitations

Recovery is not multi-process locked; concurrent instances editing the same source have no reconciliation and a later writer may replace earlier recovery. Recovery JSON contains draft text and is not encrypted. Abrupt termination can leave temporary work directories. Identity changes across a future analyser version may block initial restoration before a region is displayed: unresolved text remains in the preserved recovery file for technical inspection, with no dedicated orphan-draft UI. The normal same-build path is tested. There is no automatic merge or migration of incompatible recovery.
