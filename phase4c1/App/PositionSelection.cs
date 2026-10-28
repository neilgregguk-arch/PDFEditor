using System.Windows;
using System.Windows.Documents;
using System.Windows.Input;
namespace PdfPrototype;
public sealed partial class EditorWindow
{
 bool positionDragging;int positionAnchor;
 void UpdatePositionedSelection()
 {
  if(info?.Region?.Positioned==null||!active)return;
  int Offset(TextPointer p)=>Math.Clamp(new TextRange(editor.Document.ContentStart,p).Text.Replace("\r\n","\n").Length,0,draft.Length);
  positionedInk.Select(Offset(editor.Selection.Start),Offset(editor.Selection.End),Offset(editor.CaretPosition),editor.IsKeyboardFocusWithin);
 }
 bool BeginPositionSelection(Point pt,int clicks,bool extend)
 {
  if(!active||info?.Region is not Region r||r.Positioned==null||ParagraphLayout.Plan(r,draft).Safe!=true)return false;
  double x=pt.X/Dip,y=pt.Y/Dip,right=PositionLayout.CaretX(r,draft,draft.Length);
  if(x<r.X-3||x>Math.Max(r.X+4,right+6)||y<r.Top||y>r.Top+r.LineHeight)return false;
  int hit=ParagraphLayout.Hit(r,draft,x,y).Index;editor.Focus();
  if(clicks>=3){editor.SelectAll();return true;}
  if(clicks==2&&draft.Length>0){int a=Math.Min(hit,draft.Length-1),b=a;bool word=char.IsLetterOrDigit(draft[a]);while(a>0&&char.IsLetterOrDigit(draft[a-1])==word)a--;while(b<draft.Length&&char.IsLetterOrDigit(draft[b])==word)b++;editor.Selection.Select(Position(a),Position(b));return true;}
  positionAnchor=extend?Math.Clamp(new TextRange(editor.Document.ContentStart,editor.Selection.Start).Text.Replace("\r\n","\n").Length,0,draft.Length):hit;
  editor.Selection.Select(Position(positionAnchor),Position(hit));positionDragging=true;editor.CaptureMouse();UpdatePositionedSelection();return true;
 }
 void ExtendPositionSelection(Point pt)
 {
  if(!positionDragging||info?.Region is not Region r)return;int hit=ParagraphLayout.Hit(r,draft,pt.X/Dip,pt.Y/Dip).Index;editor.Selection.Select(Position(positionAnchor),Position(hit));UpdatePositionedSelection();
 }
}
