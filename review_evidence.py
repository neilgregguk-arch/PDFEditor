"""Make a static local evidence index and legible before/after/diff contact sheets."""
import html, json
from pathlib import Path
from PIL import Image, ImageDraw
import feasibility as f

s=json.loads((f.EVID/'summary.json').read_text())
explanations={
'e1_operand':'Direct operand change: same font resource, colour, size and position; equal advance.',
'e1_pdfium':'Existing PDFium text object changed and regenerated; resource inventory is reorganized.',
'e1_remove_reinsert':'Old content physically removed and new text inserted. This is reconstruction, not operand editing.',
'e2_overflow':'Deliberately unsafe expansion: no wrapping; intersects fixed neighbouring text.',
'e2_controlled_reflow':'Complete known paragraph replaced in a fixture-owned box; wraps without moving neighbours.',
'e2_rejected_expansion':'Width measurement refuses expansion in the original phrase region; unchanged candidate.',
'e3_bold':'Wider replacement shifts the following word. A valid PDF can still fail visual isolation.',
'e3_bold_compensated':'Known Helvetica-Bold advance difference compensated using TJ spacing; neighbour stays fixed.',
'e3_italic':'Font/style retained; small renderer-sensitive difference outside original region remains.',
'e3_table':'Equal-width numeric change preserves rules, other cells and nearby image.',
'e3_subset':'Reorders existing ASCII glyphs using original subset; font program unchanged.',
'e3_rejected_glyph':'Snowman glyph absent from subset cmap; no fallback font silently introduced.',
'e4_integrity':'Nonempty XMP, bookmarks, annotation, link, images and rotated/cropped page preserved.',
'e4_default_metadata':'Default pikepdf metadata fix rewrites XMP serialization; negative integrity example.',
'e5_mixed_edit':'Digital caption changed; full-page raster pixels and image placement preserved.',
'e5_scan_no_edit':'Raster-only page has no existing text objects; unchanged candidate.',
}
rows=[]; markdown=['# Saved experiment evidence','', 'Generated from `summary.json`. Before/after/diff PNGs are 144 DPI. Blue is change inside the allowed region; red is change outside it. Each renderer is compared against its own original rendering.','', '| Experiment | Outside pixels (MuPDF / PDFium / Poppler) | Finding |','|---|---:|---|']
for r in s['experiments']:
    name=r['id']; metrics=' / '.join(str(sum(p['outside_edit_pixels'] for p in r['visual'][e])) if e in r['visual'] else 'unavailable' for e in ['mupdf','pdfium','poppler'])
    markdown.append(f"| [{name}]({name}.json) | {metrics} | {explanations[name]} |")
    rows.append(f'<tr><td>{html.escape(name)}</td><td><a href="../output/pdf/originals/{r["source"]}">original PDF</a> &middot; <a href="../{r["output"]}">candidate PDF</a> &middot; <a href="{name}.json">metrics</a> &middot; <a href="diagnostics/{name}-after.json">diagnostics</a></td><td>{metrics}</td><td>{html.escape(explanations[name])}</td><td><a href="renders/{name}/poppler/p1-before.png">before</a> / <a href="renders/{name}/poppler/p1-after.png">after</a> / <a href="renders/{name}/poppler/p1-diff.png">diff</a></td></tr>')
    markdown.extend([])
for group in ['e1','e2','e3','e4','e5']:
    cases=[r for r in s['experiments'] if r['id'].startswith(group)]
    sheet=Image.new('RGB',(1440,len(cases)*260+42),'#edf1f4'); draw=ImageDraw.Draw(sheet)
    draw.text((18,10),f'{group.upper()} - before / after / difference (Poppler)',fill='#182733',font_size=19)
    for i,r in enumerate(cases):
        y=42+i*260; draw.text((15,y),r['id']+' | '+explanations[r['id']],fill='#182733',font_size=14)
        for j,kind in enumerate(['before','after','diff']):
            engine='poppler' if 'poppler' in r['visual'] else 'mupdf'
            im=Image.open(f.EVID/'renders'/r['id']/engine/f'p1-{kind}.png').convert('RGB')
            # Crop around relevant fixture content rather than shrinking a full page.
            box=(60,190,1000,255) if group=='e1' else ((60,150,1150,330) if group=='e2' else ((60,155,1150,810) if group in ['e3','e4'] else (60,120,1150,1530)))
            im=im.crop(box); im.thumbnail((460,210))
            sheet.paste(im,(15+j*475,y+30)); draw.text((15+j*475,y+244),kind,fill='#182733',font_size=12)
    sheet.save(f.EVID/f'{group}-review.png')
    markdown.extend(['',f'![{group} visual comparison]({group}-review.png)'])
    rows.append(f'<tr><td colspan="5"><img src="{group}-review.png" style="max-width:100%" alt="{group} comparison"></td></tr>')
(f.EVID/'INDEX.md').write_text('\n'.join(markdown)+'\n',encoding='utf-8')
(f.EVID/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>PDF Phase 1 evidence</title><style>body{font:15px system-ui;margin:32px;color:#182733}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd3da;padding:10px;text-align:left}a{color:#175a9a}</style><h1>PDF editor: Phase 1 evidence</h1><p>Local static review only. Candidate files include deliberately unsafe and refused operations. Red pixels mark changes outside the intended edit region. See the technical report before interpreting results.</p><table><tr><th>Experiment</th><th>Files</th><th>Outside pixels: MuPDF / PDFium / Poppler</th><th>Finding</th><th>144 DPI renders</th></tr>'+''.join(rows)+'</table></html>',encoding='utf-8')
print('Wrote results/index.html, INDEX.md and five visual review sheets.')
