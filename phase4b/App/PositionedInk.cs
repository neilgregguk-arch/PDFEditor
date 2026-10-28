using System.Windows;
using System.Windows.Media;
using PdfPrototype;
namespace PdfPrototype;
// Visual text only; the existing RichTextBox continues to own input/history/selection.
sealed class PositionedInk : FrameworkElement
{
    Region? region; string text="";
    public PositionedInk(){IsHitTestVisible=false;}
    public void Set(Region r,string draft){region=r;text=draft;Width=r.Width*4/3+10;Height=r.LineHeight*4/3+12;InvalidateVisual();}
    protected override void OnRender(DrawingContext dc)
    {
        if(region is not Region r||r.Positioned==null||text.Length!=r.Glyphs.Length)return;
        var face=new GlyphTypeface(new Uri(r.FontFile));
        if(text.Any(c=>!face.CharacterToGlyphMap.ContainsKey(c)))return;
        var gs=r.Positioned.OriginalGlyphs;
        for(int i=0;i<text.Length;i++)
        {
            ushort gid=face.CharacterToGlyphMap[text[i]];
            var run=new GlyphRun(face,0,false,r.FontSize*4/3,1,new ushort[]{gid},
                new Point((gs[i].OriginX-r.X)*4/3,r.Ascent*4/3),new double[]{face.AdvanceWidths[gid]*r.FontSize*4/3},null,null,null,null,null,null);
            dc.DrawGlyphRun(new SolidColorBrush(Color.FromRgb((byte)r.R,(byte)r.G,(byte)r.B)),run);
        }
    }
}
