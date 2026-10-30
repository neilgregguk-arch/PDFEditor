"""Practical historical smoke: original Phase2 sources/binary, redirected outputs."""
from pathlib import Path
import importlib.util,unittest,json,hashlib
ROOT=Path(__file__).resolve().parents[2];out=ROOT/'.local-generated/R1-validation/evidence/frozen-phase2';out.mkdir(parents=True,exist_ok=True);p=ROOT/'phase2/tools/test_engine.py'
spec=importlib.util.spec_from_file_location('r1_frozen_phase2',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.RUN=ROOT/'phase2/run';m.ORIGINALS=m.RUN/'samples';m.EVID=out;m.WORK=ROOT/'.local-generated/R1-validation/test-work/frozen-phase2';m.WORK.mkdir(parents=True,exist_ok=True)
with (out/'run.log').open('w',encoding='utf-8') as f:r=unittest.TextTestRunner(stream=f,verbosity=2,resultclass=m.RecordedResult).run(unittest.defaultTestLoader.loadTestsFromTestCase(m.Tests))
report=dict(tests=r.testsRun,success=r.wasSuccessful(),failures=len(r.failures)+len(r.errors),sourceSha256=hashlib.sha256(p.read_bytes()).hexdigest(),scope='Frozen original test source and original phase2 binary; outputs redirected only',rows=r.rows)
(ROOT/'REPOSITORY_MAINTENANCE_R1/inventory/frozen-phase2-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');assert r.wasSuccessful()
