import hashlib,json,plistlib,re,subprocess,tempfile,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
APP=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'dist/Separador de diálogo.app'
def main():
    info=plistlib.loads((APP/'Contents/Info.plist').read_bytes());assert info['LSMinimumSystemVersion']=='15.0'
    for path in (APP/'Contents/MacOS/DialogueSeparator',APP/'Contents/MacOS/dialogue-worker',*list((APP/'Contents/Frameworks').glob('*.dylib'))):
        arches=subprocess.check_output(['lipo','-archs',str(path)],text=True).split();assert set(arches)=={'arm64','x86_64'}
        for arch in arches:
            deps=subprocess.check_output(['otool','-arch',arch,'-L',str(path)],text=True)
            for dependency in deps.splitlines()[1:]:
                value=dependency.strip().split(' (')[0]
                assert value.startswith(('@rpath/','/System/Library/','/usr/lib/')),value
            loads=subprocess.check_output(['otool','-arch',arch,'-l',str(path)],text=True)
            minimum=re.search(r'\bminos (\d+)\.(\d+)',loads)
            assert minimum and (int(minimum[1]),int(minimum[2]))<=(15,0),(path,arch,'deployment target too new')
            rpaths=re.findall(r'cmd LC_RPATH\s+cmdsize \d+\s+path (.+?) \(offset',loads)
            assert all(p.startswith(('@executable_path/','@loader_path')) or p=='/usr/lib/swift' for p in rpaths),rpaths
    subprocess.run(['codesign','--verify','--deep','--strict',str(APP)],check=True)
    models=APP/'Contents/Resources/Models';manifest=json.loads((models/'manifest.json').read_text())
    for item in [*manifest['models'].values(),*manifest['assets']]:assert hashlib.sha256((models/item['file']).read_bytes()).hexdigest()==item['sha256']
    for prefix in ([],['arch','-x86_64']):
        with tempfile.TemporaryDirectory(prefix='dialogue-package-test-') as tmp:
            p=subprocess.run([*prefix,str(APP/'Contents/MacOS/dialogue-worker'),'--models',str(models)],input=json.dumps({'cmd':'separate','source':str(ROOT.parent/'voxuno-investigation/fixtures/tone44k1.wav'),'workspace':tmp,'id':1})+'\n',text=True,capture_output=True,timeout=30)
            assert p.returncode==0,p.stderr
            events=[json.loads(line) for line in p.stdout.splitlines()]
            assert events[-1]['type']=='result',events
    print('Universal self-contained signed package passed')
if __name__=='__main__':main()
