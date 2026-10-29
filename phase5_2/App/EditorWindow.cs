using Microsoft.Win32;
using System.ComponentModel;
using System.Diagnostics;
using System.Text.Json;
using System.Windows;
using System.Windows.Automation;
using System.Windows.Controls;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
namespace PdfPrototype;
public sealed partial class EditorWindow:Window
{
 const double Dip=96.0/72;
 readonly WorkerClient worker=new();
 readonly Canvas page=new(){Background=Brushes.White};
 readonly Image image=new(){Stretch=Stretch.Fill};
 readonly RichTextBox editor=new(){BorderThickness=new Thickness(0),Padding=new Thickness(0),Background=Brushes.Transparent,VerticalScrollBarVisibility=ScrollBarVisibility.Auto,HorizontalScrollBarVisibility=ScrollBarVisibility.Disabled,AcceptsReturn=true,IsUndoEnabled=false,UndoLimit=0,Visibility=Visibility.Collapsed};
 readonly TextBlock status=new(){Text="Open a PDF to begin.",VerticalAlignment=VerticalAlignment.Center,TextWrapping=TextWrapping.Wrap};
 readonly TextBlock filename=new(){VerticalAlignment=VerticalAlignment.Center,Foreground=new SolidColorBrush(Color.FromRgb(80,94,106)),TextTrimming=TextTrimming.CharacterEllipsis,MaxWidth=310};
 readonly TextBlock pageLabel=new(){VerticalAlignment=VerticalAlignment.Center};
 readonly ComboBox zoom=new(){Width=94,ItemsSource=new[]{"75%","100%","150%","200%"},SelectedIndex=1,VerticalContentAlignment=VerticalAlignment.Center};
 readonly ScrollViewer viewport=new(){HorizontalScrollBarVisibility=ScrollBarVisibility.Auto,VerticalScrollBarVisibility=ScrollBarVisibility.Auto,Background=new SolidColorBrush(Color.FromRgb(230,235,239))};
 readonly DispatcherTimer debounce=new(){Interval=TimeSpan.FromMilliseconds(300)};
 readonly DispatcherTimer auditTimer=new(){Interval=TimeSpan.FromMilliseconds(100)};
 readonly string work=Path.Combine(Path.GetTempPath(),"PdfEditorPrototype",Guid.NewGuid().ToString("N"));
 readonly string recovery=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),"PdfEditorPrototype","phase5_2","sessions");
 readonly string? auditFolder;
 DocumentInfo? info;long revision=0,verifiedRevision=-1;bool suppress=false,active=false,saving=false;string draft="",initialFile="";double zoomFactor=1;Layout? layout;
 readonly PositionedInk positionedInk=new(){Visibility=Visibility.Collapsed};
 public EditorWindow(string[] args)
 {
  Title="PDF Editor / Phase 5.2";Width=1120;Height=900;MinWidth=700;MinHeight=550;WindowStartupLocation=WindowStartupLocation.CenterScreen;Background=Brushes.White;FontFamily=new FontFamily("Segoe UI");FontSize=13;
  for(int i=0;i<args.Length;i++){if(args[i]=="--audit"&&i+1<args.Length)auditFolder=Path.GetFullPath(args[++i]);else if(File.Exists(args[i])&&args[i].EndsWith(".pdf",StringComparison.OrdinalIgnoreCase))initialFile=Path.GetFullPath(args[i]);}
  Directory.CreateDirectory(work);Directory.CreateDirectory(recovery);if(auditFolder!=null)Directory.CreateDirectory(auditFolder);
  if(args.Contains("--paragraph-stage")||args.Contains("--ui-test")||args.Contains("--discovery-ui-test")||args.Contains("--font-ui-test")||args.Contains("--position-ui-test")||args.Contains("--session-ui-test")||args.Contains("--insertion-ui-test")||args.Contains("--wrap-ui-test")){recovery=Path.Combine(work,"test-drafts");Directory.CreateDirectory(recovery);}
  int recoveryStore=Array.IndexOf(args,"--recovery-store");if(recoveryStore>=0&&recoveryStore+1<args.Length){recovery=Path.GetFullPath(args[recoveryStore+1]);Directory.CreateDirectory(recovery);}
  var root=new DockPanel{Background=Brushes.White};Content=root;
  SourceInitialized+=(s,e)=>UnicodeClipboard.Owner=new System.Windows.Interop.WindowInteropHelper(this).Handle;
  var toolbar=new StackPanel{Orientation=Orientation.Horizontal,Margin=new Thickness(18,14,18,14)};DockPanel.SetDock(toolbar,Dock.Top);root.Children.Add(toolbar);
  toolbar.Children.Add(Button("Open PDF",async()=>await OpenDialog(),"OpenPdf"));
  toolbar.Children.Add(Button("Save As",async()=>await SaveAs(),"SaveAs"));
  toolbar.Children.Add(Button("Undo",async()=>{await UndoDocument(false);editor.Focus();},"Undo"));
  toolbar.Children.Add(Button("Redo",async()=>{await UndoDocument(true);editor.Focus();},"Redo"));
  zoom.Margin=new Thickness(18,0,14,0);AutomationProperties.SetAutomationId(zoom,"Zoom");toolbar.Children.Add(zoom);
  toolbar.Children.Add(Button("‹",async()=>await ChangePage(-1),"PreviousPage"));toolbar.Children.Add(pageLabel);toolbar.Children.Add(Button("›",async()=>await ChangePage(1),"NextPage"));filename.Margin=new Thickness(18,0,0,0);toolbar.Children.Add(filename);
  var statusBorder=new Border{Padding=new Thickness(20,10,20,10),BorderBrush=new SolidColorBrush(Color.FromRgb(218,225,231)),BorderThickness=new Thickness(0,1,0,0),MinHeight=54,Child=status};DockPanel.SetDock(statusBorder,Dock.Bottom);root.Children.Add(statusBorder);AutomationProperties.SetAutomationId(status,"Status");
  var pageBorder=new Border{Child=page,Margin=new Thickness(28),HorizontalAlignment=HorizontalAlignment.Center,VerticalAlignment=VerticalAlignment.Top,Effect=new System.Windows.Media.Effects.DropShadowEffect{BlurRadius=16,Opacity=.12,ShadowDepth=2}};viewport.Content=pageBorder;root.Children.Add(viewport);
  page.Children.Add(image);page.Children.Add(editor);page.Children.Add(positionedInk);InitializeSessionEditing(root);BindPositionNavigation();AutomationProperties.SetAutomationId(editor,"InlineEditor");AutomationProperties.SetName(editor,"Owned PDF paragraph editor");
  TextOptions.SetTextFormattingMode(editor,TextFormattingMode.Ideal);Typography.SetKerning(editor,false);Typography.SetStandardLigatures(editor,false);
  foreach(var command in new[]{ApplicationCommands.Copy,ApplicationCommands.Cut,ApplicationCommands.Paste})
  {
   editor.CommandBindings.Add(new CommandBinding(command,(s,e)=>
   {
    try
    {
     if(e.Command==ApplicationCommands.Paste){string? text=UnicodeClipboard.Read();if(text!=null)InsertDraftText(text);}
     else{UnicodeClipboard.Write(editor.Selection.Text);if(e.Command==ApplicationCommands.Cut){editor.BeginChange();editor.Selection.Text="";editor.EndChange();}}
    }
    catch(Exception ex){Status(ex.Message,true);}e.Handled=true;
   },(s,e)=>{e.CanExecute=active&&(command==ApplicationCommands.Paste||!editor.Selection.IsEmpty);e.Handled=true;}));
  }
  editor.GotKeyboardFocus+=(s,e)=>UpdatePositionedSelection();editor.LostKeyboardFocus+=(s,e)=>UpdatePositionedSelection();
  page.MouseLeftButtonDown+=PageClick;editor.TextChanged+=TextChanged;editor.SelectionChanged+=(s,e)=>{if(!suppress)CaptureSelection();UpdatePositionedSelection();ScheduleAudit();};
  zoom.SelectionChanged+=(s,e)=>SetZoom(zoom.SelectedIndex);
  debounce.Tick+=async(s,e)=>{debounce.Stop();await ValidateDraft();};
  auditTimer.Tick+=(s,e)=>{auditTimer.Stop();WriteAudit();};
  PreviewKeyDown+=async(s,e)=>
  {
   if(!Keyboard.Modifiers.HasFlag(ModifierKeys.Control)&&NavigatePosition(e.Key,Keyboard.Modifiers.HasFlag(ModifierKeys.Shift))){e.Handled=true;return;}
   if(Keyboard.Modifiers.HasFlag(ModifierKeys.Control))
   {
    if(e.Key==Key.Z){e.Handled=true;await UndoDocument(false);}if(e.Key==Key.Y){e.Handled=true;await UndoDocument(true);}
    if(e.Key==Key.O){e.Handled=true;await OpenDialog();}
    if(e.Key==Key.S){e.Handled=true;await SaveAs();}
    if(e.Key>=Key.D1&&e.Key<=Key.D4){e.Handled=true;zoom.SelectedIndex=(int)e.Key-(int)Key.D1;}
   }
  };
  Loaded+=async(s,e)=>{WindowState=WindowState.Normal;Activate();if(initialFile.Length>0)await Open(initialFile);else{string sample=Path.Combine(AppContext.BaseDirectory,args.Contains("--ui-test")?"samples":"document-corpus",args.Contains("--ui-test")?"A-Simple.pdf":"multi-natural.pdf");if(!File.Exists(sample))sample=Path.Combine(AppContext.BaseDirectory,"samples","A-Simple.pdf");if(File.Exists(sample))await Open(sample);}if(args.Contains("--ui-test"))await RunControlTests();if(args.Contains("--discovery-ui-test"))await RunDiscoveryControlTests();if(args.Contains("--clipboard-probe"))await RunClipboardProbe();if(args.Contains("--font-ui-test"))await RunFontControlTests();if(args.Contains("--position-ui-test"))await RunPositionControlTests();if(args.Contains("--session-ui-test"))await RunSessionControlTests();if(args.Contains("--insertion-ui-test"))await RunInsertionControlTests();if(args.Contains("--wrap-ui-test"))await RunWrapControlTests();if(args.Contains("--paragraph-stage"))await RunParagraphControlTests(int.Parse(args[Array.IndexOf(args,"--paragraph-stage")+1]),Path.GetFullPath(args[Array.IndexOf(args,"--paragraph-shared")+1]));if(args.Contains("--recovery-stage1"))await RunProcessRecoveryTest(false);if(args.Contains("--recovery-stage2"))await RunProcessRecoveryTest(true);};
  Closing+=(s,e)=>PersistDraft();Closed+=(s,e)=>{worker.Dispose();CleanupWork();};
 }
 Button Button(string label,Action action,string id){var b=new Button{Content=label,Padding=new Thickness(12,6,12,6),Margin=new Thickness(0,0,8,0),MinHeight=32};b.Click+=(s,e)=>action();AutomationProperties.SetAutomationId(b,id);return b;}
 void Status(string text,bool warning=false){status.Text=text;status.Foreground=new SolidColorBrush(warning?Color.FromRgb(158,78,16):Color.FromRgb(55,79,96));ScheduleAudit();}
 static BitmapImage Bitmap(string path){var b=new BitmapImage();b.BeginInit();b.CacheOption=BitmapCacheOption.OnLoad;b.CreateOptions=BitmapCreateOptions.IgnoreImageCache;b.UriSource=new Uri(path);b.EndInit();b.Freeze();return b;}
 async Task OpenDialog(){try{var dialog=new OpenFileDialog{Filter="PDF documents (*.pdf)|*.pdf",InitialDirectory=Path.Combine(AppContext.BaseDirectory,"samples")};if(dialog.ShowDialog(this)==true)await Open(dialog.FileName,deliberate:true);}catch(Exception e){Status("File picker unavailable. Draft retained. You can also launch the prototype with a PDF path: "+e.Message,true);}}
 async Task Open(string path,int pageIndex=0,string regionId="",bool deliberate=false)
 {
  CaptureSelection();PersistDraft();long captured=++navigation;active=false;positionedInk.Visibility=Visibility.Collapsed;debounce.Stop();editor.Visibility=Visibility.Collapsed;inactiveDrafts.Children.Clear();Status("Opening PDF…");
  try
  {
   bool same=session!=null&&string.Equals(Path.GetFullPath(path),session.Source,StringComparison.OrdinalIgnoreCase);
   var document=await worker.Call<DocumentInfo>(new(){Source=path,Page=pageIndex,RegionId=regionId,Revision=captured,Work=work,ExpectedHash=same?session!.SourceHash:"",Changes=same&&!deliberate?session!.Changes():null});if(captured!=navigation)return;
   string recoveryWarning="";bool restored=false;
   if(same&&deliberate&&session!.SourceHash==document.Hash&&session.Modified.Length>0)document=await worker.Call<DocumentInfo>(new(){Source=path,Page=pageIndex,RegionId=regionId,Revision=captured,Work=work,ExpectedHash=session.SourceHash,Changes=session.Changes()});if(captured!=navigation)return;
   if(same&&session!.SourceHash!=document.Hash)recoveryWarning="Source changed. The previous session is preserved separately; its drafts have not been applied to this file.";
   if(!same||session!.SourceHash!=document.Hash)
   {
    session=new(){Source=document.Path,SourceHash=document.Hash};string stored=SessionRecoveryPath(document.Hash);
    if(File.Exists(stored))try{session=DocumentSession.Restore(stored,document.Hash);session.Source=document.Path;restored=true;}catch(Exception ex){recoveryWarning="Recovery could not be restored; its file is retained for inspection. "+ex.Message;File.Move(stored,stored+".invalid-"+Guid.NewGuid().ToString("N"));}
   }
   if(restored&&session!.Modified.Length>0)document=await worker.Call<DocumentInfo>(new(){Source=path,Page=pageIndex,RegionId=regionId,Revision=captured,Work=work,ExpectedHash=session.SourceHash,Changes=session.Changes()});if(captured!=navigation)return;
   session!.Register(document.Regions);session.CurrentPage=document.Page;session.PageCount=document.PageCount;session.PageSizes[document.Page]=new(0,0,document.Width,document.Height);info=document;revision=session.Revision;verifiedRevision=session.VerifiedRevision;
   draft=document.Region!=null&&session.Regions.TryGetValue(DocumentSession.Key(document.Page,document.Region.Id),out var state)?state.Text:"";
   filename.Text=Path.GetFileName(path);filename.ToolTip=path;pageLabel.Text=$"{document.Page+1} / {document.PageCount}";
   page.Width=document.Width*Dip;page.Height=document.Height*Dip;image.Width=page.Width;image.Height=page.Height;image.Source=Bitmap(document.CleanImage??document.Image);
   if(info.Region!=null){session.ActiveKey=ActiveKey;SetupEditor();}
   SetZoom(zoom.SelectedIndex);PaintInactiveDrafts();Status(document.Diagnostic);UpdateDocumentStatus();
   if(recoveryWarning.Length>0)Status(recoveryWarning,true);
   if(session.Modified.Length>0){Status("Working drafts retained · "+session.Summary());debounce.Start();}
  }
  catch(Exception ex){PaintInactiveDrafts();UpdateDocumentStatus();Status("Open failed; all session drafts retained: "+ex.Message,true);}
 }
 async Task ChangePage(int delta){if(info==null)return;int p=Math.Clamp(info.Page+delta,0,info.PageCount-1);if(p!=info.Page)await Open(info.Path,p);}
 void SetupEditor()
 {
  if(info?.Region is not Region r)return;suppress=true;
  string asset=Path.Combine(AppContext.BaseDirectory,"assets",r.FontFile);var face=new GlyphTypeface(new Uri(asset));
  var family=new FontFamily(new Uri(Path.GetDirectoryName(asset)+Path.DirectorySeparatorChar),"./#"+face.FamilyNames.Values.First());
  editor.FontFamily=family;editor.FontWeight=face.Weight;editor.FontStyle=face.Style;editor.FontSize=r.FontSize*Dip;editor.Foreground=new SolidColorBrush(Color.FromRgb((byte)r.R,(byte)r.G,(byte)r.B));
  var paragraph=new Paragraph(new Run(draft)){Margin=new Thickness(0),Padding=new Thickness(0),LineHeight=r.LineHeight*Dip,LineStackingStrategy=LineStackingStrategy.BlockLineHeight};
  editor.Document=new FlowDocument(paragraph){FontFamily=family,FontWeight=face.Weight,FontStyle=face.Style,FontSize=r.FontSize*Dip,PagePadding=new Thickness(0),TextAlignment=TextAlignment.Left,ColumnWidth=1000000,LineHeight=r.LineHeight*Dip,LineStackingStrategy=LineStackingStrategy.BlockLineHeight};
  Typography.SetKerning(editor.Document,false);Typography.SetStandardLigatures(editor.Document,false);
  editor.Width=(r.Positioned!=null?Math.Max(r.Width,ParagraphLayout.Width(r,draft))+24:r.Width)*Dip;editor.Height=(r.OriginalLines.Length*r.LineHeight)*Dip+12;Canvas.SetLeft(editor,r.X*Dip);Canvas.SetTop(editor,r.Top*Dip);
  suppress=false;
 }
 string Text()=>new TextRange(editor.Document.ContentStart,editor.Document.ContentEnd).Text.Replace("\r\n","\n").TrimEndOneNewline();
 // Shared paste insertion: WPF TextRange assignment can absorb the final LF
 // into its mandatory terminal paragraph. Restore that user-entered break.
 void InsertDraftText(string text)
 {
  string normalized=text.Replace("\r\n","\n").Replace('\r','\n'),before=Text();
  int start=new TextRange(editor.Document.ContentStart,editor.Selection.Start).Text.Replace("\r\n","\n").Length;
  int end=new TextRange(editor.Document.ContentStart,editor.Selection.End).Text.Replace("\r\n","\n").Length;
  start=Math.Min(start,before.Length);end=Math.Min(end,before.Length);
  string expected=before[..start]+normalized+before[end..];
  editor.BeginChange();
  try
  {
   editor.Selection.Text=normalized;
   if(expected.EndsWith('\n')&&Text()==expected[..^1])
   {editor.CaretPosition=editor.Document.ContentEnd;EditingCommands.EnterParagraphBreak.Execute(null,editor);}
  }
  finally{editor.EndChange();}
 }
 TextPointer Position(int index)
 {
  var p=editor.Document.ContentStart.GetInsertionPosition(LogicalDirection.Forward)!;int current=0;
  while(p!=null)
  {
   if(current>=index)return p;
   var next=p.GetNextInsertionPosition(LogicalDirection.Forward);if(next==null)break;
   // Count only the next segment, rather than copying the entire prefix at
   // every step. Native TextPointers still own selection and insertion.
   current+=new TextRange(p,next).Text.Replace("\r\n","\n").Length;p=next;
  }
  return editor.Document.ContentEnd.GetInsertionPosition(LogicalDirection.Backward)!;
 }
 void ActivateAt(int index)
 {
  if(info?.Region is not Region r)return;positionCaretRow=null;preferredCaretX=null;active=true;image.Source=Bitmap(info.CleanImage!);editor.Visibility=Visibility.Visible;
  // RichTextBox reserves an internal selection margin; align its actual text origin, not its outer control edge.
  editor.Width=(r.Positioned!=null?Math.Max(r.Width,ParagraphLayout.Width(r,draft))+24:r.Width)*Dip;Canvas.SetLeft(editor,r.X*Dip);Canvas.SetTop(editor,r.Top*Dip);editor.UpdateLayout();
  var first=Position(0).GetCharacterRect(LogicalDirection.Forward);
  editor.Width=(r.Positioned!=null?Math.Max(r.Width,ParagraphLayout.Width(r,draft))+24:r.Width)*Dip+first.X*2;Canvas.SetLeft(editor,r.X*Dip-first.X);Canvas.SetTop(editor,r.Top*Dip-first.Y);editor.UpdateLayout();
  UpdatePositionedInk();editor.Focus();editor.CaretPosition=Position(index);editor.Selection.Select(editor.CaretPosition,editor.CaretPosition);Status("Draft editing · original-font region reconstruction on save.");PaintInactiveDrafts();UpdateDocumentStatus();ScheduleAudit();
 }
 async void PageClick(object sender,MouseButtonEventArgs e)
 {
  var pt=e.GetPosition(page);await SelectRegionAt(pt.X/Dip,pt.Y/Dip);e.Handled=true;
 }
 async Task SelectRegionAt(double x,double y)
 {
  if(info==null)return;
  var target=FindRegionAt(x,y);
  if(target!=null&&target.Eligibility!="Editable"){Status(target.Eligibility+": "+EligibilityExplanation(target.Reasons),true);return;}
  if(target!=null&&target.Id!=info.Region?.Id)
  {
   await Open(info.Path,info.Page,target.Id);
  }
  if(info?.Region is not Region r||active)return;
  // Blank page clicks never snap to an unrelated region.
  if(!new Box(r.X,r.Top,r.Width,Math.Max(r.LineHeight,r.OriginalLines.Length*r.LineHeight)).Contains(x,y)&&!(r.Positioned!=null&&ParagraphLayout.Plan(r,draft).LineBoxes.Any(b=>b.Contains(x,y)))){Status(info.Diagnostic);return;}
  int index=HitIndex(x,y);
  if(index<0){Status("No reliable glyph mapping at this location.",true);return;}
  if(session?.Regions.TryGetValue(ActiveKey,out var remembered)==true&&draft!=r.OriginalText&&ParagraphLayout.Plan(r,draft).Positioned?.Lines.Length is not >1)index=Math.Clamp(remembered.Caret,0,draft.Length);
  ActivateAt(index);if(r.Positioned!=null&&ParagraphLayout.Plan(r,draft).Positioned?.Lines.Length>1){positionCaretRow=ParagraphLayout.Hit(r,draft,x,y).Line;UpdatePositionedSelection();}PaintInactiveDrafts();
 }
 int HitIndex(double x,double y)
 {
  if(info?.Region is not Region r)return -1;
  int index;
  if(draft==r.OriginalText)
  {
   var rows=info.Glyphs.GroupBy(g=>g.Baseline).OrderBy(g=>Math.Abs(g.Key-y)).FirstOrDefault();
   if(rows==null)return -1;
   var glyphs=rows.OrderBy(g=>g.Index).ToArray();index=glyphs[^1].Index+1;
   for(int i=0;i<glyphs.Length;i++){double end=i+1<glyphs.Length?glyphs[i+1].OriginX:glyphs[i].OriginX+r.Advances[glyphs[i].Text[0]-32];if(x<(glyphs[i].OriginX+end)/2){index=glyphs[i].Index;break;}}
  }
  else index=ParagraphLayout.Hit(r,draft,x,y).Index;
  return index;
 }
 static string EligibilityExplanation(string[] reasons)
 {
  if(reasons.Contains("FONT_NOT_EMBEDDED"))return "The original font is not embedded in this PDF. No substitute font will be used.";
  if(reasons.Any(r=>r.StartsWith("AMBIGUOUS")))return "These text blocks cannot yet be separated safely for editing.";
  if(reasons.Contains("INITIAL_OBJECT_RECONSTRUCTION_DIFFERS")||reasons.Contains("NON_NATURAL_GLYPH_SPACING"))return "This text uses spacing or glyph mappings the editor cannot preserve yet.";
  if(reasons.Contains("INITIAL_TEXT_MAPPING_OR_GLYPH_UNAVAILABLE"))return "This text cannot be matched reliably to the original PDF font.";
  if(reasons.Any(r=>r.Contains("SPACE")||r.Contains("INTERSECTION")||r.Contains("NEIGHBOUR")))return "There is not enough clear space to edit this text safely.";
  return "Editing this text or page structure is not supported safely yet.";
 }
 void UpdatePositionedInk()
 {
  if(info?.Region is not Region r)return;
  var brush=new SolidColorBrush(Color.FromRgb((byte)r.R,(byte)r.G,(byte)r.B));
  bool positioned=active&&r.Positioned!=null&&ParagraphLayout.Plan(r,draft).Positioned!=null;
  positionedInk.Visibility=positioned?Visibility.Visible:Visibility.Collapsed;editor.Foreground=positioned?Brushes.Transparent:brush;editor.CaretBrush=positioned?Brushes.Transparent:brush;editor.SelectionBrush=positioned?Brushes.Transparent:SystemColors.HighlightBrush;
  if(positioned){positionedInk.Set(r,draft);Canvas.SetLeft(positionedInk,r.X*Dip);Canvas.SetTop(positionedInk,r.Top*Dip);UpdatePositionedSelection();}
 }
 void TextChanged(object sender,TextChangedEventArgs e)
 {
  if(suppress||info?.Region is not Region r||session==null)return;draft=Text();
  int caret=Math.Min(draft.Length,new TextRange(editor.Document.ContentStart,editor.CaretPosition).Text.Replace("\r\n","\n").Length);
  positionCaretRow=null;preferredCaretX=null;session.Change(ActiveKey,draft,caret);revision=session.Revision;verifiedRevision=-1;layout=ParagraphLayout.Plan(r,draft);
  if(r.Positioned!=null){double margin=r.X*Dip-Canvas.GetLeft(editor);editor.Width=(Math.Max(r.Width,Math.Max(ParagraphLayout.Width(r,draft),layout.Positioned?.Origins.LastOrDefault()-r.X??0))+24)*Dip+Math.Max(0,margin)*2;}
  UpdatePositionedInk();
  var state=session.Regions[ActiveKey];state.Validation=state.Modified?(layout.Safe?"Pending":"Blocked"):"Unchanged";state.Message=layout.Diagnostic;
  recoveryTimer.Stop();recoveryTimer.Start();editor.Height=Math.Min((info.Height-r.Top-12)*Dip,Math.Max(r.LineHeight*Dip+12,layout.Height>0?layout.Height*Dip+12:(info.Height-r.Top-12)*Dip));
  Status(layout.Safe?"Working drafts updated · checking the complete document…":layout.Diagnostic,!layout.Safe);UpdateDocumentStatus();
  debounce.Stop();if(session.Modified.Length>0)debounce.Start();ScheduleAudit();
 }
 async Task ValidateDraft()
 {
  if(info==null||session==null||session.Modified.Length==0)return;long captured=revision;string source=info.Path;var owner=session;string sourceHash=session.SourceHash;
  try
  {
   var result=await worker.Call<EditResult>(Request("preview",captured));
   if(session?.MatchesResponse(owner,captured,sourceHash)!=true||info?.Hash!=sourceHash)return;verifiedRevision=result.Safe?captured:-1;ApplyValidation(result);Status(result.Diagnostic,!result.Safe);
  }
  catch(Exception ex){if(session?.MatchesResponse(owner,captured,sourceHash)==true){if(session!=null)foreach(var state in session.Modified){state.Validation="Blocked";state.Message=ex.Message;}UpdateDocumentStatus();Status("Candidate validation failed. All drafts retained: "+ex.Message,true);}}
 }
 EditRequest Request(string command,long captured,string destination="")=>new(){Command=command,Revision=captured,Source=info!.Path,ExpectedHash=info.Hash,Page=info.Page,RegionId=info.Region?.Id??"",Text=draft,Changes=session?.Changes(),Work=work,Destination=destination};
 async Task SaveAs()
 {
  if(saving)return;if(info==null||session==null){Status("View-only PDF: no supported editable region to save.",true);return;}
  if(session==null||session.Modified.Length==0){Status("No text changes to export.");return;}
  try{var dialog=new SaveFileDialog{Filter="PDF documents (*.pdf)|*.pdf",FileName=Path.GetFileNameWithoutExtension(info.Path)+"-edited.pdf",OverwritePrompt=false};if(dialog.ShowDialog(this)==true)await ExportTo(dialog.FileName);}catch(Exception e){Status("Save picker unavailable; draft retained: "+e.Message,true);}
 }
 async Task<EditResult?> ExportTo(string destination)
 {
  long captured=revision;var owner=session;var request=Request("save",captured,destination);saving=true;Status($"Generating and verifying revision {captured}…");
  try
  {
   var result=await worker.Call<EditResult>(request);
   bool current=session?.MatchesResponse(owner,captured,request.ExpectedHash)==true&&info?.Hash==request.ExpectedHash;
   if(current)ApplyValidation(result);
   if(result.Safe){Status(current?$"Verified PDF saved: {Path.GetFileName(result.Destination)} · working draft retained.":"A captured document revision was saved. The current working session is unchanged.");AuditExport(request,result);}
   else if(current)Status(result.Diagnostic,true);
   return result;
  }
  catch(Exception ex){Status("Save failed; draft retained. "+ex.Message,true);return null;}
  finally{saving=false;PersistDraft();ScheduleAudit();}
 }
 void SetZoom(int index)
 {
  zoomFactor=index switch{0=>.75,2=>1.5,3=>2,_=>1};page.LayoutTransform=new ScaleTransform(zoomFactor,zoomFactor);ScheduleAudit();
 }
 void PersistDraft()
 {
  if(session==null)return;
  try{session.Persist(SessionRecoveryPath(session.SourceHash));}
  catch(Exception e){status.Text="All drafts remain in memory; recovery write failed: "+e.Message;}
 }
 void ScheduleAudit(){if(auditFolder!=null){auditTimer.Stop();auditTimer.Start();}}
 void WriteAudit()
 {
  if(auditFolder==null)return;
  try
  {
   var caret=active?editor.CaretPosition.GetCharacterRect(LogicalDirection.Forward):Rect.Empty;int caretIndex=active?new TextRange(editor.Document.ContentStart,editor.CaretPosition).Text.Replace("\r\n","\n").Length:-1;
   var origin=PointToScreen(new Point(0,0));var pOrigin=page.PointToScreen(new Point(0,0));
   var carets=new List<object>();
   if(active)for(int i=0;i<=Math.Min(draft.Length,200);i++){var rect=Position(i).GetCharacterRect(LogicalDirection.Forward);var screen=editor.PointToScreen(new Point(rect.X,rect.Y));carets.Add(new{index=i,x=screen.X-origin.X,y=screen.Y-origin.Y,height=rect.Height*zoomFactor});}
   File.WriteAllText(Path.Combine(auditFolder,"state.json"),Wire.Write(new{revision,verifiedRevision,source=info?.Path,sourceHash=info?.Hash,active,draft,caretIndex,selection=editor.Selection.Text,zoom=zoomFactor,status=status.Text,safe=layout?.Safe,workerPid=(int?)null,pageOrigin=new{x=pOrigin.X-origin.X,y=pOrigin.Y-origin.Y},pageScale=Dip*zoomFactor,carets}));
   var content=(FrameworkElement)Content;var bmp=new RenderTargetBitmap((int)content.ActualWidth,(int)content.ActualHeight,96,96,PixelFormats.Pbgra32);bmp.Render(content);var png=new PngBitmapEncoder();png.Frames.Add(BitmapFrame.Create(bmp));using var fs=File.Create(Path.Combine(auditFolder,"window.png"));png.Save(fs);
  }
  catch{/* Test diagnostics must never interrupt user input. */}
 }
}
static class TextHelpers
{
 public static string TrimEndOneNewline(this string text)=>text.EndsWith('\n')?text[..^1]:text;
}
