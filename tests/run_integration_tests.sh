#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
source tests/test_helpers.sh
usage() { echo 'Usage: bash tests/run_integration_tests.sh [arm64|x86_64|all]'; }
if test "${1:-}" = --help && test "$#" -eq 1; then usage; exit 0; fi
if test "$#" -gt 1; then usage >&2; exit 2; fi
task_arches=$(cauces_test_arches "${1:-}")
cauces_test_integration_assets
for task_arch in $task_arches; do cauces_test_build "$task_arch"; done
cauces_test_tools xcrun lipo
for task_arch in $task_arches; do cauces_test_execution_arch "$task_arch"; done
for task_arch in $task_arches; do
  echo "Local integration: $task_arch (authorised models and reference captures required)"
  bash tests/run_swift_tests.sh --integration "$task_arch"
  DS_TEST_ARCH="$task_arch" /usr/bin/python3 tests/model_integrity_test.py
  DS_TEST_ARCH="$task_arch" /usr/bin/python3 tests/worker_test.py
  echo "Local integration PASS: $task_arch; transport, model gates and worker/export checks completed."
done
