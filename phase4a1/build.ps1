param([switch]$Portable)
$ErrorActionPreference='Stop'
Push-Location -LiteralPath $PSScriptRoot
try {
$out=Join-Path $PSScriptRoot 'run'
New-Item -ItemType Directory -Path $out -Force | Out-Null
foreach($project in @('App','Worker')) {
    if($Portable) {
        & dotnet publish "$project/$project.csproj" -c Release -r win-x64 --self-contained true -o $out --nologo -v q
    } else {
        & dotnet publish "$project/$project.csproj" -c Release --self-contained false -o $out --nologo -v q
    }
    if($LASTEXITCODE -ne 0){throw "Build failed: $project"}
}
Copy-Item -Path (Join-Path $PSScriptRoot 'runtime\*') -Destination $out -Recurse -Force
if(-not (Test-Path (Join-Path $out 'samples\A-Simple.pdf'))) {
    & (Join-Path $out 'PdfWorker.exe') --samples (Join-Path $out 'samples')
    if($LASTEXITCODE -ne 0){throw 'Sample generation failed'}
}
Write-Host "Run $out\PdfEditorPrototype.exe"
} finally { Pop-Location }
