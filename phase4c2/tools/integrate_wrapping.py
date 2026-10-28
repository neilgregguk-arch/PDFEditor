from pathlib import Path
p=Path('phase4c2/App/PositionedInk.cs');s=p.read_text(encoding='utf-8').replace('int start,end,caret;','int start,end,caret;int? affinity;')
a=s.index(' public double CaretOriginPt');b=s.index(' public void Set(',a)
s=s[:a]+''' public double CaretOriginPt=>Point(caret,affinity).X;
 public double CaretTopPt=>Point(caret,affinity).Y;
 public int CaretRow=>Point(caret,affinity).Row;
 (double X,double Y,int Row) Point(int index,int? preferred=null)
 {
  if(region==null||proposal==null||proposal.Lines.Length==0)return(region?.X??0,region?.Top??0,0);index=Math.Clamp(index,0,text.Length);
  int row=preferred is int p&&p>=0&&p<proposal.Lines.Length&&index>=proposal.Lines[p].Start&&index<=proposal.Lines[p].Start+proposal.Lines[p].Text.Length?p:Math.Max(0,Array.FindLastIndex(proposal.Lines,l=>l.Start<=index));var line=proposal.Lines[row];int n=index-line.Start;
  return(n>=line.Text.Length?(line.Text.Length==0?region.X:line.Origins[^1]+region.Advances[line.Text[^1]-32]):line.Origins[n],region.Top+line.Baseline-region.Baseline,row);
 }
'''+s[b:]
s=s.replace('Width=Math.Max(r.Width,Origin(text.Length)-r.X)*4/3+10;Height=r.LineHeight*4/3+12;','Width=Math.Max(r.Width,proposal?.Lines.Select(l=>Point(l.Start+l.Text.Length,Array.IndexOf(proposal.Lines,l)).X-r.X).DefaultIfEmpty(0).Max()??0)*4/3+10;Height=Math.Max(r.LineHeight,proposal?.Lines.Select(l=>l.Baseline-r.Baseline+r.LineHeight).DefaultIfEmpty(r.LineHeight).Max()??r.LineHeight)*4/3+12;')
s=s.replace('int active,bool focused)','int active,bool focused,int? row=null)').replace('start=Math.Clamp','affinity=row;start=Math.Clamp')
a=s.index('  if(start<end)dc.DrawRectangle');s=s[:a]+'''  foreach(var line in proposal.Lines)
  {
   int row=Array.IndexOf(proposal.Lines,line);double y=line.Baseline-r.Baseline;
   int a=Math.Max(start,line.Start),b=Math.Min(end,line.Start+line.Text.Length);
   if(a<b)dc.DrawRectangle(new SolidColorBrush(Color.FromArgb(90,51,142,230)),null,new Rect((Point(a,row).X-r.X)*dip,y*dip,Math.Max(1,(Point(b,row).X-Point(a,row).X)*dip),r.LineHeight*dip));
   for(int j=0;j<line.Text.Length;j++)
   {
    ushort gid=face.CharacterToGlyphMap[line.Text[j]];var run=new GlyphRun(face,0,false,r.FontSize*dip,1,new[]{gid},new Point((line.Origins[j]-r.X)*dip,(r.Ascent+y)*dip),new[]{face.AdvanceWidths[gid]*r.FontSize*dip},null,null,null,null,null,null);dc.DrawGlyphRun(brush,run);
   }
  }
  if(showCaret&&blink){var p=Point(caret,affinity);double x=(p.X-r.X)*dip,y=(p.Y-r.Top)*dip;dc.DrawLine(new Pen(brush,1),new System.Windows.Point(x,y),new System.Windows.Point(x,y+r.FontSize*dip));}
 }
}
''';p.write_text(s,encoding='utf-8',newline='\n')
p=Path('phase4c2/App/PositionSelection.cs');s=p.read_text(encoding='utf-8').replace('int positionAnchor;','int positionAnchor;int? positionCaretRow;double? preferredCaretX;').replace('editor.IsKeyboardFocusWithin);','editor.IsKeyboardFocusWithin,positionCaretRow);')
s=s.replace('ParagraphLayout.Plan(r,draft).Safe!=true','ParagraphLayout.Plan(r,draft).Positioned==null')
s=s.replace('double x=pt.X/Dip,y=pt.Y/Dip,right=PositionLayout.CaretX(r,draft,draft.Length);','var plan=ParagraphLayout.Plan(r,draft);double x=pt.X/Dip,y=pt.Y/Dip,right=plan.LineBoxes.Select(b=>b.Right).DefaultIfEmpty(r.X+4).Max();').replace('y>r.Top+r.LineHeight','y>r.Top+plan.Height')
s=s.replace('int hit=ParagraphLayout.Hit(r,draft,x,y).Index;editor.Focus();','var picked=ParagraphLayout.Hit(r,draft,x,y);int hit=picked.Index;positionCaretRow=picked.Line;preferredCaretX=null;editor.Focus();')
s=s.replace('int hit=ParagraphLayout.Hit(r,draft,pt.X/Dip,pt.Y/Dip).Index;editor.Selection','var picked=ParagraphLayout.Hit(r,draft,pt.X/Dip,pt.Y/Dip);int hit=picked.Index;positionCaretRow=picked.Line;editor.Selection')
pos=s.rindex('\n}')
s=s[:pos]+'''
 bool NavigatePosition(Key key,bool shift)
 {
  if(!active||info?.Region is not Region r||r.Positioned==null)return false;var plan=ParagraphLayout.Plan(r,draft);var p=plan.Positioned;if(p==null||p.Lines.Length<2)return false;
  int current=Math.Clamp(new TextRange(editor.Document.ContentStart,editor.CaretPosition).Text.Replace("\\r\\n","\\n").Length,0,draft.Length);var point=PositionLayout.Caret(r,draft,current,positionCaretRow);int row=point.Row,target=current;
  if(key==Key.Home){target=p.Lines[row].Start;preferredCaretX=null;}
  else if(key==Key.End){target=p.Lines[row].Start+p.Lines[row].Text.Length;preferredCaretX=null;}
  else if(key==Key.Up||key==Key.Down){preferredCaretX??=point.X;row=Math.Clamp(row+(key==Key.Up?-1:1),0,p.Lines.Length-1);target=PositionLayout.Hit(r,draft,preferredCaretX.Value,r.Top+p.Lines[row].Baseline-r.Baseline+r.LineHeight/2).Index;}
  else return false;
  if(shift&&editor.Selection.IsEmpty)positionAnchor=current;positionCaretRow=row;
  if(shift)editor.Selection.Select(Position(positionAnchor),Position(target));else editor.Selection.Select(Position(target),Position(target));UpdatePositionedSelection();ScheduleAudit();return true;
 }
 void BindPositionNavigation()
 {
  foreach(var (command,key,extend) in new[]{(EditingCommands.MoveDownByLine,Key.Down,false),(EditingCommands.MoveUpByLine,Key.Up,false),(EditingCommands.MoveToLineStart,Key.Home,false),(EditingCommands.MoveToLineEnd,Key.End,false),(EditingCommands.SelectDownByLine,Key.Down,true),(EditingCommands.SelectUpByLine,Key.Up,true),(EditingCommands.SelectToLineStart,Key.Home,true),(EditingCommands.SelectToLineEnd,Key.End,true)})
   editor.CommandBindings.Add(new System.Windows.Input.CommandBinding(command,(s,e)=>{e.Handled=NavigatePosition(key,extend);},(s,e)=>{if(active&&info?.Region?.Positioned!=null&&ParagraphLayout.Plan(info.Region,draft).Positioned?.Lines.Length>1){e.CanExecute=true;e.Handled=true;}}));
 }
'''+s[pos:];p.write_text(s,encoding='utf-8',newline='\n')
p=Path('phase4c2/App/EditorWindow.cs');s=p.read_text(encoding='utf-8').replace('InitializeSessionEditing(root);','InitializeSessionEditing(root);BindPositionNavigation();').replace('   if(Keyboard.Modifiers.HasFlag(ModifierKeys.Control))','   if(!Keyboard.Modifiers.HasFlag(ModifierKeys.Control)&&NavigatePosition(e.Key,Keyboard.Modifiers.HasFlag(ModifierKeys.Shift))){e.Handled=true;return;}\n   if(Keyboard.Modifiers.HasFlag(ModifierKeys.Control))',1)
s=s.replace('bool positioned=active&&r.Positioned!=null&&ParagraphLayout.Plan(r,draft).Safe;','bool positioned=active&&r.Positioned!=null&&ParagraphLayout.Plan(r,draft).Positioned!=null;')
s=s.replace('session.Change(ActiveKey,draft,caret);','positionCaretRow=null;preferredCaretX=null;session.Change(ActiveKey,draft,caret);')
s=s.replace('if(info?.Region is not Region r)return;active=true;','if(info?.Region is not Region r)return;positionCaretRow=null;preferredCaretX=null;active=true;')
p.write_text(s,encoding='utf-8',newline='\n')
p=Path('phase4c2/App/SessionEditing.cs');s=p.read_text(encoding='utf-8').replace('r.Positioned!=null&&layout.Safe','r.Positioned!=null&&layout.Positioned!=null');p.write_text(s,encoding='utf-8',newline='\n')
