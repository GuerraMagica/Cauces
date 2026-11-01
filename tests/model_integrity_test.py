"""Every public model-loading entry rejects bytes outside the pinned asset set."""
import ctypes,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
lib=ctypes.CDLL(str(root/'build/arm64/libdialogue_separator.dylib'))
lib.ds_create.argtypes=[ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_size_t];lib.ds_create.restype=ctypes.c_void_p
with tempfile.TemporaryDirectory(prefix='cauces-assets-') as tmp:
 for name in ['separator.onnx','refiner.onnx','weights.bin']:(Path(tmp)/name).write_bytes(b'unapproved synthetic model')
 error=ctypes.create_string_buffer(512)
 result=lib.ds_create(tmp.encode(),1,error,len(error))
 assert not result and b'integrity' in error.value,(result,error.value)
print('Public C API rejects unapproved assets at the shared integrity gate')
