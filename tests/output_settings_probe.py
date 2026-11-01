"""Run production settings/player in a signed sandboxed test copy; never shipped."""
import json,plistlib,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
app=Path(sys.argv[1]).resolve()
arch=sys.argv[2] if len(sys.argv)>2 else 'arm64'
assert arch in ('arm64','x86_64')
folder=Path(tempfile.mkdtemp(prefix='output-settings-probe-',dir=ROOT/'build'))
probe=folder/'CaucesOutputAudit.app'
subprocess.run(['cp','-cR',str(app),str(probe)],check=True)
info=plistlib.loads((probe/'Contents/Info.plist').read_bytes())
(probe/'Contents/MacOS'/info['CFBundleExecutable']).unlink()
info.update(CFBundleIdentifier='local.julio.cauces.outputaudit',CFBundleExecutable='CaucesOutputAudit')
(probe/'Contents/Info.plist').write_bytes(plistlib.dumps(info))
subprocess.run(['cp','-c',str(ROOT/('build/performance-fixtures/settings-44k1.wav' if '--source-44k1' in sys.argv else 'build/performance-fixtures/benchmark-8s.wav')),str(probe/'Contents/Resources/audit-input.wav')],check=True)
subprocess.run(['xcrun','swiftc','-swift-version','5','-g','-target',f'{arch}-apple-macos15.0','-module-cache-path',str(ROOT/'build/swift-cache'),str(ROOT/'src/AudioOutput.swift'),str(ROOT/'src/PreviewPlayer.swift'),str(ROOT/'tests/OutputSettingsProbe.swift'),'-o',str(probe/'Contents/MacOS/CaucesOutputAudit')],check=True)
subprocess.run(['codesign','--force','--sign','-','--options','runtime','--entitlements',str(ROOT/'resources/Cauces.entitlements'),str(probe)],check=True)
executable=str(probe/'Contents/MacOS/CaucesOutputAudit')
target=[]
if '--device-id' in sys.argv:
    target=['--device-id',sys.argv[sys.argv.index('--device-id')+1]]
if '--restore-48k' in sys.argv:
    result=subprocess.run([executable,'--restore-rate','48000']+target,capture_output=True,text=True,timeout=20)
    print(result.stdout,result.stderr);sys.exit(result.returncode)
baseline=subprocess.run([executable]+target,capture_output=True,text=True,check=True,timeout=20)
rate=next(line.split()[1] for line in baseline.stdout.splitlines() if line.startswith('RATE_BASELINE '))
try:
    result=subprocess.run([executable,'--clock-only' if '--clock-only' in sys.argv else '--exercise']+target+(['--allow-rejection'] if '--allow-rejection' in sys.argv else []),capture_output=True,text=True,timeout=60)
finally:
    restoration=subprocess.run([executable,'--restore-rate',rate]+target,capture_output=True,text=True,timeout=20)
    assert restoration.returncode==0,restoration.stderr
report={'architecture':arch,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'bundle':str(probe),'scope':'Production output settings/player; synthetic source repeated for four-track transport; requested output; rate restoration supervised','target':target,'rate_rejection_permitted':'--allow-rejection' in sys.argv,'restoration_returncode':restoration.returncode}
(ROOT/f'evidence/cauces-settings-0.4/output-probe-{arch}.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
if '--clock-only' in sys.argv: sys.exit(result.returncode)
assert result.returncode==0 and 'PLAYBACK_SETTINGS_PASS' in result.stdout and 'HARDWARE_RATE_RESTORED' in result.stdout
