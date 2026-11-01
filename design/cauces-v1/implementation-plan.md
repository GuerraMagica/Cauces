# Cauces Flow 0.3.0 Implementation Plan

> **For agentic workers:** use superpowers:executing-plans to implement the approved design inline, with a final independent review.

**Goal:** deliver the approved English Flow interface, a real app icon and a local universal ZIP for Intel testing.

**Architecture:** retain the existing SwiftUI/controller/worker boundaries. Add one native style/artwork adapter and an English diagnostic adapter. Bundle raster exports of the editable artwork and a standard macOS ICNS icon; do not embed a web page as the app UI.

**Tech Stack:** existing SwiftUI/AppKit, C++17, ONNX Runtime 1.31.1, existing Node/sharp for build-time asset export, Apple iconutil/codesign.

**Spec:** `design-brief.md`; user approved continuation and requested the executable icon and Intel test ZIP on 2026-10-28.

## Global constraints

- All app-owned text in English; label export as Export audio…; no user-facing stems terminology.
- Remove duplicate content header/beta/CPU badge and technical footer; add exactly © GuerraMagica Audio.
- Use the approved Flow concept; the graphic remains replaceable for a later supplied logo.
- Keep model bytes, inference configuration, DSP mathematics, sandbox/network restrictions and source-preserving file behavior.
- macOS 15 minimum; ARM64 and x86_64; no new runtime dependencies or global installations.
- Local deliverables only in this task. Preserve 0.2.0 and its ZIP; no automatic GitHub push.

## Review focus

- Long filenames and minimum window dimensions must not hide actions.
- Cancellation/export errors must preserve valid state and show usable English diagnostics.
- Playback selection and seek must remain keyboard/VoiceOver accessible.
- The app must contain its actual icon/artwork, not just the design kit.
- Intel slice, sandbox entitlements, model fingerprints and relocation must be verified.

## Task 1 — English diagnostics and copy

- [x] Add a focused regression for English fallback when the OS supplies a foreign-language diagnostic; run it before implementation.
- [x] Add `src/AppMessages.swift`, translate app-facing strings across controller/state/preview and C++ adapters, and update affected integration assertions.
- [x] Use English source/file/export panel messages and exported filenames. Keep protocol field names/API statuses unchanged.
- [x] Verify Swift diagnostic/state tests and existing CTest/worker safety suites.

## Task 2 — Native Flow UI and icon

- [x] Replace `src/App.swift` layout and add `src/CaucesStyle.swift`: empty/ready/processing/review/export/error presentation, semantic native controls, stable comparison labels and visible selection checks.
- [x] Preserve real audio transport; ensure non-dragging seek adjustments commit a real seek.
- [x] Export artwork and icon PNG sizes from editable SVG; run iconutil to produce `resources/Cauces.icns`.
- [x] Update Info.plist to 0.3.0, English localization and icon reference. Package resources and both architectures.
- [x] Inspect native empty/review/processing screens, minimum size, long filename and keyboard controls.

## Task 3 — Validate and deliver

- [x] Run existing security/state/file-format checks in both architectures; confirm model and algorithm integrity.
- [x] Run real controller/packaged-worker sandbox probes under ARM64 and x86_64/Rosetta, plus native GUI open/separate/play/seek/export/cancel.
- [x] Independently review the final changes; fix material findings.
- [x] Create `dist/Cauces-0.3.0-universal.zip` and checksum; extract and verify bundle equivalence, signature, assets and icon.
- [x] Document actual checks and remaining physical Intel/Pro Tools acceptance limits.
