# R1 open issues and licence risk register

| Risk | Finding and next action |
|---|---|
| Project-wide licence | No root project licence declaration found; do not assign MIT/GPL/another licence without the owner's decision. A public repository alone is not a documented redistribution grant. Seek a later licensing audit. |
| Proprietary embedded subsets | Word-Arial.pdf and Word-Calibri.pdf contain embedded ArialMT/Calibri subsets (technical fsType8). Embedding metadata is not independent permission to redistribute fixture/font programs. Record fixture authorship/source and applicable font terms with qualified review; keep current material intact pending review. |
| Fixtures and user data | Essential regression PDFs/source examples need provenance and redistribution review. The user's untracked manual PDF has no verified backup in this audit, remains private/untracked and must not enter releases/cleanup. No files removed to conceal concerns. |
| Native notices |19 pinned runtime/font/notice files are retained/restored together, including PDFium/component notices and renamed Bitstream Vera-derived font notice. Confirm notice completeness for the exact historical wheel/native build, not a newer upstream licence. |
| Development Python | Local metadata identifies PyMuPDF2.0 as AGPL/commercial; review development/distribution and generated-artifact obligations separately from the WPF application. PyMuPDF is development-only in this project. The [official licensing page](https://pymupdf.io/licensing) and [official FAQ](https://pymupdf.readthedocs.io/en/latest/faq/index.html) describe its licensing routes; no legal-compliance conclusion is made here. pikepdf/MPL and other package terms are listed in development-license-metadata.json for review. |
| Environment drift | Installed Pillow13.0.0 differs from requirements.txt12.3.0. Actual package versions are captured without credential URLs. Both environments stay; no dependency downgrade/upgrade or environment recreation was attempted. |
| Historical reproducibility | Managed DLL/PDB bit equivalence unproven even with original informational stamp; keep historical binaries. Native SHA and2host executables match; default build passes functional tests. |
| Archive storage | No approved versioned destination or release assets exists. All14,850E/F candidate paths remain in place. Independent upload/download verification and user authorisation are required before migration. |
| Local-only state | Many ignored files have no verified independent backup. Some are reproducible in principle, others may be unique evidence. Recovery/live temp outside checkout is excluded from cleanup. OneDrive path membership does not prove backup. |
| Existing platform limits | Clipboard Win32 5 intermittency, user manual/DPI/accessibility acceptance and historical frozen Phase 3 expectation mismatch remain open. R1 fixes none of these application behaviours. |

This register flags issues for a later legal/licensing/provenance audit; it does not silently resolve them, remove evidence, upload archives or choose a new project licence. No Phase 5.3 work.
