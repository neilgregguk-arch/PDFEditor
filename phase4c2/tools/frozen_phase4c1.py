from pathlib import Path
import test_engine as base
R=base.ROOT;base.RUN=R.parent/'phase4c1/run'
for name in ['test_wrap' if False else 'test_insertion','test_document','test_position']:
 out=R/'evidence'/('frozen-c1-'+name);out.mkdir(exist_ok=True)
 s=(R.parent/'phase4c1/tools'/(name+'.py')).read_text(encoding='utf-8')
 if name=='test_insertion':s=s.replace('E=b.EVID','E=Path('+repr(str(out))+')')
 else:s=s.replace("E=R/'evidence'",'E=Path('+repr(str(out))+')')
 exec(compile(s,str(R.parent/'phase4c1/tools'/(name+'.py')),'exec'),{'__file__':str(R/'tools'/('frozen-'+name+'.py')),'__name__':'frozen_'+name})
