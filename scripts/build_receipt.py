"""Bind build outputs to source/dependency inputs before packaging."""
import argparse
import hashlib
import json
from pathlib import Path


def sha256(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()


def input_hashes(root,architecture):
    if architecture not in ('arm64','x86_64'):raise ValueError('Unsupported architecture')
    names=['CMakeLists.txt','scripts/build.sh','scripts/build_receipt.py']
    names += [str(p.relative_to(root)) for p in (root/'src').iterdir() if p.is_file()]
    for folder in ['vendor/json/include','vendor/onnxruntime-osx-arm64-1.31.1/include']:
        names += [str(p.relative_to(root)) for p in (root/folder).rglob('*') if p.is_file()]
    runtime='vendor/onnxruntime-osx-arm64-1.31.1/lib/libonnxruntime.1.31.1.dylib' if architecture=='arm64' else 'build/ort-intel-1.31.1/libonnxruntime.1.31.1.dylib'
    names.append(runtime)
    return {name:sha256(root/name) for name in sorted(names)}


def capture(root,architecture):
    return {'architecture':architecture,'deployment_target':'15.0',
            'inputs':input_hashes(root,architecture),
            'outputs':{name:sha256(root/'build'/architecture/name) for name in ['Cauces','dialogue-worker','libdialogue_separator.dylib']}}


def begin(root,architecture):
    directory=root/'build'/architecture
    directory.mkdir(parents=True,exist_ok=True)
    (directory/'build-inputs-pending.json').write_text(json.dumps(input_hashes(root,architecture),indent=2)+'\n')


def record(root,architecture):
    pending=root/'build'/architecture/'build-inputs-pending.json'
    if json.loads(pending.read_text())!=input_hashes(root,architecture):
        raise ValueError('Source or dependencies changed during the build')
    path=root/'build'/architecture/'build-receipt.json'
    path.write_text(json.dumps(capture(root,architecture),indent=2)+'\n')


def verify(root,architecture):
    recorded=json.loads((root/'build'/architecture/'build-receipt.json').read_text())
    if capture(root,architecture)!=recorded:
        raise ValueError('Build inputs or binaries changed: rebuild '+architecture)
    return recorded


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['begin','record','verify'])
    parser.add_argument('architecture',choices=['arm64','x86_64','all'])
    parser.add_argument('--inventory',type=Path)
    args=parser.parse_args();root=Path(__file__).resolve().parents[1]
    try:
        for architecture in (['arm64','x86_64'] if args.architecture=='all' else [args.architecture]):
            {'begin':begin,'record':record,'verify':verify}[args.action](root,architecture)
        if args.inventory:
            inventory=json.loads(args.inventory.read_text())
            for runtime in inventory['runtimes']:
                if sha256(root/runtime['input_library'])!=runtime['input_sha256']:
                    raise ValueError('Runtime differs from reviewed inventory: '+runtime['architecture'])
    except (ValueError,FileNotFoundError) as error:
        parser.exit(1,str(error)+'\n')
