#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
task_models="${CAUCES_MODEL_DIR:-$PWD/vendor/cauces-models}"
task_default_app=$(/usr/bin/python3 -c 'import plistlib; p=plistlib.load(open("resources/Info.plist","rb")); print("dist/Cauces-"+p["CFBundleShortVersionString"]+"-build"+p["CFBundleVersion"]+"/Cauces.app")')
task_app="${CAUCES_PACKAGE_PATH:-$PWD/$task_default_app}"
if test -e "$task_app"; then
  echo "El paquete ya existe: $task_app. Muévelo antes de volver a empaquetar." >&2; exit 1
fi
/usr/bin/python3 scripts/build_receipt.py verify all --inventory docs/release/dependency-inventory.json
/usr/bin/python3 scripts/package_licenses.py "$task_app/Contents/Resources/Licenses"
mkdir -p "$task_app/Contents/"{MacOS,Frameworks,Resources/Models}
lipo -create build/arm64/Cauces build/x86_64/Cauces -output "$task_app/Contents/MacOS/Cauces"
lipo -create build/arm64/dialogue-worker build/x86_64/dialogue-worker -output "$task_app/Contents/MacOS/dialogue-worker"
lipo -create vendor/onnxruntime-osx-arm64-1.31.1/lib/libonnxruntime.1.31.1.dylib build/ort-intel-1.31.1/libonnxruntime.1.31.1.dylib -output "$task_app/Contents/Frameworks/libonnxruntime.1.31.1.dylib"
lipo -create build/arm64/libdialogue_separator.dylib build/x86_64/libdialogue_separator.dylib -output "$task_app/Contents/Frameworks/libdialogue_separator.dylib"
for task_file in separator.onnx refiner.onnx separator_gpu.onnx weights.bin manifest.json; do
  cp "$task_models/$task_file" "$task_app/Contents/Resources/Models/"
done
/usr/bin/python3 scripts/model_manifest.py "$task_app/Contents/Resources/Models/manifest.json"
cp build/arm64/build-receipt.json "$task_app/Contents/Resources/build-receipt-arm64.json"
cp build/x86_64/build-receipt.json "$task_app/Contents/Resources/build-receipt-x86_64.json"
cp src/separator.h "$task_app/Contents/Resources/"
cp resources/Cauces.icns resources/FlowArtwork.png resources/FlowArtwork@2x.png "$task_app/Contents/Resources/"
cp resources/Info.plist "$task_app/Contents/Info.plist"
# Remove build-directory rpaths and install only paths relative to the bundle.
/usr/bin/python3 scripts/bundle_paths.py "$task_app"
codesign --force --sign - "$task_app/Contents/Frameworks/libonnxruntime.1.31.1.dylib"
codesign --force --sign - "$task_app/Contents/Frameworks/libdialogue_separator.dylib"
codesign --force --sign - --options runtime --timestamp=none --entitlements resources/Worker.entitlements "$task_app/Contents/MacOS/dialogue-worker"
codesign --force --sign - --options runtime --timestamp=none --entitlements resources/Cauces.entitlements "$task_app"
codesign --verify --deep --strict "$task_app"
printf '%s\n' "$task_app"
