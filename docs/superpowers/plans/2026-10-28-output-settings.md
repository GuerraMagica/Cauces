# Cauces Output Settings Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans inline and one final independent review. The user approved the scope on 2026-10-28; do not repeat approval or commit/push.

**Goal:** native English Settings window for output device and device sample rate, shipped in universal Cauces 0.4.0.

**Architecture:** retain AVAudioEngine and the existing processing/export paths. Add a Core Audio hardware adapter and an injectable output-settings model. Route only the app's audio unit; change device rate only on Apply. Persist device UID and requested rate, validate actual hardware before playback, and pause on relevant hardware changes.

**Tech Stack:** existing SwiftUI/AppKit/AVFoundation plus system CoreAudio/AudioToolbox; no added dependencies.

**Spec:** User-approved chat scope: Settings (Command-comma), Output with System Default, supported Sample rate, Apply/Cancel, persisted selection, pause on disconnect, unchanged WAV export format, ARM64/Intel universal ZIP.

## Global Constraints
- Native English Flow UI; macOS 15.0 minimum; ARM64/x86_64; no network or microphone entitlements.
- Preserve existing uncommitted 0.3 work, app/ZIP, model bytes, C++ code and file security.
- Hardware nominal rate is shared with other applications; user approved that effect. Do not change global default output device.
- Apply pauses playback and preserves position/selected track. No automatic playback restart/fallback after a specifically selected device disappears.
- Saved rate is a request: if actual rate changed externally, require Apply in Settings rather than silently changing hardware on app launch/play.
- Local build/ZIP only; no Git commit/push or installations.

## Review Focus
- Disconnected or unavailable explicit UID must not silently route to another output.
- Rejected/unsupported/non-finite rate, hardware refusal and failed routing must not commit preferences; attempt hardware rollback with explicit diagnostics.
- External device/rate changes must pause and retain cursor; unrelated device list changes must not interrupt playback.
- Audio timing must use source sample frames through hardware-rate conversion; exported WAVs remain source rate/length.
- Settings must work before loading audio, preserve only applied values, and expose actual device rate/status.

## Task 1 — Hardware/settings model
Files: new src/AudioOutput.swift, tests/AudioOutputTests.swift; update tests/run_swift_tests.sh.
- [x] Add failing async tests using fake hardware for selection by UID/System Default, persistence, compatible rates, NaN/unsupported rate, missing device, rejection/rollback, route failure, external-rate change and disconnect.
- [x] Implement OutputDevice, OutputPreference and AudioOutputSettings with CoreAudioHardware adapter and property listeners. Expose apply(_:), playbackDevice(), refresh(), preferences, devices, actual rate and notices.
- [x] Run focused tests in both architectures; enumerate real hardware read-only.

## Task 2 — Native UI and playback integration
Files: src/AudioSettingsView.swift, src/PreviewPlayer.swift, src/App.swift, scripts/build.sh, tests/sandbox_probe.py.
- [x] Add Settings window/menu Command-comma, two selectors, actual-rate status, Apply/Cancel and English errors in Flow style.
- [x] Rebuild the output graph on selected-device changes; preserve source file formats, position and selection. Listen for AVAudioEngine configuration changes and stop safely.
- [x] Validate the saved device/rate before each play; no automatic device-rate writes during startup/play.
- [x] Test real packaged GUI open/apply/cancel/persistence/play/seek; verify 44.1/48 kHz device-rate switching if supported, restore original hardware configuration.

## Task 3 — Validation/package
Files: resources/Info.plist, README.md, docs/validation.md, tests/OutputSettingsProbe.swift and local evidence.
- [x] Run existing security/regression suites and actual controller/worker sandbox probes ARM64/x86_64 under Rosetta.
- [x] Add/run production playback/settings probe for real hardware rates, preserved cursor and export rate independence. Restore rate on exit.
- [x] Independent review and fix material findings; document physical-device/Intel limitations.
- [x] Build/sign Cauces0.4.0; universal ZIP, checksum, extraction/signature/hash verification and unchanged models/C++ compared with0.3.0.
