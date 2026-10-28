from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];ROOT=R.parent;E=R/'evidence'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=json.loads((E/'prior-baseline.json').read_text());changed=[name for name,digest in base.items() if not (ROOT/name).exists() or h(ROOT/name)!=digest]
(E/'prior-phase-preservation.json').write_text(json.dumps(dict(checked=len(base),allUnchanged=not changed,changed=changed,scope='Phase 1, 2, 3, 4A, 4A.1, 4B source/runtime/evidence/handovers; excludes bin/obj/test-work'),indent=2));assert not changed,changed
base=json.loads((ROOT/'phase2/evidence/phase1-manifest.json').read_text());changed=[name for name,digest in base.items() if not (ROOT/name).exists() or h(ROOT/name)!=digest]
(E/'phase1-preservation.json').write_text(json.dumps(dict(checked=len(base),allUnchanged=not changed,changed=changed),indent=2));assert not changed,changed
files=[p for folder in ['App','Core','Worker','Checks','runtime','run','tools'] for p in (R/folder).rglob('*') if p.is_file() and not any(x in p.parts for x in ['bin','obj','__pycache__'])]
files+=list((ROOT/'PHASE_4C1_HANDOVER').glob('*.md'))+[R/'README.md',R/'Launch.ps1',R/'build.ps1',R/'Directory.Build.props']
(E/'release-manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):h(p) for p in files},indent=2))
print('Previous release files preserved:',json.loads((E/'prior-phase-preservation.json').read_text())['checked'],'; Phase 1:',len(base),'; release hashes:',len(files))
