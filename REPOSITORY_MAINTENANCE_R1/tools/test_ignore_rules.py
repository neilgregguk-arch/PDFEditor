"""Verify narrow generated-output ignores without hiding fixtures/evidence/source."""
from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[2]
cases=[('.local-generated/new-run/report.json',True),('artifacts/staging/app.zip',True),('phase5_2_2/App/bin/Release/new.dll',True),('phase5_2_2/Core/obj/cache.json',True),('phase5_2_2/test-work/temp.pdf',True),('.venv/Scripts/python.exe',True),('phase5_2_2/run/original-paragraphs/Word-cafe-paragraph.pdf',False),('future-fixtures/new-example.pdf',False),('phase5_2_2/evidence/retained-example.png',False),('REPOSITORY_MAINTENANCE_R1/LOCAL_WORKSPACE_AUDIT.md',False),('phase5_2_2/App/EditorWindow.cs',False),('phase5_2_2/runtime/licenses/PDFium/pdfium.txt',False),('future-fixtures/new-log.log',False),('phase5_1/run/paragraph-examples/Word-two-rows-edited-manual-test.pdf',False)]
rows=[]
for path,ignored in cases:
 q=subprocess.run(['git','-C',str(ROOT),'check-ignore','--no-index','-q',path]);assert q.returncode in [0,1];actual=q.returncode==0;assert actual==ignored,(path,actual,ignored);rows.append(dict(path=path,ignored=actual,expected=ignored))
(ROOT/'REPOSITORY_MAINTENANCE_R1/inventory/ignore-rule-tests.json').write_text(json.dumps(dict(tests=len(rows),failures=0,rows=rows),indent=2),encoding='utf-8');print('Ignore rules:',len(rows),'passing')
