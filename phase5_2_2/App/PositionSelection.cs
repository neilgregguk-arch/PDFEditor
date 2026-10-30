using System.Windows;
using System.Windows.Documents;
using System.Windows.Input;
namespace PdfPrototype;
public sealed partial class EditorWindow
{
 bool positionDragging;int positionAnchor;int? positionCaretRow;double? preferredCaretX;
 void UpdatePositionedSelection()
 {
  if(!UsesPositionedPresentation)return;
  int Offset(TextPointer p)=>Math.Clamp(new TextRange(editor.Document.ContentStart,p).Text.Replace("\r\n","\n").Length,0,draft.Length);
  positionedInk.Select(Offset(editor.Selection.Start),Offset(editor.Selection.End),Offset(editor.CaretPosition),editor.IsKeyboardFocusWithin,positionCaretRow);
  if(editor.IsKeyboardFocusWithin&&positionedInk.IsVisible&&UsesPositionedPresentation)
   positionedInk.BringIntoView(new Rect((positionedInk.CaretOriginPt-info!.Region!.X)*Dip,(positionedInk.CaretTopPt-info!.Region!.Top)*Dip,4,info!.Region!.LineHeight*Dip));
 }
 bool BeginPositionSelection(Point pt,int clicks,bool extend)
 {
  if(!UsesPositionedPresentation||info?.Region is not Region r)return false;
  var plan=ParagraphLayout.Plan(r,draft);double x=pt.X/Dip,y=pt.Y/Dip,right=plan.LineBoxes.Select(b=>b.Right).DefaultIfEmpty(r.X+4).Max();
  if(x<r.X-3||x>Math.Max(r.X+4,right+6)||y<r.Top||y>r.Top+plan.Height)return false;
  var picked=ParagraphLayout.Hit(r,draft,x,y);int hit=picked.Index;positionCaretRow=picked.Line;preferredCaretX=null;editor.Focus();
  if(clicks>=3){editor.SelectAll();return true;}
  if(clicks==2&&draft.Length>0){int a=Math.Min(hit,draft.Length-1),b=a;bool word=char.IsLetterOrDigit(draft[a]);while(a>0&&char.IsLetterOrDigit(draft[a-1])==word)a--;while(b<draft.Length&&char.IsLetterOrDigit(draft[b])==word)b++;editor.Selection.Select(Position(a),Position(b));return true;}
  positionAnchor=extend?Math.Clamp(new TextRange(editor.Document.ContentStart,editor.Selection.Start).Text.Replace("\r\n","\n").Length,0,draft.Length):hit;
  editor.Selection.Select(Position(positionAnchor),Position(hit));positionDragging=true;editor.CaptureMouse();UpdatePositionedSelection();return true;
 }
 void ExtendPositionSelection(Point pt)
 {
  if(!positionDragging||info?.Region is not Region r)return;var picked=ParagraphLayout.Hit(r,draft,pt.X/Dip,pt.Y/Dip);int hit=picked.Index;positionCaretRow=picked.Line;editor.Selection.Select(Position(positionAnchor),Position(hit));UpdatePositionedSelection();
 }
 bool NavigatePosition(Key key,bool shift)
 {
  if(!UsesPositionedPresentation||info?.Region is not Region r)return false;var plan=ParagraphLayout.Plan(r,draft);var p=plan.Positioned;if(p==null||p.Lines.Length<2)return false;
  int current=Math.Clamp(new TextRange(editor.Document.ContentStart,editor.CaretPosition).Text.Replace("\r\n","\n").Length,0,draft.Length);var point=PositionLayout.Caret(r,draft,current,positionCaretRow);int row=point.Row,target=current;
  if(key==Key.Home){target=p.Lines[row].Start;preferredCaretX=null;}
  else if(key==Key.End){target=p.Lines[row].Start+p.Lines[row].Text.Length;preferredCaretX=null;}
  else if(key==Key.Up||key==Key.Down){preferredCaretX??=point.X;row=Math.Clamp(row+(key==Key.Up?-1:1),0,p.Lines.Length-1);target=PositionLayout.Hit(r,draft,preferredCaretX.Value,r.Top+p.Lines[row].Baseline-r.Baseline+r.LineHeight/2).Index;}
  else return false;
  if(shift&&editor.Selection.IsEmpty)positionAnchor=current;positionCaretRow=row;
  if(shift)editor.Selection.Select(Position(positionAnchor),Position(target));else editor.Selection.Select(Position(target),Position(target));UpdatePositionedSelection();ScheduleAudit();return true;
 }
 void BindPositionNavigation()
 {
  // The native editor is one logical unwrapped surface. Its hidden caret must
  // not pan the page away from the separately painted proposed-position caret.
  editor.AddHandler(FrameworkElement.RequestBringIntoViewEvent,new RequestBringIntoViewEventHandler((s,e)=>
  {if(UsesPositionedPresentation)e.Handled=true;}),true);
  foreach(var (command,key,extend) in new[]{(EditingCommands.MoveDownByLine,Key.Down,false),(EditingCommands.MoveUpByLine,Key.Up,false),(EditingCommands.MoveToLineStart,Key.Home,false),(EditingCommands.MoveToLineEnd,Key.End,false),(EditingCommands.SelectDownByLine,Key.Down,true),(EditingCommands.SelectUpByLine,Key.Up,true),(EditingCommands.SelectToLineStart,Key.Home,true),(EditingCommands.SelectToLineEnd,Key.End,true)})
   editor.CommandBindings.Add(new System.Windows.Input.CommandBinding(command,(s,e)=>{e.Handled=NavigatePosition(key,extend);},(s,e)=>{if(UsesPositionedPresentation&&ParagraphLayout.Plan(info!.Region!,draft).Positioned?.Lines.Length>1){e.CanExecute=true;e.Handled=true;}}));
 }

}
