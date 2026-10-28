$ErrorActionPreference='Stop'
$taskOut=Join-Path $PSScriptRoot '..\run\corpus\11-word-letter.pdf'
$taskWord=$null;$taskDoc=$null
try {
 $taskWord=New-Object -ComObject Word.Application
 $taskWord.Visible=$false
 $taskDoc=$taskWord.Documents.Add()
 $taskDoc.Content.Text="Phase 3 Office letter`r`rThis fictional letter was exported by Microsoft Word for PDF discovery testing.`r`rA separate paragraph should retain its own boundaries."
 $taskDoc.Content.Font.Name='Arial';$taskDoc.Content.Font.Size=12
 $taskDoc.ExportAsFixedFormat([IO.Path]::GetFullPath($taskOut),17)
} finally {if($taskDoc){$taskDoc.Close(0)};if($taskWord){$taskWord.Quit()}}
