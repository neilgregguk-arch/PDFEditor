# Phase 5.1 implementation report

Delivered 29 October 2026. Starting commit: `d864fbf265db32127a34e5862b30b4c72717caa9`, with no uncommitted work or partial Phase 5 implementation. The starting-state record and 5,453-file preservation baseline are under `phase5_1/evidence/`. All implementation, compilation and automated testing took place in Codex. The final commit SHA is reported in the completion message and is available with `git log -1`.

## Outcome and scope

Supported paragraphs newly exported by Phase 5.1 carry a bounded embedded declaration. A fresh process validates their actual text objects, reconstructs the exact logical text and opens every row as one in-place region. The genuine Word third paragraph passes consecutive two-row, three-row and one-row save/reopen generations. Arial and Calibri also pass repeated generations. Removed rows are actually removed; no white cover or invisible text replacement is used.

The implementation is isolated under `phase5_1/`. Earlier source, delivered binaries, evidence and handovers remain unchanged. START_HERE is the sole intentional pre-existing entry-guide update and is audited separately. Generic discovery of original Word paragraphs and retroactive grouping of unmarked C2 exports were not added. Development stops after Phase 5.1.

## Source map

- `Core/ParagraphMarks.cs`: PDFium public marked-content bindings, bounded schema, persistent row declarations, actual-member validation, document-wide duplicate-ID index, existing semantic-mark handling and pointer-free ownership observations.
- `Core/Discovery.cs`: validates declarations before existing proximity/natural grouping. Rejected marked members stay Limited/View Only. The document index is cached by exact source hash, while the existing eight-page discovery cache remains.
- `Core/Models.cs`: optional logical text and paragraph ownership distinguish soft rows from natural explicit newlines. Discovery timing is non-authoritative and excluded from identity.
- `Core/PositionLayout.cs`: immutable actual source rows, exact unchanged-row presentation, bounded flattening for alignment during edits, and a surviving-sequence check that cannot borrow an overlap exception across a source soft boundary.
- `Core/DocumentSession.cs`: source identity includes the validated declaration and complete row observations. Stable paragraph ID never substitutes for the new source fingerprint.
- `Core/DocumentTransaction.cs`: inserts genuine original-font rows before their still-live source anchor, preserving the content stream, paint order and shared accessibility scope. Only owned originals are removed. Untouched objects are not detached. The candidate must rediscover its complete declared groups before Save As commits.
- `Core/PdfEngine.cs`: grouped logical glyph offsets omit synthetic newlines; all grouped single requests use the combined transaction. Preserved-object snapshots also compare content-mark signatures.
- `App/PositionSelection.cs`: the page follows the proposed caret and suppresses hidden unwrapped-caret scroll requests.
- `App/ParagraphControlTests.cs`, `tools/paragraph_process.py`, `Checks/Program.cs`: fresh-process interaction, recovery and model coverage. Independent Python readers are development-only.

## Editing and transaction behaviour

The existing proposed-position glyph/caret/selection layer is reused. WPF owns text, input and selection; Up/Down, Home/End, shift selection and mapped drag work across reopened rows. The unchanged source uses observed row geometry. Edits flatten only an ephemeral alignment copy, retaining source-row boundaries for spacing exceptions. New rows reset to the anchor and use verified original-font advances. No source observation is rewritten by layout planning.

Every request still resolves source identities against the immutable opened file, includes all modified regions, rejects collisions and stale/source-changed requests, creates one candidate, reopens it and atomically saves to a new destination. New paragraph IDs are allocated on first marked export and retained when editing a validated marked source. Save As retains the original working session; reopening the output starts a new fingerprint-bound session.

Target/unaffected geometry stays at 0.01 pt and outside-region changed pixels must remain zero above the existing channel-difference threshold of 8. Natural tolerances are unchanged. Font programs, used mapping/width rules, glyph identities/outlines, whitespace objects, page properties and existing accessibility structures remain checked. No fidelity threshold was relaxed.

## Distribution

Run `phase5_1/run/PdfEditorPrototype.exe` or `phase5_1/Launch.ps1`. Windows x64 and the .NET 8 Windows Desktop runtime are required; this is a framework-dependent build. Build with `phase5_1/build.ps1`. Python and Poppler are verification tools, not application dependencies. No paid SDK, network/cloud feature, installer, font substitution, subset rebuilding, undo grouping or new production dependency was introduced.

The pinned PDFium 156.0.8076.0 binary remains SHA256 `bede3932ce96a2e1ed9a7e6cae71aec8914efd2907d37ab44b1b81f9c8a6d04e`. Existing PDFium/native/font notices remain in runtime/run. Inherited embedded fonts and development-library licensing warrant a dedicated distribution audit; this phase does not make a new licence or redistribution-rights determination.
