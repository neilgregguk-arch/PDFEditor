$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$taskPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) {
    throw 'Create .venv and install requirements.txt as described in README.md first.'
}
& $taskPython feasibility.py run
if ($LASTEXITCODE -ne 0) { throw 'Experiment execution failed; do not trust previous results.' }
& $taskPython run_tests.py
if ($LASTEXITCODE -ne 0) { throw 'Saved-output verification failed.' }
& $taskPython review_evidence.py
if ($LASTEXITCODE -ne 0) { throw 'Evidence index generation failed.' }
