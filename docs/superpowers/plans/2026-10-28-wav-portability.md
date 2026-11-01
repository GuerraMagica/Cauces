# Cauces WAV Portability 0.4.1 Implementation Plan

> Use superpowers:executing-plans inline, TDD and one final independent review. User approved correction and upload to existing TLS FTP /SONIDO. No Git commit/push.

**Goal:** remove the WAV reader's dependency on reopening /dev/fd while retaining pinned-file security and ship0.4.1 universal.
**Architecture:** a small RAII reader owns the original verified regular-file descriptor, size and read position. It reads directly with pread, retries EINTR and handles short reads/EOF explicitly. The parser and numerical conversions stay unchanged.
**Tech stack:** existing C++17/POSIX, CMake, SwiftUI and packaging tools; no new dependencies/permissions.
**Spec:** approved chat scope; same error reproduced on a synthetic valid WAV by denying /dev/fd. Target user machine is8-core IntelXeonW/96GB; Sequoia15.7.5 from prior context, physical confirmation still pending.

## Constraints / review focus
- Preserve all existing uncommitted0.3/0.4 work, app/ZIP archives, models and DSP.
- Retain O_NOFOLLOW/O_NONBLOCK/O_CLOEXEC, fstat regular-file verification, one descriptor for headers/samples and exclusive export verification.
- Handle truncation after header parsing, read failures, offsets, descriptor cleanup and path replacement without weakening the sandbox.
- No claim of a physical Intel fix before the user retests; Rosetta + controlled policy are evidence with explicit limits.

## Task1 — Reader/regression
- [x] Add deny-/dev/fd CTest wrapping real WAV contracts; reproduce RED with old reader.
- [x] Extend independent PCM16 extrema, truncation-after-header and descriptor cleanup tests.
- [x] Replace ifstream reopen with direct descriptor RAII/pread in src/wav.cpp; preserve parser/conversion semantics.
- [x] Run normal/restricted WAV and full safety suites on ARM64 and x86_64.

## Task2 — Package/validate
- [x] Bump Info.plist/CMake to0.4.1, build/sign a new universal bundle.
- [x] Verify packaged controller/worker ARM/Intel under App Sandbox and separately the reader under /dev/fd denial; confirm source preservation and export rate/frame count. Combining profiles aborts in libsecinit before entry; documented as unsupported.
- [x] Verify relocated ZIP-only bundle outside repo, architecture/rpaths/signatures/model hashes; compare numerical DSP/model bytes unchanged.
- [x] Independent hotfix review; document actual results and physical-target acceptance.
- [x] ZIP/checksum; extract/hash-check; upload only new0.4.1ZIP+checksum via existing FileZilla TLS session to hal.xpoststudios.com:2121 /SONIDO; verify transfer/remote sizes.
