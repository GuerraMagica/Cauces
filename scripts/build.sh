#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
project_dir="$PWD"
for task_arch in "${@:-arm64 x86_64}"; do
  for task_target in $task_arch; do
    case "$task_target" in
      arm64) runtime_lib="$project_dir/vendor/onnxruntime-osx-arm64-1.24.2/lib/libonnxruntime.1.24.2.dylib" ;;
      x86_64) runtime_lib="$project_dir/build/ort-intel/libonnxruntime.1.24.2.dylib" ;;
      *) echo "Arquitectura no válida: $task_target" >&2; exit 1 ;;
    esac
    test -f "$runtime_lib" || { echo "Falta ONNX Runtime $task_target; consulta README.md" >&2; exit 1; }
    cmake -S . -B "build/$task_target" -G Ninja -DCMAKE_BUILD_TYPE=Release \
      "-DCMAKE_OSX_ARCHITECTURES=$task_target" -DCMAKE_OSX_DEPLOYMENT_TARGET=15.0 "-DORT_LIBRARY=$runtime_lib"
    cmake --build "build/$task_target" --parallel 2
    xcrun swiftc -swift-version 5 -O -target "$task_target-apple-macos15.0" \
      -module-cache-path "build/swift-cache-$task_target" \
      src/App.swift src/JobState.swift src/JobController.swift src/WorkerConnection.swift src/PreviewPlayer.swift \
      -o "build/$task_target/DialogueSeparator"
  done
done
