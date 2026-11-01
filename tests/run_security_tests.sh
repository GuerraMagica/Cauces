#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
ctest --test-dir build/arm64 --output-on-failure
ctest --test-dir build/x86_64 --output-on-failure
bash tests/run_swift_tests.sh
for task_arch in arm64 x86_64; do
  DS_TEST_ARCH="$task_arch" /usr/bin/python3 tests/security_regression.py
  DS_TEST_ARCH="$task_arch" /usr/bin/python3 tests/model_integrity_test.py
done
/usr/bin/python3 tests/wav_adversarial.py
/usr/bin/python3 tests/worker_test.py
