"""Bind all original/native samples, exact bit masks and tolerance masks to hashes."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
from fixture_support import FIXTURES, MODELS, read_wav, VALID, compare_arrays

def collect(directory):
    directory=Path(directory);report=json.loads((directory/'results.json').read_text());manifest=[]
    for case in report['cases']:
        name=case['case']
        for stem in ('speaker_1','speaker_2','noise'):
            original_path=FIXTURES/f'{name}_{stem}.wav';native_path=directory/name/f'{stem}.wav'
            original,rate=read_wav(original_path);native,nrate=read_wav(native_path)
            bits=original.view(np.uint32)!=native.view(np.uint32)
            outside=np.abs(original.astype(np.float64)-native.astype(np.float64))>1e-5+1e-4*np.abs(original.astype(np.float64))
            artifact=directory/name/f'{stem}-differences.npz'
            np.savez_compressed(artifact,original=original,native=native,bit_differences=bits,outside_tolerance=outside)
            manifest.append({'case':name,'stem':stem,'rate':rate,'original_sha256':hashlib.sha256(original_path.read_bytes()).hexdigest(),'native_sha256':hashlib.sha256(native_path.read_bytes()).hexdigest(),'npz':str(artifact.relative_to(directory)),'npz_sha256':hashlib.sha256(artifact.read_bytes()).hexdigest(),'bit_differences':int(bits.sum()),'outside_tolerance':int(outside.sum())})
    (directory/'difference-manifest.json').write_text(json.dumps(manifest,indent=2))
    print(directory,'all differences bound:',len(manifest),'stems')
if __name__=='__main__':
    for path in sys.argv[1:]:collect(path)
