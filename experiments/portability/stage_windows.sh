#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ -e windows-test-kit ]; then
  printf '%s\n' 'Refusing to replace existing windows-test-kit; preserve or move it first.' >&2
  exit 1
fi
mkdir -p windows-test-kit/bin windows-test-kit/licenses
cp build-windows-x64/*.exe windows-test-kit/bin/
cp deps/onnxruntime-win-x64-1.31.1/lib/*.dll windows-test-kit/bin/
cp "$(x86_64-w64-mingw32-g++-posix -print-file-name=libwinpthread-1.dll)" windows-test-kit/bin/
cp deps/onnxruntime-win-x64-1.31.1/LICENSE windows-test-kit/licenses/ONNXRuntime-LICENSE
cp deps/onnxruntime-win-x64-1.31.1/ThirdPartyNotices.txt windows-test-kit/licenses/ONNXRuntime-ThirdPartyNotices.txt
cp source/LICENSE windows-test-kit/licenses/Cauces-GPL-3.0-only
cp /usr/share/doc/mingw-w64-x86-64-dev/copyright windows-test-kit/licenses/MinGW-copyright
cp /usr/share/doc/g++-mingw-w64-x86-64-posix/copyright windows-test-kit/licenses/GCC-MinGW-copyright
cp verify_probe.py Run-Probe.ps1 WINDOWS.md windows-test-kit/
cp -R fixtures windows-test-kit/
cp -R results/mac-arm64 windows-test-kit/reference-mac-arm64
for binary in windows-test-kit/bin/*.exe windows-test-kit/bin/*.dll; do
  printf '\n%s\n' "$binary"
  x86_64-w64-mingw32-objdump -p "$binary" | sed -n 's/^[[:space:]]*DLL Name: /  import: /p'
done
