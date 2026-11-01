"""Real worker/API gates reject each unapproved, missing or FIFO model asset.

Only a test-owned clone is modified. Subprocess timeouts detect a blocking FIFO
without hanging ctypes in the parent test runner.
"""
import ctypes
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

from local_paths import ROOT, MODELS

ASSETS = ('separator.onnx', 'refiner.onnx', 'weights.bin')
ARCHITECTURE = os.environ.get('DS_TEST_ARCH', platform.machine())
if ARCHITECTURE not in ('arm64', 'x86_64'):
    raise ValueError('Unsupported test architecture')


def api_probe(directory, expected):
    assert platform.machine() == ARCHITECTURE, 'API probe is running the wrong architecture'
    library = ctypes.CDLL(str(ROOT / 'build' / ARCHITECTURE / 'libdialogue_separator.dylib'))
    library.ds_create.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_size_t]
    library.ds_create.restype = ctypes.c_void_p
    library.ds_destroy.argtypes = [ctypes.c_void_p]
    library.ds_destroy.restype = None
    error = ctypes.create_string_buffer(512)
    context = library.ds_create(os.fsencode(directory), 1, error, len(error))
    if context:
        library.ds_destroy(context)
    if expected == 'accept':
        assert context, error.value
    else:
        assert not context and b'integrity' in error.value.lower(), (bool(context), error.value)
    print(f'API {ARCHITECTURE}: {expected}')


def fingerprint(path):
    info = path.stat()
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return info.st_size, info.st_mtime_ns, digest.hexdigest()


def clone_asset(source, destination):
    if destination.exists():
        destination.unlink()  # only inside this private test clone
    subprocess.run(['/bin/cp', '-c', str(source), str(destination)], check=True)


def main():
    before = {name: fingerprint(MODELS / name) for name in ASSETS}
    worker = ROOT / 'build' / ARCHITECTURE / 'dialogue-worker'
    try:
        with tempfile.TemporaryDirectory(prefix='cauces-model-gates-', dir=ROOT / 'build') as temporary:
            root = Path(temporary)
            models = root / 'models'
            models.mkdir(mode=0o700)
            for name in ASSETS:
                clone_asset(MODELS / name, models / name)
            source = root / 'source.wav'
            with wave.open(str(source), 'wb') as output:
                output.setparams((1, 2, 16000, 512, 'NONE', 'not compressed'))
                output.writeframes(b'\x00\x40' + b'\0\0' * 511)

            def check_gates(expected, label):
                # A universal Python exec may return to ARM64 from a Rosetta
                # parent unless the architecture is requested explicitly.
                api = subprocess.run(['/usr/bin/arch', '-' + ARCHITECTURE, sys.executable,
                                      str(Path(__file__).resolve()), '--api-probe', str(models), expected],
                                     capture_output=True, text=True, timeout=15)
                assert api.returncode == 0, (label, 'API', api.returncode, api.stdout, api.stderr)
                request = {'cmd': 'separate', 'id': 1, 'source': str(source), 'workspace': str(root)}
                result = subprocess.run([str(worker), '--models', str(models)],
                                        input=json.dumps(request) + '\n', capture_output=True,
                                        text=True, timeout=15)
                assert result.returncode == 0, (label, 'worker', result.returncode, result.stderr)
                events = [json.loads(line) for line in result.stdout.splitlines()]
                assert events[0]['type'] == 'ready' and events[0]['architecture'] == ARCHITECTURE, events
                final = events[-1]
                if expected == 'accept':
                    assert final['type'] == 'result' and final['frames'] == 512, final
                else:
                    assert final['type'] == 'error' and 'integrity' in final['message'].lower(), (label, final)
                print(f'{ARCHITECTURE}: {label}: API and worker {expected}', flush=True)

            check_gates('accept', 'approved assets control')
            for name in ASSETS:
                target = models / name
                for mode in ('altered', 'missing', 'fifo'):
                    if mode == 'altered':
                        with target.open('r+b') as asset:
                            value = asset.read(1)
                            asset.seek(0)
                            asset.write(bytes([value[0] ^ 1]))
                    else:
                        target.unlink()
                        if mode == 'fifo':
                            os.mkfifo(target, 0o600)
                    check_gates('reject', name + ' ' + mode)
                    clone_asset(MODELS / name, target)
            check_gates('accept', 'restored assets control')
    finally:
        assert before == {name: fingerprint(MODELS / name) for name in ASSETS}, 'Original model assets changed'
    print(f'{ARCHITECTURE}: 18 isolated asset rejections, valid controls and original integrity passed')


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == '--api-probe':
        api_probe(sys.argv[2], sys.argv[3])
    else:
        main()
