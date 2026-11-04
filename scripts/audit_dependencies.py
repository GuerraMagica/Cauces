"""Record source pins and architecture evidence; never infer a binary SBOM from a notice."""
import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

ARM_COMMIT = '41d4d61f14b9c1dd0b2ccda1e9b85dd415fd0496'
INTEL_COMMIT = '6af1a932e2286d5c58166085d24c68783033edee'


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def tree_hash(directory):
    digest = hashlib.sha256()
    for path in sorted(directory.rglob('*')):
        if path.is_symlink():
            target=os.readlink(path)
            if Path(target).is_absolute():raise ValueError('Absolute source symlink: '+str(path))
            try:path.resolve().relative_to(directory.resolve())
            except ValueError:raise ValueError('Source symlink escapes tree: '+str(path))
            digest.update((path.relative_to(directory).as_posix()+'\0LINK:'+target+'\n').encode())
            continue
        if path.is_file():
            digest.update((path.relative_to(directory).as_posix() + '\0' + sha256(path) + '\n').encode())
    return digest.hexdigest()


def verify_dependency_trees(root, inventory):
    directory=root/'build/ort-intel-1.31.1/_deps'
    actual={p.name:p for p in directory.glob('*-src') if p.name!='protoc_binary-src'}
    if set(actual)!=set(inventory['local_source_trees']):
        raise ValueError('Third-party source trees are missing or unreviewed')
    for name,digest in inventory['local_source_trees'].items():
        if tree_hash(actual[name])!=digest:
            raise ValueError('Third-party source tree changed: '+name)
    return actual


def runtime_metadata(root, architecture, library):
    with tempfile.TemporaryDirectory(prefix='cauces-runtime-metadata-') as directory:
        executable = Path(directory)/'metadata'
        subprocess.run(['xcrun','clang','-arch',architecture,'-I',
                        str(root/'vendor/onnxruntime-osx-arm64-1.31.1/include'),
                        str(root/'scripts/runtime_metadata.c'),'-o',str(executable)],check=True)
        lines = subprocess.check_output([str(executable),str(library)],text=True).splitlines()
    if len(lines)<3 or lines[0]!='1.31.1':
        raise ValueError('Unexpected runtime metadata')
    return {'version':lines[0],'build_info':lines[1],'providers':lines[2:]}


