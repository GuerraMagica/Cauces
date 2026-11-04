# Cauces public tests — approved implementation plan

Approved scope: public model-free test command, architecture selection, explicit
diagnostics, separate private integration, README/CONTRIBUTING, clean-source
validation. No production DSP/inference/models/entitlement/package changes.

Implementation uses the existing checkout and working branch. No new dependency,
service, account or automated CI is introduced. Public tests require a compiled
worker/runtime and Apple development tools, not models or reference captures.

## Tasks

- [x] Watch CLI/preflight contracts fail before the runner implementation.
- [x] Add public and integration entry points with shared preflight; retain the
  existing full security command as an explicit aggregator.
- [x] Split the Swift runner into public/integration modes with per-architecture
  libraries. Reuse all five public Swift suites and the transport test unchanged.
- [x] Run WAV/protocol checks against the requested architecture; bound the WAV
  subprocess and require recovery with a valid synthetic WAV.
- [x] Verify CLI contracts, then clean-source public builds/tests with only
  allowlisted runtime/header dependencies and no model/fixture access.
- [x] Run the complete existing integration coverage when local authorised assets
  are available; preserve and verify model/original-package hashes.
- [x] Update README, CONTRIBUTING and validation evidence with actual results,
  prerequisites and remaining limitations; review the exact diff.

## Acceptance

`bash tests/run_public_tests.sh [arm64|x86_64|all]` defaults to the current process
architecture. It executes every registered CTest, all five public Swift suites,
protocol regressions and deterministic WAV tests, and fails on errors. There is
no implicit download, model/fixture lookup or silent skip. Help and invalid
arguments require no build. Missing builds/tools and integration assets produce
actionable diagnostics. Explicit integration and full-suite commands remain.

The clean copy contains the source under review and only ONNX Runtime binaries,
headers and JSON headers needed for compilation; no vendor model directory, private
fixtures, environment or old build tree is copied. ARM64 and x86_64/Rosetta results
are reported separately. App Sandbox probes and professional listening are not
equated with this public test route. Tests do not change audio output devices.

## Review and verification

Independent review found a partial-CTest-registration false-PASS path. Fixed by
requiring the eight published contract names and rejecting skipped/failed/error
cases, without forbidding additional passing tests. Six report contracts observed
RED then GREEN; real temporary removal of wav_without_dev_fd rejected, followed
by final clean public and full local regression PASS in both architectures.
Seven CLI/preflight contracts pass. No review issue was deferred.

Clean dependency preparation initially omitted the internal ORT .1 dylib links;
this was corrected only in the disposable validation copy. No runtime or build
code was changed. Raw evidence stays local under evidence/public-tests-20261104/;
the durable results and environment limits are in docs/validation.md.
