#Requires -Version 7.0
[CmdletBinding()]
param([string]$Workspace=(Split-Path (Split-Path $PSScriptRoot -Parent) -Parent))
$ErrorActionPreference='Stop'
$r1Workspace=[IO.Path]::GetFullPath($Workspace)
$manifest=Get-Content -Raw -LiteralPath (Join-Path (Split-Path $PSScriptRoot -Parent) 'inventory/pinned-runtime.json') | ConvertFrom-Json
$cache=Join-Path $r1Workspace ('.local-generated/dependencies/'+$manifest.id+'-'+$manifest.nativeSha256.Substring(0,12))
if($manifest.id -notmatch '^[a-z0-9._-]+$' -or $manifest.id.Contains('..')){throw 'Invalid runtime cache identifier.'}
$check=$cache
while($check -and $check.Length -ge $r1Workspace.Length){if((Test-Path -LiteralPath $check) -and ((Get-Item -LiteralPath $check -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'Cache ancestry contains a reparse point.'};$check=[IO.Path]::GetDirectoryName($check)}
New-Item -ItemType Directory -Path $cache -Force | Out-Null
foreach($entry in $manifest.files){
    if([IO.Path]::IsPathRooted($entry.path) -or $entry.path -match '(^|/)\.\.(/|$)' -or $entry.path.Contains(':')){throw 'Invalid dependency target.'}
    $target=[IO.Path]::GetFullPath((Join-Path $cache $entry.path))
    if(!$target.StartsWith($cache+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Dependency target leaves cache.'}
    $node=$target
    while($node -and $node.Length -ge $r1Workspace.Length){if((Test-Path -LiteralPath $node) -and ((Get-Item -LiteralPath $node -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'Cache ancestry contains a reparse point.'};$node=[IO.Path]::GetDirectoryName($node)}
    $actualBlob=(& git -C $r1Workspace rev-parse ($manifest.sourceCommit+':'+$entry.sourcePath)).Trim()
    if($LASTEXITCODE -ne 0 -or $actualBlob -ne $entry.gitBlob){throw 'Pinned blob/source-commit mismatch.'}
    if(Test-Path -LiteralPath $target){if((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256){throw "Existing cache content differs: $($entry.path)"};continue}
    New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($target)) -Force | Out-Null
    $tmp=$target+'.r1-'+[Guid]::NewGuid().ToString('N')+'.tmp'
    $pi=[Diagnostics.ProcessStartInfo]::new('git');$pi.WorkingDirectory=$r1Workspace;$pi.UseShellExecute=$false;$pi.RedirectStandardOutput=$true;$pi.RedirectStandardError=$true
    $pi.ArgumentList.Add('cat-file');$pi.ArgumentList.Add('blob');$pi.ArgumentList.Add($entry.gitBlob)
    # Exact binary stdout. Failed staging files are retained for inspection.
    $proc=[Diagnostics.Process]::Start($pi);$fs=[IO.File]::Open($tmp,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write)
    try{$proc.StandardOutput.BaseStream.CopyTo($fs)}finally{$fs.Dispose()}
    $err=$proc.StandardError.ReadToEnd();$proc.WaitForExit();if($proc.ExitCode -ne 0){throw "Pinned Git object unavailable. Fetch the documented source commit before retrying. $err"}
    if((Get-FileHash -LiteralPath $tmp -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256){throw 'Pinned runtime checksum mismatch; staging retained.'}
    [IO.File]::Move($tmp,$target)
}
Write-Output $cache
