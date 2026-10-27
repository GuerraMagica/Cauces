"""Real worker protocol, source preservation, export collision and error recovery."""
import hashlib,json,os,select,subprocess,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
from local_paths import FIXTURES, MODELS

def request(proc,message):
    if message.get('cmd')=='export' and 'staging' not in message:
        message=dict(message,staging=tempfile.mkdtemp(prefix='.export-',dir=message['destination']))
    proc.stdin.write(json.dumps(message)+'\n');proc.stdin.flush()
    events=[]
    while True:
        line=proc.stdout.readline()
        if not line:raise AssertionError('Worker exited unexpectedly')
        event=json.loads(line);events.append(event)
        if event['type'] in ('info','result','error','exported'):return event,events

def main():
    binary=ROOT/'build/arm64/dialogue-worker'
    assert binary.exists(),'Worker executable is missing'
    with tempfile.TemporaryDirectory(prefix='dialogue-worker-test-') as tmp:
        p=subprocess.Popen([str(binary),'--models',str(MODELS)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            assert json.loads(p.stdout.readline())['type']=='ready'
            ev,_=request(p,{'cmd':'nonsense','id':1});assert ev['type']=='error'
            source=FIXTURES/'signed_zero.wav'
            before=(hashlib.sha256(source.read_bytes()).hexdigest(),source.stat().st_mtime_ns)
            ev,_=request(p,{'cmd':'inspect','source':str(source),'id':2});assert ev['type']=='info' and ev['frames']>0
            ev,_=request(p,{'cmd':'separate','source':str(source),'workspace':tmp,'id':3});assert ev['type']=='result',ev
            assert len(ev['stems'])==3 and all(Path(s).is_file() for s in ev['stems'])
            ev,_=request(p,{'cmd':'export','destination':tmp,'id':4});assert ev['type']=='exported',ev
            target=Path(ev['directory']);assert len(list(target.glob('*.wav')))==3
            hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in target.iterdir()}
            ev,_=request(p,{'cmd':'export','destination':tmp,'id':5});assert ev['type']=='error','existing export overwritten'
            assert hashes=={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in target.iterdir()}
            assert before==(hashlib.sha256(source.read_bytes()).hexdigest(),source.stat().st_mtime_ns)
            for name in ('malformed','empty_48k','nan_float','inf_float','stereo_16k','three_channels','rate_96k','nan_then_stereo','stereo_then_nan'):
                ev,_=request(p,{'cmd':'separate','source':str(FIXTURES/f'{name}.wav'),'workspace':tmp,'id':6})
                assert ev['type']=='error',(name,ev)
            ev,_=request(p,{'cmd':'inspect','source':str(source),'id':7});assert ev['type']=='info'
            assert not list(Path(tmp).glob('.export-*')),'left an export staging directory'
        finally:
            p.stdin.close();p.wait(timeout=10)
            errors=p.stderr.read()
            assert p.returncode==0,errors
        assert not list(Path(tmp).glob('job-*')),'worker left job data after clean shutdown'
        invalid=subprocess.run([str(binary),'--models',tmp],input=json.dumps({'cmd':'separate','source':str(source),'workspace':tmp,'id':9})+'\n',text=True,capture_output=True,timeout=15)
        assert invalid.returncode==0 and json.loads(invalid.stdout.splitlines()[-1])['type']=='error','invalid model accepted or worker crashed'
    print('Worker protocol and export safety passed')
if __name__=='__main__':main()
