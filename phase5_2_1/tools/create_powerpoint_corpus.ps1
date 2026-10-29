$ErrorActionPreference='Stop'
$taskApp=$null;$taskPresentation=$null
try {
 $taskApp=New-Object -ComObject PowerPoint.Application
 $taskPresentation=$taskApp.Presentations.Add(0)
 $taskSlide=$taskPresentation.Slides.Add(1,12)
 foreach($taskItem in @(@('cafe calm.',100,12),@('Protected reference block.',300,10))) {
  $taskText=$taskSlide.Shapes.AddTextbox(1,60,$taskItem[1],400,80)
  $taskText.TextFrame.MarginLeft=0;$taskText.TextFrame.MarginTop=0
  $taskText.TextFrame.TextRange.Text=$taskItem[0]
  $taskText.TextFrame.TextRange.Font.Name='Arial';$taskText.TextFrame.TextRange.Font.Size=$taskItem[2]
 }
 $taskOutput=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\run\font-corpus\PowerPoint-Arial-subset.pdf'))
 $taskPresentation.SaveAs($taskOutput,32)
} finally {if($taskPresentation){$taskPresentation.Saved=-1;$taskPresentation.Close()};if($taskApp -and $taskApp.Presentations.Count -eq 0){$taskApp.Quit()}}
