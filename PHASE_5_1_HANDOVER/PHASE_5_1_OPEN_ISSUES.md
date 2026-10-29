# Phase 5.1 open issues

## Retained restrictions

- Unmarked C2 exports and arbitrary original Word multi-line paragraphs are not automatically grouped. Nearby matching text is insufficient ownership evidence. Older prototype marker formats from development are diagnostic and are not release inputs; the final published schema is Version 1.
- Positioned hard newlines and demonstrated adjacent-space extraction failures still block export while preserving the exact draft and recovery. Unsupported Unicode/glyph mapping is retained and refused; this does not expand the inherited ASCII editing model.
- Empty paragraph deletion intentionally leaves no invisible tombstone. A completely deleted group has no remaining text region to click/re-edit.
- Mixed fonts/styles, unsupported transforms/clipping/paint, cross-page paragraphs and general document reflow remain out of scope. No unrelated object is moved.
- Marker validation is bounded: 512 characters/eight rows/28,000 bytes, page/group/object budgets and a 256-page/65,536-object document mark index. Larger marked operations can be restricted. The envelope is a cap plus freshly checked exclusions, not blanket ownership of empty page space.

## Trust and external tools

The declaration is not a signature or proof of producing-editor authenticity. A third party can author a fully consistent declaration; the app validates actual content, supported geometry and safe ownership. External tools may remove private marks or change font/tag structure, which can prevent group-level editing. An external save preserving validated data is demonstrated only with pikepdf. Raw PDF parser normalisation and malformed native input need broader security/fuzzing review; bounded application metadata validation is not a native sandbox.

Supported existing accessibility scopes are narrow: shared Span marks with MCID/Lang. Other or independently changed semantics are refused. Existing semantic sequence, structure graph and page linkage preservation is checked, but pre-existing accessibility defects are not repaired and PDF/UA is not certified. Screen readers, high contrast, IME, touch and unusual reading-order structures require dedicated evaluation.

## Interaction and operations

The inherited clipboard Win32 error 5 is still reproducible in both the final build and untouched C2 in this session, including a retry. It is explicitly not fixed or counted as passing. Physical Windows testing is still required for clipboard reliability, typing comfort, actual mouse selection, native dialogs and OS display scales. Automated controls use WPF routed input/commands/shared mapping at 96 DPI and four app zooms.

Small-fixture timings are descriptive. Larger/complex files, malicious fonts, memory pressure and prolonged sessions need additional testing. Existing 30-second worker timeout, source/revision guards, bounded caches/candidates, 2,000-entry/2-million-character history and 16 MB recovery protection remain; no new in-flight native cancellation is claimed. Undo grouping is unchanged.

## Repository and compliance

No new production dependencies, paid SDKs or cloud requirements were added. Python readers/Poppler are development-only. Existing native/font notices are preserved. Embedded Arial/Calibri resources and inherited development-library licences require a dedicated distribution/compliance audit; this phase makes no new redistribution-rights determination and does not restructure the repository licence.

Evidence contains workstation-specific paths and some references to excluded transient fonts/candidates. Certified exported PDFs, source fixtures, independent reports and reproducible tools are retained. Virtual environments, bin/obj/test-work/caches and temporary credentials/private user files are excluded. Frozen historical failures, development attempts and initial reader/test-harness mistakes remain visible. Read the evidence index to identify the final approved feature runs.

Phase 5.1 is the review stop point. Phase 5.2 has not started.
