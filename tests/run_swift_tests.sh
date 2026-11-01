#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build/swift-cache
xcrun swiftc -swift-version 5 -module-cache-path build/swift-cache src/JobState.swift tests/JobStateTests.swift -o build/job-state-tests
build/job-state-tests
xcrun swiftc -swift-version 5 -module-cache-path build/swift-cache src/LocalFilePolicy.swift tests/LocalFilePolicyTests.swift -o build/local-policy-tests
build/local-policy-tests
xcrun swiftc -swift-version 5 -module-cache-path build/swift-cache -import-objc-header src/security.h src/PrivateDirectory.swift tests/PrivateDirectoryTests.swift build/arm64/libcauces_security.a -lc++ -o build/private-directory-tests
build/private-directory-tests
xcrun swiftc -swift-version 5 -module-cache-path build/swift-cache -import-objc-header src/security.h src/PrivateDirectory.swift src/WorkerConnection.swift tests/WorkerConnectionTests.swift build/arm64/libcauces_security.a -lc++ -o build/worker-connection-tests
build/worker-connection-tests "$PWD" "${CAUCES_MODEL_DIR:-$PWD/vendor/cauces-models}" "${CAUCES_REFERENCE_FIXTURES_DIR:-$PWD/build/reference-fixtures}"

xcrun swiftc -swift-version 5 -module-cache-path build/swift-cache src/JobState.swift src/AppMessages.swift tests/AppMessagesTests.swift -o build/app-message-tests
build/app-message-tests

xcrun swiftc -swift-version 5 -module-cache-path build/swift-cache src/AudioOutput.swift tests/AudioOutputTests.swift -o build/audio-output-tests
build/audio-output-tests
