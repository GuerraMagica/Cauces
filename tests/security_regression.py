"""Adversarial stdin stays bounded and does not crash the actual worker."""
import json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
binary=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'build/arm64/dialogue-worker'
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
  assert len(events)==3 and events[1]['type']=='error' and events[2]['id']==42,(label,events)
  assert events[1].get('id') is None,(label,'malformed input id reflected')
print(f'{len(cases)} adversarial protocol cases rejected; worker recovers')

for argument in ['abc','0','65','4garbage','99999999999999999999999999999']:
 result=subprocess.run([str(binary),'--models','/tmp','--threads',argument],capture_output=True,timeout=5)
 assert result.returncode==2,(argument,result.returncode)
print('5 malformed thread arguments rejected without crash')
