"""Reproducible malformed WAVs and valid recovery, with a bounded real-worker run."""
import json
import os
import random
import subprocess
import tempfile
import wave
from pathlib import Path

root = Path(__file__).resolve().parents[1]
architecture = os.environ.get('DS_TEST_ARCH', 'arm64')
if architecture not in ('arm64', 'x86_64'):
    raise ValueError('Unsupported test architecture')
rng = random.Random(20261027)
with tempfile.TemporaryDirectory(prefix='cauces-wav-fuzz-') as temporary:
    directory = Path(temporary)
    commands = []
    for index in range(100):
        path = directory / f'malformed-{index}.wav'
        path.write_bytes(b'RIFF' + (0xffffffff).to_bytes(4, 'little') + b'WAVE'
                         + rng.randbytes(index * 7))
        commands.append({'cmd': 'inspect', 'source': str(path), 'id': index})
    valid = directory / 'recovery.wav'
    with wave.open(str(valid), 'wb') as output:
        output.setparams((1, 2, 16000, 1, 'NONE', 'not compressed'))
        output.writeframes(b'\0\0')
    commands.append({'cmd': 'inspect', 'source': str(valid), 'id': 100})
    result = subprocess.run([str(root / 'build' / architecture / 'dialogue-worker'),
                             '--models', temporary],
                            input=''.join(json.dumps(c) + '\n' for c in commands),
                            text=True, capture_output=True, timeout=15)
    assert result.returncode == 0, (result.returncode, result.stderr[:500])
    events = [json.loads(line) for line in result.stdout.splitlines()]
    assert len(events) == 102, len(events)
    assert events[0]['type'] == 'ready' and events[0]['architecture'] == architecture, events[0]
    for index, event in enumerate(events[1:101]):
        assert event['type'] == 'error' and event['id'] == index, event
    assert events[-1]['type'] == 'info' and events[-1]['id'] == 100 and events[-1]['frames'] == 1, events[-1]
print(f'{architecture}: 100 deterministic malformed WAVs rejected; valid inspection recovered')
