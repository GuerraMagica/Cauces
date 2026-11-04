"""CLI/preflight contracts in disposable source-only trees; no models or compiler needed."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RunnerContracts(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='cauces public runner ')
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / 'tests', self.root / 'tests',
                        ignore=shutil.ignore_patterns('__pycache__'))

    def tearDown(self):
        self.temporary.cleanup()

    def run_script(self, name, *arguments):
        environment = os.environ.copy()
        environment.pop('CAUCES_MODEL_DIR', None)
        environment.pop('CAUCES_REFERENCE_FIXTURES_DIR', None)
        return subprocess.run(['/bin/bash', str(self.root / 'tests' / name), *arguments],
                              cwd='/', env=environment, capture_output=True, text=True, timeout=15)

    def test_help_needs_no_build_models_or_sources(self):
        for script in ['run_public_tests.sh', 'run_integration_tests.sh',
                       'run_swift_tests.sh', 'run_security_tests.sh']:
            with self.subTest(script=script):
                result = self.run_script(script, '--help')
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn('Usage:', result.stdout)
                self.assertFalse((self.root / 'build').exists())

    def test_invalid_architecture_stops_before_any_tests(self):
        for script in ['run_public_tests.sh', 'run_integration_tests.sh',
                       'run_swift_tests.sh', 'run_security_tests.sh']:
            with self.subTest(script=script):
                result = self.run_script(script, 'invalid-architecture')
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn('architecture', result.stderr.lower())
                self.assertFalse((self.root / 'build').exists())

    def test_extra_arguments_are_rejected(self):
        for script in ['run_public_tests.sh', 'run_integration_tests.sh',
                       'run_security_tests.sh']:
            with self.subTest(script=script):
                result = self.run_script(script, 'arm64', 'unexpected')
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn('Usage:', result.stderr)
                self.assertFalse((self.root / 'build').exists())

    def test_public_missing_build_has_an_actionable_diagnostic(self):
        result = self.run_script('run_public_tests.sh', 'arm64')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('build/arm64', result.stderr)
        self.assertIn('scripts/build.sh arm64', result.stderr)
        self.assertFalse((self.root / 'build').exists())

    def test_integration_missing_assets_stops_before_compilation(self):
        for script, arguments in [('run_integration_tests.sh', ['arm64']),
                                  ('run_swift_tests.sh', ['--integration', 'arm64'])]:
            with self.subTest(script=script):
                result = self.run_script(script, *arguments)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn('CAUCES_MODEL_DIR', result.stderr)
                self.assertIn('not skipped', result.stderr)
                self.assertFalse((self.root / 'build').exists())

    def test_wav_probe_rejects_invalid_architecture_before_worker_launch(self):
        environment = dict(os.environ, DS_TEST_ARCH='invalid-architecture')
        result = subprocess.run(['/usr/bin/python3', str(self.root / 'tests/wav_adversarial.py')],
                                env=environment, capture_output=True, text=True, timeout=15)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Unsupported test architecture', result.stderr)
        self.assertNotIn('FileNotFoundError', result.stderr)

    def test_missing_tool_has_a_diagnostic_before_compilation(self):
        result = subprocess.run(['/bin/bash', '-c',
                                 'source "$1/tests/test_helpers.sh"; cauces_test_tools cauces_missing_test_tool',
                                 'runner-preflight', str(self.root)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('Missing tool: cauces_missing_test_tool', result.stderr)
        self.assertFalse((self.root / 'build').exists())


if __name__ == '__main__':
    unittest.main()
