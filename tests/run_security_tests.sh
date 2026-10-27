#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
ctest --test-dir build/arm64 --output-on-failure
ctest --test-dir build/x86_64 --output-on-failure
bash tests/run_swift_tests.sh
/usr/bin/python3 tests/security_regression.py
/usr/bin/python3 tests/model_integrity_test.py
/usr/bin/python3 tests/wav_adversarial.py
/usr/bin/python3 tests/worker_test.py
