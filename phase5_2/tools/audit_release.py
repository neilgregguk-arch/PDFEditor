"""Preserve every previous tracked byte except the intentional repository entry guide."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];ROOT=R.parent;E=R/'evidence'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
baseline=json.loads((E/'starting-preservation.json').read_text(encoding='utf-8'));changed=[n for n,h in baseline.items() if not (ROOT/n).is_file() or digest(ROOT/n)!=h];entry=None
if 'START_HERE.md' in changed:
 assert 'Phase 5.2' in (ROOT/'START_HERE.md').read_text(encoding='utf-8');entry=dict(path='START_HERE.md',beforeSha256=baseline['START_HERE.md'],afterSha256=digest(ROOT/'START_HERE.md'),reason='Intentional latest-phase entry guide update');changed.remove('START_HERE.md')
(E/'prior-phase-preservation.json').write_text(json.dumps(dict(checked=len(baseline),historicalPhaseFilesUnchanged=not changed,intentionalRepositoryGuideUpdate=entry,changed=changed),indent=2),encoding='utf-8');assert not changed,changed
phase1=json.loads((ROOT/'phase2/evidence/phase1-manifest.json').read_text(encoding='utf-8'));bad=[n for n,h in phase1.items() if not (ROOT/n).is_file() or digest(ROOT/n)!=h];assert not bad,bad
(E/'phase1-preservation.json').write_text(json.dumps(dict(checked=len(phase1),allUnchanged=True),indent=2),encoding='utf-8')
private=ROOT/'phase5_1/run/paragraph-examples/Word-two-rows-edited-manual-test.pdf';assert private.is_file();assert not (R/'run/paragraph-examples'/private.name).exists()
files=[p for p in R.rglob('*') if p.is_file() and not any(part in {'bin','obj','test-work','__pycache__'} for part in p.relative_to(R).parts) and p!=E/'release-manifest.json']
files+=list((ROOT/'PHASE_5_2_HANDOVER').glob('*.md'))+[ROOT/'PHASE_5_2_PROGRESS.md',ROOT/'START_HERE.md'];assert len(list((ROOT/'PHASE_5_2_HANDOVER').glob('*.md')))==6
(E/'release-manifest.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():digest(p) for p in sorted(files)},indent=2),encoding='utf-8');print('Preserved previous tracked files:',len(baseline),'(only START_HERE intentional update); Phase 1:',len(phase1),'; release paths:',len(files))
