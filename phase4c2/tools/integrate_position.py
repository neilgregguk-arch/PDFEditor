from pathlib import Path
p=Path('phase4c2/Core/DocumentTransaction.cs');s=p.read_text(encoding='utf-8')
s=s.replace('return new(r.X-2,r.Top-2,r.Width+4,bottom-r.Top+2);','double right=r.Positioned==null?r.X+r.Width:Math.Max(r.ObservedBounds!.Right,t.Layout.LineBoxes.Select(b=>b.Right).DefaultIfEmpty(r.X).Max());\n  return new(r.X-2,r.Top-2,right-r.X+4,bottom-r.Top+2);')
s=s.replace('r.Positioned.RelativePositions,(nuint)r.Positioned.RelativePositions.Length','t.Layout.Positioned!.RelativePositions,(nuint)t.Layout.Positioned.RelativePositions.Length')
s=s.replace('r.Positioned?.RelativePositions','t.Layout.Positioned?.RelativePositions')
s=s.replace('r.Positioned?.OriginalGlyphs[j].OriginX??x','t.Layout.Positioned?.Origins[j]??x')
start=s.index('     if(run.Text[j]==r.OriginalText[j]');end=s.index('\n    }\n    else if',start)
s=s[:start]+'''     var plan=t.Layout.Positioned!;var predicted=plan.InkBounds[j];
     if(run.Text[j]!=' '&&BoxShift(g.Bounds,predicted)>.01)throw new IOException("Proposed positioned glyph ink differs from saved glyph.");
     if(run.Glyphs.Where((other,k)=>k!=j&&run.Text[k]!=' '&&run.Text[j]!=' '&&!(plan.OriginalIndices[j]>=0&&plan.OriginalIndices[k]>=0&&plan.OriginalIndices[k]-plan.OriginalIndices[j]==k-j)).Any(other=>g.Bounds.Intersects(other.Bounds)))throw new IOException("Positioned edited join overlaps another letter.");'''+s[end:]
p.write_text(s,encoding='utf-8',newline='\n')
p=Path('phase4c2/Core/PdfEngine.cs');s=p.read_text(encoding='utf-8')
# All ordinary positioned single requests use the same verified document transaction.
needle='        if(region.Positioned!=null&&Wire.Hash'
s=s.replace(needle,'''        if(region.Positioned!=null&&req.Command!="reconstruct")return EditDocument(req with{Changes=[new(req.Page,region.Id,region.SourceIdentity,req.Text)]});
'''+needle,1)
p.write_text(s,encoding='utf-8',newline='\n')
# Ink layer uses the shared proposal even after length changes.
p=Path('phase4c2/App/PositionedInk.cs');s=p.read_text(encoding='utf-8').replace('Width=r.Width*4/3+10','Width=Math.Max(r.Width,PositionLayout.CaretX(r,draft,draft.Length)-r.X)*4/3+10').replace('||text.Length!=r.Glyphs.Length','')
s=s.replace('var gs=r.Positioned.OriginalGlyphs;','var gs=PositionLayout.Plan(r,text).Positioned;if(gs==null)return;').replace('(gs[i].OriginX-r.X)','(gs.Origins[i]-r.X)');p.write_text(s,encoding='utf-8',newline='\n')
# bounded proposal hit testing in one plan, rather than recalculating per glyph
p=Path('phase4c2/Core/Models.cs');s=p.read_text(encoding='utf-8');a=s.index('if(r.Positioned!=null){int n=0;');b=s.index('\n        var p=Plan(r,text);',a)
s=s[:a]+'''if(r.Positioned!=null){var model=Plan(r,text).Positioned;double x0=r.X;int n=0;for(int i=0;i<text.Length;i++){double a=model?.Origins[i]??x0,b=i+1<text.Length?(model?.Origins[i+1]??a+(text[i]>=32&&text[i]<=126?Math.Max(0,r.Advances[text[i]-32]):0)):a+(text[i]>=32&&text[i]<=126?Math.Max(0,r.Advances[text[i]-32]):0);if(x<(a+b)/2)return(i,a,0);x0=b;n++;}return(n,x0,0);}
'''+s[b:];p.write_text(s,encoding='utf-8',newline='\n')
