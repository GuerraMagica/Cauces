"""Minimal strict RIFF adapter for synthetic tests and native exported WAVs."""
from pathlib import Path
import struct
import numpy as np


def read_wav(path):
    raw = Path(path).read_bytes()
    if raw[:4] != b'RIFF' or raw[8:12] != b'WAVE':
        raise ValueError('Cannot read the source audio.')
    chunks = {}; position = 12
    while position+8 <= len(raw):
        tag = raw[position:position+4]
        size = struct.unpack_from('<I', raw, position+4)[0]
        value = raw[position+8:position+8+size]
        if len(value) != size:
            raise ValueError('Could not read the complete source audio.' if tag == b'data'
                             else 'Cannot read the source audio.')
        chunks[tag] = value
        position += 8+size+(size%2)
    if b'fmt ' not in chunks or len(chunks[b'fmt ']) < 16 or b'data' not in chunks:
        raise ValueError('Cannot read the source audio.')
    fmt, channels, rate, _, align, bits = struct.unpack_from('<HHIIHH', chunks[b'fmt '])
    if fmt == 0xfffe and len(chunks[b'fmt ']) >= 40:
        fmt = struct.unpack_from('<H', chunks[b'fmt '], 24)[0]
    data = chunks[b'data']
    if not channels or align != channels*((bits+7)//8) or len(data)%align:
        raise ValueError('Cannot read the source audio.')
    if fmt == 3 and bits in (32,64):
        a = np.frombuffer(data, dtype='<f4' if bits == 32 else '<f8').astype(np.float32)
    elif fmt == 1 and bits in (16,32):
        a = np.frombuffer(data, dtype='<i2' if bits == 16 else '<i4').astype(np.float32)/np.float32(2**(bits-1))
    elif fmt == 1 and bits == 24:
        b = np.frombuffer(data, np.uint8).reshape(-1,3).astype(np.int32)
        a = ((b[:,0] | b[:,1]<<8 | b[:,2]<<16) << 8).astype(np.float32)/np.float32(2**31)
    else:
        raise ValueError('WAV test adapter supports PCM16/24/32 and IEEEfloat32/64')
    return a.reshape(-1,channels).T.copy(), rate

from local_paths import ROOT, FIXTURES, MODELS
VALID=['tone_cpu_48k','silence_48k','impulse1_16k','boundary511_48k','boundary512_48k','boundary513_48k','tone8k','tone44k1','dualmono_16k','hf3_plus','chunk8_minus','chunk8_exact','chunk8_plus','tone_cpu_repeat','signed_zero']
ATOL=1e-5;RTOL=1e-4

def compare_arrays(original,clone):
    if original.shape!=clone.shape:
        return {'shape_match':False,'original_shape':list(original.shape),'clone_shape':list(clone.shape),'tolerance_match':False}
    difference=clone.astype(np.float64)-original.astype(np.float64)
    absolute=np.abs(difference);finite=bool(np.isfinite(clone).all() and np.isfinite(original).all())
    bits=original.view(np.uint32)!=clone.view(np.uint32)
    mismatch=~(absolute<=ATOL+RTOL*np.abs(original.astype(np.float64)))
    return {'shape_match':True,'shape':list(original.shape),'finite':finite,'exact_match':bool(not bits.any()),'tolerance_match':bool(finite and not mismatch.any()),'exact_differences':int(bits.sum()),'numerically_unequal_values':int(np.count_nonzero(difference)),'outside_tolerance':int(mismatch.sum()),'sample_values':int(original.size),'max_abs':float(absolute.max(initial=0)),'rms_error':float(np.sqrt(np.mean(difference*difference))) if difference.size else 0,'first_outside_tolerance':np.argwhere(mismatch)[:12].tolist()}
