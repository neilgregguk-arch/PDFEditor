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
 readonly RichTextBox editor=new(){BorderThickness=new Thickness(0),Padding=new Thickness(0),Background=Brushes.Transparent,VerticalScrollBarVisibility=ScrollBarVisibility.Auto,HorizontalScrollBarVisibility=ScrollBarVisibility.Disabled,AcceptsReturn=true,IsUndoEnabled=true,UndoLimit=1000,Visibility=Visibility.Collapsed};
 readonly TextBlock status=new(){Text="Open a PDF to begin.",VerticalAlignment=VerticalAlignment.Center,TextWrapping=TextWrapping.Wrap};
 readonly TextBlock filename=new(){VerticalAlignment=VerticalAlignment.Center,Foreground=new SolidColorBrush(Color.FromRgb(80,94,106)),TextTrimming=TextTrimming.CharacterEllipsis,MaxWidth=310};
 readonly TextBlock pageLabel=new(){VerticalAlignment=VerticalAlignment.Center};
 readonly ComboBox zoom=new(){Width=94,ItemsSource=new[]{"75%","100%","150%","200%"},SelectedIndex=1,VerticalContentAlignment=VerticalAlignment.Center};
 readonly ScrollViewer viewport=new(){HorizontalScrollBarVisibility=ScrollBarVisibility.Auto,VerticalScrollBarVisibility=ScrollBarVisibility.Auto,Background=new SolidColorBrush(Color.FromRgb(230,235,239))};
 readonly DispatcherTimer debounce=new(){Interval=TimeSpan.FromMilliseconds(300)};
 readonly DispatcherTimer auditTimer=new(){Interval=TimeSpan.FromMilliseconds(100)};
 readonly string work=Path.Combine(Path.GetTempPath(),"PdfEditorPrototype",Guid.NewGuid().ToString("N"));
 readonly string recovery=Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),"PdfEditorPrototype","drafts");
 readonly string? auditFolder;
 DocumentInfo? info;long revision=0,verifiedRevision=-1;bool suppress=false,active=false,saving=false;string draft="",initialFile="";double zoomFactor=1;Layout? layout;
 public EditorWindow(string[] args)
 {
  Title="PDF Editor / Phase 2";Width=1120;Height=900;MinWidth=700;MinHeight=550;WindowStartupLocation=WindowStartupLocation.CenterScreen;Background=Brushes.White;FontFamily=new FontFamily("Segoe UI");FontSize=13;
  for(int i=0;i<args.Length;i++){if(args[i]=="--audit"&&i+1<args.Length)auditFolder=Path.GetFullPath(args[++i]);else if(File.Exists(args[i])&&args[i].EndsWith(".pdf",StringComparison.OrdinalIgnoreCase))initialFile=Path.GetFullPath(args[i]);}
  Directory.CreateDirectory(work);Directory.CreateDirectory(recovery);if(auditFolder!=null)Directory.CreateDirectory(auditFolder);
  if(args.Contains("--ui-test")){recovery=Path.Combine(work,"test-drafts");Directory.CreateDirectory(recovery);}
  var root=new DockPanel{Background=Brushes.White};Content=root;
  SourceInitialized+=(s,e)=>UnicodeClipboard.Owner=new System.Windows.Interop.WindowInteropHelper(this).Handle;
  var toolbar=new StackPanel{Orientation=Orientation.Horizontal,Margin=new Thickness(18,14,18,14)};DockPanel.SetDock(toolbar,Dock.Top);root.Children.Add(toolbar);
  toolbar.Children.Add(Button("Open PDF",async()=>await OpenDialog(),"OpenPdf"));
  toolbar.Children.Add(Button("Save As",async()=>await SaveAs(),"SaveAs"));
  toolbar.Children.Add(Button("Undo",()=>{if(active&&editor.CanUndo)editor.Undo();editor.Focus();},"Undo"));
  toolbar.Children.Add(Button("Redo",()=>{if(active&&editor.CanRedo)editor.Redo();editor.Focus();},"Redo"));
  zoom.Margin=new Thickness(18,0,14,0);AutomationProperties.SetAutomationId(zoom,"Zoom");toolbar.Children.Add(zoom);
  toolbar.Children.Add(Button("‹",async()=>await ChangePage(-1),"PreviousPage"));toolbar.Children.Add(pageLabel);toolbar.Children.Add(Button("›",async()=>await ChangePage(1),"NextPage"));filename.Margin=new Thickness(18,0,0,0);toolbar.Children.Add(filename);
  var statusBorder=new Border{Padding=new Thickness(20,10,20,10),BorderBrush=new SolidColorBrush(Color.FromRgb(218,225,231)),BorderThickness=new Thickness(0,1,0,0),MinHeight=54,Child=status};DockPanel.SetDock(statusBorder,Dock.Bottom);root.Children.Add(statusBorder);AutomationProperties.SetAutomationId(status,"Status");
  var pageBorder=new Border{Child=page,Margin=new Thickness(28),HorizontalAlignment=HorizontalAlignment.Center,VerticalAlignment=VerticalAlignment.Top,Effect=new System.Windows.Media.Effects.DropShadowEffect{BlurRadius=16,Opacity=.12,ShadowDepth=2}};viewport.Content=pageBorder;root.Children.Add(viewport);
  page.Children.Add(image);page.Children.Add(editor);AutomationProperties.SetAutomationId(editor,"InlineEditor");AutomationProperties.SetName(editor,"Owned PDF paragraph editor");
  TextOptions.SetTextFormattingMode(editor,TextFormattingMode.Ideal);Typography.SetKerning(editor,false);Typography.SetStandardLigatures(editor,false);
  foreach(var command in new[]{ApplicationCommands.Copy,ApplicationCommands.Cut,ApplicationCommands.Paste})
  {
   editor.CommandBindings.Add(new CommandBinding(command,(s,e)=>
   {
    try
    {
     if(e.Command==ApplicationCommands.Paste){string? text=UnicodeClipboard.Read();if(text!=null){editor.BeginChange();editor.Selection.Text=text;editor.EndChange();}}
     else{UnicodeClipboard.Write(editor.Selection.Text);if(e.Command==ApplicationCommands.Cut){editor.BeginChange();editor.Selection.Text="";editor.EndChange();}}
    }
    catch(Exception ex){Status(ex.Message,true);}e.Handled=true;
   },(s,e)=>{e.CanExecute=active&&(command==ApplicationCommands.Paste||!editor.Selection.IsEmpty);e.Handled=true;}));
  }
  page.MouseLeftButtonDown+=PageClick;editor.TextChanged+=TextChanged;editor.SelectionChanged+=(s,e)=>ScheduleAudit();
  zoom.SelectionChanged+=(s,e)=>SetZoom(zoom.SelectedIndex);
  debounce.Tick+=async(s,e)=>{debounce.Stop();await ValidateDraft();};
  auditTimer.Tick+=(s,e)=>{auditTimer.Stop();WriteAudit();};
  PreviewKeyDown+=async(s,e)=>
  {
   if(Keyboard.Modifiers.HasFlag(ModifierKeys.Control))
   {
    if(e.Key==Key.O){e.Handled=true;await OpenDialog();}
    if(e.Key==Key.S){e.Handled=true;await SaveAs();}
    if(e.Key>=Key.D1&&e.Key<=Key.D4){e.Handled=true;zoom.SelectedIndex=(int)e.Key-(int)Key.D1;}
   }
  };
  Loaded+=async(s,e)=>{WindowState=WindowState.Normal;Activate();if(initialFile.Length>0)await Open(initialFile);else{string sample=Path.Combine(AppContext.BaseDirectory,"samples","A-Simple.pdf");if(File.Exists(sample))await Open(sample);}if(args.Contains("--ui-test"))await RunControlTests();};
  Closing+=(s,e)=>PersistDraft();Closed+=(s,e)=>worker.Dispose();
 }
 Button Button(string label,Action action,string id){var b=new Button{Content=label,Padding=new Thickness(12,6,12,6),Margin=new Thickness(0,0,8,0),MinHeight=32};b.Click+=(s,e)=>action();AutomationProperties.SetAutomationId(b,id);return b;}
 void Status(string text,bool warning=false){status.Text=text;status.Foreground=new SolidColorBrush(warning?Color.FromRgb(158,78,16):Color.FromRgb(55,79,96));ScheduleAudit();}
 static BitmapImage Bitmap(string path){var b=new BitmapImage();b.BeginInit();b.CacheOption=BitmapCacheOption.OnLoad;b.CreateOptions=BitmapCreateOptions.IgnoreImageCache;b.UriSource=new Uri(path);b.EndInit();b.Freeze();return b;}
 async Task OpenDialog(){try{var dialog=new OpenFileDialog{Filter="PDF documents (*.pdf)|*.pdf",InitialDirectory=Path.Combine(AppContext.BaseDirectory,"samples")};if(dialog.ShowDialog(this)==true)await Open(dialog.FileName);}catch(Exception e){Status("File picker unavailable. Draft retained. You can also launch the prototype with a PDF path: "+e.Message,true);}}
 async Task Open(string path,int pageIndex=0)
 {
  PersistDraft();long captured=++revision;active=false;debounce.Stop();editor.Visibility=Visibility.Collapsed;verifiedRevision=-1;Status("Opening PDF…");
  try
  {
   var document=await worker.Call<DocumentInfo>(new(){Source=path,Page=pageIndex,Revision=captured,Work=work});if(captured!=revision)return;
   info=document;draft=document.Region?.OriginalText??"";filename.Text=Path.GetFileName(path);filename.ToolTip=path;pageLabel.Text=$"{document.Page+1} / {document.PageCount}";
   page.Width=document.Width*Dip;page.Height=document.Height*Dip;image.Width=page.Width;image.Height=page.Height;image.Source=Bitmap(document.Image);
   if(info.Region!=null)
   {
    string stored=Path.Combine(recovery,info.Hash+".json");
    if(File.Exists(stored)){try{var cached=Wire.Read<DraftRecovery>(File.ReadAllText(stored));if(cached.SourceHash==info.Hash)draft=cached.Text;}catch{/* A damaged recovery file never changes the immutable source. */}}
    SetupEditor();
   }
   SetZoom(zoom.SelectedIndex);Status(document.Diagnostic);
   if(info.Region!=null&&draft!=info.Region.OriginalText){ActivateAt(0);Status("Recovered unsaved working draft. Original PDF remains unchanged.");debounce.Start();}
  }
  catch(Exception ex){info=null;Status("Open failed: "+ex.Message,true);}
 }
 async Task ChangePage(int delta){if(info==null)return;int p=Math.Clamp(info.Page+delta,0,info.PageCount-1);if(p!=info.Page)await Open(info.Path,p);}
 void SetupEditor()
 {
  if(info?.Region is not Region r)return;suppress=true;
  string asset=Path.Combine(AppContext.BaseDirectory,"assets",r.FontFile);var face=new GlyphTypeface(new Uri(asset));
  var family=new FontFamily(new Uri(Path.GetDirectoryName(asset)+Path.DirectorySeparatorChar),"./#"+face.FamilyNames.Values.First());
  editor.FontFamily=family;editor.FontSize=r.FontSize*Dip;editor.Foreground=new SolidColorBrush(Color.FromRgb((byte)r.R,(byte)r.G,(byte)r.B));
  var paragraph=new Paragraph(new Run(draft)){Margin=new Thickness(0),Padding=new Thickness(0),LineHeight=r.LineHeight*Dip,LineStackingStrategy=LineStackingStrategy.BlockLineHeight};
  editor.Document=new FlowDocument(paragraph){FontFamily=family,FontSize=r.FontSize*Dip,PagePadding=new Thickness(0),TextAlignment=TextAlignment.Left,ColumnWidth=1000000,LineHeight=r.LineHeight*Dip,LineStackingStrategy=LineStackingStrategy.BlockLineHeight};
  Typography.SetKerning(editor.Document,false);Typography.SetStandardLigatures(editor.Document,false);
  editor.Width=r.Width*Dip;editor.Height=(r.OriginalLines.Length*r.LineHeight)*Dip+12;Canvas.SetLeft(editor,r.X*Dip);Canvas.SetTop(editor,r.Top*Dip);
  suppress=false;
 }
 string Text()=>new TextRange(editor.Document.ContentStart,editor.Document.ContentEnd).Text.Replace("\r\n","\n").TrimEndOneNewline();
 TextPointer Position(int index)
 {
  var p=editor.Document.ContentStart.GetInsertionPosition(LogicalDirection.Forward)!;
  while(p!=null)
  {
   int current=new TextRange(editor.Document.ContentStart,p).Text.Replace("\r\n","\n").Length;
   if(current>=index)return p;
   var next=p.GetNextInsertionPosition(LogicalDirection.Forward);if(next==null)break;p=next;
  }
  return editor.Document.ContentEnd.GetInsertionPosition(LogicalDirection.Backward)!;
 }
 void ActivateAt(int index)
 {
  if(info?.Region is not Region r)return;active=true;image.Source=Bitmap(info.CleanImage!);editor.Visibility=Visibility.Visible;
  // RichTextBox reserves an internal selection margin; align its actual text origin, not its outer control edge.
  editor.Width=r.Width*Dip;Canvas.SetLeft(editor,r.X*Dip);Canvas.SetTop(editor,r.Top*Dip);editor.UpdateLayout();
  var first=Position(0).GetCharacterRect(LogicalDirection.Forward);
  editor.Width=r.Width*Dip+first.X*2;Canvas.SetLeft(editor,r.X*Dip-first.X);Canvas.SetTop(editor,r.Top*Dip-first.Y);editor.UpdateLayout();
  editor.Focus();editor.CaretPosition=Position(index);editor.Selection.Select(editor.CaretPosition,editor.CaretPosition);Status("Draft editing · original-font region reconstruction on save.");ScheduleAudit();
 }
 void PageClick(object sender,MouseButtonEventArgs e)
 {
  if(info?.Region is not Region r||active)return;var pt=e.GetPosition(page);double x=pt.X/Dip,y=pt.Y/Dip;
  // Blank page clicks never snap to an unrelated region.
  if(!new Box(r.X,r.Top,r.Width,Math.Max(r.LineHeight,r.OriginalLines.Length*r.LineHeight)).Contains(x,y)){Status(info.Diagnostic);return;}
  int index=HitIndex(x,y);
  if(index<0){Status("No reliable glyph mapping at this location.",true);return;}
  ActivateAt(index);e.Handled=true;
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
 void TextChanged(object sender,TextChangedEventArgs e)
 {
  if(suppress||info?.Region is not Region r)return;draft=Text();revision++;verifiedRevision=-1;layout=ParagraphLayout.Plan(r,draft);PersistDraft();
  editor.Height=Math.Min((info.Height-r.Top-12)*Dip,Math.Max(r.LineHeight*Dip+12,layout.Height>0?layout.Height*Dip+12:(info.Height-r.Top-12)*Dip));
  if(draft==r.OriginalText){debounce.Stop();Status("Draft matches the original. No text changes to export.");ScheduleAudit();return;}
  Status(layout.Safe?$"Draft revision {revision} · {layout.Lines.Length} line(s) · checking PDF candidate…":layout.Diagnostic,!layout.Safe);
  debounce.Stop();if(layout.Safe)debounce.Start();ScheduleAudit();
 }
 async Task ValidateDraft()
 {
  if(info?.Region==null||draft==info.Region.OriginalText)return;long captured=revision;string source=info.Path;
  try
  {
   var result=await worker.Call<EditResult>(Request("preview",captured));
   if(captured!=revision||info?.Path!=source)return;verifiedRevision=result.Safe?captured:-1;Status(result.Diagnostic,!result.Safe);
  }
  catch(Exception ex){if(captured==revision)Status("Candidate validation failed. Draft retained: "+ex.Message,true);}
 }
 EditRequest Request(string command,long captured,string destination="")=>new(){Command=command,Revision=captured,Source=info!.Path,ExpectedHash=info.Hash,Page=info.Page,Text=draft,Work=work,Destination=destination};
 async Task SaveAs()
 {
  if(saving)return;if(info?.Region==null){Status("View-only PDF: no supported editable region to save.",true);return;}
  layout=ParagraphLayout.Plan(info.Region,draft);if(!layout.Safe){Status(layout.Diagnostic,true);return;}if(draft==info.Region.OriginalText){Status("No text changes to export.");return;}
  try{var dialog=new SaveFileDialog{Filter="PDF documents (*.pdf)|*.pdf",FileName=Path.GetFileNameWithoutExtension(info.Path)+"-edited.pdf",OverwritePrompt=false};if(dialog.ShowDialog(this)==true)await ExportTo(dialog.FileName);}catch(Exception e){Status("Save picker unavailable; draft retained: "+e.Message,true);}
 }
 async Task<EditResult?> ExportTo(string destination)
 {
  long captured=revision;var request=Request("save",captured,destination);saving=true;Status($"Generating and verifying revision {captured}…");
  try
  {
   var result=await worker.Call<EditResult>(request);
   if(result.Safe){Status(captured==revision?$"Verified PDF saved: {Path.GetFileName(result.Destination)} · working draft retained.":$"Saved revision {captured}. Newer draft revision {revision} remains unsaved.");if(auditFolder!=null)File.WriteAllText(Path.Combine(auditFolder,"last-save.json"),Wire.Write(result));}
   else if(captured==revision)Status(result.Diagnostic,true);
   return result;
  }
  catch(Exception ex){Status("Save failed; draft retained. "+ex.Message,true);return null;}
  finally{saving=false;PersistDraft();ScheduleAudit();}
 }
 void SetZoom(int index)
 {
  zoomFactor=index switch{0=>.75,2=>1.5,3=>2,_=>1};page.LayoutTransform=new ScaleTransform(zoomFactor,zoomFactor);ScheduleAudit();
 }
 sealed record DraftRecovery(string SourceHash,string Source,string Text,long Revision);
 void PersistDraft()
 {
  if(info?.Region==null)return;
  try{string path=Path.Combine(recovery,info.Hash+".json"),temporary=path+".tmp";File.WriteAllText(temporary,Wire.Write(new DraftRecovery(info.Hash,info.Path,draft,revision)));File.Move(temporary,path,true);}
  catch(Exception e){status.Text="Draft remains in memory; recovery write failed: "+e.Message;}
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
