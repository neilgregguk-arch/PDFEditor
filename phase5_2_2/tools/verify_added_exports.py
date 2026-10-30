"""Verify only successful UI exports added after the full independent snapshot."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];E=R/'evidence';previous=json.loads((E/'verified-export-records.json').read_text(encoding='utf-8'));known={r['destination'] for r in previous};added={}
for p in E.rglob('export-record-*.json'):
 if any(part.startswith('frozen') for part in p.relative_to(E).parts):continue
 r=json.loads(p.read_text(encoding='utf-8'))
 if r['destination'] not in known:added[r['destination']]=r
if added:
 (E/'added-export-records.json').write_text(json.dumps(list(added.values()),indent=2),encoding='utf-8')
 code=(R/'tools/verify_wrap.py').read_text(encoding='utf-8');old="unique={r['destination']:r for r in records};records=list(unique.values());w=base.Worker();cache={}"
 assert old in code;code=code.replace(old,"records=json.loads((E/'added-export-records.json').read_text(encoding='utf-8'));w=base.Worker();cache={}").replace("P=E/'document-poppler'","P=E/'added-poppler'").replace("E/'verified-export-records.json'","E/'added-verified-records.json'").replace("E/'wrap-independent-verification.json'","E/'added-independent-verification.json'")
 exec(compile(code,str(R/'tools/verify_wrap.py'),'exec'),{'__name__':'additional_export_reader','__file__':str(R/'tools/verify_wrap.py')})
 previous+=json.loads((E/'added-verified-records.json').read_text(encoding='utf-8'));(E/'verified-export-records.json').write_text(json.dumps(previous,indent=2),encoding='utf-8');report=json.loads((E/'wrap-independent-verification.json').read_text(encoding='utf-8'));report['cases']+=json.loads((E/'added-independent-verification.json').read_text(encoding='utf-8'))['cases'];(E/'wrap-independent-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('Additional exports independently verified:',len(added))
else:print('No unverified additional exports')
