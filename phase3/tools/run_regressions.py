"""Execute frozen Phase 2 suites without overwriting their evidence/source."""
import importlib.util,unittest,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'phase3/evidence';OUT.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('phase2_original_tests',ROOT/'phase2/tools/test_engine.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for version in ['phase2','phase3']:
    m.RUN=ROOT/version/'run';m.ORIGINALS=m.RUN/'samples';m.WORK=ROOT/'phase3/test-work'/('regression-'+version+'-'+str(time.time_ns()));m.WORK.mkdir(parents=True)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(m.Tests)
    with (OUT/(version+'-regression.log')).open('w') as log:result=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=m.RecordedResult).run(suite)
    (OUT/(version+'-regression.json')).write_text(json.dumps(dict(tests=result.testsRun,success=result.wasSuccessful(),results=result.rows,saved_outputs=m.Tests.outputs),indent=2))
    print(version,result.testsRun,len(result.failures),len(result.errors))
