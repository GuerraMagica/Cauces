#!/bin/bash
# Development only: official downloads/builds stay inside this project.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p vendor build evidence
task_commit=6af1a932e2286d5c58166085d24c68783033edee
task_archive=vendor/onnxruntime-osx-arm64-1.31.1.tgz
if ! test -e "$task_archive"; then
  curl -L --fail --retry 2 https://github.com/microsoft/onnxruntime/releases/download/v1.31.1/onnxruntime-osx-arm64-1.31.1.tgz -o "$task_archive"
fi
printf '%s  %s\n' 2e1344a1926ee50eb25b38153cb6992c3567515aef0e677a1a520a1798896d6f "$task_archive" | shasum -a 256 -c -
if ! test -d vendor/onnxruntime-osx-arm64-1.31.1; then tar -xzf "$task_archive" -C vendor; fi
if ! test -d vendor/onnxruntime-src-1.31.1; then git clone --depth 1 --branch v1.31.1 --filter=blob:none https://github.com/microsoft/onnxruntime.git vendor/onnxruntime-src-1.31.1; fi
test "$(git -C vendor/onnxruntime-src-1.31.1 rev-parse HEAD)" = "$task_commit" || { echo 'La fuente ORT no corresponde al commit fijado.' >&2; exit 1; }
cmake -S vendor/onnxruntime-src-1.31.1/cmake -B build/ort-intel-1.31.1 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_OSX_ARCHITECTURES=x86_64 -DCMAKE_OSX_DEPLOYMENT_TARGET=15.0 \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -Donnxruntime_BUILD_SHARED_LIB=ON -Donnxruntime_BUILD_UNIT_TESTS=OFF \
  -Donnxruntime_BUILD_BENCHMARKS=OFF -Donnxruntime_ENABLE_PYTHON=OFF -Donnxruntime_USE_COREML=OFF \
  -Donnxruntime_USE_MIMALLOC=OFF -Donnxruntime_ENABLE_LTO=OFF
cmake --build build/ort-intel-1.31.1 --target onnxruntime --parallel 2
if ! test -d vendor/json/include; then
  mkdir -p vendor/json
  cp -R build/ort-intel-1.31.1/_deps/nlohmann_json-src/include vendor/json/
  cp build/ort-intel-1.31.1/_deps/nlohmann_json-src/LICENSE.MIT vendor/json/
fi
