#!/bin/bash
# Shared preflight only. Sourced by the test entry points; never downloads assets.
cauces_test_error() { echo "Cauces tests: $*" >&2; exit 2; }

cauces_test_arches() {
  case "${1:-$(uname -m)}" in
    arm64) echo arm64 ;;
    x86_64) echo x86_64 ;;
    all) echo 'arm64 x86_64' ;;
    *) cauces_test_error 'Unsupported architecture. Choose arm64, x86_64 or all.' ;;
  esac
}

cauces_test_tools() {
  test "$(uname -s)" = Darwin || cauces_test_error 'macOS 15 or later is required.'
  local task_version
  task_version=$(/usr/bin/sw_vers -productVersion)
  test "${task_version%%.*}" -ge 15 || cauces_test_error 'macOS 15 or later is required.'
  local task_tool
  for task_tool in "$@"; do
    command -v "$task_tool" >/dev/null 2>&1 || cauces_test_error "Missing tool: $task_tool. See README.md, Compilar y verificar."
  done
  test -x /usr/bin/python3 || cauces_test_error 'Apple Python 3 is missing; check the Apple development tools.'
  /usr/bin/python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' || cauces_test_error 'Python 3.9 or later is required.'
  xcrun --find swiftc >/dev/null 2>&1 || cauces_test_error 'Swift compiler unavailable. Configure the Apple development tools before running tests.'
}

cauces_test_build() {
  local task_arch="$1" task_file
  for task_file in CTestTestfile.cmake dialogue-worker libdialogue_separator.dylib libcauces_security.a \
      dsp_tests pipeline_tests wav_tests api_tests cleanup_tests storage_tests nonregular_copy_tests; do
    test -r "build/$task_arch/$task_file" || cauces_test_error "Missing build/$task_arch/$task_file. Run: bash scripts/build.sh $task_arch"
  done
}

cauces_test_execution_arch() {
  local task_arch="$1" task_file task_actual
  /usr/bin/arch "-$task_arch" /usr/bin/true || cauces_test_error "Cannot execute $task_arch on this Mac. x86_64 on Apple Silicon requires an existing Rosetta installation. No installation was attempted."
  for task_file in dialogue-worker libdialogue_separator.dylib libcauces_security.a \
      dsp_tests pipeline_tests wav_tests api_tests cleanup_tests storage_tests nonregular_copy_tests; do
    task_actual=$(lipo -archs "build/$task_arch/$task_file") || cauces_test_error "Cannot inspect build/$task_arch/$task_file. Rebuild with bash scripts/build.sh $task_arch"
    test "$task_actual" = "$task_arch" || cauces_test_error "Wrong architecture in build/$task_arch/$task_file: $task_actual. Rebuild with bash scripts/build.sh $task_arch"
  done
}

cauces_test_integration_assets() {
  local task_asset
  task_models="${CAUCES_MODEL_DIR:-$PWD/vendor/cauces-models}"
  task_fixtures="${CAUCES_REFERENCE_FIXTURES_DIR:-$PWD/build/reference-fixtures}"
  for task_asset in separator.onnx refiner.onnx weights.bin; do
    test -r "$task_models/$task_asset" && test -f "$task_models/$task_asset" || \
      cauces_test_error "Integration requires readable $task_models/$task_asset. Set CAUCES_MODEL_DIR to your authorised local assets. Integration tests were not skipped."
  done
  for task_asset in signed_zero chunk8_exact malformed empty_48k nan_float inf_float \
      stereo_16k three_channels rate_96k nan_then_stereo stereo_then_nan; do
    test -r "$task_fixtures/$task_asset.wav" && test -f "$task_fixtures/$task_asset.wav" || \
      cauces_test_error "Integration requires $task_fixtures/$task_asset.wav. Set CAUCES_REFERENCE_FIXTURES_DIR to your local reference captures. Integration tests were not skipped."
  done
}
