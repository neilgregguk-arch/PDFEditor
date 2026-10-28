from pathlib import Path
import subprocess,json,time,statistics
R=Path(__file__).resolve().parents[1];E=R/'evidence';rows=[]
def start(version):return subprocess.Popen([str(R.parent/version/'run/PdfWorker.exe')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,encoding='utf-8')
def call(p,version,path):
 q=dict(Source=str(path),Command='inspect',Work=str(R/'test-work'/('matrix-'+version)));t=time.perf_counter();p.stdin.write(json.dumps(q)+'\n');p.stdin.flush();a=json.loads(p.stdout.readline());assert a['Ok'],a;return a['Data'],(time.perf_counter()-t)*1000
old=start('phase4a');new=start('phase4a1')
for path in sorted(p for folder in ['corpus','font-corpus','position-corpus'] for p in (R/'run'/folder).glob('*.pdf')):
 a,ta=call(old,'old',path);b,tb=call(new,'new',path)
 rows.append(dict(source=str(path),name=path.relative_to(R/'run').as_posix(),phase4aMs=ta,phase4a1Ms=tb,phase4a=a['Regions'],phase4a1=b['Regions']))
for p in [old,new]:p.stdin.close();p.wait(timeout=10)
bench=R/'run/corpus/11-word-letter.pdf';new=start('phase4a1');cold,ms=call(new,'cache',bench);warm=[call(new,'cache',bench)[1] for _ in range(8)];new.stdin.close();new.wait(timeout=10)
(E/'position-matrix.json').write_text(json.dumps(dict(cases=rows,timings=dict(phase4aMedianMs=statistics.median(r['phase4aMs'] for r in rows),phase4a1MedianMs=statistics.median(r['phase4a1Ms'] for r in rows),wordColdMs=ms,wordWarmMedianMs=statistics.median(warm),wordWarmMs=warm)),indent=2));print('Compared',len(rows),'identical source files; fresh Word',round(ms,2),'ms, warm median',round(statistics.median(warm),2),'ms')
