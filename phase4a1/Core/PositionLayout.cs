namespace PdfPrototype;

// Pointer-free, source-hash-bound observations. Drafts never mutate these records.
public sealed record PositionedSource(Glyph[] OriginalGlyphs, float[] RelativePositions,
    string Strategy, string MappingEvidence, PageObjectObservation[] ProtectedObjects)
{ public int[] CoexistingWhitespace {get;init;}=[]; }

public static class PositionLayout
{
    public static Layout Plan(Region r,string text)
    {
        string reason="";
        var issues=new List<CharacterCompatibility>();
        foreach(char c in text.Distinct())
        {
            if(c<32||c>126)issues.Add(new(c,"UnsupportedCharacter","POSITION_ASCII_ONLY",null,-1));
            else if(r.Advances[c-32]<0)issues.Add(r.Characters[c-32]);
        }
        if(issues.Count>0)reason="The original PDF font cannot safely display one of these characters.";
        else if(text.Length!=r.OriginalText.Length)reason="This line needs the original number of characters. Longer or shorter text needs spacing or wrapping this version cannot preserve.";
        else for(int i=0;i<text.Length;i++)
        {
            if(text[i]!=r.OriginalText[i]&&r.Advances[text[i]-32]>r.Advances[r.OriginalText[i]-32]+.001)
            {reason="A replacement character is wider than its original space. Nearby letters must stay in place.";break;}
        }
        var b=r.ObservedBounds!;
        return new([text],r.LineHeight,reason.Length==0,reason.Length==0?"Original letter positions retained; checking the PDF candidate.":reason+" Your changes have been kept; shorten, replace or undo before saving.",[b]){GlyphIssues=issues.ToArray(),ReasonCodes=reason.Length==0?[]:issues.Count>0?["POSITION_CHARACTER_MAPPING_UNSUPPORTED"]:text.Length!=r.OriginalText.Length?["POSITION_CHARACTER_COUNT_CHANGED"]:["POSITION_REPLACEMENT_ADVANCE_TOO_WIDE"]};
    }
}

public sealed partial class PdfEngine
{
    const string PositionBinaryHash="bede3932ce96a2e1ed9a7e6cae71aec8914efd2907d37ab44b1b81f9c8a6d04e";
    static int[] ObserveNonPaintingSpaces(IntPtr page)
    {
        var result=new List<int>();var objects=Objects(page);var tp=N.FPDFText_LoadPage(page);
        byte[]? baseline=null;
        try
        {
            for(int i=0;i<objects.Length;i++)
            {
                var o=objects[i];if(N.FPDFPageObj_GetType(o)!=1||N.FPDFTextObj_GetTextRenderMode(o)!=0)continue;
                string text=N.Text(o,tp);if(text.Any(c=>c!=' '))continue;
                N.FPDFPageObj_GetFillColor(o,out var r,out var g,out var b,out var a);
                if(a!=255||N.FPDFPageObj_HasTransparency(o)!=0)continue;
                // Coexistence evidence, never ownership: separately retained text/semantics.
                // PDFium may omit standalone space extraction. Empty extraction is not
                // proof of whitespace semantics: require zero extent AND no page paint.
                // Retain this object verbatim in the candidate, never absorb or delete it.
                var bounds=Bounds(o,N.FPDF_GetPageHeight(page));if(bounds.Width!=0||bounds.Height!=0)continue;
                baseline??=Pixels(page,2,out _,out _);
                try
                {
                    N.Check(N.FPDFPageObj_SetFillColor(o,r,g,b,0),"test space paint");
                    if(baseline.SequenceEqual(Pixels(page,2,out _,out _)))result.Add(i);
                }
                finally{N.Check(N.FPDFPageObj_SetFillColor(o,r,g,b,a),"restore space paint");}
            }
        }
        finally{N.FPDFText_ClosePage(tp);}
        return result.ToArray();
    }
    static bool TryPositioned(IntPtr document,IntPtr page,IntPtr o,Region r,N.Matrix m,List<string> reasons)
    {
        if(!reasons.Contains("NON_NATURAL_GLYPH_SPACING")&&!reasons.Contains("INITIAL_OBJECT_RECONSTRUCTION_DIFFERS"))return false;
        if(reasons.Any(x=>x!="NON_NATURAL_GLYPH_SPACING"&&x!="INITIAL_OBJECT_RECONSTRUCTION_DIFFERS"))return false;
        var gs=r.Glyphs;
        if(gs.Length<2||gs.Length!=r.OriginalText.Length||Math.Abs(gs[0].OriginX-r.X)>.01||gs.Any(g=>Math.Abs(g.Baseline-r.Baseline)>.01))return false;
        if(gs.Zip(gs.Skip(1)).Any(p=>p.Second.OriginX<=p.First.OriginX))return false;
        // Additional position-path guard: PDF width rounding can make readers
        // disagree despite PDFium's own exact-origin roundtrip (ReportLab case).
        var font=N.FPDFTextObj_GetFont(o);
        foreach(char c in r.Characters.Where(c=>c.Advance>=0).Select(c=>(char)c.Unicode))
            if(N.FPDFFont_GetGlyphWidth(font,c,(float)r.FontSize,out var width)==0||Math.Abs(width-r.Advances[c-32])>.01)
            {reasons.Add("POSITION_FONT_METRIC_ROUNDING_UNSUPPORTED");return false;}
        if(Wire.Hash(Path.Combine(AppContext.BaseDirectory,"pdfium.dll"))!=PositionBinaryHash)return false;
        float[] positions=gs.Skip(1).Select(g=>(float)(g.OriginX-r.X)).ToArray();
        if(!OriginalReconstructionMatches(document,page,o,r.OriginalText,m,r.R,r.G,r.B,positions))return false;
        r.Positioned=new(gs.ToArray(),positions,"FixedOriginsEqualOrNarrowerSubstitution",
            "Unicode reverse mapping, original embedded cmap GID, outline, width, roundtrip and exact positioned object bitmap verified; no raw codes guessed.",[]);
        r.Width=Math.Max(.01,r.ObservedBounds!.Right-r.X);
        reasons.RemoveAll(x=>x=="NON_NATURAL_GLYPH_SPACING"||x=="INITIAL_OBJECT_RECONSTRUCTION_DIFFERS");
        r.Observed=r.Observed.Append("POSITIONED_ORIGINAL_BITMAP_IDENTICAL_144DPI").ToArray();
        return true;
    }
}
