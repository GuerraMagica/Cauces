"""Adversarial stdin stays bounded and does not crash the actual worker."""
import json, os, subprocess, sys, tempfile, wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
architecture=os.environ.get('DS_TEST_ARCH','arm64')
if architecture not in ('arm64','x86_64'):raise ValueError('Unsupported test architecture')
binary=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'build'/architecture/'dialogue-worker'
cases=[
 ('deep', '{"cmd":"nonsense","id":'+'['*50000+'0'+']'*50000+'}\n'),
 ('oversized', ' '*1048577+'\n'),
 ('unsigned-id', '{"cmd":"nonsense","id":18446744073709551615}\n'),
 ('object-id', '{"cmd":"nonsense","id":{"x":1}}\n'),
 ('array-command', '[]\n'),
 ('malformed', '{bad}\n'),
]
with tempfile.TemporaryDirectory(prefix='cauces-protocol-') as tmp:
 for label,payload in cases:
  result=subprocess.run([str(binary),'--models',tmp],input=payload+'{"cmd":"nonsense","id":42}\n',text=True,capture_output=True,timeout=10)
  assert result.returncode==0,(label,result.returncode,result.stderr[:500])
  events=[json.loads(line) for line in result.stdout.splitlines()]
  if 'DS_TEST_ARCH' in os.environ:assert events[0]['architecture']==architecture,(architecture,events[0])
  assert len(events)==3 and events[1]['type']=='error' and events[2]['id']==42,(label,events)
  assert events[1].get('id') is None,(label,'malformed input id reflected')
print(f'{len(cases)} adversarial protocol cases rejected; worker recovers')

for argument in ['abc','0','65','4garbage','99999999999999999999999999999']:
 result=subprocess.run([str(binary),'--models','/tmp','--threads',argument],capture_output=True,timeout=5)
 assert result.returncode==2,(argument,result.returncode)
print('5 malformed thread arguments rejected without crash')

# Missing nonblocking/regular-file checks must cause rejection/recovery failure
# or an external timeout, rather than hanging the whole suite.
with tempfile.TemporaryDirectory(prefix='cauces-worker-fifo-') as tmp:
 source=Path(tmp)/'fifo.wav';os.mkfifo(source,0o600)
 regular=Path(tmp)/'regular.wav'
 with wave.open(str(regular),'wb') as output:
  output.setparams((1,2,16000,1,'NONE','not compressed'));output.writeframes(b'\0\0')
 for command in ('inspect','separate'):
  messages=[{'cmd':command,'source':str(source),'workspace':tmp,'id':1},
            {'cmd':'inspect','source':str(regular),'id':2}]
  result=subprocess.run([str(binary),'--models',tmp],input=''.join(json.dumps(v)+'\n' for v in messages),text=True,capture_output=True,timeout=5)
  assert result.returncode==0,(command,result.returncode,result.stderr[:500])
  events=[json.loads(line) for line in result.stdout.splitlines()]
  assert len(events)==3 and events[1]['type']=='error' and events[1]['id']==1,(command,events)
  assert events[2]['type']=='info' and events[2]['id']==2 and events[2]['frames']==1,(command,events)
print(f'{architecture}: inspector and source hash reject FIFO without blocking; worker recovers')
