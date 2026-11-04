import hashlib,json,plistlib,re,subprocess,tempfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from local_paths import FIXTURES
source_info=plistlib.loads((ROOT/'resources/Info.plist').read_bytes())
APP=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/('dist/Cauces-'+source_info['CFBundleShortVersionString']+'-build'+source_info['CFBundleVersion']+'/Cauces.app')
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
    assert info['CFBundleDevelopmentRegion']=='en' and info['CFBundleLocalizations']==['en']
    icon=APP/'Contents/Resources'/info['CFBundleIconFile']
    assert icon.read_bytes()[:4]==b'icns'
    for asset in ['FlowArtwork.png','FlowArtwork@2x.png']:
        assert (APP/'Contents/Resources'/asset).read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
    for path,required in [(APP/'Contents/MacOS/Cauces',{'com.apple.security.app-sandbox','com.apple.security.files.user-selected.read-write'}),(APP/'Contents/MacOS/dialogue-worker',{'com.apple.security.app-sandbox','com.apple.security.inherit'})]:
        raw=subprocess.check_output(['codesign','-d','--entitlements','-','--xml',str(path)],stderr=subprocess.DEVNULL)
        entitlements=plistlib.loads(raw);assert all(entitlements.get(key) is True for key in required)
        assert not any(entitlements.get(key) for key in ['com.apple.security.network.client','com.apple.security.network.server','com.apple.security.cs.allow-dyld-environment-variables','com.apple.security.get-task-allow'])
        signature=subprocess.check_output(['codesign','-dvv',str(path)],stderr=subprocess.STDOUT,text=True)
        assert 'runtime' in signature
    licences=APP/'Contents/Resources/Licenses'
    for name in ['GPL-3.0-only.txt','Apache-2.0.txt','COPYRIGHT','LICENSE_SCOPE.md',
                 'ONNXRuntime-LICENSE','ONNXRuntime-ThirdPartyNotices.txt',
                 'nlohmann-json-LICENSE','nlohmann-json-HEADER-NOTICES.txt',
                 'Model-NOTICE.txt','dependency-inventory.json','SOURCE_INFORMATION.md']:
        assert (licences/name).is_file(),name
    assert (licences/'GPL-3.0-only.txt').read_bytes()==(ROOT/'LICENSE').read_bytes()
    assert (licences/'Apache-2.0.txt').read_bytes()==(ROOT/'docs/commercial/licenses/Apache-2.0.txt').read_bytes()
    assert (APP/'Contents/Resources/SOURCE_INPUTS.json').is_file()
    inventory=json.loads((licences/'dependency-inventory.json').read_text())
    assert inventory['json']['version']=='3.11.3'
    assert manifest['integration']['onnx_conversion_author'] is None
    assert manifest['integration']['refiner_author'] is None
    assert manifest['integration']['base_model_licence_declared']=='Apache-2.0'
    assert manifest['integration']['refiner_licence_status']=='not_determined'
    print('Universal self-contained signed package and scoped licence material passed')
if __name__=='__main__':main()
