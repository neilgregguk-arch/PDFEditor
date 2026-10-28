# Phase 4A open issues

28 October 2026. The phase delivers a verified narrow compatibility improvement, not general Office PDF editing.

| Priority | Issue / consequence | Recommended next investigation |
|---|---|---|
| High | Original Word lines remain view-only: actual TJ spacing, initial reconstruction differences and separately owned whitespace remain after the broad font blocker is resolved. | A glyph-positioned single-region model and explicit, conservative space-fragment ownership; do not simply raise tolerances. |
| High | Physical Phase 4A input/file dialogs remain unverified. WPF programmatic controls pass; prior native automation could not activate the window. | Complete the manual guide on the user's interactive desktop. |
| High | Clipboard is historically intermittent. It passes this run, but prior Win32 5 failures have no established root cause. | Cross-application tests under actual desktop/remote/lock conditions; retain failures rather than claiming a fix. |
| High scope | Missing/unusable font cmap, unmapped retained characters and genuinely unavailable subset characters remain restricted. Some absent cmap coverage may mean an inaccessible outline rather than physical deletion. | A maintained structural font/encoding adapter only if justified; inspect actual ToUnicode/CIDToGID/width relationships rather than guessing raw codes. |
| High scope | No font or mapping extension. The product never invents codes, substitutes fonts or rebuilds a subset. | If later considered, separately address rights, cmap/glyph IDs, widths/descriptors/resources and independent readers. |
| High scope | ASCII, standalone TrueType and natural horizontal text only. CFF/collections, arbitrary Unicode, shaping/bidi/IME, ligatures, kerning and mixed-style paragraphs are not newly supported. | Add narrow independently generated classes with equivalent outline/geometry/export evidence. |
| High | Runtime proves the selected reverse mapping, not every unused alias in a font's complete ToUnicode structure. | Retain original-object render proof and final saved glyph checks; a structural parser may be needed for broader mapping diagnostics. |
| High | Geometric paragraph inference can still join unrelated long lines or reject legitimate layouts. Explicit full-page background bounds can conservatively block Office text, as in PowerPoint. | Expand adverse ownership/background fixtures without weakening collision checks. |
| Medium-High | WPF and PDF font metrics still have bounded discrepancies. Local/cumulative tolerances remain 0.05/1 pt, and typography is not universally pixel-identical. | More fonts, DPI and live/saved wrap comparisons; use glyph checks alongside raster checks. |
| Medium-High | Variable/colour fonts, descriptor-driven simulated styles and nonzero crop offsets are not certified by this corpus. | Dedicated fixtures and explicit eligibility gates before expanding the supported class. |
| Medium | Consecutive-space extraction can still reject an otherwise visible edit. No whitespace-normalising acceptance was added. | Establish exact logical-space/object mapping while preserving complete drafts. |
| Medium | Only one changed region per export; native undo history does not survive reopening. | Reserved for review before Phase 4B, not implemented here. |
| Medium | Eight-page observation cache, but no hard total temp-disk/font-per-page bound or in-flight native cancellation. Large responses can still burden WPF deserialisation. | Cancellation, cleanup/resource limits and realistic large-document profiling. |
| High scope | Info metadata/count/raster/glyph checks do not prove full XMP, tagging, reading order, annotation dictionary, signatures/forms/encryption or PDF/A preservation. | Define explicit supported document classes and structural invariants before broadening promises. |
| Medium | Framework-dependent Windows build; no installer, clean disconnected VM or OS security sandbox. | Deployment/security validation before production use. |

The Word API lab demonstrates a feasible explicit-position existing-glyph correction, but it uses known object/font mappings and is not available through product eligibility. It must not become a raw-code bypass for unsupported UI drafts. Existing-glyph reuse is the evidence-backed route; automatic font replacement/subset rebuilding is not recommended on this evidence.

Phase 4A stops here. Review the new mapping/outline checks, the J before/after result and the remaining Word ownership/positioning restrictions before authorising any Phase 4B work.
