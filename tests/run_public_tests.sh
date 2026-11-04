#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
source tests/test_helpers.sh
usage() { echo 'Usage: bash tests/run_public_tests.sh [arm64|x86_64|all]'; }
if test "${1:-}" = --help && test "$#" -eq 1; then usage; exit 0; fi
if test "$#" -gt 1; then usage >&2; exit 2; fi
task_arches=$(cauces_test_arches "${1:-}")
for task_arch in $task_arches; do cauces_test_build "$task_arch"; done
cauces_test_tools ctest xcrun lipo
for task_arch in $task_arches; do cauces_test_execution_arch "$task_arch"; done
/usr/bin/python3 tests/test_runner_tests.py
/usr/bin/python3 tests/ctest_report_tests.py
for task_arch in $task_arches; do
  echo "Public tests: $task_arch (no model or reference-fixture assets)"
  task_report="$PWD/build/$task_arch/public-ctest.xml"
  ctest --test-dir "build/$task_arch" --output-on-failure --no-tests=error --timeout 60 --output-junit "$task_report"
  /usr/bin/python3 tests/check_ctest_report.py "$task_report"
  bash tests/run_swift_tests.sh --public "$task_arch"
  DS_TEST_ARCH="$task_arch" /usr/bin/python3 tests/security_regression.py
  DS_TEST_ARCH="$task_arch" /usr/bin/python3 tests/wav_adversarial.py
  echo "Public tests PASS: $task_arch; CTest, five Swift suites, protocol and WAV checks completed."
done
