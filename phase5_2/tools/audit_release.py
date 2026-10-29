"""Byte preservation and portable release hashes, with one explicit entry-guide update."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];ROOT=R.parent;E=R/'evidence'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
baseline=json.loads((E/'prior-baseline.json').read_text(encoding='utf-8'));changed=[n for n,v in baseline.items() if not (ROOT/n).is_file() or h(ROOT/n)!=v];entry=None
if 'START_HERE.md' in changed:
 assert 'Phase 5.1' in (ROOT/'START_HERE.md').read_text(encoding='utf-8');entry=dict(path='START_HERE.md',beforeSha256=baseline['START_HERE.md'],afterSha256=h(ROOT/'START_HERE.md'),reason='Intentional current-phase repository entry guide update');changed.remove('START_HERE.md')
(E/'prior-phase-preservation.json').write_text(json.dumps(dict(checked=len(baseline),historicalPhaseFilesUnchanged=not changed,allUnchanged=not changed and entry is None,intentionalRepositoryGuideUpdate=entry,changed=changed),indent=2),encoding='utf-8');assert not changed,changed
phase1=json.loads((ROOT/'phase2/evidence/phase1-manifest.json').read_text(encoding='utf-8'));changed=[n for n,v in phase1.items() if not (ROOT/n).is_file() or h(ROOT/n)!=v];(E/'phase1-preservation.json').write_text(json.dumps(dict(checked=len(phase1),allUnchanged=not changed,changed=changed),indent=2),encoding='utf-8');assert not changed,changed
files=[p for folder in ['App','Core','Worker','Checks','runtime','run','tools'] for p in (R/folder).rglob('*') if p.is_file() and not any(part in p.parts for part in ['bin','obj','__pycache__'])]
files+=list((ROOT/'PHASE_5_1_HANDOVER').glob('*.md'))+[R/'README.md',R/'Launch.ps1',R/'build.ps1',R/'Directory.Build.props',ROOT/'START_HERE.md']
(E/'release-manifest.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():h(p) for p in files},indent=2),encoding='utf-8')
print('Prior files audited:',len(baseline),'; historical phases unchanged; Phase 1:',len(phase1),'; new release paths:',len(files))
