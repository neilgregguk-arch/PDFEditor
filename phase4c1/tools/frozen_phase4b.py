from pathlib import Path
import test_engine as base
R=base.ROOT;base.RUN=R.parent/'phase4b/run'
for name in ['test_document','test_position']:
 out=R/'evidence'/('frozen-phase4b-'+name);out.mkdir(exist_ok=True)
 s=(R.parent/'phase4b/tools'/(name+'.py')).read_text(encoding='utf-8').replace("E=R/'evidence'",'E=Path('+repr(str(out))+')')
 exec(compile(s,str(R.parent/'phase4b/tools'/(name+'.py')),'exec'),{'__file__':str(R/'tools'/('frozen-'+name+'.py')),'__name__':'frozen_'+name})
