import json, unittest
from pathlib import Path

suite=unittest.defaultTestLoader.discover(str(Path(__file__).parent),pattern='test_*.py')
result=unittest.TextTestRunner(verbosity=2).run(suite)
Path('results/tests.json').write_text(json.dumps({'tests_run':result.testsRun,'successful':result.wasSuccessful(),'failures':[{'test':str(t),'traceback':s} for t,s in result.failures],'errors':[{'test':str(t),'traceback':s} for t,s in result.errors],'skipped':[{'test':str(t),'reason':s} for t,s in result.skipped]},indent=2))
raise SystemExit(0 if result.wasSuccessful() else 1)
