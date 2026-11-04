"""Build-time naming only; never changes model tensors or asset fingerprints."""
import json,sys
from pathlib import Path
path=Path(sys.argv[1]);manifest=json.loads(path.read_text())
manifest['name']='Cauces Multi-Speaker Separation ONNX v1 (selective FP16)'
manifest['integration']={
    'application':'Cauces',
    'provider':'CPU',
    'base_model':'MossFormer2_SS_16K',
    'base_model_author':'Alibaba Speech Lab',
    'source':'https://huggingface.co/alibabasglab/MossFormer2_SS_16K',
    'base_model_licence_declared':'Apache-2.0',
    'asset_provenance':'Local third-party distribution; recorded asset fingerprints',
    'onnx_conversion_author':None,
    'onnx_conversion_licence_status':'Source distribution declares Apache-2.0 for the low-band model; scope over specific export contributions pending clarification',
    'refiner_author':None,
    'refiner_licence_status':'not_determined',
    'provenance_revision_date':'2026-11-04',
}
path.write_text(json.dumps(manifest,indent=2)+'\n')
