"""Actual WPF correction matrix; per-case checkpoints remain if interrupted."""
from pathlib import Path
import subprocess,time,json,sys
R=Path(__file__).resolve().parents[1];E=R/'evidence';out=E/('presentation-release-'+str(time.time_ns()));out.mkdir();print('Presentation output:',out,flush=True)
extra=[]
if len(sys.argv)>1:
 payload=Path(sys.argv[1]).resolve();assert payload.is_file();extra=['--reproduction-text',str(payload)]
p=subprocess.Popen([str(R/'run/PdfEditorPrototype.exe'),'--presentation-ui-test','--audit',str(out)]+extra);p.wait(timeout=900);result=json.loads((out/'presentation-tests.json').read_text(encoding='utf-8'));(E/'presentation-release.json').write_text(json.dumps(dict(folder=str(out),result=result),indent=2),encoding='utf-8');print('Presentation:',result['tests'],'checks;',result['failures'],'failures',flush=True)
