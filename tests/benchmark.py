"""Isolated persistent-worker timings and a 30-minute silent resource boundary.

The long silent case checks I/O/storage, not sustained neural inference quality.
"""
import hashlib,json,resource,struct,subprocess,tempfile,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
from fixture_support import MODELS
from worker_test import request

def wav(path,seconds,silent=False):
    count=int(seconds*48000);size=count*4
    with path.open('wb') as f:
        f.write(b'RIFF'+struct.pack('<I',36+size)+b'WAVEfmt '+struct.pack('<IHHIIHH',16,3,1,48000,192000,4,32)+b'data'+struct.pack('<I',size))
        if silent:f.truncate(44+size)
        else:
            t=np.arange(count)/48000
            x=(.15*np.sin(2*np.pi*173*t)+.08*np.sin(2*np.pi*367*t))*(.55+.4*np.sin(2*np.pi*.7*t))
            f.write(x.astype('<f4').tobytes())

def main():
    report={'timings':[],'note':'M2 local; Intel physical remains untested. Long silent case skips neural inference inside the core.'}
    fixtures=ROOT/'build/performance-fixtures';fixtures.mkdir(exist_ok=True)
    for seconds in (8,30):wav(fixtures/f'benchmark-{seconds}s.wav',seconds)
    wav(fixtures/'boundary-30min-silence.wav',1800,True)
    with tempfile.TemporaryDirectory(prefix='dialogue-benchmark-',dir=ROOT/'build') as tmp:
        p=subprocess.Popen([str(ROOT/'build/arm64/dialogue-worker'),'--models',str(MODELS)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        assert json.loads(p.stdout.readline())['type']=='ready'
        try:
            for index,name in enumerate(('benchmark-8s','benchmark-8s','benchmark-30s','boundary-30min-silence')):
                source=fixtures/f'{name}.wav';before=(hashlib.sha256(source.read_bytes()).hexdigest(),source.stat().st_mtime_ns)
                started=time.monotonic();ev,events=request(p,{'cmd':'separate','source':str(source),'workspace':tmp,'id':index})
                assert ev['type']=='result',ev
                assert before==(hashlib.sha256(source.read_bytes()).hexdigest(),source.stat().st_mtime_ns)
                report['timings'].append({'case':name,'wall_seconds':time.monotonic()-started,'model_load_seconds':ev['load_seconds'],'process_seconds':ev['process_seconds'],'frames':ev['frames'],'rate':ev['rate'],'input_unchanged':True})
                print(report['timings'][-1],flush=True)
                (ROOT/'evidence/benchmark.json').write_text(json.dumps(report,indent=2))
        finally:p.stdin.close();p.wait(timeout=15)
        report['child_maxrss_bytes']=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        assert p.returncode==0,p.stderr.read()
    (ROOT/'evidence/benchmark.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':main()
