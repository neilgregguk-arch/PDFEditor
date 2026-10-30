"""Independently verify only the additional final-caption smoke export."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1];E=R/'evidence';smoke=json.loads((E/'final-caption-smoke.json').read_text(encoding='utf-8'));record=next(Path(smoke['folder']).glob('export-record-*.json'))
code=(R/'tools/verify_wrap.py').read_text(encoding='utf-8');old="unique={r['destination']:r for r in records};records=list(unique.values());w=base.Worker();cache={}"
assert old in code
code=code.replace(old,"records=[json.loads(Path("+repr(str(record))+").read_text(encoding='utf-8'))];w=base.Worker();cache={}")
code=code.replace("P=E/'document-poppler'","P=E/'caption-smoke-poppler'").replace("E/'verified-export-records.json'","E/'caption-smoke-verified-records.json'").replace("E/'wrap-independent-verification.json'","E/'caption-smoke-independent-verification.json'")
exec(compile(code,str(R/'tools/verify_wrap.py'),'exec'),{'__name__':'final_caption_reader','__file__':str(R/'tools/verify_wrap.py')})
records=json.loads((E/'verified-export-records.json').read_text(encoding='utf-8'));extra=json.loads((E/'caption-smoke-verified-records.json').read_text(encoding='utf-8'));records=list({v['destination']:v for v in records+extra}.values());(E/'verified-export-records.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
a=json.loads((E/'wrap-independent-verification.json').read_text(encoding='utf-8'));b=json.loads((E/'caption-smoke-independent-verification.json').read_text(encoding='utf-8'));a['cases']=list({v['destination']:v for v in a['cases']+b['cases']}.values());(E/'wrap-independent-verification.json').write_text(json.dumps(a,indent=2),encoding='utf-8');assert len(a['cases'])==119
