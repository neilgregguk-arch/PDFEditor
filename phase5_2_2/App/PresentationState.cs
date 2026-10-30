using System.Windows;
using System.Windows.Controls;
using System.Windows.Automation;
namespace PdfPrototype;
public sealed partial class EditorWindow
{
 sealed record DraftEvidence(string Source,string Identity,string Text,long Revision,string State,string Message);
 readonly Dictionary<string,DraftEvidence> currentEvidence=[];
 DocumentSession? evidenceOwner;
 void EnsureEvidenceOwner(){if(evidenceOwner!=session){currentEvidence.Clear();evidenceOwner=session;}}
 DraftEvidence? CurrentEvidence(Region r,string text)
 {
  EnsureEvidenceOwner();string key=DocumentSession.Key(r.Page,r.Id);
  return session!=null&&currentEvidence.TryGetValue(key,out var e)&&e.Source==session.SourceHash&&session.Regions.TryGetValue(key,out var state)&&e.Identity==state.Identity&&e.Text==text?e:null;
 }
 string PresentationState(Region r,string text,Layout plan)
 {
  if(session?.Regions.TryGetValue(DocumentSession.Key(r.Page,r.Id),out var state)==true&&!state.Compatible)return "Rejected";
  if(text==r.OriginalText)return "Unchanged";
  if(!plan.Safe)return "Rejected";
  var e=CurrentEvidence(r,text);
  if(e==null)return "Pending";
  return e.Revision!=session!.Revision?"Stale":e.State;
 }
 string PresentationSummary()
 {
  if(session==null||session.Modified.Length==0)return "No unsaved text changes.";
  var groups=session.Modified.GroupBy(s=>PresentationState(s.Original,s.Text,ParagraphLayout.Plan(s.Original,s.Text)));
  return $"{session.Modified.Length} text area(s) changed · "+string.Join(" · ",groups.Select(g=>$"{g.Count()} {g.Key.ToLowerInvariant()}"))+(session.VerifiedRevision==session.Revision?" · ready to export":" · complete current verification required before export");
 }
 void RecordIncompleteValidation()
 {
  if(session==null)return;EnsureEvidenceOwner();
  foreach(var s in session.Modified)
  {
   // A failed combined worker call cannot identify a locally fitting region as
   // a geometry failure. Existing evidence becomes stale; no approval survives.
   currentEvidence.Remove(s.Key);s.Validation=!s.Compatible||!ParagraphLayout.Plan(s.Original,s.Text).Safe?"Blocked":"Pending";s.Message="Incomplete combined validation; retry required.";
  }
 }
 readonly ComboBox regionPicker=new(){MinWidth=230,MaxWidth=510,Margin=new Thickness(8,0,0,0),DisplayMemberPath="Label"};
 sealed record RegionChoice(string Id,string Identity,string Label);
 bool refreshingRegionPicker;
 void InitializeRegionPicker(DockPanel root)
 {
  var row=new StackPanel{Orientation=Orientation.Horizontal,Margin=new Thickness(20,0,20,10)};
  row.Children.Add(new TextBlock{Text="Text area",VerticalAlignment=VerticalAlignment.Center});row.Children.Add(regionPicker);
  DockPanel.SetDock(row,Dock.Top);root.Children.Insert(2,row);AutomationProperties.SetAutomationId(regionPicker,"SourceRegionPicker");
  regionPicker.ToolTip="Return to any editable source area, including overlapping retained previews. This does not change PDF ownership.";
  regionPicker.DropDownClosed+=(s,e)=>
  {
   if(opening||active||regionPicker.SelectedItem is not RegionChoice choice||info?.Region?.Id!=choice.Id)return;
   var state=session!.Regions[ActiveKey];int start=state.Caret,end=state.SelectionEnd;ActivateAt(Math.Clamp(start,0,draft.Length));editor.Selection.Select(Position(Math.Clamp(start,0,draft.Length)),Position(Math.Clamp(end,0,draft.Length)));
  };
  regionPicker.SelectionChanged+=async(s,e)=>
  {
   if(refreshingRegionPicker||opening||regionPicker.SelectedItem is not RegionChoice choice||info==null)return;
   var target=info.Regions.FirstOrDefault(r=>r.Id==choice.Id&&r.SourceIdentity==choice.Identity&&r.Eligibility=="Editable");if(target==null)return;
   string source=info.Path;int pageIndex=info.Page;
   await Open(source,pageIndex,target.Id);
   if(info?.Path!=source||info.Page!=pageIndex||info.Region?.Id!=target.Id)return;
   var state=session!.Regions[ActiveKey];int start=state.Caret,end=state.SelectionEnd;ActivateAt(Math.Clamp(start,0,draft.Length));editor.Selection.Select(Position(Math.Clamp(start,0,draft.Length)),Position(Math.Clamp(end,0,draft.Length)));
  };
 }
 void RefreshRegionPicker()
 {
  refreshingRegionPicker=true;
  try
  {
   var choices=(info?.Regions??[]).Where(r=>r.Eligibility=="Editable").OrderBy(r=>r.ObservedBounds?.Y??r.Top).ThenBy(r=>r.Id,StringComparer.Ordinal).Select((r,i)=>new RegionChoice(r.Id,r.SourceIdentity,$"{i+1}. {r.OriginalText[..Math.Min(48,r.OriginalText.Length)]}" )).ToArray();
   regionPicker.ItemsSource=choices;regionPicker.SelectedItem=choices.FirstOrDefault(c=>c.Id==info?.Region?.Id);regionPicker.IsEnabled=choices.Length>0;
  }
  finally{refreshingRegionPicker=false;}
 }
}
