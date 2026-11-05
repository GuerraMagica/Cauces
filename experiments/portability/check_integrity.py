"""Reject an altered COPY specifically by its hash; preserve originals."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if not __debug__:
    raise SystemExit("Verification requires assertions: do not use -O or PYTHONOPTIMIZE.")

root = Path(__file__).resolve().parent
binary, models, report = (Path(arg).resolve() for arg in sys.argv[1:])
source = models / "separator.onnx"
before = hashlib.sha256(source.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as temporary:
    bad = Path(temporary)
    shutil.copyfile(source, bad / "separator.onnx")
    with (bad / "separator.onnx").open("r+b") as file:
        first = file.read(1);file.seek(0);file.write(bytes([first[0] ^ 1]))
    proc = subprocess.run([str(binary), str(bad), str(root / "fixtures/pcm24_48000.wav"),
                           str(bad / "outputs"), "1"], capture_output=True, text=True, timeout=60)
    assert proc.returncode != 0 and any(s in proc.stderr for s in (
        "assets do not match this version", "asset hash mismatch")), proc.stderr
    assert not (bad / "outputs").exists()
assert hashlib.sha256(source.read_bytes()).hexdigest() == before, "original model changed"
result = dict(passed=True, rejection=proc.stderr.strip(), original_sha256=before,
              original_preserved=True, no_output_created=True)
report.write_text(json.dumps(result, indent=2))
print(json.dumps(result))
