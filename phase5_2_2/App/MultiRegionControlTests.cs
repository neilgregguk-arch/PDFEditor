using System.Windows;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Threading;
namespace PdfPrototype;
public sealed partial class EditorWindow
{
 async Task RunMultiRegionControlTests(bool baseline)
 {
  string folder=auditFolder!,source=Path.Combine(AppContext.BaseDirectory,"original-paragraphs","Word-cafe-paragraph.pdf"),sourceHash=Wire.Hash(Path.Combine(AppContext.BaseDirectory,"original-paragraphs","Word-cafe-paragraph.pdf"));
  var rows=new List<object>();int failures=0;
  void Assert(bool b,string message){if(!b)throw new Exception(message);}
  async Task Pump(){((FrameworkElement)Content).UpdateLayout();await Dispatcher.InvokeAsync(()=>{},DispatcherPriority.ApplicationIdle);await Task.Delay(65);}
  async Task Check(string name,Func<Task<object>> action){try{rows.Add(new{name,status="pass",detail=await action()});}catch(Exception ex){failures++;rows.Add(new{name,status="fail",error=ex.ToString(),draft});}File.WriteAllText(Path.Combine(folder,"multi-region-progress.json"),Wire.Write(new{baseline,tests=rows.Count,failures,rows}));}
  async Task Capture(string name){await Pump();WriteAudit();File.Copy(Path.Combine(folder,"window.png"),Path.Combine(folder,name+".png"),true);File.Copy(Path.Combine(folder,"state.json"),Path.Combine(folder,name+".json"),true);}
  async Task<object> Click(Region expected,double x,double y,bool require)
  {
   var pt=new Point(x*Dip,y*Dip);var hit=page.InputHitTest(pt);var before=ActiveKey;string? policy=FindRegionAt(x,y)?.Id;routedPagePointForControlTest=pt;routedTaskForControlTest=null;
   try
   {
    var preview=new MouseButtonEventArgs(Mouse.PrimaryDevice,Environment.TickCount,MouseButton.Left){RoutedEvent=Mouse.PreviewMouseDownEvent};
    if(hit is UIElement ui)ui.RaiseEvent(preview);else if(hit is ContentElement ce)ce.RaiseEvent(preview);else throw new Exception("No WPF input element");
    if(routedTaskForControlTest!=null)await routedTaskForControlTest;
    if(!preview.Handled&&routedTaskForControlTest==null)
    {
     var bubble=new MouseButtonEventArgs(Mouse.PrimaryDevice,Environment.TickCount,MouseButton.Left){RoutedEvent=Mouse.MouseDownEvent};if(hit is UIElement u)u.RaiseEvent(bubble);else ((ContentElement)hit!).RaiseEvent(bubble);if(routedTaskForControlTest!=null)await routedTaskForControlTest;
    }
    await Pump();var screen=page.PointToScreen(pt);var result=new{expected=expected.Id,pageX=x,pageY=y,screenX=screen.X,screenY=screen.Y,visualHit=hit?.GetType().Name,policyTarget=policy,before,after=ActiveKey,active,preview.Handled,original=expected.ObservedBounds,retained=RetainedDraftBounds(expected),editorZ=Panel.GetZIndex(editor),editorOrder=page.Children.IndexOf(editor),inactiveOrder=page.Children.IndexOf(inactiveDrafts),focus=Keyboard.FocusedElement?.GetType().Name};
    if(require)Assert(active&&info!.Region!.Id==expected.Id,"Routed page click failed to activate "+expected.Id);return result;
   }
   finally{routedPagePointForControlTest=null;routedTaskForControlTest=null;}
  }
  void Replace(string text){editor.SelectAll();InsertDraftText(text);debounce.Stop();}
  await Open(source);var upper=info!.Regions.Single(r=>r.Paragraph!=null);var lower=info.Regions.Single(r=>r.Id!=upper.Id&&r.Eligibility=="Editable");string longText=string.Join(" ",Enumerable.Repeat("cafe calm.",70));
  await Check("two-retained-regions-original-and-expanded-routed-hit-diagnostics",async()=>
  {
   await Click(lower,lower.ObservedBounds!.X+4,lower.Baseline-3,true);Replace(longText);await Pump();await Click(upper,upper.X+4,upper.Baseline-3,true);Replace(longText);await Pump();await Capture("two-invalid-upper-active");var clicks=new List<object>();
   foreach(var r in new[]{lower,upper,lower})
   {
    var box=RetainedDraftBounds(r);clicks.Add(await Click(r,box.Right-20,box.Y+Math.Min(box.Height-3,45),!baseline));
    if(!active)await Click(r,r.ObservedBounds!.X+4,r.Baseline-3,true);
   }
   await Capture("two-invalid-return");return new{clicks,upperId=upper.Id,lowerId=lower.Id,exactTexts=session!.Regions[DocumentSession.Key(0,upper.Id)].Text==longText&&session.Regions[DocumentSession.Key(0,lower.Id)].Text==longText};
  });
  await Check("exact-original-shortening-and-u-compatibility-diagnostics",async()=>
  {
   await Click(lower,lower.ObservedBounds!.X+4,lower.Baseline-3,true);Replace("u");await Pump();await ValidateDraft();var uPlan=ParagraphLayout.Plan(lower,draft);var mapping=lower.Characters.Single(c=>c.Unicode==117);bool outline=new GlyphTypeface(new Uri(lower.FontFile)).CharacterToGlyphMap.ContainsKey(117);await Capture("unmapped-u");Replace(lower.OriginalText);await Pump();await ValidateDraft();var exact=new{draft,original=lower.OriginalText,retained=IsRetainedDraft(lower,draft,ParagraphLayout.Plan(lower,draft)),session!.VerifiedRevision,revision=session!.Revision,message=session.Regions[ActiveKey].Message,status=status.Text};await Capture("lower-exact-original");if(!baseline)Assert(draft==lower.OriginalText&&!IsRetainedDraft(lower,draft,ParagraphLayout.Plan(lower,draft)),"Exact original remained retained");return new{mapping,outline,uPlan.ReasonCodes,uPlan.GlyphIssues,exact};
  });

  if(!baseline)
  {
   async Task Choose(Region r){await Open(source,0,r.Id);await Click(r,r.ObservedBounds!.X+4,r.Baseline-3,true);debounce.Stop();}
   async Task Reset(){await Choose(upper);Replace(upper.OriginalText);await Choose(lower);Replace(lower.OriginalText);}
   string safe="calm cafe.";
   foreach(bool upperBad in new[]{true,false})
   await Check(upperBad?"invalid-upper-valid-lower":"valid-upper-invalid-lower",async()=>
   {
    await Reset();await Choose(upper);Replace(upperBad?longText:safe);await Choose(lower);Replace(upperBad?safe:longText);await ValidateDraft();
    var good=upperBad?lower:upper;var bad=upperBad?upper:lower;
    Assert(!IsRetainedDraft(good,safe,ParagraphLayout.Plan(good,safe)),"Fitting region inherited another rejection");Assert(IsRetainedDraft(bad,longText,ParagraphLayout.Plan(bad,longText)),"Invalid region lost retention");Assert(session!.VerifiedRevision==-1&&!saveButton!.IsEnabled,"Mixed session exportable");
    for(int i=0;i<6;i++){var r=i%2==0?upper:lower;await Click(r,r.ObservedBounds!.X+5,r.Baseline-3,true);Assert(draft==(r==bad?longText:safe),"Switch changed text");}
    await Capture(upperBad?"invalid-upper-valid-lower":"valid-upper-invalid-lower");return new{switches=6,summary=documentStatus.Text};
   });
   await Check("overlapping-interactive-editor-original-source-priority",async()=>
   {
    await Reset();await Choose(upper);Replace(longText);await Pump();
    // Adversarial UI-only overlap: retain source geometry, move the interactive
    // upper control over the lower original. Real InputHitTest must see editor.
    Canvas.SetTop(editor,lower.ObservedBounds!.Y*Dip);Canvas.SetLeft(editor,lower.ObservedBounds.X*Dip);editor.Height=150;editor.Width=400;await Pump();
    var hit=page.InputHitTest(new Point((lower.ObservedBounds.X+8)*Dip,(lower.Baseline-3)*Dip));
    DependencyObject? node=hit as DependencyObject;bool inside=false;while(node!=null){if(node==editor){inside=true;break;}node=node is Visual?VisualTreeHelper.GetParent(node):node is FrameworkContentElement fc?fc.Parent:null;}
    Assert(inside,"Adversarial hit did not enter the upper interactive editor");await Capture("adversarial-overlap-before-click");var click=await Click(lower,lower.ObservedBounds.X+8,lower.Baseline-3,true);Assert(draft==lower.OriginalText,"Overlap changed lower content");await Capture("adversarial-overlap-source-selected");return new{hit=hit?.GetType().Name,insideUpperEditor=inside,click,pdfGeometryUnchanged=true};
   });
   await Check("source-picker-overlapping-retained-previews-selection-restoration",async()=>
   {
    await Reset();await Choose(lower);Replace(longText);editor.Selection.Select(Position(10),Position(24));CaptureSelection();await Choose(upper);Replace(longText);
    // Two presentation surfaces overlap in this adversarial setup only.
    var lowerPreview=inactiveDrafts.Children.OfType<FrameworkElement>().First();Canvas.SetTop(lowerPreview,upper.ObservedBounds!.Y*Dip);await Pump();await Capture("adversarial-preview-overlap");
    var choice=regionPicker.Items.Cast<RegionChoice>().Single(c=>c.Id==lower.Id);regionPicker.SelectedItem=choice;
    for(int i=0;i<150&&(opening||info!.Region!.Id!=lower.Id||!active);i++)await Task.Delay(40);debounce.Stop();
    Assert(active&&info!.Region!.Id==lower.Id&&draft==longText,"Source picker failed");Assert(editor.Selection.Text==longText[10..24],"Selection not restored");await Capture("source-picker-lower-restored");return new{sourceIdentity=choice.Identity,selection=editor.Selection.Text,caret=session!.Regions[ActiveKey].Caret};
   });
   await Check("both-exact-originals-after-rejection",async()=>
   {
    await Choose(upper);Replace(upper.OriginalText);await Choose(lower);Replace(lower.OriginalText);await ValidateDraft();Assert(session!.Modified.Length==0&&!IsRetainedDraft(lower,draft,ParagraphLayout.Plan(lower,draft)),"Original remained amber");await Capture("originals-restored");return new{summary=PresentationSummary(),draft};
   });
   await Check("different-safe-shortening-pending-verified-and-stale",async()=>
   {
    await Reset();await Choose(upper);Replace(longText);await ValidateDraft();Replace(safe);Assert(PresentationState(upper,draft,ParagraphLayout.Plan(upper,draft))=="Pending"&&!saveButton!.IsEnabled,"New safe text reused rejection or approval");await Capture("shortened-pending");await ValidateDraft();Assert(PresentationState(upper,draft,ParagraphLayout.Plan(upper,draft))=="Verified"&&!IsRetainedDraft(upper,draft,layout!)&&saveButton!.IsEnabled,"Safe shortening not verified");await Capture("shortened-verified");
    await Choose(lower);Replace(safe);Assert(PresentationState(upper,safe,ParagraphLayout.Plan(upper,safe))=="Stale"&&!saveButton!.IsEnabled,"Other edit did not stale verification");await ValidateDraft();Assert(session!.VerifiedRevision==session!.Revision&&saveButton!.IsEnabled,"Both safe drafts failed");return new{state=PresentationSummary()};
   });
   foreach(var input in new[]{("ordinary-u","u"),("crlf","cafe\r\ncalm"),("lf","cafe\ncalm"),("multiple-paragraphs","cafe\n\ncalm\ncafe"),("trailing-break","cafe\n"),("tab","cafe\tcalm"),("nbsp","cafe\u00a0calm"),("unmapped-symbol","cafe \u2603"),("mapped-only",safe)})
   await Check("current-character-sequence-"+input.Item1,async()=>
   {
    await Reset();await Choose(upper);Replace(input.Item2);string expected=input.Item2.Replace("\r\n","\n").Replace('\r','\n');await Pump();await ValidateDraft();var plan=ParagraphLayout.Plan(upper,draft);string reason=DraftReason(upper,draft,plan);bool supported=input.Item1=="mapped-only";
    Assert(draft==expected&&Text()==expected,"Pasted characters lost");Assert((session!.VerifiedRevision==session!.Revision)==supported,"Unexpected eligibility");if(!supported){Assert(IsRetainedDraft(upper,draft,plan),"Unsupported text not retained");Assert(!reason.Contains(" or hard line break"),"Ambiguous generic reason");if(expected.Contains('\n'))Assert(reason.StartsWith("Hard line break"),"Break reason missing");if(input.Item1=="ordinary-u")Assert(reason.Contains("U+0075")&&!reason.Contains("Hard line"),"u confused with newline");}
    string[] points=draft.EnumerateRunes().Select(r=>$"U+{r.Value:X4}").ToArray();return new{input=input.Item1,expected,points,plan.Safe,plan.GlyphIssues,reason,sourceIdentity=upper.SourceIdentity};
   });
   foreach(bool navigate in new[]{false,true})
   await Check(navigate?"late-response-after-region-switch":"late-response-after-rapid-corrections",async()=>
   {
    await Reset();await Choose(upper);Replace(longText);var arrived=new TaskCompletionSource();var release=new TaskCompletionSource();
    worker.BeforeDeliveryForControlTest=async req=>{if(req.Command=="preview"){worker.BeforeDeliveryForControlTest=null;arrived.SetResult();await release.Task;}};
    Task held=ValidateDraft();await arrived.Task.WaitAsync(TimeSpan.FromSeconds(15));
    try
    {
     if(navigate){Task moving=Open(source,0,lower.Id);release.SetResult();await held;await moving;await Click(lower,lower.X+4,lower.Baseline-3,true);Replace(safe);}
     else{Replace("u");Replace("cafe");Replace(safe);release.SetResult();await held;Assert(PresentationState(upper,draft,ParagraphLayout.Plan(upper,draft))is "Pending" or "Stale","Old response overwrote correction");}
     Assert(session!.VerifiedRevision==-1&&!saveButton!.IsEnabled,"Stale response enabled save");if(!navigate){await ValidateDraft();Assert(session.VerifiedRevision==session!.Revision,"Current correction not approved");}return new{revision,session.VerifiedRevision,draft,activeKey=ActiveKey};
    }
    finally{release.TrySetResult();worker.BeforeDeliveryForControlTest=null;}
   });
   await Check("global-undo-redo-two-region-drafts",async()=>
   {
    await Reset();await Choose(lower);Replace(longText);await Choose(upper);Replace("u");await UndoDocument(false);debounce.Stop();Assert(draft==upper.OriginalText,"Upper undo failed");await UndoDocument(false);debounce.Stop();Assert(draft==lower.OriginalText,"Lower undo failed");await UndoDocument(true);debounce.Stop();Assert(draft==longText,"Lower redo failed");await UndoDocument(true);debounce.Stop();Assert(draft=="u"&&session!.Modified.Length==2,"Upper redo failed");return new{session!.Cursor,session!.CanUndo,session!.CanRedo};
   });
   foreach(int z in new[]{0,1,2,3})
   await Check("two-regions-routed-hits-zoom-"+z,async()=>
   {
    await Reset();await Choose(lower);Replace(longText);await Choose(upper);Replace(longText);zoom.SelectedIndex=z;var clicks=new List<object>();foreach(var r in new[]{lower,upper,lower}){viewport.ScrollToVerticalOffset(r.Top*Dip*zoomFactor);await Pump();clicks.Add(await Click(r,r.ObservedBounds!.X+5,r.Baseline-3,true));Assert(page.ClipToBounds&&editor.ClipToBounds,"Clipping disabled");}await Capture("both-retained-zoom-"+z);return clicks;
   });
   zoom.SelectedIndex=1;
   await Check("rejected-combined-export-keeps-source-destination-and-drafts",async()=>
   {
    string dest=Path.Combine(folder,"invalid-combined-must-not-exist.pdf");await ValidateDraft();var result=await ExportTo(dest);Assert(result?.Safe!=true&&!File.Exists(dest)&&session!.Modified.Length==2&&Wire.Hash(source)==sourceHash,"Refusal corrupted state");return new{result?.Diagnostic,sourceHash,upperText=session!.Regions[DocumentSession.Key(0,upper.Id)].Text,lowerText=session.Regions[DocumentSession.Key(0,lower.Id)].Text};
   });
   await Check("incomplete-validation-does-not-impute-geometry-failure",async()=>
   {
    await Reset();await Choose(upper);Replace(safe);await ValidateDraft();worker.BeforeDeliveryForControlTest=req=>throw new IOException("Injected delivery failure after worker response, UI control test only");await ValidateDraft();worker.BeforeDeliveryForControlTest=null;
    Assert(!IsRetainedDraft(upper,draft,layout!)&&PresentationState(upper,draft,layout!)=="Pending"&&!saveButton!.IsEnabled,"Unknown failure labelled geometry rejection or approval");await ValidateDraft();Assert(saveButton!.IsEnabled,"Retry failed");return new{summary=PresentationSummary()};
   });
   await Check("multi-region-recovery-stage-one-persist",async()=>
   {
    await Reset();await Choose(lower);Replace(longText);editor.Selection.Select(Position(8),Position(19));CaptureSelection();await Choose(upper);Replace("cafe\ncalm");CaptureSelection();PersistDraft();
    var expected=new{source,hash=sourceHash,texts=session!.Regions.ToDictionary(k=>k.Key,k=>k.Value.Text),cursor=session.Cursor,history=session.History.Count};File.WriteAllText(Path.Combine(folder,"recovery-reopen-expectation.json"),Wire.Write(expected));File.Copy(SessionRecoveryPath(sourceHash),Path.Combine(folder,"multi-region-recovery.session.json"),true);return expected;
   });
   await Check("corrected-combined-save-reopen-and-reedit",async()=>
   {
    await Reset();await Choose(upper);Replace(safe);await Choose(lower);Replace("cafe calm.");await ValidateDraft();Assert(saveButton!.IsEnabled&&session!.VerifiedRevision==session!.Revision,"Corrected drafts not current");await Capture("both-corrected-verified");string dest=Path.Combine(folder,"multi-region-corrected.pdf");var result=await ExportTo(dest);Assert(result?.Safe==true,"Corrected save failed");
    await Open(dest);var group=info!.Regions.Where(r=>r.Paragraph!=null).OrderBy(r=>r.Top).First();await Click(group,group.X+4,group.Baseline-3,true);Assert(draft==safe,"Reopened paragraph differs");Replace("cafe calm.");await ValidateDraft();Assert(session!.VerifiedRevision==session!.Revision,"Reopened reedit refused");string reedit=Path.Combine(folder,"multi-region-reedited.pdf");Assert((await ExportTo(reedit))?.Safe==true,"Reedited save failed");await Capture("reopened-reedited-verified");return new{result,reedit};
   });
  }
  Assert(Wire.Hash(source)==sourceHash,"Source modified");File.WriteAllText(Path.Combine(folder,"multi-region-tests.json"),Wire.Write(new{baseline,tests=rows.Count,failures,rows,scope="Actual WPF InputHitTest and routed tunnel/bubble events, explicit page-point override in diagnostic harness; not physical mouse input"}));Close();
 }
}
