param([string]$Pdf)
$taskApp=Join-Path $PSScriptRoot 'run\PdfEditorPrototype.exe'
if(-not(Test-Path -LiteralPath $taskApp)){throw 'Build the prototype with build.ps1 first.'}
if($Pdf){$taskPdf=(Resolve-Path -LiteralPath $Pdf).Path;Start-Process -FilePath $taskApp -ArgumentList ('"'+$taskPdf+'"') -WindowStyle Normal}
else{Start-Process -FilePath $taskApp -WindowStyle Normal}
