import importlib.util,sys,json,time,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1];E=R/'evidence/frozen-phase4a';E.mkdir(exist_ok=True)
sys.path.insert(0,str(R.parent/'phase4a/tools'))
spec=importlib.util.spec_from_file_location('frozencompat',R.parent/'phase4a/tools/test_compatibility.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.OUT=E;m.base.EVID=E;m.base.WORK=R/'test-work'/('frozen4a-'+str(time.time_ns()));m.base.WORK.mkdir(parents=True)
with (E/'tests.log').open('w') as log:r=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=m.base.RecordedResult).run(unittest.defaultTestLoader.loadTestsFromTestCase(m.Tests))
(E/'tests.json').write_text(json.dumps(dict(tests=r.testsRun,success=r.wasSuccessful(),results=r.rows,saved=m.Tests.saved),indent=2));print('Frozen Phase 4A compatibility:',r.testsRun,'tests,',len(r.failures),'failures,',len(r.errors),'errors')
