"""Build-time naming only; never changes model tensors or asset fingerprints."""
import json,sys
from pathlib import Path
path=Path(sys.argv[1]);manifest=json.loads(path.read_text())
manifest['name']='Cauces Multi-Speaker Separation ONNX v1 (selective FP16)'
manifest['integration']={'application':'Cauces','provider':'CPU','base_model':'MossFormer2_SS_16K','base_model_author':'Alibaba Speech Lab','source':'https://huggingface.co/alibabasglab/MossFormer2_SS_16K','refiner_public_provenance':'not identified'}
path.write_text(json.dumps(manifest,indent=2)+'\n')
