"""Local-only integration assets; no model or fixture downloads."""
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FIXTURES=Path(os.environ.get('CAUCES_REFERENCE_FIXTURES_DIR',ROOT/'build/reference-fixtures'))
MODELS=Path(os.environ.get('CAUCES_MODEL_DIR',ROOT/'vendor/cauces-models'))
