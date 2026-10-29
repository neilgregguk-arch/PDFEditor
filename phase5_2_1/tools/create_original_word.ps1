param([string]$Name='Word-original-multiline',[string]$Text='')
$ErrorActionPreference='Stop'
Add-Type @"
using System;using System.Runtime.InteropServices;
public static class WordCorpusFont {
 [DllImport("gdi32.dll",CharSet=CharSet.Unicode)] public static extern int AddFontResourceEx(string path,uint flags,IntPtr reserved);
 [DllImport("gdi32.dll",CharSet=CharSet.Unicode)] public static extern bool RemoveFontResourceEx(string path,uint flags,IntPtr reserved);
}
"@
$taskFont=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../run/assets/PrototypeSansAscii.ttf'))
$taskOut=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../run/original-paragraphs'))
New-Item -ItemType Directory -Force $taskOut|Out-Null
$taskLoaded=[WordCorpusFont]::AddFontResourceEx($taskFont,0,[IntPtr]::Zero)
if($taskLoaded -lt 1){throw 'Open font registration failed'}
$taskWord=$null;$taskDoc=$null
try {
 $taskWord=New-Object -ComObject Word.Application
 $taskWord.Visible=$false
 $taskDoc=$taskWord.Documents.Add()
 $taskDoc.PageSetup.PageWidth=595.32;$taskDoc.PageSetup.PageHeight=841.92
 $taskDoc.PageSetup.LeftMargin=72;$taskDoc.PageSetup.RightMargin=72
 $taskText='A calm office letter carries clear words across several visual rows. Each original row belongs to this single paragraph, with spaces retained between ordinary words. A reader can follow the complete text without guessing a paragraph boundary.'
 $taskDoc.RemovePersonalInformation=$true
 if($Text){$taskText=$Text}
 $taskDoc.Content.Text=$taskText+"`r`rProtected reference block remains in place."
 $taskDoc.Content.Font.Name='Prototype Sans';$taskDoc.Content.Font.Size=12
 $taskDoc.Content.ParagraphFormat.SpaceAfter=12
 $taskDoc.Content.ParagraphFormat.LineSpacingRule=0
 $taskPdf=Join-Path $taskOut ($Name+'.pdf')
 $taskDoc.SaveAs2((Join-Path $taskOut ($Name+'.docx')),16)
 $taskDoc.ExportAsFixedFormat($taskPdf,17,$false,0,0,1,1,0,$false,$true,0,$true,$true,$false)
 $taskDoc.SaveAs2((Join-Path $taskOut ($Name+'.docx')),16)
 [pscustomobject]@{generator='Microsoft Word';version=$taskWord.Version;build=$taskWord.Build;requestedFont='Prototype Sans';registeredFontCount=$taskLoaded;text=$taskText;sha256=(Get-FileHash $taskPdf).Hash.ToLower();note='Original Word export; no PDFEditor preprocessing. Fictional authored text. Open Bitstream-derived renamed font supplied with licence.'}|ConvertTo-Json|Set-Content -Encoding utf8 (Join-Path $taskOut ($Name+'-provenance.json'))
}finally{if($taskDoc){$taskDoc.Close(0)};if($taskWord){$taskWord.Quit()};[WordCorpusFont]::RemoveFontResourceEx($taskFont,0,[IntPtr]::Zero)|Out-Null}
