#!/bin/bash
# Development only: official downloads/builds stay inside this project.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p vendor build evidence
task_commit=058787ceead760166e3c50a0a4cba8a833a6f53f
task_archive=vendor/onnxruntime-osx-arm64-1.24.2.tgz
if ! test -e "$task_archive"; then
  curl -L --fail --retry 2 https://github.com/microsoft/onnxruntime/releases/download/v1.24.2/onnxruntime-osx-arm64-1.24.2.tgz -o "$task_archive"
fi
printf '%s  %s\n' 0af4fa503e8ea285245b47ee42d0a7461b8156a81270857da0c1d4ecf858abde "$task_archive" | shasum -a 256 -c -
if ! test -d vendor/onnxruntime-osx-arm64-1.24.2; then tar -xzf "$task_archive" -C vendor; fi
if ! test -d vendor/onnxruntime-src; then git clone --depth 1 --branch v1.24.2 --filter=blob:none https://github.com/microsoft/onnxruntime.git vendor/onnxruntime-src; fi
test "$(git -C vendor/onnxruntime-src rev-parse HEAD)" = "$task_commit" || { echo 'La fuente ORT no corresponde al commit fijado.' >&2; exit 1; }
cmake -S vendor/onnxruntime-src/cmake -B build/ort-intel -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_OSX_ARCHITECTURES=x86_64 -DCMAKE_OSX_DEPLOYMENT_TARGET=15.0 \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -Donnxruntime_BUILD_SHARED_LIB=ON -Donnxruntime_BUILD_UNIT_TESTS=OFF \
  -Donnxruntime_BUILD_BENCHMARKS=OFF -Donnxruntime_ENABLE_PYTHON=OFF -Donnxruntime_USE_COREML=OFF \
  -Donnxruntime_USE_MIMALLOC=OFF -Donnxruntime_ENABLE_LTO=OFF
cmake --build build/ort-intel --target onnxruntime --parallel 2
if ! test -d vendor/json/include; then
  mkdir -p vendor/json
  cp -R build/ort-intel/_deps/nlohmann_json-src/include vendor/json/
  cp build/ort-intel/_deps/nlohmann_json-src/LICENSE.MIT vendor/json/
fi
