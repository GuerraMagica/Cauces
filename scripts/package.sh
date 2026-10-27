#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
task_models="${MODEL_DIR:-/Library/Application Support/VoxUno/Models/5d6702c37dfb17e5eebe55213eb4f0b22da81bf00ee506257d44107cf3b34195}"
task_app="$PWD/dist/Separador de diálogo.app"
if test -e "$task_app"; then
  echo "El paquete ya existe: $task_app. Muévelo antes de volver a empaquetar." >&2; exit 1
fi
mkdir -p "$task_app/Contents/"{MacOS,Frameworks,Resources/Models,Resources/Licenses}
lipo -create build/arm64/DialogueSeparator build/x86_64/DialogueSeparator -output "$task_app/Contents/MacOS/DialogueSeparator"
lipo -create build/arm64/dialogue-worker build/x86_64/dialogue-worker -output "$task_app/Contents/MacOS/dialogue-worker"
lipo -create vendor/onnxruntime-osx-arm64-1.24.2/lib/libonnxruntime.1.24.2.dylib build/ort-intel/libonnxruntime.1.24.2.dylib -output "$task_app/Contents/Frameworks/libonnxruntime.1.24.2.dylib"
lipo -create build/arm64/libdialogue_separator.dylib build/x86_64/libdialogue_separator.dylib -output "$task_app/Contents/Frameworks/libdialogue_separator.dylib"
for task_file in separator.onnx refiner.onnx separator_gpu.onnx weights.bin manifest.json; do
  cp "$task_models/$task_file" "$task_app/Contents/Resources/Models/"
done
cp vendor/onnxruntime-src/LICENSE "$task_app/Contents/Resources/Licenses/ONNXRuntime-LICENSE"
cp vendor/onnxruntime-src/ThirdPartyNotices.txt "$task_app/Contents/Resources/Licenses/ONNXRuntime-ThirdPartyNotices.txt"
cp vendor/json/LICENSE.MIT "$task_app/Contents/Resources/Licenses/nlohmann-json-LICENSE"
cp src/separator.h "$task_app/Contents/Resources/"
cp resources/Info.plist "$task_app/Contents/Info.plist"
# Remove build-directory rpaths and install only paths relative to the bundle.
/usr/bin/python3 scripts/bundle_paths.py "$task_app"
codesign --force --sign - "$task_app/Contents/Frameworks/libonnxruntime.1.24.2.dylib"
codesign --force --sign - "$task_app/Contents/Frameworks/libdialogue_separator.dylib"
codesign --force --sign - "$task_app/Contents/MacOS/dialogue-worker"
codesign --force --sign - "$task_app"
codesign --verify --deep --strict "$task_app"
printf '%s\n' "$task_app"
