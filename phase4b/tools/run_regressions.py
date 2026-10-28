"""Run preserved suites with all new outputs redirected under Phase 4A."""
import importlib.util,unittest,json,time,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'phase4b/evidence'
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
for version in ['phase2','phase3','phase4a','phase4a1']:
 source=ROOT/(version if version in ['phase4a','phase4a1'] else 'phase2')/'tools/test_engine.py'
 m=load(source,'regression_'+version);m.RUN=ROOT/version/'run';m.ORIGINALS=m.RUN/'samples';m.EVID=OUT;m.WORK=ROOT/'phase4b/test-work'/('regression-'+version+'-'+str(time.time_ns()));m.WORK.mkdir(parents=True)
 with (OUT/(version+'-regression.log')).open('w') as log:r=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=m.RecordedResult).run(unittest.defaultTestLoader.loadTestsFromTestCase(m.Tests))
 (OUT/(version+'-regression.json')).write_text(json.dumps(dict(tests=r.testsRun,success=r.wasSuccessful(),results=r.rows,saved_outputs=m.Tests.outputs),indent=2));print(version,r.testsRun,'failures',len(r.failures),'errors',len(r.errors),flush=True)
sys.path.insert(0,str(ROOT/'phase3/tools'));sys.modules.pop('test_engine',None)
m=load(ROOT/'phase3/tools/test_discovery.py','frozen_phase3_discovery');m.OUT=OUT/'frozen-phase3-discovery';m.OUT.mkdir(exist_ok=True);m.base.EVID=m.OUT;m.base.WORK=ROOT/'phase4b/test-work'/('frozen-discovery-'+str(time.time_ns()));m.base.WORK.mkdir(parents=True)
with (m.OUT/'tests.log').open('w') as log:r=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=m.base.RecordedResult).run(unittest.defaultTestLoader.loadTestsFromTestCase(m.Tests))
(m.OUT/'tests.json').write_text(json.dumps(dict(tests=r.testsRun,success=r.wasSuccessful(),results=r.rows,saved=m.Tests.saved),indent=2));print('frozen Phase 3 discovery',r.testsRun,'failures',len(r.failures),'errors',len(r.errors))
