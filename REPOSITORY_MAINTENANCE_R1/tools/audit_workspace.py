"""Read-only PDFEditor storage/content audit. Outputs go outside root by default."""
from pathlib import Path
import os,sys,json,hashlib,subprocess,gzip,csv,collections,datetime,time,argparse
ap=argparse.ArgumentParser();ap.add_argument('--root',default=str(Path.cwd()));ap.add_argument('--out',required=True);ap.add_argument('--label',default='baseline');args=ap.parse_args();root=Path(args.root).resolve();out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
def git(*a):return subprocess.check_output(['git','-C',str(root),*a])
index={}
for row in git('ls-files','--stage','-z').split(b'\0'):
 if row:
  meta,path=row.split(b'\t',1);mode,blob,stage=meta.decode().split();index[path.decode('utf-8')]=blob
ignored=set(x.decode('utf-8') for x in git('ls-files','--others','--ignored','--exclude-standard','-z').split(b'\0') if x)
untracked=set(x.decode('utf-8') for x in git('ls-files','--others','--exclude-standard','-z').split(b'\0') if x)
rows=[];errors=[];skipped=[];total=0;dirs=collections.defaultdict(lambda:[0,0]);phases=collections.defaultdict(lambda:[0,0]);groups=collections.defaultdict(list);category=collections.defaultdict(lambda:[0,0]);statusTotals=collections.defaultdict(lambda:[0,0]);allHashes={};digestCache={}
def cat(rel):
 ps=rel.split('/');lo=rel.lower();suffix=Path(rel).suffix.lower();base=Path(rel).name.lower()
 if ps[0]=='.git':return 'Git metadata'
 if 'license' in base or 'licence' in base or 'notice' in base or 'attribution' in base:return 'D'
 if any(x in ps for x in ['bin','obj','__pycache__','.vs','.idea']):return 'G'
 if ps[0] in ['.venv','.venv-clean','tmp','.local-generated']:return 'Local generated - review'
 if suffix in ['.ttf','.otf'] or base=='pdfium.dll' or '/licenses/' in lo:return 'D'
 if 'evidence' in ps or 'test-work' in ps:return 'F'
 if suffix in ['.cs','.csproj','.props','.sln','.py','.ps1','.js','.mjs','.json','.toml','.yml','.yaml','.config','.txt']:
  if 'run' in ps and suffix in ['.json','.config'] and ('.deps.' in base or '.runtimeconfig.' in base):return 'E'
  if suffix=='.json' and ('runtime' in ps or 'run' in ps):return 'C'
  return 'A'
 if suffix in ['.md','.rst','.html']:return 'B'
 if suffix in ['.pdf','.docx','.pptx','.svg','.png','.jpg','.jpeg'] and 'test-work' not in ps:return 'C'
 if 'run' in ps or 'runtime' in ps or suffix in ['.exe','.dll','.pdb','.zip']:return 'E'
 return 'A' if Path(rel).name.startswith('.') else 'Uncertain - preserve'
for base,ds,fs in os.walk(root,followlinks=False):
 for name in list(ds):
  p=Path(base)/name
  if p.is_symlink() or (hasattr(os.path,'isjunction') and os.path.isjunction(p)):
   ds.remove(name);skipped.append(str(p.relative_to(root)))
 for name in fs:
  p=Path(base)/name;rel=p.relative_to(root).as_posix()
  try:
   if p.is_symlink():skipped.append(rel);continue
   st=p.stat();size=st.st_size;state='git-metadata' if rel.startswith('.git/') else 'tracked' if rel in index else 'ignored' if rel in ignored else 'untracked'
   c=cat(rel);sha='';blob=index.get(rel,'')
   # Never print local document/credential contents; hash only, never execute.
   if state!='git-metadata':
    k=(st.st_dev,st.st_ino,size,st.st_mtime_ns)
    if k not in digestCache:
     h=hashlib.sha256()
     with p.open('rb') as f:
      for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
     digestCache[k]=h.hexdigest()
    sha=digestCache[k];allHashes[rel]=sha;groups[sha].append((rel,size,state))
   row=dict(path=rel,bytes=size,status=state,category=c,sha256=sha,gitBlob=blob,mtimeNs=st.st_mtime_ns);rows.append(row);total+=size;category[c][0]+=1;category[c][1]+=size;statusTotals[state][0]+=1;statusTotals[state][1]+=size
   phase=rel.split('/')[0];phases[phase][0]+=1;phases[phase][1]+=size
   par=Path(rel).parent
   while str(par) not in ['.','']:
    key=par.as_posix();dirs[key][0]+=1;dirs[key][1]+=size;par=par.parent
  except Exception as e:errors.append(dict(path=rel,error=str(e)))
  if len(rows)%10000==0:print('Audited',len(rows),'files;',round(total/1048576,1),'MiB',flush=True)
