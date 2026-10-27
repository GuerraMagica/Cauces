"""Test-only sandboxed bundle built from real controller sources and packaged worker.

No NSOpenPanel automation: source/destination are inside the test bundle/container.
GUI user-selected file grants need a separate manual/UI acceptance test.
"""
import json,plistlib,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
app=Path(sys.argv[1]).resolve()
source=Path(sys.argv[2]).resolve()
architecture=sys.argv[3] if len(sys.argv)>3 else 'arm64'
assert architecture in ('arm64','x86_64')
folder=Path(tempfile.mkdtemp(prefix='sandbox-probe-',dir=ROOT/'build'))
probe=folder/'CaucesAudit.app'
subprocess.run(['cp','-cR',str(app),str(probe)],check=True)
info=plistlib.loads((probe/'Contents/Info.plist').read_bytes())
(probe/'Contents/MacOS'/info['CFBundleExecutable']).unlink()  # test copy only; production app is untouched
info.update(CFBundleIdentifier='local.julio.cauces.audit',CFBundleExecutable='CaucesAudit')
(probe/'Contents/Info.plist').write_bytes(plistlib.dumps(info))
subprocess.run(['cp','-c',str(source),str(probe/'Contents/Resources/audit-input.wav')],check=True)
sources=['JobState','JobController','PreviewPlayer','WorkerConnection','PrivateDirectory','LocalFilePolicy']
command=['xcrun','swiftc','-swift-version','5','-O','-target',f'{architecture}-apple-macos15.0','-module-cache-path',str(ROOT/'build/swift-cache'),'-import-objc-header',str(ROOT/'src/security.h')]
command += [str(ROOT/'src'/f'{name}.swift') for name in sources]
command += [str(ROOT/'tests/SandboxProbe.swift'),str(ROOT/'build'/architecture/'libcauces_security.a'),'-lc++','-o',str(probe/'Contents/MacOS/CaucesAudit')]
subprocess.run(command,check=True)
worker=probe/'Contents/MacOS/dialogue-worker'
thin=folder/'worker-thin'
subprocess.run(['lipo',str(worker),'-thin',architecture,'-output',str(thin)],check=True)
thin.replace(worker)
subprocess.run(['codesign','--force','--sign','-','--options','runtime','--entitlements',str(ROOT/'resources/Worker.entitlements'),str(worker)],check=True)
control=probe/'Contents/MacOS/network-control'
subprocess.run(['clang','-arch',architecture,str(ROOT/'tests/network_denied.c'),'-o',str(control)],check=True)
subprocess.run(['codesign','--force','--sign','-','--options','runtime','--entitlements',str(ROOT/'resources/Worker.entitlements'),str(control)],check=True)
subprocess.run(['codesign','--force','--sign','-','--options','runtime','--entitlements',str(ROOT/'resources/Cauces.entitlements'),str(probe)],check=True)
subprocess.run(['codesign','--verify','--deep','--strict',str(probe)],check=True)
result=subprocess.run([str(probe/'Contents/MacOS/CaucesAudit')],capture_output=True,text=True,timeout=240)
report={'architecture':architecture,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'bundle':str(probe),'scope':'Production controller + packaged worker; test executable replaces GUI entry point; no user-selected grants tested'}
(ROOT/'evidence/security-audit-20261027'/f'sandbox-{architecture}-result.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
assert result.returncode==0 and 'CAUCES_SANDBOX_PASS' in result.stdout
