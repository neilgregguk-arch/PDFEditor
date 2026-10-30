"""Contact sheets of genuine WPF control captures; full originals retained."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
R=Path(__file__).resolve().parents[1];E=R/'evidence';out=E/'visual-qa';out.mkdir(exist_ok=True)
m=Path(json.loads((E/'multi-region-release.json').read_text(encoding='utf-8'))['folder']);p=Path(json.loads((E/'presentation-release.json').read_text(encoding='utf-8'))['folder']);b=E/'baseline-multi-1793356252749531400'
sheets={
 'multi-region': [('Baseline: expanded click leaves inactive',b/'two-invalid-return.png'),('Shipping: either retained draft activates',m/'two-invalid-return.png'),('Shipping: original lower restored',m/'lower-exact-original.png'),('Shipping: safe shortening verified',m/'shortened-verified.png'),('Shipping: source picker restores selection',m/'source-picker-lower-restored.png'),('Shipping: corrected combined save',m/'both-corrected-verified.png')],
 'overlap-and-mapping':[('Adversarial interactive overlap, test only',m/'adversarial-overlap-before-click.png'),('Source priority selects lower despite overlap',m/'adversarial-overlap-source-selected.png'),('Adversarial preview overlap, test only',m/'adversarial-preview-overlap.png'),('Ordinary u: mapping refusal retained',m/'unmapped-u.png'),('Safe lower with invalid upper',m/'invalid-upper-valid-lower.png'),('Safe upper with invalid lower',m/'valid-upper-invalid-lower.png')],
 'inherited-presentation':[(label,p/(name+'.png')) for label,name in [('Original','original-unmodified'),('Active verified','active-valid-verified'),('Inactive verified','inactive-valid'),('Invalid long active','replace-70-active'),('Invalid long inactive','replace-70-inactive'),('Saved and reopened','saved-reopened')]]}
for name,frames in sheets.items():
 sheet=Image.new('RGB',(1240,1740),'#e7ebef');draw=ImageDraw.Draw(sheet)
 for i,(label,path) in enumerate(frames):
  im=Image.open(path).convert('RGB');im.thumbnail((608,536));x=(i%2)*620;y=(i//2)*580;draw.text((x+8,y+8),label,fill='black');sheet.paste(im,(x+6,y+34))
 sheet.save(out/(name+'.png'))
(out/'captures.json').write_text(json.dumps(dict(baseline=str(b),multi=str(m),presentation=str(p),sheets={k:[str(path) for _,path in v] for k,v in sheets.items()},note='Scaled real WPF renders, not mockups. Original PNG/JSON retained. Routed harness is programmatic, not physical input.'),indent=2),encoding='utf-8')
print('Visual sheets:',out)
