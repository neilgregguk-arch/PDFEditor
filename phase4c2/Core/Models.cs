using System.Text.Json;
using System.Text.Json.Serialization;
namespace PdfPrototype;
public static class Wire
{
    public static readonly JsonSerializerOptions Options = new() { PropertyNameCaseInsensitive=true, WriteIndented=false, NumberHandling=JsonNumberHandling.AllowReadingFromString };
    public static T Read<T>(string text) => JsonSerializer.Deserialize<T>(text, Options)!;
    public static string Write(object value) => JsonSerializer.Serialize(value, Options);
    public static string Hash(string path) => Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(path))).ToLowerInvariant();
}
public record Box(double X, double Y, double Width, double Height)
{
    public double Right=>X+Width; public double Bottom=>Y+Height;
    public bool Contains(double x,double y)=>x>=X&&x<=Right&&y>=Y&&y<=Bottom;
    public bool Intersects(Box b,double pad=0)=>X-pad<b.Right&&Right+pad>b.X&&Y-pad<b.Bottom&&Bottom+pad>b.Y;
}
public record Region
{
    public PositionedSource? Positioned {get;set;}
    public string SourceIdentity=>DocumentSession.Identity(this);
    public string StructuralEligibility=>Eligibility;
    public string ProposedTextEligibility=>"DependsOnDraft";
    public CharacterCompatibility[] Characters {get;set;}=[];
    public string Id {get;set;}="";
    public string Eligibility {get;set;}="Editable";
    public string[] Reasons {get;set;}=[];
    public string[] Observed {get;set;}=[];
    public string[] Inferred {get;set;}=[];
    public Box? ObservedBounds {get;set;}
    public Glyph[] Glyphs {get;set;}=[];
    public string SourceHash {get;set;}="";
    public string Name {get;set;}="";
    public int Page {get;set;}
    public int[] Objects {get;set;}=[];
    public string[] OriginalLines {get;set;}=[];
    public double X {get;set;}=60;
    public double Baseline {get;set;}=140; // Top-down PDF points.
    public double Width {get;set;}=420;
    public double SafeBottom {get;set;}=650;
    public double FontSize {get;set;}=12;
    public double LineHeight {get;set;}=18;
    public double Ascent {get;set;}
    public string FontHash {get;set;}="";
    public string FontFile {get;set;}="PrototypeSansAscii.ttf";
    public uint R {get;set;}=35; public uint G {get;set;}=56; public uint B {get;set;}=72;
    public double[] Advances {get;set;}=[];
    public string OriginalText=>string.Join("\n",OriginalLines);
    public double Top=>Baseline-Ascent;
}
public record Glyph(int Index,string Text,Box Bounds,double OriginX,double Baseline,int ObjectIndex);
public record CharacterCompatibility(int Unicode,string State,string Reason,ushort? GlyphId,double Advance);
public record PageObjectObservation(int Index,int Type,Box Bounds);
public record DocumentInfo(string Path,string Hash,int PageCount,int Page,double Width,double Height,string Image,string? CleanImage,Region? Region,Glyph[] Glyphs,string Diagnostic)
{ public Region[] Regions {get;init;}=[]; public PageObjectObservation[] PageObjects {get;init;}=[]; }
public record EditRequest
{
    public RegionChange[]? Changes {get;set;}
    public string Command {get;set;}="inspect";
    public long Revision {get;set;}
    public string Source {get;set;}="";
    public string ExpectedHash {get;set;}="";
    public string Work {get;set;}="";
    public string Destination {get;set;}="";
    public int Page {get;set;}
    public string RegionId {get;set;}="";
    public string Text {get;set;}="";
}
public record Layout(string[] Lines,double Height,bool Safe,string Diagnostic,Box[] LineBoxes)
{ public PositionedDraft? Positioned {get;init;}
 public string[] ReasonCodes {get;init;}=[];public CharacterCompatibility[] GlyphIssues {get;init;}=[];public string ProposedTextEligibility=>GlyphIssues.Length==0?"Supported":"Unsupported"; }
