"""Actual unaltered WPF captures remain beside labelled visual comparison sheets."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
R=Path(__file__).resolve().parents[1];E=R/'evidence';current=Path(json.loads((E/'presentation-release.json').read_text(encoding='utf-8'))['folder']);baseline=next(E.glob('baseline-presentation-*'));out=E/'visual-qa';out.mkdir(exist_ok=True)
items=[('Before: unsafe proposed rows',baseline/'replace-30-active.png'),('After: retained draft, not PDF positions',current/'replace-30-active.png'),('Before: unwrapped native editor spills',baseline/'replace-70-active.png'),('After: contained native editor with scroll',current/'replace-70-active.png'),('After: inactive retained draft, same bounds',current/'replace-70-inactive.png'),('After: returned invalid draft',current/'replace-70-returned.png')]
for name,frames in [('before-after',items),('states',[(n,current/(p+'.png')) for n,p in [('Unmodified original','original-unmodified'),('Active valid, verified','active-valid-verified'),('Inactive valid','inactive-valid'),('Saved and reopened','saved-reopened'),('Native focus lost, text retained','invalid-blurred'),('Protected graphic excluded','invalid-near-graphic')]])]:
 sheet=Image.new('RGB',(1240,1110),'#e7ebef');draw=ImageDraw.Draw(sheet)
 for i,(label,path) in enumerate(frames):
  im=Image.open(path).convert('RGB');body=im.crop((140,88,980,400));body.thumbnail((608,244));status=im.crop((0,im.height-100,im.width,im.height));status.thumbnail((608,80));x=(i%2)*620;y=(i//2)*370;draw.text((x+8,y+10),label,fill='black');sheet.paste(body,(x+6,y+34));sheet.paste(status,(x+6,y+282))
 sheet.save(out/(name+'.png'))
(out/'captures.json').write_text(json.dumps(dict(baseline=str(baseline),shipping=str(current),note='Contacts crop/scale actual WPF captures for comparison; original full PNG/state JSON retained. User original screenshots/exact pasted text were not provided.'),indent=2),encoding='utf-8');print('Visual sheets:',out)
