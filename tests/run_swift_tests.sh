#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
source tests/test_helpers.sh
usage() { echo 'Usage: bash tests/run_swift_tests.sh [--public|--integration|--all] [arm64|x86_64|all]'; }
if test "${1:-}" = --help && test "$#" -eq 1; then usage; exit 0; fi
task_mode=all
case "${1:-}" in --public|--integration|--all) task_mode="${1#--}"; shift ;; esac
if test "$#" -gt 1; then usage >&2; exit 2; fi
# No arguments retain the historical full, dual-architecture intention.
task_arches=$(cauces_test_arches "${1:-all}")
if test "$task_mode" != public; then cauces_test_integration_assets; fi
for task_arch in $task_arches; do cauces_test_build "$task_arch"; done
cauces_test_tools xcrun lipo
for task_arch in $task_arches; do cauces_test_execution_arch "$task_arch"; done

swift_suite() {
  local task_label="$1"; shift
  local task_executable="$PWD/build/$task_arch/swift-tests/$task_label"
  echo "Swift $task_arch: $task_label"
  case "$task_label" in
    private-directory|worker-connection)
      xcrun swiftc -swift-version 5 -target "$task_arch-apple-macos15.0" \
        -module-cache-path "build/swift-cache-$task_arch" -import-objc-header src/security.h \
        "$@" "build/$task_arch/libcauces_security.a" -lc++ -o "$task_executable" ;;
    *)
      xcrun swiftc -swift-version 5 -target "$task_arch-apple-macos15.0" \
        -module-cache-path "build/swift-cache-$task_arch" "$@" -o "$task_executable" ;;
  esac
  if test "$task_label" = worker-connection; then
    "$task_executable" "$PWD" "$task_models" "$task_fixtures"
  else
    "$task_executable"
  fi
}

for task_arch in $task_arches; do
  mkdir -p "build/swift-cache-$task_arch" "build/$task_arch/swift-tests"
  if test "$task_mode" != integration; then
    swift_suite job-state src/JobState.swift tests/JobStateTests.swift
    swift_suite local-policy src/LocalFilePolicy.swift tests/LocalFilePolicyTests.swift
    swift_suite private-directory src/PrivateDirectory.swift tests/PrivateDirectoryTests.swift
    swift_suite app-messages src/JobState.swift src/AppMessages.swift tests/AppMessagesTests.swift
    swift_suite audio-output src/AudioOutput.swift tests/AudioOutputTests.swift
  fi
  if test "$task_mode" != public; then
    swift_suite worker-connection src/PrivateDirectory.swift src/WorkerConnection.swift tests/WorkerConnectionTests.swift
  fi
done