public record EditResult(long Revision,bool Safe,string Diagnostic,string? Image,object? Verification,string? Destination=null)
{ public RegionValidation[] Regions {get;init;}=[];public string ProposedTextEligibility {get;init;}="NotAssessed";public string ExportEligibility=>Safe?"Verified":"Blocked";public CharacterCompatibility[] GlyphIssues {get;init;}=[]; }
public record Envelope(long Revision,bool Ok,JsonElement? Data,string? Error);
public static class ParagraphLayout
{
    // Deliberately simple ASCII region model. No shaping/kerning/reflow claim.
    public static Layout Plan(Region r,string draft)
    {
        if(r.Positioned!=null)return PositionLayout.Plan(r,draft);
        draft=draft.Replace("\r\n","\n").Replace('\r','\n');
        var badCharacters=draft.Where(c=>c!='\n'&&(c<32||c>126)).Take(1).ToArray();char bad=badCharacters.FirstOrDefault();
        if(badCharacters.Length>0) return new([],0,false,$"This editor cannot safely save U+{(int)bad:X4} with the original PDF font and text layout. Your changes have been kept; you can keep typing or undo.",[]){GlyphIssues=[new(bad,"UnsupportedShapingOrCharacterRange","UNSUPPORTED_TEXT_MODEL",null,-1)]};
        var missing=draft.FirstOrDefault(c=>c!='\n'&&(r.Advances.Length!=95||r.Advances[c-32]<0));
        if(missing!='\0')
        {
            var detail=r.Characters.FirstOrDefault(c=>c.Unicode==missing)??new(missing,"Unavailable","ORIGINAL_FONT_MAPPING_UNAVAILABLE",null,-1);
            string explanation=detail.State=="AbsentFromEmbeddedSubset"?"The embedded PDF font has no usable glyph for this character":detail.State=="FontPresentEncodingUnavailable"?"The original PDF cannot safely encode this character with its existing font":"The original PDF cannot reliably map this character to the correct glyph";
            return new([],0,false,$"{explanation} (U+{(int)missing:X4}). Your changes have been kept, but this version cannot be saved yet.",[]){GlyphIssues=[detail]};
        }
        if(draft.Length>16000) return new([],0,false,"Draft retained. This prototype exports at most 16,000 characters per region.",[]);
        var lines=new List<string>();
        foreach(var paragraph in draft.Split('\n'))
        {
            if(paragraph.Length==0){lines.Add("");continue;}
            string remaining=paragraph;
            while(remaining.Length>0)
            {
                double w=0; int take=0,lastSpace=-1;
                while(take<remaining.Length && w+r.Advances[remaining[take]-32]<=r.Width+.001)
                {w+=r.Advances[remaining[take]-32]; if(remaining[take]==' ')lastSpace=take; take++;}
                if(take==0)return new([],0,false,"One glyph exceeds the owned paragraph width. Draft retained.",[]);
                if(take<remaining.Length&&lastSpace>0)take=lastSpace+1;
                lines.Add(remaining[..take]); remaining=remaining[take..];
            }
        }
        double height=Math.Max(1,lines.Count)*r.LineHeight;
        var boxes=lines.Select((line,i)=>new Box(r.X,r.Top+i*r.LineHeight,Width(r,line),r.LineHeight)).ToArray();
        bool safe=r.Top+height<=r.SafeBottom;
        return new(lines.ToArray(),height,safe,safe?"Draft layout fits the owned paragraph region.":"Unsafe expansion: draft reaches protected content or the safe page boundary. All text is retained; shorten the draft or undo before exporting.",boxes);
    }
    public static double Width(Region r,string text)=>text.Sum(c=>c>=32&&c<=126?r.Advances[c-32]:0);
    public static (int Index,double X,int Line) Hit(Region r,string text,double x,double y)
    {
        if(r.Positioned!=null)return PositionLayout.Hit(r,text,x,y);

        var p=Plan(r,text); var lines=p.Lines.Length>0?p.Lines:[text];
        int row=Math.Clamp((int)Math.Floor((y-r.Top)/r.LineHeight),0,lines.Length-1),index=lines.Take(row).Sum(l=>l.Length);
        // Explicit newlines are absent from wrapped lines; account for them using sequential matching.
        int cursor=0;
        for(int j=0;j<row;j++){cursor+=lines[j].Length;if(cursor<text.Length&&text[cursor]=='\n')cursor++;}
        index=cursor; double advance=r.X;
        foreach(char c in lines[row]){double w=c>=32&&c<=126?r.Advances[c-32]:0;if(x<advance+w/2)break;advance+=w;index++;}
        return (Math.Min(index,text.Length),advance,row);
    }
}
