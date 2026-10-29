"""Use original C2 engine and independent verifier for original C2 exports."""
from pathlib import Path
import sys,shutil
R=Path(__file__).resolve().parents[1];C2=R.parent/'phase4c2';E=R/'evidence/frozen-c2-readers';E.mkdir(exist_ok=True)
for suite in ['wrap','insertion','document','position']:
 source=R/'evidence/frozen-phase4c2'/suite/(suite+'-tests.json');assert source.exists(),source;shutil.copy2(source,E/source.name)
raw=E/'ui-records';raw.mkdir(exist_ok=True)
for p in (R/'evidence/frozen-c2-controls').glob('export-record-*.json'):shutil.copy2(p,raw/p.name)
sys.path.insert(0,str(C2/'tools'));import test_engine as b
b.ROOT=R;b.RUN=C2/'run';b.EVID=E;b.WORK=R/'test-work/frozen-c2-readers';b.WORK.mkdir(exist_ok=True)
source=(C2/'tools/verify_wrap.py').read_text(encoding='utf-8').replace("R=base.ROOT;E=R/'evidence'","R=base.ROOT;E=base.EVID")
source=source.replace("if page.get_contents() else []","if page.get_contents() is not None else []")
exec(compile(source,str(C2/'tools/verify_wrap.py'),'exec'),{'__name__':'frozen_c2_independent','__file__':str(C2/'tools/verify_wrap.py')})
