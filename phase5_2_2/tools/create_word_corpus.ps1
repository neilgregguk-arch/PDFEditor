$ErrorActionPreference='Stop'
$taskFolder=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\run\font-corpus'))
$taskWord=$null;$taskDoc=$null;$taskRows=@()
try {
 $taskWord=New-Object -ComObject Word.Application
 $taskWord.Visible=$false
 foreach($taskFont in @('Arial','Calibri','Consolas')) {
  $taskDoc=$taskWord.Documents.Add()
  $taskDoc.Content.Text="cafe calm. cafe calm.`r`rProtected reference block."
  $taskDoc.Content.Font.Name=$taskFont;$taskDoc.Content.Font.Size=12
  $taskPath=Join-Path $taskFolder ('Word-'+$taskFont+'.pdf')
  $taskDoc.ExportAsFixedFormat($taskPath,17)
  $taskRows+=[pscustomobject]@{file=[IO.Path]::GetFileName($taskPath);generator='Microsoft Word';version=$taskWord.Version;font=$taskFont;sha256=(Get-FileHash -LiteralPath $taskPath -Algorithm SHA256).Hash.ToLower()}
  $taskDoc.Close(0);$taskDoc=$null
 }
 $taskRows|ConvertTo-Json|Set-Content (Join-Path $taskFolder 'word-corpus.json')
} finally {if($taskDoc){$taskDoc.Close(0)};if($taskWord){$taskWord.Quit()}}
