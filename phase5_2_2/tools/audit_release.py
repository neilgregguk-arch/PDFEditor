"""Final prior-phase preservation and corrective source/build/evidence manifest."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];ROOT=R.parent;E=R/'evidence'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
baseline=json.loads((E/'starting-preservation.json').read_text(encoding='utf-8'));changed=[n for n,v in baseline.items() if not (ROOT/n).is_file() or h(ROOT/n)!=v];entry=None
if 'START_HERE.md' in changed:
 assert 'Phase 5.2.2' in (ROOT/'START_HERE.md').read_text(encoding='utf-8');entry=dict(path='START_HERE.md',beforeSha256=baseline['START_HERE.md'],afterSha256=h(ROOT/'START_HERE.md'),reason='Intentional latest corrective-phase entry guide update');changed.remove('START_HERE.md')
assert not changed,changed
(E/'prior-phase-preservation.json').write_text(json.dumps(dict(checked=len(baseline),historicalPhaseFilesUnchanged=True,intentionalEntryGuideUpdate=entry),indent=2),encoding='utf-8')
first=json.loads((ROOT/'phase2/evidence/phase1-manifest.json').read_text(encoding='utf-8'));assert all(h(ROOT/n)==v for n,v in first.items());(E/'phase1-preservation.json').write_text(json.dumps(dict(checked=len(first),allUnchanged=True),indent=2),encoding='utf-8')
assert (ROOT/'phase5_1/run/paragraph-examples/Word-two-rows-edited-manual-test.pdf').is_file();assert not (R/'run/paragraph-examples/Word-two-rows-edited-manual-test.pdf').exists()
for p in (R/'Core').glob('*.cs'):assert p.read_bytes()==(ROOT/'phase5_2_1/Core'/p.name).read_bytes()
reports=list((ROOT/'PHASE_5_2_2_HANDOVER').glob('*.md'));assert len(reports)==6
files=[p for p in R.rglob('*') if p.is_file() and not any(part in {'bin','obj','test-work','__pycache__'} for part in p.relative_to(R).parts) and p!=E/'release-manifest.json']+reports+[ROOT/'PHASE_5_2_2_PROGRESS.md',ROOT/'START_HERE.md']
(E/'release-manifest.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():h(p) for p in sorted(files)},indent=2),encoding='utf-8');print('Previous tracked files preserved:',len(baseline),'(only intentional START_HERE update); Phase 1:',len(first),'; new release paths:',len(files))
