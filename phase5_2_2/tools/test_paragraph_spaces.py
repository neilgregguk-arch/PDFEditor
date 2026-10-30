"""Keep the prior exact-space restriction after whole-paragraph reopening."""
from pathlib import Path
import json,hashlib,time
import test_engine as b
record=json.loads((b.EVID/'roundtrip-tests.json').read_text())['saved'][0];source=Path(record['destination']);w=b.Worker()
try:
 d=w.call(Source=str(source))['Data'];r=next(r for r in d['Regions'] if r.get('Paragraph'));draft=r['OriginalText'].replace('Phase 3','Phase  3',1);destination=b.EVID/('must-not-save-adjacent-spaces-'+str(time.time_ns())+'.pdf');v=w.call(Command='save',Source=str(source),ExpectedHash=d['Hash'],Changes=[dict(Page=r['Page'],RegionId=r['Id'],Identity=r['SourceIdentity'],Text=draft)],Destination=str(destination));assert not v['Ok'] or not v['Data']['Safe'];assert not destination.exists();assert hashlib.sha256(source.read_bytes()).hexdigest()==d['Hash'];assert '  ' in draft
 (b.EVID/'paragraph-space-restriction.json').write_text(json.dumps(dict(success=True,source=str(source),draft=draft,normalised=False,outputCreated=False,result=v,scope='Complete reopened logical draft submitted exactly; inherited exact-extraction restriction remains, no successful export claimed'),indent=2),encoding='utf-8');print('Reopened adjacent-space draft retained exactly; unsafe extraction refused')
finally:w.close()
