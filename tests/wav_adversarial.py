"""Reproducible malformed RIFF inputs never crash the persistent inspector."""
import json,random,subprocess,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
rng=random.Random(20261027)
with tempfile.TemporaryDirectory(prefix='cauces-wav-fuzz-') as tmp:
 p=subprocess.Popen([str(root/'build/arm64/dialogue-worker'),'--models',tmp],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 assert json.loads(p.stdout.readline())['type']=='ready'
 for index in range(100):
  path=Path(tmp)/'malformed.wav'
  path.write_bytes(b'RIFF'+(0xffffffff).to_bytes(4,'little')+b'WAVE'+rng.randbytes(index*7))
  p.stdin.write(json.dumps({'cmd':'inspect','source':str(path),'id':index})+'\n');p.stdin.flush()
  event=json.loads(p.stdout.readline());assert event['type']=='error' and event['id']==index,event
 p.stdin.close();assert p.wait(timeout=10)==0
 print('100 deterministic malformed WAV cases rejected; inspector recovered throughout')
