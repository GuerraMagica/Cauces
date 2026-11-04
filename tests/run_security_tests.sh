#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
source tests/test_helpers.sh
usage() { echo 'Usage: bash tests/run_security_tests.sh [arm64|x86_64|all]'; }
if test "${1:-}" = --help && test "$#" -eq 1; then usage; exit 0; fi
if test "$#" -gt 1; then usage >&2; exit 2; fi
# Preserve the full-suite default. Missing private assets are errors, never skips.
task_arches=$(cauces_test_arches "${1:-all}")
cauces_test_integration_assets
for task_arch in $task_arches; do cauces_test_build "$task_arch"; done
for task_arch in $task_arches; do
  bash tests/run_public_tests.sh "$task_arch"
  bash tests/run_integration_tests.sh "$task_arch"
done
