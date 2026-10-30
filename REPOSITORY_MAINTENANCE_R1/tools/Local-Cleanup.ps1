#Requires -Version 7.0
[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [ValidateSet('Audit','DryRun','Clean')][string]$Mode='Audit',
    [string]$Workspace=(Split-Path (Split-Path $PSScriptRoot -Parent) -Parent),
    [string]$PlanPath=(Join-Path (Split-Path $PSScriptRoot -Parent) 'inventory/local-cleanup-plan.json'),
    [switch]$ApproveCleanup
)
$ErrorActionPreference='Stop'
# No recursive deletion. Every candidate is rechecked immediately before removal.
$r1Root=[IO.Path]::GetFullPath($Workspace).TrimEnd('\','/')
$r1Prefix=$r1Root+[IO.Path]::DirectorySeparatorChar
$gitRoot=(& git -C $r1Root rev-parse --show-toplevel).Trim()
if($LASTEXITCODE -ne 0 -or [IO.Path]::GetFullPath($gitRoot).TrimEnd('\','/') -ne $r1Root){throw 'Workspace must be the exact Git checkout root.'}
if($Mode -eq 'Clean' -and !$ApproveCleanup){throw 'Clean requires explicit -ApproveCleanup. R1 itself does not grant deletion approval.'}
$plan=Get-Content -Raw -LiteralPath $PlanPath | ConvertFrom-Json
if($plan.schema -ne 1 -or [IO.Path]::GetFullPath($plan.workspace).TrimEnd('\','/') -ne $r1Root){throw 'Plan belongs to a different workspace or schema.'}
if($plan.backupCommit -notmatch '^[a-fA-F0-9]{40}$' -or !$plan.remoteVerification){throw 'Missing verified backup provenance.'}
& git -C $r1Root cat-file -e "$($plan.backupCommit)^{commit}"
if($LASTEXITCODE -ne 0){throw 'Backup commit is unavailable locally.'}
$buildPath=[IO.Path]::GetFullPath($plan.validatedBuildManifest)
$buildPrefix=(Join-Path $r1Root '.local-generated')+[IO.Path]::DirectorySeparatorChar
if(!$buildPath.StartsWith($buildPrefix,[StringComparison]::OrdinalIgnoreCase)){throw 'Validated build manifest must be in the local generated root.'}
if((Get-FileHash -LiteralPath $buildPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $plan.validatedBuildSha256){throw 'Validated build manifest changed.'}
$build=Get-Content -Raw -LiteralPath $buildPath | ConvertFrom-Json
foreach($source in $build.sources){
    $sourcePath=[IO.Path]::GetFullPath((Join-Path $r1Root $source.path))
    if(!$sourcePath.StartsWith($r1Prefix,[StringComparison]::OrdinalIgnoreCase) -or (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $source.sha256){throw 'Application source changed since the validated build; rebuild and re-audit.'}
}
$tracked=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
(& git -C $r1Root ls-files -z).Split([char]0) | ForEach-Object {if($_){[void]$tracked.Add($_)}}
if($LASTEXITCODE -ne 0){throw 'Cannot establish tracked paths.'}
function Get-WorkspaceSnapshot {
    $q=[Collections.Generic.Stack[IO.DirectoryInfo]]::new();$q.Push([IO.DirectoryInfo]::new($r1Root));[long]$bytes=0;[long]$count=0;$skipped=[Collections.Generic.List[string]]::new()
    while($q.Count){foreach($entry in $q.Pop().EnumerateFileSystemInfos()){
        if($entry.Attributes -band [IO.FileAttributes]::ReparsePoint){$skipped.Add($entry.FullName);continue}
        if($entry -is [IO.DirectoryInfo]){$q.Push($entry)}else{$bytes+=$entry.Length;$count++}
    }}
    [pscustomobject]@{logicalBytes=$bytes;files=$count;skippedReparsePaths=@($skipped)}
}
function Resolve-SafeCandidate($item) {
    $rel=[string]$item.path
    if([IO.Path]::IsPathRooted($rel) -or $rel -match '(^|[\\/])\.\.([\\/]|$)' -or $rel.Contains(':')){throw "Invalid relative path: $rel"}
    $norm=$rel.Replace('\','/')
    # Explicit exclusions take priority over the manifest, even if tampered with.
    if($norm -match '(?i)(^|/)(\.git|\.venv[^/]*|credentials?|secrets?|recovery|sessions?|drafts?|evidence|fixtures?|assets|licenses?|runtime|run|test-work)(/|$)' -or
       $norm -match '(?i)(\.pdf|\.docx?|\.xlsx?|\.pptx?|\.png|\.jpe?g|\.svg|\.ttf|\.otf|\.cs|\.csproj|\.props|\.py|\.ps1|\.md|\.txt|\.pem|\.key|\.pfx|\.env|\.session\.json)$' -or
       $norm -match '(?i)(credential|secret|token|password|recovery|session|draft|licen[sc]e|notice)'){throw "Protected path: $rel"}
    if($norm -notmatch '^(phase[0-9][a-z0-9_]*)/(App|Core|Worker|Checks)/(bin|obj)/' -or $norm -notmatch '(?i)\.(dll|exe|pdb)$'){throw "Outside conservative build-duplicate allowlist: $rel"}
    if([IO.Path]::GetFileName($norm) -notmatch '^(PdfEditorPrototype|PdfWorker|Core)\.(dll|exe|pdb)$'){throw "Not a known project build product: $rel"}
    if($tracked.Contains($norm)){throw "Tracked file must never be removed: $rel"}
    if(!($build.files | Where-Object {$_.sha256 -eq $item.sha256})){throw "Candidate does not match the validated build: $rel"}
    if($item.reason -ne 'Reproducible build duplicate with byte-identical verified Git backup' -or !$item.backupPath){throw "No approved retention classification: $rel"}
    $full=[IO.Path]::GetFullPath((Join-Path $r1Root $rel))
    if(!$full.StartsWith($r1Prefix,[StringComparison]::OrdinalIgnoreCase)){throw "Path leaves workspace: $rel"}
    $ancestor=$full
    while($ancestor){
        if(Test-Path -LiteralPath $ancestor){if((Get-Item -LiteralPath $ancestor -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw "Reparse point in candidate ancestry: $rel"}}
        if($ancestor -eq $r1Root){break}
        $ancestor=[IO.Path]::GetDirectoryName($ancestor)
    }
    [IO.Path]::GetFullPath((Join-Path $r1Root $rel))
}
function Get-GitBlobSha256([string]$commit,[string]$path) {
    # Binary-safe Git stdout, no PowerShell text redirection or shell quoting.
    if($path -match '[:\r\n]' -or $path.StartsWith('-')){throw 'Invalid backup path.'}
    $pi=[Diagnostics.ProcessStartInfo]::new('git');$pi.UseShellExecute=$false;$pi.RedirectStandardOutput=$true;$pi.RedirectStandardError=$true;$pi.WorkingDirectory=$r1Root
    $pi.ArgumentList.Add('show');$pi.ArgumentList.Add($commit+':'+$path)
    $proc=[Diagnostics.Process]::Start($pi);$sha=[Security.Cryptography.SHA256]::Create()
    try{$hash=$sha.ComputeHash($proc.StandardOutput.BaseStream);$err=$proc.StandardError.ReadToEnd();$proc.WaitForExit();if($proc.ExitCode -ne 0){throw "Cannot verify Git backup: $err"};([BitConverter]::ToString($hash)).Replace('-','').ToLowerInvariant()}
    finally{$sha.Dispose();$proc.Dispose()}
}
$before=Get-WorkspaceSnapshot
$resolved=[Collections.Generic.List[object]]::new();[long]$proposed=0
$seen=[Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach($item in $plan.files){
    $path=Resolve-SafeCandidate $item
    if(!$seen.Add($path)){throw 'Duplicate target in plan.'}
    if(!(Test-Path -LiteralPath $path -PathType Leaf)){continue}
    $file=Get-Item -LiteralPath $path
    if($file.Length -ne $item.bytes -or (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.sha256){throw "Candidate changed since audit: $($item.path)"}
    if((Get-GitBlobSha256 $plan.backupCommit $item.backupPath) -ne $item.sha256){throw "Backup bytes disagree: $($item.path)"}
    $resolved.Add([pscustomobject]@{item=$item;full=$path});$proposed+=$file.Length
}
Write-Output "Mode=$Mode; verified proposed files=$($resolved.Count); estimated logical savings=$proposed bytes. No directory trees are removed."
if($Mode -ne 'Audit'){foreach($row in $resolved){Write-Output ("PROPOSED {0} bytes {1}" -f $row.item.bytes,$row.item.path)}}
[long]$removed=0;[long]$removedFiles=0
$cleanupError=$null
try {
if($Mode -eq 'Clean'){
    foreach($row in $resolved){
        $fresh=Resolve-SafeCandidate $row.item
        if((Get-FileHash -LiteralPath $fresh -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row.item.sha256){throw 'File changed after preflight; stopped.'}
        if($PSCmdlet.ShouldProcess($fresh,'Remove exact hash-verified reproducible duplicate')){
            Remove-Item -LiteralPath $fresh -Force -ErrorAction Stop
            $removed+=$row.item.bytes;$removedFiles++
        }
    }
}
} catch {$cleanupError=$_.Exception.Message}
$after=Get-WorkspaceSnapshot
[pscustomobject]@{error=$cleanupError;mode=$Mode;cleanupOptIn=$ApproveCleanup.IsPresent;before=$before;after=$after;estimatedLogicalSavingsBytes=$proposed;removedFiles=$removedFiles;removedLogicalBytes=$removed;observedWorkspaceDeltaBytes=($before.logicalBytes-$after.logicalBytes);note='Logical sizes, not physical allocation. Concurrent processes may affect observed delta. Clean is file-by-file, not atomic; stop on any validation error. Rebuild/launch and critical tests required after an approved cleanup.'}

if($cleanupError){throw "Cleanup stopped after $removedFiles verified removals; measurements above. $cleanupError"}
