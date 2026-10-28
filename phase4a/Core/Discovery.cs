using System.Runtime.InteropServices;
using System.Windows.Media;
namespace PdfPrototype;

public sealed partial class PdfEngine
{
    // Only pointer-free observations are cached. Every commit opens and reanalyses the source.
    readonly Dictionary<string,Region[]> discoveries=new();
    Region? SelectDiscovered(string source,IntPtr document,IntPtr page,int index,string work,string id,out Region[] regions,out string diagnostic)
    {
        string fingerprint=Wire.Hash(source),key=fingerprint+":"+index;
        if(!discoveries.TryGetValue(key,out regions!))
        {
            regions=Discover(document,page,index,fingerprint,work);
            if(discoveries.Count>=8)discoveries.Clear();
            discoveries[key]=regions;
        }
        // Cached font files may have been removed externally; fail closed.
        var selected=id.Length>0?regions.FirstOrDefault(r=>r.Id==id&&r.Eligibility=="Editable"):regions.FirstOrDefault(r=>r.Eligibility=="Editable");
        if(selected!=null&&(!File.Exists(selected.FontFile)||Wire.Hash(selected.FontFile)!=selected.FontHash))selected=null;
        diagnostic=$"Page analysed · {regions.Count(r=>r.Eligibility=="Editable")} editable, {regions.Count(r=>r.Eligibility=="Limited")} limited, {regions.Count(r=>r.Eligibility=="View Only")} view only. Click supported text. Boundaries are conservative geometric inferences.";
        if(id.Length>0&&selected==null)diagnostic="Region unavailable for editing. "+string.Join(", ",regions.FirstOrDefault(r=>r.Id==id)?.Reasons??["REGION_NOT_FOUND"]);
        return selected;
    }
    Region[] Discover(IntPtr document,IntPtr page,int pageIndex,string fingerprint,string work)
    {
        double w=N.FPDF_GetPageWidth(page),h=N.FPDF_GetPageHeight(page);
        var objects=Objects(page);var bounds=objects.Select(o=>Bounds(o,h)).ToArray();
        var candidates=new List<Region>();
        var tp=N.FPDFText_LoadPage(page);
        bool pageUnsupported=N.FPDF_GetSignatureCount(document)>0||N.FPDF_GetFormType(document)!=0||N.FPDF_GetSecurityHandlerRevision(document)!=-1||N.FPDFPage_GetRotation(page)!=0||N.FPDFPage_GetAnnotCount(page)>0||objects.Any(o=>N.FPDFPageObj_GetType(o)==5);
        string fontDir=Path.Combine(work,"fonts");Directory.CreateDirectory(fontDir);
        using var fonts=new FontAnalysisScope();
        try
        {
            // Index once; extraction order is used only *within* one PDF text object.
            var glyphMap=new Dictionary<IntPtr,List<Glyph>>();
            for(int i=0;i<N.FPDFText_CountChars(tp);i++)
            {
                var pointer=N.FPDFText_GetTextObject(tp,i);if(pointer==IntPtr.Zero)continue;
                uint code=N.FPDFText_GetUnicode(tp,i);if(code<32)continue;
                if(!glyphMap.TryGetValue(pointer,out var list))glyphMap[pointer]=list=[];
                if(N.FPDFText_GetCharBox(tp,i,out var l,out var right,out var b,out var t)==0||N.FPDFText_GetCharOrigin(tp,i,out var x,out var y)==0)continue;
                list.Add(new(list.Count,char.ConvertFromUtf32((int)Math.Min(code,0x10ffff)),new(l,h-t,right-l,t-b),x,h-y,Array.IndexOf(objects,pointer)));
            }
            for(int i=0;i<objects.Length;i++)
            {
                var o=objects[i];if(N.FPDFPageObj_GetType(o)!=1)continue;
                string text=N.Text(o,tp);if(string.IsNullOrWhiteSpace(text))continue;
                N.FPDFPageObj_GetMatrix(o,out var m);N.FPDFTextObj_GetFontSize(o,out var size);
                N.FPDFPageObj_GetFillColor(o,out var red,out var green,out var blue,out var alpha);
                var glyphs=glyphMap.GetValueOrDefault(o,[]).ToArray();
                var r=new Region{Id=$"p{pageIndex}-o{i}",Name=$"Text object {i}",SourceHash=fingerprint,Page=pageIndex,Objects=[i],OriginalLines=[text],X=m.E,Baseline=h-m.F,FontSize=size,R=red,G=green,B=blue,ObservedBounds=bounds[i],Glyphs=glyphs,LineHeight=size*1.5,Ascent=size,Advances=Enumerable.Repeat(-1.0,95).ToArray(),Eligibility="Editable",
                    Observed=[$"object-index:{i}",$"matrix:{m.A},{m.B},{m.C},{m.D},{m.E},{m.F}",$"font-size:{size}",$"rgba:{red},{green},{blue},{alpha}",$"glyph-count:{glyphs.Length}"],Inferred=["One complete text object is a candidate visual line; paragraph semantics are absent."]};
                var reasons=new List<string>();
                if(pageUnsupported)reasons.Add("DOCUMENT_OR_PAGE_SIGNATURE_ENCRYPTION_ROTATION_ANNOTATION_OR_FORM");
                if(Math.Abs(m.A-1)>.0001||Math.Abs(m.D-1)>.0001||Math.Abs(m.B)>.0001||Math.Abs(m.C)>.0001)reasons.Add("UNSUPPORTED_TRANSFORM");
                if(size<6||size>48||alpha!=255||N.FPDFPageObj_HasTransparency(o)!=0||N.FPDFTextObj_GetTextRenderMode(o)!=0)reasons.Add("UNSUPPORTED_PAINT_OR_SIZE");
                var clip=N.FPDFPageObj_GetClipPath(o);if(clip!=IntPtr.Zero&&N.FPDFClipPath_CountPaths(clip)>0)reasons.Add("CLIPPED_TEXT");
                if(text.Any(c=>c<32||c>126))reasons.Add("NON_ASCII_OR_COMPLEX_TEXT");
                if(string.Concat(glyphs.Select(g=>g.Text))!=text)reasons.Add("INCOMPLETE_GLYPH_OWNERSHIP");
                try
                {
                    var font=N.FPDFTextObj_GetFont(o);var analysis=fonts.Analyse(document,page,font,work);
                    r.FontHash=analysis.Hash;r.FontFile=analysis.File;var face=analysis.Face;
                    r.Characters=analysis.Characters.Select(c=>c with{Advance=c.Advance<0?-1:c.Advance*size}).ToArray();
                    r.Ascent=face.Baseline*size;r.Advances=r.Characters.Select(c=>c.Advance).ToArray();
                    bool initialMapped=!text.Any(c=>c<32||c>126||r.Advances[c-32]<0);
                    if(!initialMapped)reasons.Add("INITIAL_TEXT_MAPPING_OR_GLYPH_UNAVAILABLE");
                    if(!OriginalReconstructionMatches(document,page,o,text,m,red,green,blue))reasons.Add("INITIAL_OBJECT_RECONSTRUCTION_DIFFERS");
                    double expected=r.X;
                    if(!initialMapped)reasons.Add("GLYPH_SPACING_UNASSESSABLE");
                    else foreach(var g in glyphs)
                    {
                        int gi=Array.IndexOf(glyphs,g);
                        double local=gi==0?g.OriginX-r.X:g.OriginX-glyphs[gi-1].OriginX-(glyphs[gi-1].Text.Length==1&&glyphs[gi-1].Text[0]>=32&&glyphs[gi-1].Text[0]<=126?Math.Max(0,r.Advances[glyphs[gi-1].Text[0]-32]):0);
                        if(Math.Abs(g.Baseline-r.Baseline)>.15||Math.Abs(local)>.05||Math.Abs(g.OriginX-expected)>1){reasons.Add("NON_NATURAL_GLYPH_SPACING");break;}
                        expected+=g.Text.Length==1&&g.Text[0]>=32&&g.Text[0]<=126?Math.Max(0,r.Advances[g.Text[0]-32]):0;
                    }
                    r.Observed=r.Observed.Concat([$"embedded-font-sha256:{r.FontHash}",$"family:{face.FamilyNames.Values.FirstOrDefault()}",$"style:{face.Style}",$"weight:{face.Weight}",$"verified-ascii-glyphs:{r.Advances.Count(a=>a>=0)}"]).ToArray();
                }
                catch(Exception ex){reasons.Add(ex.Message=="FONT_NOT_EMBEDDED"?ex.Message:"UNUSABLE_EMBEDDED_FONT");r.Observed=r.Observed.Append("font-diagnostic:"+ex.ToString()).ToArray();}
                r.Width=Math.Max(1,w-r.X-Math.Max(20,r.X));
                if(r.X<0||r.Top<0||bounds[i].Right>w-10||bounds[i].Bottom>h-20||bounds[i].Width>r.Width+1)reasons.Add("PAGE_BOUNDARY_OR_METRICS");
                r.Reasons=reasons.Distinct().ToArray();if(reasons.Count>0)r.Eligibility="View Only";
                candidates.Add(r);
            }
        }
        finally{N.FPDFText_ClosePage(tp);}
        // Competing blocks on the same baseline are columns, labels, or fragmented lines.
        foreach(var a in candidates)
        {
            if(candidates.Any(b=>b!=a&&Math.Abs(a.Baseline-b.Baseline)<Math.Max(a.FontSize,b.FontSize)*.6))Limit(a,"AMBIGUOUS_COLUMNS_LABELS_OR_FRAGMENTED_LINE");
            if(objects.Select((o,i)=>(o,i)).Any(v=>N.FPDFPageObj_GetType(v.o)!=1&&bounds[v.i].Intersects(a.ObservedBounds!,2)))Limit(a,"GRAPHIC_IMAGE_OR_TABLE_INTERSECTION");
        }
        var ordered=candidates.OrderBy(r=>r.Baseline).ThenBy(r=>r.X).ToList();var grouped=new List<Region>();
        foreach(var next in ordered)
        {
            var prior=grouped.LastOrDefault();
            bool matching=prior!=null&&prior.Eligibility=="Editable"&&next.Eligibility=="Editable"&&prior.FontHash==next.FontHash&&prior.Characters.SequenceEqual(next.Characters)&&Math.Abs(prior.FontSize-next.FontSize)<.001&&prior.R==next.R&&prior.G==next.G&&prior.B==next.B&&Math.Abs(prior.X-next.X)<.25;
            double gap=prior==null?0:next.Baseline-(prior.Baseline+(prior.OriginalLines.Length-1)*prior.LineHeight);
            if(matching&&gap>=next.FontSize*1.05&&gap<=next.FontSize*1.65)
            {
                if(ParagraphLayout.Width(prior!,prior!.OriginalLines[^1])>=prior.Width*.7&&(prior.OriginalLines.Length==1||Math.Abs(gap-prior.LineHeight)<.25))
                {
                    int offset=prior.OriginalText.Length+1;
                    prior.Glyphs=prior.Glyphs.Concat(next.Glyphs.Select(g=>g with{Index=g.Index+offset})).ToArray();
                    prior.Objects=prior.Objects.Concat(next.Objects).ToArray();prior.OriginalLines=prior.OriginalLines.Concat(next.OriginalLines).ToArray();prior.LineHeight=gap;
                    prior.Observed=prior.Observed.Concat(next.Observed).ToArray();
                    prior.ObservedBounds=new(prior.ObservedBounds!.X,prior.ObservedBounds.Y,Math.Max(prior.ObservedBounds.Width,next.ObservedBounds!.Width),next.ObservedBounds.Bottom-prior.ObservedBounds.Y);
                    prior.Inferred=["Paragraph: common left edge, font, size, colour, natural glyph spacing, stable leading, preceding line occupies at least 70% of inferred width."];
                    continue;
                }
                Limit(prior!,"AMBIGUOUS_SHORT_LINE_PARAGRAPH_BOUNDARY");Limit(next,"AMBIGUOUS_SHORT_LINE_PARAGRAPH_BOUNDARY");
            }
            grouped.Add(next);
        }
        foreach(var r in grouped)
        {
            var excluded=r.Objects.ToHashSet();r.SafeBottom=h-20;
            foreach(var entry in bounds.Select((box,i)=>(box,i)).Where(v=>!excluded.Contains(v.i)))
            {
                var b=entry.box;
                if(b.Y>r.Baseline&&b.X<r.X+r.Width&&b.Right>r.X)r.SafeBottom=Math.Min(r.SafeBottom,b.Y-3);
                if(b.Intersects(new(r.X,r.Top,r.Width,r.OriginalLines.Length*r.LineHeight),.5))Limit(r,"OWNED_SPACE_INTERSECTS_NEIGHBOUR");
            }
            if(r.Top+r.OriginalLines.Length*r.LineHeight>r.SafeBottom)Limit(r,"INSUFFICIENT_VERTICAL_SPACE");
            r.Inferred=r.Inferred.Concat([$"width:{r.Width:F3}; symmetric margin capped by page boundary",$"safe-bottom:{r.SafeBottom:F3}; nearest overlapping neighbour minus 3pt"]).ToArray();
            if(r.Eligibility=="Editable")r.Reasons=["COMPLETE_OBJECT_OWNERSHIP","ORIGINAL_CHARACTER_OUTLINES_WIDTHS_AND_ENCODING_VERIFIED","NATURAL_HORIZONTAL_GLYPH_GEOMETRY","CONSERVATIVE_SPACE_AVAILABLE"];
        }
        return grouped.ToArray();
    }
    static void Limit(Region r,string reason){if(r.Eligibility=="Editable")r.Eligibility="Limited";r.Reasons=r.Reasons.Append(reason).Distinct().ToArray();}
}

