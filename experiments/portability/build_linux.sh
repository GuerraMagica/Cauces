#!/bin/sh
set -eu
cd "$(dirname "$0")"
cmake -S probe -B build-linux-x64 -G Ninja -DCMAKE_BUILD_TYPE=Release -DORT_ROOT="$PWD/deps/onnxruntime-linux-x64-1.31.1"
cmake --build build-linux-x64 --parallel 2
ctest --test-dir build-linux-x64 --output-on-failure
