"""Compare two complete local inventories; report approved build-cache changes separately."""
from pathlib import Path
import gzip,csv,json,argparse
ROOT=Path(__file__).resolve().parents[2];R=ROOT/'REPOSITORY_MAINTENANCE_R1'
ap=argparse.ArgumentParser();ap.add_argument('--before',required=True);ap.add_argument('--after',required=True);args=ap.parse_args()
def rows(p):
 with gzip.open(p,'rt',encoding='utf-8') as f:return {r['path']:r for r in csv.DictReader(f)}
before=rows(args.before);after=rows(args.after);bad=[];buildChanges=[];intentional=[];private=[];unchangedLocal=0
for name,old in before.items():
 if old['status']=='git-metadata':continue
 new=after.get(name);same=new is not None and new['sha256']==old['sha256']
 if old['status']=='tracked':
  if not same:
   if name=='.gitignore':intentional.append(dict(path=name,before=old['sha256'],after=new['sha256'] if new else None))
   else:bad.append(name)
 elif not same:
  parts=name.split('/')
  if any(p in ['bin','obj','__pycache__'] for p in parts):buildChanges.append(dict(path=name,reason='Compiler/model/Python build cache regenerated during authorised build; not maintenance cleanup',existedAfter=new is not None))
  else:bad.append(name)
 else:unchangedLocal+=1
 if old['status']=='untracked':private.append(dict(path=name,bytes=int(old['bytes']),hashUnchanged=same,preserved=True if same else False,cleanupExcluded=True))
missing=[name for name,r in before.items() if r['status']!='git-metadata' and name not in after]
report=dict(preexistingNonGitMissing=missing,startingTrackedFiles=sum(r['status']=='tracked' for r in before.values()),allStartingTrackedPreservedExceptIgnore=not bad,intentionalChanges=intentional,preexistingLocalNonBuildUnchanged=unchangedLocal,regeneratedCacheFiles=buildChanges,preexistingUntracked=private,unexpectedChanges=bad,cleanupExecuted=False,note='New R1 outputs/metadata are additive. Compiler caches may change when rebuilding. No user/private document, fixture, evidence, licence or old source removal is permitted.')
(R/'inventory/preservation-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8',newline='\n');assert not bad,bad;assert all(p['hashUnchanged'] for p in private);print('Preserved',report['startingTrackedFiles'],'starting tracked files (only .gitignore intentional); preexisting local nonbuild unchanged',unchangedLocal,'; build cache changes',len(buildChanges))