def audit(root):
    source = root/'vendor/onnxruntime-src-1.31.1'
    arm_source = root/f'vendor/onnxruntime-{ARM_COMMIT}'
    build = root/'build/ort-intel-1.31.1'
    arm = root/'vendor/onnxruntime-osx-arm64-1.31.1'
    deps = source/'cmake/deps.txt'
    if deps.read_bytes() != (arm_source/'cmake/deps.txt').read_bytes():
        raise ValueError('Architecture source pins differ; review before generating inventory')
    if (arm/'GIT_COMMIT_ID').read_text().strip() != ARM_COMMIT:
        raise ValueError('Unexpected ARM source revision')
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()!=INTEL_COMMIT:
        raise ValueError('Unexpected Intel source revision')
    subprocess.run(['git','diff','--exit-code','HEAD','--'],cwd=source,check=True,stdout=subprocess.DEVNULL)
    arm_metadata = runtime_metadata(root,'arm64',arm/'lib/libonnxruntime.1.31.1.dylib')
    intel_metadata = runtime_metadata(root,'x86_64',build/'libonnxruntime.1.31.1.dylib')
    for metadata,commit in [(arm_metadata,ARM_COMMIT),(intel_metadata,INTEL_COMMIT)]:
        if 'git-commit-id='+commit[:7] not in metadata['build_info']:
            raise ValueError('Runtime binary source revision differs from reviewed source')
    vendor_json = root/'vendor/json'
    json_source = build/'_deps/nlohmann_json-src'
    if tree_hash(vendor_json/'include') != tree_hash(json_source/'include'):
        raise ValueError('Compiled JSON headers differ from the pinned source tree')
    if (vendor_json/'LICENSE.MIT').read_bytes() != (json_source/'LICENSE.MIT').read_bytes():
        raise ValueError('JSON root licence differs from pinned source')
    copyrights = set()
    for path in (vendor_json/'include').rglob('*.hpp'):
        for line in path.read_text().splitlines():
            if 'SPDX-FileCopyrightText:' in line:
                copyrights.add(line.split('SPDX-FileCopyrightText:', 1)[1].strip())
    ninja = (build/'build.ninja').read_text()
    link = next(line for line in ninja.splitlines() if line.startswith('build libonnxruntime.1.31.1.dylib:'))
    linked = set(re.findall(r'_deps/([^/ ]+)-build/', link))
    compile_inputs = set(re.findall(r'_deps/([^/ ]+)-src', ninja))
    cache = {}
    for line in (build/'CMakeCache.txt').read_text().splitlines():
        match = re.match(r'(onnxruntime_[^:]+):[^=]+=(ON|OFF)$', line)
        if match:
            cache[match[1]] = match[2]
    aliases = {'json':'nlohmann_json', 'eigen':'eigen3', 'microsoft_gsl':'gsl'}
    pins = []
    for line in deps.read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        name, url, sha1 = line.split(';')
        local_name = aliases.get(name, name)
        evidence = 'linked_static_library' if local_name in linked else ('present_in_build_inputs' if local_name in compile_inputs else 'upstream_pin_only')
        pins.append({'name':name, 'source_url':url, 'upstream_archive_sha1':sha1,
                     'x86_64_evidence':evidence,
                     'arm64_evidence':'upstream_pin_only_not_binary_inclusion_proof'})
    notice = arm/'ThirdPartyNotices.txt'
    sections = [part.strip().splitlines()[0] for part in notice.read_text().split('_____')[1:] if part.strip()]
    return {
        'schema_version':1, 'review_date':'2026-11-04',
        'scope':'architecture_evidence_and_conservative_upstream_dependency_inventory',
        'completeness':{'x86_64':'source_pins_link_inputs_and_full_upstream_notices_reviewed',
                        'arm64':'official_binary_and_exact_source_identified_no_vendor_binary_sbom_available',
                        'limitation':'Upstream pins and notice sections are a superset, not proof every listed component is embedded. ARM exact per-component inclusion remains unverified; no runtime replacement was made.'},
        'runtimes':[
            {'architecture':'arm64','version':'1.31.1','source_commit':ARM_COMMIT,
             'source_url':f'https://github.com/microsoft/onnxruntime/tree/{ARM_COMMIT}',
             'source_archive_url':f'https://codeload.github.com/microsoft/onnxruntime/tar.gz/{ARM_COMMIT}',
             'source_archive_sha256':'2534907510879a8bfd9d11bae7c42a6632600960089b9f6cd2f6794404b9c111',
             'input_library':'vendor/onnxruntime-osx-arm64-1.31.1/lib/libonnxruntime.1.31.1.dylib',
             'input_sha256':sha256(arm/'lib/libonnxruntime.1.31.1.dylib'),
             'providers_reported':arm_metadata['providers'],'build_info':arm_metadata['build_info'],
             'provenance':'official_release_archive','build_options':'not_supplied_as_cache_by_vendor'},
            {'architecture':'x86_64','version':'1.31.1','source_commit':INTEL_COMMIT,
             'source_url':f'https://github.com/microsoft/onnxruntime/tree/{INTEL_COMMIT}',
             'input_library':'build/ort-intel-1.31.1/libonnxruntime.1.31.1.dylib',
             'input_sha256':sha256(build/'libonnxruntime.1.31.1.dylib'),
             'providers_reported':intel_metadata['providers'],'build_info':intel_metadata['build_info'],'provenance':'local_pinned_source_build',
             'build_options':cache}],
        'application_provider':'CPUExecutionProvider',
        'local_source_trees':{p.name:tree_hash(p) for p in sorted((build/'_deps').glob('*-src')) if p.name!='protoc_binary-src'},
        'onnxruntime_source_pins':pins,
        'additional_nested_dependency':{'name':'utf8_range','source':'protobuf/third_party/utf8_range','evidence':'x86_64_link_inputs_libutf8_validity','licence':'MIT'},
        'upstream_notice_sections':sections,
        'notices':{'path':'vendor/onnxruntime-osx-arm64-1.31.1/ThirdPartyNotices.txt','sha256':sha256(notice),'policy':'retain_complete_original_superset_without_claiming_all_components_are_embedded'},
        'json':{'version':'3.11.3','licence':'MIT','source_url':'https://github.com/nlohmann/json/tree/v3.11.3',
                'header_tree_sha256':tree_hash(vendor_json/'include'),'tree_hash_format':'sorted relative POSIX path + NUL + file SHA256 + LF',
                'root_licence_sha256':sha256(vendor_json/'LICENSE.MIT'),
                'header_copyrights':sorted(copyrights),'reconciliation':'all_headers_and_root_licence_match_pinned_upstream_source_both_attribution_sets_retained'},
        'system_dependencies':'Apple frameworks and system C/C++ libraries are linked, not copied as SDK sources',
        'reviewed_licence_files':{p.name:sha256(p) for p in sorted((root/'docs/release/licenses').iterdir()) if p.is_file()},
        'source_tree_hash_format':'sorted relative POSIX path + NUL + file SHA256 (or LINK:relative-target) + LF; external links rejected',
        'model_rights':'separate_not_granted_by_library_licences'
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, default=Path('docs/release/dependency-inventory.json'))
    args = parser.parse_args()
    result = audit(args.root.resolve())
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print('Dependency evidence written; ARM binary-component completeness is explicitly limited.')
