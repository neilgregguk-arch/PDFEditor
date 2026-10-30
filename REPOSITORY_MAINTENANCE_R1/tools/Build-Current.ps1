#Requires -Version 7.0
[CmdletBinding()]
param(
    [string]$Workspace=(Split-Path (Split-Path $PSScriptRoot -Parent) -Parent),
    [string]$SourcePhase='phase5_2_2',
    [string]$SourceRevisionId='',
    [string]$OutputRelative=('.local-generated/R1-validation-'+(Get-Date -Format 'yyyyMMdd-HHmmss'))
)
$ErrorActionPreference='Stop'
$r1Workspace=[IO.Path]::GetFullPath($Workspace)
if($SourcePhase -notmatch '^phase[0-9][a-z0-9_]*$'){throw 'Source phase must be one top-level phase directory.'}
$out=[IO.Path]::GetFullPath((Join-Path $r1Workspace $OutputRelative));$allowed=Join-Path $r1Workspace '.local-generated'
if(!$out.StartsWith($allowed+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Build output must be under .local-generated, never a historical run/evidence directory.'}
if(Test-Path -LiteralPath $out){throw 'Choose a new output folder; existing validation outputs are preserved.'}
$ancestor=[IO.Path]::GetDirectoryName($out)
while($ancestor -and $ancestor.Length -ge $r1Workspace.Length){if((Test-Path -LiteralPath $ancestor) -and ((Get-Item -LiteralPath $ancestor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'Build output ancestor is a reparse point.'};$ancestor=[IO.Path]::GetDirectoryName($ancestor)}
$cache=& (Join-Path $PSScriptRoot 'Restore-PinnedRuntime.ps1') -Workspace $r1Workspace
$run=Join-Path $out 'run';New-Item -ItemType Directory -Path $run -Force | Out-Null
$stampArgs=@()
if($SourceRevisionId){if($SourceRevisionId -notmatch '^[a-fA-F0-9]{40}$'){throw 'SourceRevisionId must be an explicit 40-character historical build stamp.'};$stampArgs=@('-p:SourceRevisionId='+$SourceRevisionId)}
foreach($project in @('App','Worker')){
    & dotnet publish (Join-Path $r1Workspace "$SourcePhase/$project/$project.csproj") -c Release --self-contained false -o $run --nologo -v q @stampArgs
    if($LASTEXITCODE -ne 0){throw "Build failed: $project"}
}
$pinned=Get-Content -Raw -LiteralPath (Join-Path (Split-Path $PSScriptRoot -Parent) 'inventory/pinned-runtime.json') | ConvertFrom-Json
foreach($entry in $pinned.files){$dest=Join-Path $run $entry.path;New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($dest)) -Force | Out-Null;Copy-Item -LiteralPath (Join-Path $cache $entry.path) -Destination $dest}
# Fixture selection is taken from tracked paths, never from unknown local files.
$fixtureDirs=@('samples','corpus','document-corpus','font-corpus','position-corpus','wrap-corpus','paragraph-examples','original-paragraphs','original-examples','corrective-examples')
$tracked=(& git -C $r1Workspace ls-files -z -- "$SourcePhase/run/").Split([char]0)
foreach($rel in $tracked){if(!$rel){continue};$tail=$rel.Substring(($SourcePhase+'/run/').Length);if($tail.Split('/')[0] -notin $fixtureDirs){continue};$dest=Join-Path $run $tail;New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($dest)) -Force | Out-Null;Copy-Item -LiteralPath (Join-Path $r1Workspace $rel) -Destination $dest}
$files=@(Get-ChildItem -LiteralPath $run -File -Recurse | ForEach-Object {[ordered]@{path=[IO.Path]::GetRelativePath($out,$_.FullName).Replace('\','/');bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}})
$sources=@((& git -C $r1Workspace ls-files -z -- "$SourcePhase/App" "$SourcePhase/Core" "$SourcePhase/Worker" "$SourcePhase/Checks" "$SourcePhase/Directory.Build.props").Split([char]0) | Where-Object {$_} | ForEach-Object {[ordered]@{path=$_;sha256=(Get-FileHash -LiteralPath (Join-Path $r1Workspace $_) -Algorithm SHA256).Hash.ToLowerInvariant()}})
[ordered]@{schema=1;head=(& git -C $r1Workspace rev-parse HEAD).Trim();sdk=(& dotnet --version).Trim();sourcePhase=$SourcePhase;explicitInformationalStamp=$SourceRevisionId;output=$out;runtimeCache=$cache;sources=$sources;files=$files;configuration='Release framework-dependent Windows x64';note='Historical run/evidence files are not overwritten. bin/obj intermediates may be regenerated. No cleanup executed.'} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $out 'build-manifest.json') -Encoding utf8NoBOM
Write-Output "R1_OUTPUT=$out"
