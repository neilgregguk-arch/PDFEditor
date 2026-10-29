using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Threading;
using System.Windows.Media;
using System.Windows.Media.Imaging;
namespace PdfPrototype;
public sealed partial class EditorWindow
{
 async Task RunControlTests()
 {
  var results=new List<object>();int failures=0;
  async Task Check(string name,Func<Task<object>> test)
  {try{var metrics=await test();results.Add(new{name,status="pass",metrics});}catch(Exception ex){failures++;results.Add(new{name,status="fail",error=ex.Message,draft,controlText=Text()});}}
  void Assert(bool value,string error){if(!value)throw new InvalidOperationException(error);}
  async Task Pump(){await Dispatcher.InvokeAsync(()=>{},DispatcherPriority.ApplicationIdle);editor.UpdateLayout();await Task.Delay(40);}
  void Replace(string value){editor.BeginChange();editor.SelectAll();editor.Selection.Text=value;editor.EndChange();editor.CaretPosition=Position(value.Length);editor.Selection.Select(editor.CaretPosition,editor.CaretPosition);}
  string folder=auditFolder??work;
  await Check("native-glyph-hit-test-and-caret-at-four-zooms",async()=>
  {
   var checks=new List<object>();var r=info!.Region!;string original=r.OriginalText;
   foreach(int z in new[]{0,1,2,3})
   {
    zoom.SelectedIndex=z;await Pump();
    foreach(int index in new[]{0,5,20,original.Length})
    {
     double x=index==original.Length?info.Glyphs[^1].OriginX+r.Advances[original[^1]-32]+.1:info.Glyphs[index].OriginX+.1;
     var screen=page.PointToScreen(new Point(x*Dip,(r.Baseline-3)*Dip));var local=page.PointFromScreen(screen);
     int selected=HitIndex(local.X/Dip,local.Y/Dip);Assert(selected==index,$"Zoom {zoomFactor}, requested {index}, hit {selected}");
     ActivateAt(selected);await Pump();int observed=new TextRange(editor.Document.ContentStart,editor.CaretPosition).Text.Replace("\r\n","\n").Length;Assert(observed==index,"Caret text offset mismatch");
     var rect=editor.CaretPosition.GetCharacterRect(LogicalDirection.Forward);double expectedX=index==original.Length?r.Advances.Take(0).Sum()+ParagraphLayout.Width(r,original):info.Glyphs[index].OriginX-r.X;
     double xErrorPt=(Canvas.GetLeft(editor)+rect.X)/Dip-r.X-expectedX;
     checks.Add(new{zoom=zoomFactor,index,observed,liveCaretXErrorPt=xErrorPt,caretRectTopDip=rect.Y,caretHeightDip=rect.Height});
     Assert(Math.Abs(xErrorPt)<.75,$"Live caret displaced by {xErrorPt:F3} pt at index {index}");
    }
   }
   zoom.SelectedIndex=1;await Pump();WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"inline-caret.png"),true);return checks;
  });
  await Check("document-switch-displays-current-pdf-bitmap",async()=>
  {
   foreach(string name in new[]{"C-Restricted","D-Font","A-Simple"})
   {
    await Open(Path.Combine(AppContext.BaseDirectory,"samples",name+".pdf"));await Pump();Assert(info!.Image.Contains(info.Hash[..16]),"Render key missing source fingerprint");
    var expected=BitmapDecoder.Create(new Uri(info.CleanImage??info.Image),BitmapCreateOptions.IgnoreImageCache,BitmapCacheOption.OnLoad).Frames[0];
    var a=new FormatConvertedBitmap((BitmapSource)image.Source,PixelFormats.Bgra32,null,0);var b=new FormatConvertedBitmap(expected,PixelFormats.Bgra32,null,0);
    int stride=a.PixelWidth*4;var first=new byte[stride*a.PixelHeight];var second=new byte[stride*b.PixelHeight];a.CopyPixels(first,stride,0);b.CopyPixels(second,stride,0);Assert(first.SequenceEqual(second),"Source-clean bitmap differs from current document: "+name);
   }
   return new{documents=3,currentBitmapPixelEquality=true};
  });
  await Check("native-input-navigation-selection-deletion",async()=>
  {
   ActivateAt(0);Replace("alpha beta gamma");await Pump();editor.CaretPosition=Position(5);
   EditingCommands.MoveRightByCharacter.Execute(null,editor);Assert(new TextRange(editor.Document.ContentStart,editor.CaretPosition).Text.Length==6,"Right arrow command");
   EditingCommands.MoveLeftByCharacter.Execute(null,editor);EditingCommands.Delete.Execute(null,editor);Assert(Text()=="alphabeta gamma","Delete command");
   EditingCommands.Backspace.Execute(null,editor);Assert(Text()=="alphbeta gamma","Backspace command");
   EditingCommands.MoveToLineStart.Execute(null,editor);Assert(new TextRange(editor.Document.ContentStart,editor.CaretPosition).Text.Length==0,"Home command");
   EditingCommands.MoveToLineEnd.Execute(null,editor);Assert(new TextRange(editor.Document.ContentStart,editor.CaretPosition).Text.Length==Text().Length,"End command");
   editor.Selection.Select(Position(0),Position(4));Assert(editor.Selection.Text=="alph","Native selection");
   editor.RaiseEvent(new TextCompositionEventArgs(InputManager.Current.PrimaryKeyboardDevice,new TextComposition(InputManager.Current,editor,"typed")){RoutedEvent=TextCompositionManager.TextInputEvent});await Pump();
   Assert(Text()=="typedbeta gamma","Native TextInput composition did not replace selection");return new{draft=Text(),input="WPF routed TextInput and EditingCommands, not physical SendInput"};
  });
  await Check("native-multi-action-undo-redo",async()=>
  {
   Replace("one two");await Pump();editor.Selection.Select(Position(7),Position(7));
   editor.BeginChange();editor.Selection.Text="!";editor.EndChange();editor.Selection.Select(Position(8),Position(8));Assert(Text()=="one two!","Typing history state: "+Text());
   editor.BeginChange();EditingCommands.Backspace.Execute(null,editor);editor.EndChange();Assert(Text()=="one two","Deletion history state");
   editor.Selection.Select(Position(0),Position(3));editor.BeginChange();editor.Selection.Text="ONE";editor.EndChange();Assert(Text()=="ONE two","Replacement history state");
   foreach(var expected in new[]{"one two","one two!","one two"}){await UndoDocument(false);Assert(Text()==expected,"Undo expected: "+expected+", got: "+Text());}
   foreach(var expected in new[]{"one two!","one two","ONE two"}){await UndoDocument(true);Assert(Text()==expected,"Redo expected: "+expected+", got: "+Text());}
   await Pump();return new{typingInsertionViaNativeSelection=true,deletion=true,replacement=true,threeUndos=true,threeRedos=true};
  });
  await Check("native-copy-cut-paste-undo-redo",async()=>
  {
   var previous=UnicodeClipboard.Read();
   try
   {
    Replace("first second");editor.Selection.Select(Position(0),Position(5));ApplicationCommands.Copy.Execute(null,editor);Assert(UnicodeClipboard.Read()=="first","Copy");
    ApplicationCommands.Cut.Execute(null,editor);Assert(Text()==" second","Cut");
    editor.CaretPosition=Position(Text().Length);ApplicationCommands.Paste.Execute(null,editor);Assert(Text()==" secondfirst","Paste");
    await UndoDocument(false);Assert(Text()==" second","Undo paste");await UndoDocument(true);Assert(Text()==" secondfirst","Redo paste");await Pump();return new{copy=true,cut=true,paste=true,undo=true,redo=true};
   }
   finally{if(previous!=null)UnicodeClipboard.Write(previous);}
  });
  await Check("live-wrap-and-supported-candidate",async()=>
  {
   string text=string.Concat(Enumerable.Repeat("A much longer replacement remains editable and wraps naturally within its owned paragraph. ",4)).TrimEnd();Replace(text);await Pump();
   Assert(draft==text,"Draft truncated");var plan=ParagraphLayout.Plan(info!.Region!,draft);Assert(plan.Safe&&plan.Lines.Length>1,"No safe wrapped plan");
   var rowTops=Enumerable.Range(0,draft.Length).Select(i=>Math.Round(Position(i).GetCharacterRect(LogicalDirection.Forward).Y,2)).Distinct().ToArray();
   Assert(rowTops.Length>1,"RichTextBox did not wrap");
   var visualLines=Enumerable.Range(0,draft.Length).GroupBy(i=>Math.Round(Position(i).GetCharacterRect(LogicalDirection.Forward).Y,2)).OrderBy(g=>g.Key).Select(g=>new string(g.Select(i=>draft[i]).ToArray()).TrimEnd()).ToArray();
   Assert(visualLines.SequenceEqual(plan.Lines.Select(l=>l.TrimEnd())),"Live wrap differs from PDF layout: "+string.Join(" / ",visualLines));
   await ValidateDraft();Assert(verifiedRevision==revision,"Worker candidate failed: "+status.Text);
   WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"wrapped-draft.png"),true);
   return new{characters=draft.Length,uiLines=rowTops.Length,engineLines=plan.Lines.Length,verifiedRevision,status=status.Text};
  });
  await Check("restricted-space-preserves-draft-and-history",async()=>
  {
   await Open(Path.Combine(AppContext.BaseDirectory,"samples","C-Restricted.pdf"));ActivateAt(0);
   string text=string.Concat(Enumerable.Repeat("This expansion must not erase any typed words when it reaches the neighbouring block. ",8));Replace(text);await Pump();
   Assert(draft==text,"Overflow text lost");Assert(layout?.Safe==false,"Overflow not flagged");string saved=draft;await UndoDocument(false);Assert(draft!=saved,"Undo overflow");await UndoDocument(true);Assert(draft==saved,"Redo overflow");
   WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"overflow-warning.png"),true);return new{characters=draft.Length,safe=layout?.Safe,status=status.Text,undoRedoPreserved=true};
  });
  await Check("unsupported-font-glyph-keeps-working-state",async()=>
  {
   await Open(Path.Combine(AppContext.BaseDirectory,"samples","D-Font.pdf"));ActivateAt(0);Replace("A snowman \u2603 remains in this draft.");await Pump();
   Assert(draft.Contains('\u2603')&&layout?.Safe==false&&status.Text.Contains("U+2603"),"Missing-glyph diagnostic or draft missing");
   PersistDraft();Assert(DocumentSession.Restore(SessionRecoveryPath(session!.SourceHash),session.SourceHash).Regions[ActiveKey].Text==draft,"Recovery draft differs");
   WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,"font-warning.png"),true);return new{draft,status=status.Text,sourcePreserved=Wire.Hash(info!.Path)==info.Hash};
  });
  await Check("save-from-live-working-state-and-failure-retains-draft",async()=>
  {
   await Open(Path.Combine(AppContext.BaseDirectory,"samples","A-Simple.pdf"));ActivateAt(0);string text="This live working draft is genuine saved PDF content.";Replace(text);await Pump();
   string destination=Path.Combine(folder,"UI-saved-"+Guid.NewGuid().ToString("N")+".pdf");var saved=await ExportTo(destination);Assert(saved?.Safe==true&&File.Exists(destination),"Working-draft export failed: "+status.Text);Assert(draft==text,"Save replaced draft");
   var failed=await ExportTo(info!.Path);Assert(failed==null&&draft==text&&Wire.Hash(info!.Path)==info.Hash,"Failed export changed draft/source");return new{destination,sourcePreserved=true,draftRetained=true,verification=saved!.Verification};
  });
  await Check("latest-revision-controls-async-validation",async()=>
  {
   await Open(Path.Combine(AppContext.BaseDirectory,"samples","B-Longer.pdf"));ActivateAt(0);Replace("Earlier request text.");var pending=ValidateDraft();long old=revision;Replace("Newer draft must survive a delayed worker response.");await pending;Assert(revision>old&&draft.StartsWith("Newer"),"Older result overwrote draft");await ValidateDraft();Assert(verifiedRevision==revision,"Latest revision not verified");return new{oldRevision=old,revision,verifiedRevision,draft};
  });
  await Check("worker-restart-does-not-replace-draft",async()=>
  {
   string before=draft;worker.TerminateForControlTest();await ValidateDraft();Assert(draft==before&&verifiedRevision==revision,"Worker restart changed or failed latest draft: "+status.Text);return new{draftRetained=true,verifiedRevision};
  });
  File.WriteAllText(Path.Combine(folder,"control-tests.json"),Wire.Write(new{suite="WPF window/control integration (not physical mouse/keyboard automation)",tests=results.Count,failures,results}));
  Status($"Control integration tests: {results.Count-failures}/{results.Count} passed. Physical input tests are recorded separately.",failures>0);WriteAudit();
 }
}
