"""Create local release archives from a committed source tree; never upload assets."""
import argparse
import hashlib
import json
import plistlib
import subprocess
import tarfile
import tempfile
from pathlib import Path


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            digest.update(block)
    return digest.hexdigest()


def prepare(root, app, output, commit):
    commit = subprocess.check_output(['git','rev-parse',commit+'^{commit}'],cwd=root,text=True).strip()
    if commit != subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip():
        raise ValueError('Use the tested HEAD commit for the paired source archive')
    if subprocess.check_output(['git','status','--porcelain','--untracked-files=normal'],cwd=root,text=True).strip():
        raise ValueError('Commit all release source changes before creating paired source archives')
    info = plistlib.loads((app/'Contents/Info.plist').read_bytes())
    if info != plistlib.loads((root/'resources/Info.plist').read_bytes()):
        raise ValueError('App version/build information differs from the source commit')
    from package_licenses import source_inputs
    if json.loads((app/'Contents/Resources/SOURCE_INPUTS.json').read_text()) != source_inputs(root):
        raise ValueError('App source/licence inputs differ from the committed source tree')
    label = 'Cauces-'+info['CFBundleShortVersionString']+'-build'+info['CFBundleVersion']
    if output.exists():
        raise FileExistsError(output)
    if app in output.parents:
        raise ValueError('The delivery directory must be outside the signed app')
    if app.is_symlink() or any(p.is_symlink() for p in app.rglob('*')):
        raise ValueError('The application archive must not contain symlinks')
    inventory = json.loads((root/'docs/release/dependency-inventory.json').read_text())
    from audit_dependencies import verify_dependency_trees
    dependency_sources=verify_dependency_trees(root,inventory)
    if any(path==output or path in output.parents for path in dependency_sources.values()):
        raise ValueError('Delivery must be outside dependency source trees')
    arm_archive=root/'vendor/onnxruntime-arm64-src-1.31.1.tar.gz'
    if sha256(arm_archive)!=inventory['runtimes'][0]['source_archive_sha256']:
        raise ValueError('ARM upstream source archive differs from the reviewed archive')
    intel=root/'vendor/onnxruntime-src-1.31.1'
    intel_commit=inventory['runtimes'][1]['source_commit']
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=intel,text=True).strip()!=intel_commit:
        raise ValueError('Intel source revision differs')
    subprocess.run(['git','diff','--exit-code','HEAD','--'],cwd=intel,check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['codesign','--verify','--deep','--strict',str(app)],check=True)
    output.mkdir(parents=True)
    app_zip = output/(label+'-universal.zip')
    subprocess.run(['ditto','-c','-k','--sequesterRsrc','--keepParent',str(app),str(app_zip)],check=True)
    sources = output/(label+'-sources.tar.gz')
    subprocess.run(['git','archive','--format=tar.gz','--prefix='+label+'-sources/',
                    '-o',str(sources),commit],cwd=root,check=True)
    dep_sources = output/(label+'-third-party-sources.tar.gz')
    with tempfile.TemporaryDirectory(prefix='cauces-third-party-') as temporary:
        intel_archive=Path(temporary)/'onnxruntime-x86_64.tar'
        subprocess.run(['git','archive','--format=tar','-o',str(intel_archive),intel_commit],cwd=intel,check=True)
        with tarfile.open(dep_sources,'w:gz') as archive:
            archive.add(arm_archive,arcname=label+'-third-party-sources/onnxruntime-arm64-upstream.tar.gz')
            archive.add(intel_archive,arcname=label+'-third-party-sources/onnxruntime-x86_64-upstream.tar')
            for name,path in sorted(dependency_sources.items()):
                archive.add(path,arcname=label+'-third-party-sources/'+name)
    files = [app_zip,sources,dep_sources]
    manifest = {
        'version':info['CFBundleShortVersionString'],'build':info['CFBundleVersion'],
        'source_commit':commit,'signature':'ad_hoc_not_notarized',
        'distribution_status':'local_candidate_model_redistribution_rights_pending',
        'files':{p.name:{'sha256':sha256(p),'bytes':p.stat().st_size} for p in files},
        'third_party_sources':{'arm64_commit':inventory['runtimes'][0]['source_commit'],'x86_64_commit':intel_commit,'verified_dependency_trees':inventory['local_source_trees']},
        'dependency_inventory':'docs/release/dependency-inventory.json',
        'source_scope':'project source plus exact runtime source revisions and locally available pinned CPU dependency trees; vendor ARM build options and exact transitive binary inclusion not supplied',
        'unresolved_acceptance':['professional_listening','physical_Intel','Pro_Tools','manual_GUI','Internet_Gatekeeper']
    }
    manifest_path = output/(label+'-manifest.json')
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    files.append(manifest_path)
    (output/'SHA256SUMS').write_text(''.join(sha256(p)+'  '+p.name+'\n' for p in files))
    print(output)

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--commit',default='HEAD')
    args=parser.parse_args()
    try:
        prepare(Path(__file__).resolve().parents[1],args.app.resolve(),args.output.resolve(),args.commit)
    except (ValueError,FileNotFoundError,FileExistsError) as error:
        parser.exit(1,str(error)+'\n')
