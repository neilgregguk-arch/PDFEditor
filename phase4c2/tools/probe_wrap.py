import test_engine as b
import json,time
w=b.Worker();d=w.call(Source=str(b.RUN/'corpus/11-word-letter.pdf'))['Data'];r=d['Regions'][0]
for count in [4,5,6,7,9]:
 t=('Phase 3 letter '*count).strip();dest=b.EVID/('probe-wrap-'+str(count)+'.pdf');v=w.call(Command='save',Source=d['Path'],ExpectedHash=d['Hash'],Changes=[dict(Page=0,RegionId=r['Id'],Identity=r['SourceIdentity'],Text=t)],Destination=str(dest));print(count,v['Ok'],v.get('Error') or (v['Data']['Safe'],v['Data']['Diagnostic']));
 if v['Ok'] and v['Data']['Safe']:
  print([(l['Text'],l['Baseline']) for l in v['Data']['Verification']['pages'][0]['regions'][0]['layout']['Positioned']['Lines']]);info=w.call(Source=str(dest))['Data'];print('rediscovery',[(x['OriginalText'],x['Eligibility'],x['Reasons']) for x in info['Regions']]);(b.EVID/('probe-wrap-'+str(count)+'.json')).write_text(json.dumps(dict(source=d['Path'],destination=str(dest),changes=[dict(Page=0,RegionId=r['Id'],Identity=r['SourceIdentity'],Text=t)],result=v['Data']),indent=2),encoding='utf-8')
w.close()
