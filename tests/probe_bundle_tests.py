"""Exercise the real probe entry points with disposable, non-executable bundles."""
import os
import plistlib
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
PROBES = ('sandbox_probe.py', 'output_settings_probe.py')


class PreparationComplete(Exception):
    """Stop before any compiler, signature, playback or app execution."""


def snapshot(directory):
    return {str(p.relative_to(directory)): ('link', os.readlink(p)) if p.is_symlink()
            else ('file', p.read_bytes()) for p in directory.rglob('*') if not p.is_dir()}


class ProbeBundleTests(unittest.TestCase):
    def run_probe(self, name, change=None, valid=False, architecture='arm64', flags=(), during_copy=None):
        with tempfile.TemporaryDirectory(prefix='cauces probe boundary ') as temporary:
            root = Path(temporary)
            tests = root/'tests'; tests.mkdir()
            shutil.copyfile(ROOT/'tests'/name, tests/name)
            helper = ROOT/'tests/probe_bundle.py'
            if helper.exists():
                shutil.copyfile(helper, tests/helper.name)
            (root/'build/performance-fixtures').mkdir(parents=True)
            source = root/'build/performance-fixtures/benchmark-8s.wav'
            source.write_bytes(b'synthetic copy fixture; never decoded or played')
            (source.parent/'settings-44k1.wav').write_bytes(source.read_bytes())
            app = root/'input.app'
            (app/'Contents/MacOS').mkdir(parents=True)
            (app/'Contents/Resources').mkdir()
            info = {'CFBundleExecutable': 'Cauces', 'CFBundleName': 'Cauces'}
            (app/'Contents/Info.plist').write_bytes(plistlib.dumps(info))
            (app/'Contents/MacOS/Cauces').write_bytes(b'not an executable')
            outside = root/'outside'; outside.mkdir()
            (outside/'sentinel').write_bytes(b'preserve external original')
            if change:
                change(app, outside, info)
            before = snapshot(outside)
            original = snapshot(app)
            commands = []
            real_run = subprocess.run

            def intercept(command, *args, **kwargs):
                nonlocal original
                commands.append(command)
                if command[0] == 'cp':
                    if during_copy and len(commands) == 1:
                        during_copy(app, outside)
                        original = snapshot(app)
                    return real_run(command, *args, **kwargs)
                raise PreparationComplete()

            arguments = [str(tests/name), str(app)]
            arguments += [str(source), architecture] if name == 'sandbox_probe.py' else [architecture, *flags]
            previous = sys.modules.pop('probe_bundle', None)
            try:
                with mock.patch.object(sys, 'argv', arguments), \
                     mock.patch.object(sys, 'path', [str(tests), *sys.path]), \
                     mock.patch('subprocess.run', side_effect=intercept):
                    try:
                        runpy.run_path(str(tests/name), run_name='__main__')
                    except PreparationComplete:
                        stopped_at_compiler = True
                    except (ValueError, OSError, KeyError, TypeError, plistlib.InvalidFileException,
                            subprocess.CalledProcessError):
                        stopped_at_compiler = False
                    else:
                        self.fail('Probe unexpectedly completed')
            finally:
                sys.modules.pop('probe_bundle', None)
                if previous is not None:
                    sys.modules['probe_bundle'] = previous
            self.assertEqual(snapshot(outside), before, 'Probe modified an external file')
            self.assertEqual(snapshot(app), original, 'Probe modified its input bundle')
            self.assertEqual(stopped_at_compiler, valid, commands)
            if not valid:
                self.assertLessEqual(len(commands), 1, 'Invalid bundle reached a write after copying')
            if valid:
                destination = next(Path(c[-1]) for c in commands if c[0] == 'cp')
                expected = 'CaucesAudit' if name == 'sandbox_probe.py' else 'CaucesOutputAudit'
                copied = plistlib.loads((destination/'Contents/Info.plist').read_bytes())
                self.assertEqual(copied['CFBundleExecutable'], expected)
                self.assertFalse((destination/'Contents/MacOS/Cauces').exists())
                self.assertTrue((destination/'Contents/Resources/audit-input.wav').is_file())

    def test_valid_bundles_reach_preparation_without_executing_code(self):
        for name in PROBES:
            for architecture in ('arm64', 'x86_64'):
                with self.subTest(probe=name, architecture=architecture):
                    self.run_probe(name, valid=True, architecture=architecture)

    def test_output_options_keep_the_same_preparation_path(self):
        for flag in ('--source-44k1', '--restore-48k', '--clock-only', '--allow-rejection'):
            with self.subTest(option=flag):
                self.run_probe('output_settings_probe.py', valid=True,
                               flags=(flag, '--device-id', '42'))

    def test_a_source_changed_during_copy_is_revalidated(self):
        for name in PROBES:
            with self.subTest(probe=name):
                def redirect(app, outside):
                    (app/'Contents/Info.plist').unlink()
                    (app/'Contents/Info.plist').symlink_to(outside/'sentinel')
                self.run_probe(name, during_copy=redirect)

    def test_hostile_executable_values_preserve_external_files(self):
        values = ('absolute', 'traversal', '', '.', '..', 'sub/Cauces',
                  'sub\\Cauces', 'Cauces\0', 42, True, ['Cauces'], 'missing')
        for name in PROBES:
            for value in values:
                with self.subTest(probe=name, value=value):
                    def change(app, outside, info):
                        if value == 'missing':
                            info.pop('CFBundleExecutable')
                        else:
                            info['CFBundleExecutable'] = (str(outside/'sentinel') if value == 'absolute'
                                else '../../../../../outside/sentinel' if value == 'traversal' else value)
                        (app/'Contents/Info.plist').write_bytes(plistlib.dumps(info, fmt=plistlib.FMT_BINARY))
                    self.run_probe(name, change)

    def test_symlink_components_and_write_targets_are_rejected(self):
        targets = ('Contents', 'Contents/MacOS', 'Contents/Resources',
                   'Contents/Info.plist', 'Contents/MacOS/Cauces',
                   'Contents/Resources/audit-input.wav', 'Contents/MacOS/CaucesAudit',
                   'Contents/MacOS/CaucesOutputAudit', 'Contents/MacOS/network-control',
                   'Contents/MacOS/dialogue-worker')
        for name in PROBES:
            for relative in targets:
                with self.subTest(probe=name, target=relative):
                    def change(app, outside, info):
                        target = app/relative
                        external = outside/'redirected'
                        if target.exists():
                            shutil.move(str(target), str(external))
                        else:
                            external.write_bytes(b'preserve external write target')
                        target.symlink_to(external, target_is_directory=external.is_dir())
                    self.run_probe(name, change)

    def test_invalid_plist_and_missing_directories_are_rejected(self):
        for name in PROBES:
            for kind in ('invalid', 'not-dict', 'missing-resources', 'missing-executable'):
                with self.subTest(probe=name, case=kind):
                    def change(app, outside, info):
                        if kind == 'invalid':
                            (app/'Contents/Info.plist').write_bytes(b'not a plist')
                        elif kind == 'not-dict':
                            (app/'Contents/Info.plist').write_bytes(plistlib.dumps(['Cauces']))
                        elif kind == 'missing-resources':
                            (app/'Contents/Resources').rmdir()
                        else:
                            (app/'Contents/MacOS/Cauces').unlink()
                    self.run_probe(name, change)


if __name__ == '__main__':
    unittest.main()
