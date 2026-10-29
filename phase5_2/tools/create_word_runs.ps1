$ErrorActionPreference='Stop'
$taskWord=$null;$taskDoc=$null
try {
 $taskWord=New-Object -ComObject Word.Application
 $taskWord.Visible=$false
 $taskDoc=$taskWord.Documents.Add()
 $taskDoc.Content.Text="Phase cafe calm and office letter.`r`rProtected reference block."
 $taskDoc.Content.Font.Name='Arial';$taskDoc.Content.Font.Size=12
 $taskRange=$taskDoc.Range(6,10);$taskRange.Font.Bold=1
 $taskDoc.ExportAsFixedFormat((Join-Path $PSScriptRoot '../run/position-corpus/Word-multiple-runs.pdf'),17)
} finally {if($taskDoc){$taskDoc.Close(0)};if($taskWord){$taskWord.Quit()}}
