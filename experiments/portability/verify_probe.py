"""Local deterministic synthetic corpus, independent RIFF checks and comparison.

Only Python standard library. Never uploads data. Nonzero signals are mathematical
test signals, not speech; these checks cannot establish perceptual quality.
"""
import argparse
import hashlib
import json
import math
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

if not __debug__:
    raise SystemExit("Verification requires assertions: do not use -O or PYTHONOPTIMIZE.")

ROOT = Path(__file__).resolve().parent
STEMS = ("speaker_1.wav", "speaker_2.wav", "noise.wav")
ATOL, RTOL = 1e-5, 1e-4


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def chunk(tag, data):
    return tag + struct.pack("<I", len(data)) + data + b"\0" * (len(data) % 2)


def encode(rate, channels, bits, floating, samples, time_reference):
    fmt = struct.pack("<HHIIHH", 3 if floating else 1, channels, rate,
                      rate * channels * bits // 8, channels * bits // 8, bits)
    data = bytearray()
    for sample in samples:
        if floating:
            raw = struct.pack("<f", sample)
        else:
            scale = 1 << (bits - 1)
            value = max(-scale, min(scale - 1, round(sample * scale)))
            raw = int(value).to_bytes(bits // 8, "little", signed=True)
        data.extend(raw * channels)
    body = b"WAVE" + chunk(b"fmt ", fmt)
    if time_reference is not None:
        bext = bytearray(602)
        struct.pack_into("<Q", bext, 338, time_reference)
        body += chunk(b"bext", bext)
    body += chunk(b"data", data)
    return b"RIFF" + struct.pack("<I", len(body)) + body


def read_wav(path):
    raw = Path(path).read_bytes()
    assert raw[:4] == b"RIFF" and raw[8:12] == b"WAVE", "bad RIFF header"
    assert struct.unpack_from("<I", raw, 4)[0] + 8 == len(raw), "RIFF size mismatch"
    fmt = data = None
    time_reference = None
    pos = 12
    while pos < len(raw):
        assert pos + 8 <= len(raw), "truncated chunk"
        tag, length = struct.unpack_from("<4sI", raw, pos)
        value = raw[pos + 8:pos + 8 + length]
        assert len(value) == length, "truncated chunk body"
        if tag == b"fmt ":
            assert fmt is None, "duplicate fmt"
            fmt = struct.unpack_from("<HHIIHH", value)
        elif tag == b"data":
            assert data is None, "duplicate data"
            data = value
        elif tag == b"bext":
            assert len(value) >= 602 and time_reference is None, "bad bext"
            time_reference = struct.unpack_from("<Q", value, 338)[0]
        pos += 8 + length + length % 2
    assert fmt is not None and data is not None, "missing fmt/data"
    code, channels, rate, byte_rate, align, bits = fmt
    assert align == channels * bits // 8 and byte_rate == rate * align, "bad alignment"
    assert len(data) % align == 0 and channels in (1, 2), "bad sample count/channels"
    if code == 3 and bits == 32:
        samples = [v[0] for v in struct.iter_unpack("<f", data)]
    else:
        assert code == 1 and bits in (16, 24), "unsupported test format"
        step = bits // 8
        samples = [int.from_bytes(data[i:i + step], "little", signed=True) / (1 << (bits - 1))
                   for i in range(0, len(data), step)]
    return dict(rate=rate, channels=channels, bits=bits, format=code,
                frames=len(data) // align, time_reference=time_reference,
                samples=samples, data_sha256=hashlib.sha256(data).hexdigest())


def generate():
    folder = ROOT / "fixtures"
    folder.mkdir(exist_ok=True)
    cases = [
        ("pcm16_44100", 44100, 1, 16, False, 2206, "tone", 0),
        ("pcm24_48000", 48000, 1, 24, False, 2401, "tone", 0x123456789ABC),
        ("float32_8000", 8000, 1, 32, True, 511, "tone", None),
        ("boundary513_16000", 16000, 1, 32, True, 513, "tone", 1234567890123),
        ("impulse512_16000", 16000, 1, 32, True, 512, "impulse", 999),
        ("dualmono_48000", 48000, 2, 32, True, 2401, "tone", 0x100000001),
        ("silence_48000", 48000, 1, 32, True, 241, "silence", 1),
        ("signed_zero_16000", 16000, 1, 32, True, 1, "signed_zero", None),
        ("chunk8_plus_16000", 16000, 1, 32, True, 128001, "tone", 48000 * 3600),
    ]
    manifest = []
    for name, rate, channels, bits, floating, frames, kind, reference in cases:
        def value(i):
            if kind == "silence": return 0.0
            if kind == "signed_zero": return -0.0
            if kind == "impulse": return .25 if i == 0 else 0.0
            t = i / rate
            envelope = .55 + .45 * math.sin(2 * math.pi * 2.7 * t)
            return envelope * (.17 * math.sin(2 * math.pi * 173 * t)
                               + .09 * math.sin(2 * math.pi * 431 * t)
                               + .03 * math.sin(2 * math.pi * (701 * t + 43 * t * t)))
        path = folder / f"{name}.wav"
        content = encode(rate, channels, bits, floating, [value(i) for i in range(frames)], reference)
        if path.exists():
            assert path.read_bytes() == content, f"refusing to replace changed fixture: {path}"
        else:
            path.write_bytes(content)
        manifest.append(dict(name=name, sha256=digest(path), rate=rate, channels=channels,
                             frames=frames, bits=bits, time_reference=reference, signal=kind))
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"Generated/verified {len(manifest)} synthetic fixtures")


def validate_export(source, outputs):
    for output in outputs:
        for key in ("rate", "channels", "frames", "time_reference"):
            assert output[key] == source[key], f"{key} changed"
        assert output["format"] == 3 and output["bits"] == 32, "output must be float32"
        assert all(math.isfinite(v) for v in output["samples"]), "nonfinite output"
        if source["channels"] == 2:
            assert output["samples"][0::2] == output["samples"][1::2], "dual mono changed"
    residual_error = max(abs(sum(o["samples"][i] for o in outputs) - sample)
                         for i, sample in enumerate(source["samples"]))
    assert residual_error <= 1e-6, f"stem reconstruction error: {residual_error}"
    return residual_error


def run(binary, models, destination):
    binary, models, destination = binary.resolve(), models.resolve(), destination.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    report = dict(binary=str(binary), binary_sha256=digest(binary), cases=[], passed=False)
    manifest = json.loads((ROOT / "fixtures/manifest.json").read_text())
    try:
        for case in manifest:
            path = ROOT / "fixtures" / (case["name"] + ".wav")
            assert digest(path) == case["sha256"], "fixture was modified"
            output = destination / case["name"]
            command = [str(binary), str(models), str(path), str(output), "1"]
            proc = subprocess.run(command, capture_output=True, text=True, timeout=900)
            assert proc.returncode == 0, proc.stderr
            decoded = [read_wav(output / stem) for stem in STEMS]
            source = read_wav(path)
            error = validate_export(source, decoded)
            if case["signal"] in ("tone", "impulse"):
                assert any(v != 0 for o in decoded[:2] for v in o["samples"]), "voices are zero"
            before = [digest(output / stem) for stem in STEMS]
            refused = subprocess.run(command, capture_output=True, text=True, timeout=900)
            assert refused.returncode != 0, "existing output was overwritten"
            assert before == [digest(output / stem) for stem in STEMS], "existing output changed"
            assert digest(path) == case["sha256"], "input changed"
            item = dict(name=case["name"], passed=True, timing=proc.stdout.strip(),
                        reconstruction_max_abs=error, overwrite_refused=True,
                        outputs=[{k: v for k, v in o.items() if k != "samples"} for o in decoded])
            report["cases"].append(item)
            print(case["name"], "PASS", proc.stdout.strip(), flush=True)
        # Only a COPY of separator is modified; originals are never opened for writing.
        with tempfile.TemporaryDirectory() as temporary:
            bad = Path(temporary)
            shutil.copyfile(models / "separator.onnx", bad / "separator.onnx")
            with (bad / "separator.onnx").open("r+b") as file:
                first = file.read(1);file.seek(0);file.write(bytes([first[0] ^ 1]))
            proc = subprocess.run([str(binary), str(bad), str(ROOT / "fixtures/pcm24_48000.wav"),
                                   str(bad / "outputs"), "1"], capture_output=True, text=True, timeout=60)
            assert proc.returncode != 0 and any(message in proc.stderr for message in (
                "assets do not match this version", "asset hash mismatch")), proc.stderr
            assert not (bad / "outputs").exists(), "bad model produced output"
        report["corrupt_model_rejected"] = True
        report["passed"] = True
    finally:
        (destination / "report.json").write_text(json.dumps(report, indent=2))
    print("All export contracts PASS")


def compare(reference, candidate):
    cases = json.loads((ROOT / "fixtures/manifest.json").read_text())
    report = dict(atol=ATOL, rtol=RTOL, reference=str(reference), candidate=str(candidate),
                  cases=[], passed=True)
    for case in cases:
        item = dict(name=case["name"], stems={})
        source = read_wav(ROOT / "fixtures" / (case["name"] + ".wav"))
        validate_export(source, [read_wav(reference / case["name"] / s) for s in STEMS])
        validate_export(source, [read_wav(candidate / case["name"] / s) for s in STEMS])
        for stem in STEMS:
            a = read_wav(reference / case["name"] / stem)
            b = read_wav(candidate / case["name"] / stem)
            stats = sample_stats(a["samples"], b["samples"])
            stats["data_bit_exact"] = a["data_sha256"] == b["data_sha256"]
            item["stems"][stem] = stats
            report["passed"] = report["passed"] and stats["outside_tolerance"] == 0
        report["cases"].append(item)
    return report


def sample_stats(reference, candidate):
    assert len(reference) == len(candidate) and reference, "comparison length mismatch"
    assert all(math.isfinite(v) for v in reference + candidate), "nonfinite comparison"
    differences = [abs(x - y) for x, y in zip(reference, candidate)]
    return dict(max_abs=max(differences),
                outside_tolerance=sum(d > ATOL + RTOL * abs(x) for d, x in zip(differences, reference)),
                rms_error=math.sqrt(sum(d*d for d in differences)/len(differences)))


def self_test():
    source = dict(rate=48000, channels=1, frames=1, time_reference=0, samples=[.25])
    output = dict(source, format=3, bits=32)
    validate_export(source, [dict(output, samples=[.1]), dict(output, samples=[.1]), dict(output, samples=[.05])])
    for changed in (dict(output, time_reference=1), dict(output, frames=2),
                    dict(output, samples=[float("nan")]), dict(output, bits=16),
                    dict(output, samples=[.5])):
        try:
            validate_export(source, [changed, dict(output, samples=[0]), dict(output, samples=[0])])
        except AssertionError:
            continue
        raise AssertionError("verifier accepted altered audio/metadata")
    assert sample_stats([.25], [.35])["outside_tolerance"] == 1
    assert sample_stats([.25], [.250001])["outside_tolerance"] == 0
    assert sample_stats([0.0], [2e-5])["outside_tolerance"] == 1
    print("Verifier controls PASS: metadata/length/NaN/format/audio corruption and numerical divergence detected")


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("generate")
    commands.add_parser("self-test")
    runner = commands.add_parser("run")
    runner.add_argument("binary", type=Path);runner.add_argument("models", type=Path)
    runner.add_argument("destination", type=Path)
    comparator = commands.add_parser("compare")
    comparator.add_argument("reference", type=Path);comparator.add_argument("candidate", type=Path)
    comparator.add_argument("report", type=Path)
    args = parser.parse_args()
    if args.command == "generate": generate()
    elif args.command == "self-test": self_test()
    elif args.command == "run": run(args.binary, args.models, args.destination)
    else:
        report = compare(args.reference, args.candidate)
        args.report.write_text(json.dumps(report, indent=2))
        maximum = max(s["max_abs"] for c in report["cases"] for s in c["stems"].values())
        print("PASS" if report["passed"] else "FAIL", "max_abs=", maximum)
        if not report["passed"]: sys.exit(1)


if __name__ == "__main__":
    main()
