# Phase 2 proposal - Constrained editing engine validation

Status: proposal only. Phase 1 is complete; no Phase 2 implementation is authorized or started by this deliverable.

## Objective

Prove a dependable offline Windows engine for **eligible selected-text corrections** on independently generated PDFs. Replace fixture-specific assumptions with explicit eligibility checks. Do not build a complete editor or promise general paragraph reflow.

## Priorities

1. Build a PDFium-first inspection/edit path that does not import PyMuPDF in the candidate proprietary runtime. Keep reference renderers as separate development tools subject to their licenses. Define versioned worker commands and stable glyph/object selection identities.
2. Support a narrow, documented horizontal-text class: available glyphs, valid encoding round trips, original style/transform, known advance and sufficient space. Check neighbours before mutation. Use explicit compensation only where spacing semantics are understood; refuse rather than silently shrinking or substituting fonts.
3. Implement source-safe transactional Save As, independent reopening, per-edit change evidence, and clear failure reasons. Handle locked destinations, worker crashes and disk-write failure. Keep originals unchanged and support repeated edits and undo in the working session.
4. Expand the corpus and evaluate confidence/refusal quality before introducing a minimal selection/preview shell. Test Windows packaging and native runtime dependencies on a disconnected clean VM.

## Corpus and unresolved risks

Collect at least 30 non-private independently produced documents, with provenance/permissions recorded and immutable hashes. Include Office/LibreOffice exports, browser print PDFs, typeset documents, invoices/tables, mixed pages and scanned/OCR pages. Add targeted fixtures for fragmented `TJ` arrays; non-identity Unicode mappings; missing ToUnicode; full and subset fonts; repeated/shared Form XObjects; character/word spacing; rotation/skew; clipping; ligatures; RTL/complex scripts; invisible OCR text; overlapping objects; reused resources; colour spaces; annotations; XMP; forms; tagged content; encryption; signatures and damaged input.

Unsupported features may be refused; they must be identified correctly and remain unmodified. In particular, scan pixels are not editable text, Unicode extraction does not establish reversible encoding, and shared resources can make a local-looking edit affect other occurrences. The Phase 1 one-pixel italic discrepancy needs glyph-level geometry investigation. PDFium object regeneration must be tested against explicit character positions and subset encodings. Resource reorganization needs semantic checks rather than brittle xref equality.

General reflow remains out of scope. A separate opt-in experiment may support complete user-owned plain-text boxes with explicit boundaries, no hidden neighbours, legal font access and defined shaping. It must be labelled reconstruction, with fit failure leaving the document unchanged. Do not silently extend that result to arbitrary paragraphs or multipage layout.

## Acceptance criteria for review

| Area | Required evidence |
|---|---|
| Genuine edits | Every accepted edit reopens through at least two engines; intended replacement extracts correctly, original targeted content is removed, unrelated text remains. A covering-overlay negative control fails these checks. |
| Fidelity | No unexplained changes outside declared glyph/region masks in two independent renderers at two resolutions. Character advance, neighbours, style, image placement and untouched pages are checked separately. Every tolerated raster difference requires an explicit recorded reason. |
| Fonts | Existing font resource/program retained where promised; glyph coverage and encoding verified before save. Unsupported new glyphs and restricted/unavailable fonts produce deterministic refusals, never invisible text or silent substitution. |
| Longer text | Measure fit and collisions before applying. Either a valid isolated correction or a clear refusal. No automatic paragraph movement is claimed. Owned-box reconstruction, if included, has explicit boundaries and fit tests. |
| Integrity | Hash-identical originals after success, cancellation and failure; page boxes/rotation, images, annotations, links, metadata and supported forms preserved. Signatures and unsupported structures handled through explicit eligibility policy. |
| Reliability | All accepted cases meet invariants across the corpus; report acceptance/refusal rates separately with counts and reasons. No aggregate "success" score that treats safe refusals as edits. Crash/failure injection leaves source and destination consistent. |
| Performance | Record hardware, cold/warm latency, peak memory and representative 1/10/100-page workloads. Proposed initial targets: visible-page preview under 500 ms warm at normal zoom, no UI stalls, cancellable long operations. Review targets against real data rather than claiming them achieved. |
| Offline Windows delivery | Install and run inspect/render/edit/save without network on a clean x64 Windows VM. Include native DLL/runtime/font/license inventory. Test Unicode/long paths and locked files. No online font or license activation dependence unless separately approved. |
| Licensing | Exact dependency bill of materials and application licensing decision. Confirm whether the intended open-source or closed-source distribution complies; obtain commercial terms only if needed and explicitly chosen. |

## Deliverables and stopping point

Deliver a versioned engine CLI/worker spike, expanded immutable corpus, machine-readable eligibility and verification results, independent visual evidence, failure-injection results and a revised architecture decision record. A small local selection/preview shell is optional only after engine gates pass, not a full editor.

At review, choose among continuing the constrained PDFium path, accepting an AGPL/commercial MuPDF route, funding a commercial SDK evaluation, or narrowing product promises. Stop for that architectural review before full application development.
