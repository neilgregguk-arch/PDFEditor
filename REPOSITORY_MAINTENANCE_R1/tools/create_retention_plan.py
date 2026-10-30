"""Classify, propose migration, and plan only proven local build duplicates. No deletion."""
from pathlib import Path
import csv,gzip,json,collections,argparse,re,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[2];R=ROOT/'REPOSITORY_MAINTENANCE_R1';I=R/'inventory'
ap=argparse.ArgumentParser();ap.add_argument('--local-inventory',required=True);ap.add_argument('--build-manifest',required=True);args=ap.parse_args()
with gzip.open(I/'baseline-tracked.csv.gz','rt',encoding='utf-8') as f:tracked=list(csv.DictReader(f))
with gzip.open(args.local_inventory,'rt',encoding='utf-8') as f:allfiles=list(csv.DictReader(f))
baseline=json.loads((I/'baseline-summary.json').read_text(encoding='utf-8'));build=json.loads(Path(args.build_manifest).read_text(encoding='utf-8'));rebuilt={f['sha256'] for f in build['files']}
remote={}
for row in tracked:remote.setdefault(row['sha256'],row['path'])
records=[];categories=collections.defaultdict(lambda:dict(files=0,bytes=0));phases=collections.defaultdict(lambda:dict(files=0,bytes=0,evidenceBytes=0,buildBytes=0))
for row in tracked:
 cat=row['category'];cat='F' if cat.startswith('Uncertain') and row['path'].endswith('.log') else cat
 assert cat in 'ABCDEFG',row
 tier='1' if cat in ['A','B','C','D'] else '2-review-retain' if cat in ['E','F'] else '3-verify-before-untracking'
 purpose='Historical generated log: preserve forensic context' if row['category'].startswith('Uncertain') else 'Conservative path/type classification; no deletion authorisation'
 r=dict(path=row['path'],bytes=int(row['bytes']),sha256=row['sha256'],gitBlob=row['gitBlob'],category=cat,proposedTier=tier,disposition='Retain in place during R1',reason=purpose);records.append(r)
 categories[cat]['files']+=1;categories[cat]['bytes']+=r['bytes'];phase=row['path'].split('/')[0];phases[phase]['files']+=1;phases[phase]['bytes']+=r['bytes']
 if cat=='F':phases[phase]['evidenceBytes']+=r['bytes']
 if cat in ['D','E'] and any(p in row['path'].split('/') for p in ['run','runtime']):phases[phase]['buildBytes']+=r['bytes']
