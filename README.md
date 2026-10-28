# PDF Editor V2 - Phase 1 only

This is an offline command-line feasibility laboratory, not an editor application. Six immutable synthetic originals, saved candidates, diagnostics and render comparisons are included. Some candidates deliberately demonstrate failures; do not treat every output as a successful edit.

Start with [TECHNICAL_FEASIBILITY_REPORT.md](TECHNICAL_FEASIBILITY_REPORT.md), then [engine comparison](PDF_ENGINE_COMPARISON.md), [architecture recommendation](ARCHITECTURE_RECOMMENDATION.md), and [Phase 2 proposal](PHASE_2_PROPOSAL.md). Open [the local evidence index](results/index.html) in a browser for PDF links and before/after/diff images, or read [the evidence table](results/INDEX.md).

## Reproduce on Windows

Python 3.12 x64 was used. In PowerShell, from this directory:

```powershell
python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\run.ps1
```

Dependency installation needs package access on the first machine. Execution, analysis, editing, tests and the evidence viewer require no network. For an air-gapped machine, prepare wheels on a matching Windows/Python machine with `python -m pip download -r requirements.txt -d wheelhouse`, then use `pip install --no-index --find-links wheelhouse -r requirements.txt`. A redistributable application/installer and offline wheel archive were not built in this phase.

Optional: put Poppler's `pdftoppm.exe` on PATH before running for the third renderer. MuPDF and PDFium are required and installed by the requirements file. Tested package versions and native engine builds are in `results/summary.json`. The delivered run includes Poppler results. The original execution used a project venv inheriting the bundled runtime; requirements.txt records the full runtime dependency closure for a clean setup.

The requirements were also installed and all 14 tests passed in `.venv-clean`, without inherited packages. `offline_check.py` repeats the complete experiment with Python socket connections refused; this check passed, but does not sandbox native processes or verify a Windows installer.

```powershell
# Inspect an arbitrary local PDF without modifying it:
& .\.venv\Scripts\python.exe feasibility.py analyze 'C:\path\document.pdf' --output diagnostics.json
# Recheck delivered evidence without recreating it:
& .\.venv\Scripts\python.exe run_tests.py
```

`feasibility.py run` creates missing synthetic originals only; existing originals are never overwritten. The SHA256 manifest rejects changed originals. Candidate outputs and result files are regenerated on rerun. The operand editor is intentionally fixture-specific ASCII code, not a general PDF search/replace API. Do not point its internal functions at arbitrary documents.

## Files

- `feasibility.py`: sample generator, edits, diagnostic CLI, reopened checks and raster comparison.
- `test_feasibility.py`, `run_tests.py`: saved-output tests and machine-readable test result.
- `output/pdf/originals/`: six originals and immutable hash manifest.
- `output/pdf/edited/`: sixteen candidate PDFs, including three refused unchanged copies.
- `results/`: per-experiment JSON, before/after diagnostics, all page PNGs, summary, test results and local review index.
- `assets/`: generated images and redistributable Bitstream Vera font with its license.
- `requirements.txt`: exact dependency pins; `run.ps1`: fail-fast local runner.

Research was checked against primary documentation on 27 October 2026. Distribution licensing is discussed in the engine comparison. The installed research environment includes AGPL PyMuPDF; its presence in this experiment is not a closed-source distribution decision. No application, deployment, installer or Phase 2 work was started.
