"""Copy release licence material only after checking every required input."""
import json
import shutil
import sys
from pathlib import Path

MATERIAL = {
    'LICENSE':'GPL-3.0-only.txt', 'COPYRIGHT':'COPYRIGHT',
    'LICENSE_SCOPE.md':'LICENSE_SCOPE.md',
    'docs/commercial/licenses/Apache-2.0.txt':'Apache-2.0.txt',
    'vendor/onnxruntime-osx-arm64-1.31.1/LICENSE':'ONNXRuntime-LICENSE',
    'vendor/onnxruntime-osx-arm64-1.31.1/ThirdPartyNotices.txt':'ONNXRuntime-ThirdPartyNotices.txt',
    'vendor/json/LICENSE.MIT':'nlohmann-json-LICENSE',
    'resources/Model-NOTICE.txt':'Model-NOTICE.txt',
    'docs/release/dependency-inventory.json':'dependency-inventory.json',
    'docs/release/SOURCE_INFORMATION.md':'SOURCE_INFORMATION.md',
}


def copy_licences(root, destination):
    from hashlib import sha256
    if destination.exists():
        raise FileExistsError(destination)
    for relative in MATERIAL:
        if not (root/relative).is_file():
            raise FileNotFoundError(root/relative)
    inventory = json.loads((root/'docs/release/dependency-inventory.json').read_text())
    if sha256((root/'vendor/json/LICENSE.MIT').read_bytes()).hexdigest() != inventory['json']['root_licence_sha256']:
        raise ValueError('JSON licence differs from reviewed material')
    notice = root/inventory['notices']['path']
    if sha256(notice.read_bytes()).hexdigest() != inventory['notices']['sha256']:
        raise ValueError('Runtime notices differ from reviewed material')
    digest = sha256()
    copyrights = set()
    for path in sorted((root/'vendor/json/include').rglob('*')):
        if path.is_file():
            digest.update((path.relative_to(root/'vendor/json/include').as_posix()+'\0'+sha256(path.read_bytes()).hexdigest()+'\n').encode())
            for line in path.read_text().splitlines():
                if 'SPDX-FileCopyrightText:' in line:
                    copyrights.add(line.split('SPDX-FileCopyrightText:',1)[1].strip())
    if digest.hexdigest()!=inventory['json']['header_tree_sha256'] or sorted(copyrights)!=inventory['json']['header_copyrights']:
        raise ValueError('JSON headers or attributions differ from the reviewed source')
    additional={name:root/'docs/release/licenses'/name for name in inventory['reviewed_licence_files']}
    for name,path in additional.items():
        if not path.is_file() or sha256(path.read_bytes()).hexdigest()!=inventory['reviewed_licence_files'][name]:
            raise ValueError('Reviewed dependency notice missing or changed: '+name)
    destination.mkdir(parents=True)
    for relative, name in MATERIAL.items():
        shutil.copyfile(root/relative, destination/name)
    for name,path in additional.items():
        shutil.copyfile(path,destination/name)
    attribution = 'nlohmann/json 3.11.3 header notices (verbatim SPDX attribution values)\n\n'
    attribution += '\n'.join(inventory['json']['header_copyrights'])
    attribution += '\n\nSPDX-License-Identifier: MIT\nSee nlohmann-json-LICENSE for the complete permission and disclaimer.\n'
    (destination/'nlohmann-json-HEADER-NOTICES.txt').write_text(attribution)

def source_inputs(root):
    from hashlib import sha256
    names = set(MATERIAL)
    names.update(str(p.relative_to(root)) for p in (root/'docs/release/licenses').iterdir() if p.is_file())
    names.update(str(p.relative_to(root)) for p in (root/'src').iterdir() if p.is_file())
    names.update(['CMakeLists.txt','scripts/build.sh','scripts/package.sh',
                  'scripts/bundle_paths.py','scripts/model_manifest.py',
                  'scripts/package_licenses.py','scripts/build_receipt.py','resources/Info.plist',
                  'resources/Cauces.entitlements','resources/Worker.entitlements',
                  'resources/Cauces.icns','resources/FlowArtwork.png','resources/FlowArtwork@2x.png'])
    return {name:sha256((root/name).read_bytes()).hexdigest() for name in sorted(names)}


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    destination = Path(sys.argv[1])
    copy_licences(root, destination)
    (destination.parent/'SOURCE_INPUTS.json').write_text(json.dumps(source_inputs(root),indent=2)+'\n')
