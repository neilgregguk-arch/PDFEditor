"""Exercise audit/dry-run/refusals and ShouldProcess WhatIf. Never delete files."""
from pathlib import Path
import subprocess,json,hashlib,copy,tempfile
ROOT=Path(__file__).resolve().parents[2];R=ROOT/'REPOSITORY_MAINTENANCE_R1';script=R/'tools/Local-Cleanup.ps1';plan=json.loads((R/'inventory/local-cleanup-plan.json').read_text(encoding='utf-8'));out=Path(tempfile.mkdtemp(prefix='pdfeditor-r1-cleanup-tests-'));rows=[]
before={f['path']:hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest() for f in plan['files']}
def run(name,extra,expected=0,modified=None):
 args=['pwsh','-NoProfile','-File',str(script)]+extra
 if modified is not None:
  p=out/(name+'.json');p.write_text(json.dumps(modified),encoding='utf-8');args+=['-PlanPath',str(p)]
 q=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',errors='replace');(out/(name+'.log')).write_text(q.stdout+q.stderr,encoding='utf-8')
 ok=(q.returncode==0) if expected==0 else (q.returncode!=0);assert ok,(name,q.returncode,(q.stdout+q.stderr)[-1200:]);rows.append(dict(name=name,pass_=ok,exit=q.returncode,scope='No deletion; Audit/DryRun/WhatIf/refusal only'))
run('default-audit',[])
run('dry-run-every-target',['-Mode','DryRun'])
run('clean-without-approval-refused',['-Mode','Clean'],1)
run('clean-approved-whatif-no-removal',['-Mode','Clean','-ApproveCleanup','-WhatIf'])
assert plan['files'],'A positive verified candidate is needed to test the preflight path'
for name,path in [('parent-traversal','../outside.dll'),('absolute-path',str(ROOT.parent/'outside.dll')),('source-code','phase5_2_2/App/EditorWindow.cs'),('fixture','phase5_2_2/run/original-paragraphs/Word-cafe-paragraph.pdf'),('user-document','phase5_1/run/paragraph-examples/Word-two-rows-edited-manual-test.pdf'),('git-data','.git/config'),('credentials','phase5_2_2/App/bin/credentials.dll'),('unknown-assembly','phase5_2_2/App/bin/Custom.dll'),('historical-binary','phase5_2_2/run/PdfEditorPrototype.exe')]:
 p=copy.deepcopy(plan);p['files'][0]['path']=path;run(name,['-Mode','Audit'],1,p)
p=copy.deepcopy(plan);p['files'][0]['sha256']='0'*64;run('changed-file-hash',['-Mode','Audit'],1,p)
p=copy.deepcopy(plan);p['files'][0]['backupPath']='phase5_2_2/run/Core.dll';run('wrong-backup-bytes',['-Mode','Audit'],1,p)
p=copy.deepcopy(plan);p['files'].append(p['files'][0]);run('duplicate-target',['-Mode','Audit'],1,p)
p=copy.deepcopy(plan);p['workspace']=str(ROOT.parent);run('wrong-workspace',['-Mode','Audit'],1,p)
p=copy.deepcopy(plan);p['validatedBuildSha256']='0'*64;run('changed-build-manifest',['-Mode','Audit'],1,p)
after={f['path']:hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest() for f in plan['files']};assert before==after
report=dict(tests=len(rows),failures=0,rows=rows,candidateHashesUnchanged=True,cleanupExecuted=False,whatIfOnly=True,logs=str(out),limitations='No real cleanup/deletion is executed or approved. Reparse-point rejection is implemented and inspected but a live junction test was not created during this R1 run.')
(R/'inventory/cleanup-safety-tests.json').write_text(json.dumps(report,indent=2),encoding='utf-8',newline='\n');print('Cleanup safety:',len(rows),'passing; no removal')
