"""Execute original C2 test sources/binaries; redirect every output into this phase."""
from pathlib import Path
import subprocess,sys,json
R=Path(__file__).resolve().parents[1];BASE=R.parent/'phase4c2';E=R/'evidence/frozen-phase4c2';E.mkdir(exist_ok=True)
for name in ['engine','discovery','compatibility','position','insertion','document','wrap']:
 out=E/name;out.mkdir(exist_ok=True)
 code=f'''import sys,importlib.util,unittest,json
from pathlib import Path
sys.path.insert(0,{str(BASE/'tools')!r})
import test_engine as b
b.ROOT=Path({str(R)!r});b.RUN=Path({str(BASE/'run')!r});b.ORIGINALS=b.RUN/'samples';b.EVID=Path({str(out)!r});b.WORK=Path({str(R/'test-work'/('frozen-c2-'+name))!r});b.WORK.mkdir(parents=True,exist_ok=True)
if {name!r}=='engine':m=b
else:
 import types
 m=types.ModuleType('frozen_suite');m.__file__={str(BASE/'tools'/('test_'+name+'.py'))!r}
 source=Path(m.__file__).read_text(encoding='utf-8').replace("E=R/'evidence'",'E=base.EVID').replace("OUT=ROOT/'evidence'",'OUT=base.EVID')
 exec(compile(source,m.__file__,'exec'),m.__dict__)
if hasattr(m,'Tests'):
 if hasattr(m,'OUT'):m.OUT=b.EVID
 result=unittest.TextTestRunner(verbosity=2,resultclass=b.RecordedResult).run(unittest.defaultTestLoader.loadTestsFromTestCase(m.Tests))
 (b.EVID/'tests.json').write_text(json.dumps(dict(tests=result.testsRun,success=result.wasSuccessful(),results=result.rows),indent=2))
 assert result.wasSuccessful()
'''
 with (out/'run.log').open('w',encoding='utf-8') as log:p=subprocess.run([sys.executable,'-c',code],stdout=log,stderr=subprocess.STDOUT)
 assert p.returncode==0,(name,p.returncode);print('Frozen Phase 4C.2',name,'completed',flush=True)