with gzip.open(I/'artifact-classification.csv.gz','wt',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
migration=[dict(r,archiveDestination='PENDING explicit approved versioned archive',verifiedDestination=False,removalApproved=False) for r in records if r['category'] in ['E','F']]
with gzip.open(I/'proposed-archive-migration.csv.gz','wt',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(migration[0]));w.writeheader();w.writerows(migration)
localDirs=collections.defaultdict(lambda:dict(files=0,bytes=0,withoutVerifiedBackupFiles=0))
for row in allfiles:
 if row['status'] not in ['ignored','untracked']:continue
 for p in Path(row['path']).parents:
  if p.as_posix()=='.':continue
  v=localDirs[p.as_posix()];v['files']+=1;v['bytes']+=int(row['bytes']);v['withoutVerifiedBackupFiles']+=row['backup'].startswith('No independently')
directoryRecords=[]
for name,v in sorted(localDirs.items(),key=lambda kv:kv[1]['bytes'],reverse=True):
 if v['bytes']<1024*1024:continue
 ps=name.split('/')
 if any(p in ['bin','obj','__pycache__'] for p in ps):classification='Reproducible';rule='Only matching verified build duplicates are planned. Preserve unknown files/source/user documents.'
 else:classification='Requiring preservation';rule='Unique local outputs/environment or evidence not verified in external archive; no blanket removal.'
 directoryRecords.append(dict(path=name,**v,classification=classification,retention=rule))
(I/'local-directory-classification.json').write_text(json.dumps(directoryRecords,indent=2),encoding='utf-8',newline='\n')
# Also classify identified tracked/mixed render/evidence/dependency directories.
allDirs=collections.defaultdict(lambda:dict(bytes=0,files=0,tracked=0,localDocumentFiles=0))
for row in allfiles:
 for parent in Path(row['path']).parents:
  if parent.as_posix()=='.':continue
  d=allDirs[parent.as_posix()];d['bytes']+=int(row['bytes']);d['files']+=1;d['tracked']+=row['status']=='tracked';d['localDocumentFiles']+=row['status'] in ['ignored','untracked'] and Path(row['path']).suffix.lower() in ['.pdf','.docx','.xlsx','.pptx']
identified=[]
for name,d in allDirs.items():
 parts=name.split('/');leaf=parts[-1].lower()
 if d['bytes']<1048576 and leaf not in ['bin','obj','test-work','__pycache__']:continue
 if parts[0]=='.git' or (not any(t in parts for t in ['run','evidence','test-work','.venv','.venv-clean','.local-generated']) and d['tracked']==d['files']):kind='Essential';why='Source/fixture/notice or Git administration: retain'
 elif any(t in parts for t in ['bin','obj','__pycache__']) and not d['localDocumentFiles']:kind='Reproducible';why='Compiler/Python intermediates; file-level review and approval required, never a directory sweep'
 else:kind='Requiring preservation';why='Historical artifacts, unverified environment or unique local documents/evidence'
 identified.append(dict(path=name,**d,classification=kind,reason=why,cleanupApproved=False))
(I/'directory-retention.json').write_text(json.dumps(sorted(identified,key=lambda d:d['bytes'],reverse=True),indent=2),encoding='utf-8',newline='\n')

files=[]
for row in allfiles:
 rel=row['path'];sha=row['sha256']
 if row['status']!='ignored' or not re.match(r'^phase5_2_2/(App|Core|Worker|Checks)/(bin|obj)/',rel):continue
 if not re.search(r'/(PdfEditorPrototype|PdfWorker|Core)\.(dll|exe|pdb)$',rel):continue
 if sha not in remote or sha not in rebuilt:continue
 # The clean script rechecks all path, source-code/document/credential exclusions.
 files.append(dict(path=rel,bytes=int(row['bytes']),sha256=sha,backupPath=remote[sha],reason='Reproducible build duplicate with byte-identical verified Git backup'))
plan=dict(schema=1,workspace=str(ROOT),backupCommit=baseline['head'],remoteVerification=baseline['remoteMain'],validatedBuildManifest=str(Path(args.build_manifest).resolve()),validatedBuildSha256=hashlib.sha256(Path(args.build_manifest).read_bytes()).hexdigest(),files=files,estimatedLogicalSavingsBytes=sum(f['bytes'] for f in files),cleanupAuthorised=False,note='Explicit user approval required to execute. No directory-wide deletion; only current phase matching backed-up SDK products. Test-work, environments, unique evidence and user files retained.')
(I/'local-cleanup-plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8',newline='\n')
# Minimum useful records are indexed, not moved or silently discarded.
index=[]
for phase,data in sorted(phases.items()):
 if not phase.startswith('phase'):continue
 phaseRows=[r for r in records if r['path'].split('/')[0]==phase];docs=[r['path'] for r in phaseRows if r['path'].endswith('.md')]
 summaries=[r['path'] for r in phaseRows if '/evidence/' in r['path'] and len(Path(r['path']).parts)==3 and r['path'].endswith('.json')]
 failures=[r['path'] for r in phaseRows if any(s in r['path'].lower() for s in ['baseline-','root-cause','failure','refused','blocked','warning'])]
 index.append(dict(phase=phase,**data,essentialDocs=docs,authoritativeRootRecords=summaries,criticalFailureReferences=failures,rootHandoverDocuments=[p.relative_to(ROOT).as_posix() for folder in ROOT.iterdir() if folder.is_dir() and re.sub('[^a-z0-9]','',folder.name.lower()).removesuffix('handover')==re.sub('[^a-z0-9]','',phase.lower()) for p in sorted(folder.glob('*.md'))],policy='Retain source/fixture/notice/summary/recipe/hash Tier1; final binary/raster and critical originals Tier2 only after verified approved archive; unique failures retained. No artifact is removed by this index.'))
(I/'evidence-retention-index.json').write_text(json.dumps(index,indent=2),encoding='utf-8',newline='\n')
(I/'classification-summary.json').write_text(json.dumps(dict(categories=categories,phases=phases,archiveCandidates=len(migration),archiveCandidateBytes=sum(r['bytes'] for r in migration),plannedLocalFiles=len(files),plannedLogicalBytes=plan['estimatedLogicalSavingsBytes'],noDeletionPerformed=True),indent=2),encoding='utf-8',newline='\n')
print('Classified',len(records),'tracked files; migration proposals',len(migration),'kept in place; local plan',len(files),'files /',plan['estimatedLogicalSavingsBytes'],'bytes; no deletion')
