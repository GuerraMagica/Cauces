#!/bin/sh
set -eu
cd "$(dirname "$0")"
cmake -S probe -B build-windows-x64 -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_TOOLCHAIN_FILE="$PWD/probe/mingw.cmake" -DORT_ROOT="$PWD/deps/onnxruntime-win-x64-1.31.1"
cmake --build build-windows-x64 --parallel 2