remote=git('ls-remote','origin','refs/heads/main').decode().strip();head=git('rev-parse','HEAD').decode().strip()
remoteHashes={r['sha256'] for r in rows if r['status']=='tracked'} if remote.split()[0]==head else set()
for r in rows:
 r['retention']='Preserve until reviewed'
 if r['status']=='tracked':r['backup']='Remote HEAD verified' if remoteHashes else 'Remote HEAD differs; verify separately'
 elif r['status']=='git-metadata':r['backup']='Git administrative data; never clean via script'
 elif r['sha256'] in remoteHashes:r['backup']='Byte-identical tracked content at remote HEAD'
 else:r['backup']='No independently verified backup in audit'
 if r['category'] in ['A','B','C','D']:r['retention']='Essential or uncertain; retain'
 elif r['category']=='E':r['retention']='Retain historical reference binary until verified migration'
 elif r['category']=='F':r['retention']='Evidence: tier/index review required before deletion'
 elif r['category']=='G':r['retention']='Potential reproducible intermediate; explicit validated plan required'
fields=list(rows[0]) if rows else []
with gzip.open(out/(args.label+'-files.csv.gz'),'wt',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
tracked=[r for r in rows if r['status']=='tracked'];dupes=[dict(sha256=h,bytes=vs[0][1],copies=len(vs),logicalDuplicateBytes=vs[0][1]*(len(vs)-1),paths=[v[0] for v in vs]) for h,vs in groups.items() if len(vs)>1]
# A separate tracked-only duplicate view avoids confusing cache copies with repository content.
tg=collections.defaultdict(list)
for r in tracked:tg[r['sha256']].append(r)
td=[dict(sha256=h,bytes=vs[0]['bytes'],copies=len(vs),logicalDuplicateBytes=vs[0]['bytes']*(len(vs)-1),paths=[v['path'] for v in vs]) for h,vs in tg.items() if len(vs)>1]
with gzip.open(out/(args.label+'-tracked.csv.gz'),'wt',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(tracked)
with gzip.open(out/(args.label+'-duplicates.json.gz'),'wt',encoding='utf-8') as f:json.dump(dict(tracked=sorted(td,key=lambda d:d['logicalDuplicateBytes'],reverse=True),allWorkspace=sorted(dupes,key=lambda d:d['logicalDuplicateBytes'],reverse=True)),f,separators=(',',':'))
byStatus=lambda path,items:dict(path=path,files=items[0],bytes=items[1])
interesting=[]
for d,v in dirs.items():
 ps=d.split('/');name=ps[-1]
 if name in ['bin','obj','test-work','__pycache__','tmp','document-poppler','position-poppler','poppler','visual-qa'] or d in ['.venv','.venv-clean','.git'] or (len(ps)==2 and name in ['run','runtime','evidence']):interesting.append(byStatus(d,v))
summary=dict(schema=1,label=args.label,root=str(root),startedUtc=start,finishedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),head=head,branch=git('branch','--show-current').decode().strip(),status=git('status','--short').decode(),remoteMain=remote,logicalBytes=total,files=len(rows),statusTotals={k:dict(files=v[0],bytes=v[1]) for k,v in statusTotals.items()},categoryTotals={k:dict(files=v[0],bytes=v[1]) for k,v in category.items()},phases=[byStatus(k,v) for k,v in sorted(phases.items())],largestDirectories=sorted([byStatus(k,v) for k,v in dirs.items()],key=lambda d:d['bytes'],reverse=True)[:60],largestFiles=[{k:r[k] for k in ['path','bytes','status','category']} for r in sorted(rows,key=lambda r:r['bytes'],reverse=True)[:40]],artifactDirectories=sorted(interesting,key=lambda d:d['bytes'],reverse=True),trackedDuplicateGroups=len(td),trackedDuplicateBytes=sum(d['logicalDuplicateBytes'] for d in td),trackedUniqueContentBytes=sum(v[0]['bytes'] for v in tg.values()),workspaceDuplicateBytes=sum(d['logicalDuplicateBytes'] for d in dupes),localWithoutVerifiedBackupFiles=sum(r['status'] in ['ignored','untracked'] and r['backup'].startswith('No independently') for r in rows),localWithoutVerifiedBackupBytes=sum(r['bytes'] for r in rows if r['status'] in ['ignored','untracked'] and r['backup'].startswith('No independently')),gitCountObjects=git('count-objects','-v').decode(),errors=errors,skippedReparsePaths=skipped,limitations='Logical byte counts, not allocated disk usage. Duplicate logical path bytes are not independent Git blob storage. OneDrive folder membership is not a verified off-machine backup. .git is measured but never a cleanup candidate. Live filesystem is a time-bounded scan, not a volume snapshot.')
(out/(args.label+'-summary.json')).write_text(json.dumps(summary,indent=2),encoding='utf-8',newline='\n')
print(json.dumps({k:summary[k] for k in ['files','logicalBytes','statusTotals','trackedDuplicateBytes','localWithoutVerifiedBackupFiles','errors']},indent=2),flush=True)
