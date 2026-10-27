import hashlib,json,plistlib,re,subprocess,tempfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from local_paths import FIXTURES
APP=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'dist/Cauces.app'
def main():
    info=plistlib.loads((APP/'Contents/Info.plist').read_bytes());assert info['LSMinimumSystemVersion']=='15.0'
    for path in (APP/'Contents/MacOS/Cauces',APP/'Contents/MacOS/dialogue-worker',*list((APP/'Contents/Frameworks').glob('*.dylib'))):
        arches=subprocess.check_output(['lipo','-archs',str(path)],text=True).split();assert set(arches)=={'arm64','x86_64'}
        for arch in arches:
            deps=subprocess.check_output(['otool','-arch',arch,'-L',str(path)],text=True)
            for dependency in deps.splitlines()[1:]:
                value=dependency.strip().split(' (')[0]
                assert value.startswith(('@rpath/','/System/Library/','/usr/lib/')),value
                if value.startswith('@rpath/'):assert (APP/'Contents/Frameworks'/value.removeprefix('@rpath/')).is_file(),value
            loads=subprocess.check_output(['otool','-arch',arch,'-l',str(path)],text=True)
            minimum=re.search(r'\bminos (\d+)\.(\d+)',loads)
            assert minimum and (int(minimum[1]),int(minimum[2]))<=(15,0),(path,arch,'deployment target too new')
            rpaths=re.findall(r'cmd LC_RPATH\s+cmdsize \d+\s+path (.+?) \(offset',loads)
            assert all(p.startswith(('@executable_path/','@loader_path')) or p=='/usr/lib/swift' for p in rpaths),rpaths
    subprocess.run(['codesign','--verify','--deep','--strict',str(APP)],check=True)
    models=APP/'Contents/Resources/Models';manifest=json.loads((models/'manifest.json').read_text())
    for item in [*manifest['models'].values(),*manifest['assets']]:assert hashlib.sha256((models/item['file']).read_bytes()).hexdigest()==item['sha256']
    assert manifest['name']=='Cauces Multi-Speaker Separation ONNX v1 (selective FP16)'
    assert info['CFBundleName']=='Cauces'
    for path,required in [(APP/'Contents/MacOS/Cauces',{'com.apple.security.app-sandbox','com.apple.security.files.user-selected.read-write'}),(APP/'Contents/MacOS/dialogue-worker',{'com.apple.security.app-sandbox','com.apple.security.inherit'})]:
        raw=subprocess.check_output(['codesign','-d','--entitlements','-','--xml',str(path)],stderr=subprocess.DEVNULL)
        entitlements=plistlib.loads(raw);assert all(entitlements.get(key) is True for key in required)
        assert not any(entitlements.get(key) for key in ['com.apple.security.network.client','com.apple.security.network.server','com.apple.security.cs.allow-dyld-environment-variables','com.apple.security.get-task-allow'])
        signature=subprocess.check_output(['codesign','-dvv',str(path)],stderr=subprocess.STDOUT,text=True)
        assert 'runtime' in signature
    print('Universal self-contained signed package passed')
if __name__=='__main__':main()
