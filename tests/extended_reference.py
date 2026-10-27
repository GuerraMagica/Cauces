"""Thirty-second regression against frozen sample arrays from a prior CPU capture."""
import csv,hashlib,json,os,subprocess
from pathlib import Path
import numpy as np
from fixture_support import ROOT,MODELS,read_wav,compare_arrays
arch=os.environ.get('DS_TEST_ARCH','arm64')
reference=ROOT/'evidence/extended-30s'
source=ROOT/'build/performance-fixtures/benchmark-30s.wav'
output=ROOT/'evidence'/f'runtime-1.31.1-30s-{arch}'
output.mkdir(exist_ok=False)
before=(hashlib.sha256(source.read_bytes()).hexdigest(),source.stat().st_mtime_ns)
proc=subprocess.run([str(ROOT/'build'/arch/'pipeline_cli'),str(MODELS),str(source),str(output),'4'],capture_output=True,text=True,check=True)
report={'architecture':arch,'runtime':'1.31.1','atol':1e-5,'rtol':1e-4,'source_sha256':before[0],'timing':proc.stdout.strip(),'reference':'frozen original arrays in prior extended-30s NPZ files','stems':{}}
with (output/'divergences.csv').open('w') as file:
 writer=csv.writer(file);writer.writerow(['stem','channel','sample','original','clone','absolute_error'])
 for stem in ['speaker_1','speaker_2','noise']:
  frozen=reference/f'{stem}-differences.npz';original=np.load(frozen)['original'];clone,rate=read_wav(output/f'{stem}.wav')
  item=compare_arrays(original,clone);item.update(rate_match=rate==48000,reference_npz_sha256=hashlib.sha256(frozen.read_bytes()).hexdigest());report['stems'][stem]=item
  difference=np.abs(original.astype(np.float64)-clone.astype(np.float64));outside=difference>1e-5+1e-4*np.abs(original.astype(np.float64))
  np.savez_compressed(output/f'{stem}-differences.npz',original=original,native=clone,bit_differences=original.view(np.uint32)!=clone.view(np.uint32),outside_tolerance=outside)
  for c,n in np.argwhere(outside):writer.writerow([stem,int(c),int(n),float(original[c,n]),float(clone[c,n]),float(difference[c,n])])
report['input_unchanged']=before==(hashlib.sha256(source.read_bytes()).hexdigest(),source.stat().st_mtime_ns)
report['pass']=report['input_unchanged'] and all(i['tolerance_match'] and i['rate_match'] for i in report['stems'].values())
(output/'results.json').write_text(json.dumps(report,indent=2));print(report['pass'],report['timing']);assert report['pass']
