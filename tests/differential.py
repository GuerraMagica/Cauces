"""Native engine vs recorded original CPU, fixed tolerances and complete divergence CSV."""
import csv, hashlib, json, subprocess, sys, time, os
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
INV=ROOT.parent/'voxuno-investigation'
sys.path.insert(0,str(INV))
from oracle.wav_io import read_wav
from oracle.run_app_differential import VALID, compare_arrays
MODELS=Path('/Library/Application Support/VoxUno/Models/5d6702c37dfb17e5eebe55213eb4f0b22da81bf00ee506257d44107cf3b34195')

def main():
    arch=os.environ.get('DS_TEST_ARCH','arm64')
    if arch not in ('arm64','x86_64'):raise ValueError('Unsupported test architecture')
    binary=ROOT/'build'/arch/'pipeline_cli'
    if not binary.exists():
        raise AssertionError('Native pipeline executable is missing')
    destination=ROOT/'evidence'/f'native-cpu-{arch}-{time.strftime("%Y%m%d-%H%M%S")}'
    destination.mkdir(parents=True)
    report={'atol':1e-5,'rtol':1e-4,'architecture':arch,'execution':'native M2' if arch=='arm64' else 'Rosetta on M2, not physical Intel','binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'cases':[]}
    with (destination/'divergences.csv').open('w') as f:
        writer=csv.writer(f);writer.writerow(['case','stem','channel','sample','original','native','absolute_error'])
        for name in sys.argv[1:] or VALID:
            source=INV/'fixtures'/f'{name}.wav';before=(source.stat().st_mtime_ns,hashlib.sha256(source.read_bytes()).hexdigest())
            proc=subprocess.run([str(binary),str(MODELS),str(source),str(destination/name),'4'],capture_output=True,text=True)
            if proc.returncode: raise AssertionError(f'{name}: {proc.stderr}')
            case={'case':name,'timing':proc.stdout.strip(),'stems':{}}
            for stem in ('speaker_1','speaker_2','noise'):
                original,rate=read_wav(INV/'fixtures'/f'{name}_{stem}.wav')
                native,nrate=read_wav(destination/name/f'{stem}.wav')
                comparison=compare_arrays(original,native);comparison['rate_match']=rate==nrate;case['stems'][stem]=comparison
                if original.shape==native.shape:
                    diff=np.abs(original.astype(np.float64)-native.astype(np.float64))
                    for channel,sample in np.argwhere(diff>1e-5+1e-4*np.abs(original.astype(np.float64))):
                        writer.writerow([name,stem,int(channel),int(sample),float(original[channel,sample]),float(native[channel,sample]),float(diff[channel,sample])])
            case['input_unchanged']=before==(source.stat().st_mtime_ns,hashlib.sha256(source.read_bytes()).hexdigest())
            case['pass']=case['input_unchanged'] and all(v['tolerance_match'] and v['rate_match'] for v in case['stems'].values())
            report['cases'].append(case)
            print(name,case['pass'],case['timing'],flush=True)
            (destination/'results.json').write_text(json.dumps(report,indent=2))
    report['passed']=sum(c['pass'] for c in report['cases']);report['total']=len(report['cases'])
    (destination/'results.json').write_text(json.dumps(report,indent=2))
    print(destination)
    if report['passed']!=report['total']:sys.exit(1)
if __name__=='__main__': main()
