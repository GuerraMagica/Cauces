"""Check release licence material on disk without models or inference."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class LicencePackageTests(unittest.TestCase):
    def load(self):
        spec = importlib.util.spec_from_file_location('package_licenses', ROOT/'scripts/package_licenses.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_material_is_copied_exactly_with_scoped_licence_and_json_attributions(self):
        module = self.load()
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)/'Licenses'
            module.copy_licences(ROOT, destination)
            self.assertEqual((destination/'GPL-3.0-only.txt').read_bytes(), (ROOT/'LICENSE').read_bytes())
            self.assertEqual((destination/'Apache-2.0.txt').read_bytes(), (ROOT/'docs/commercial/licenses/Apache-2.0.txt').read_bytes())
            self.assertEqual((destination/'LICENSE_SCOPE.md').read_bytes(), (ROOT/'LICENSE_SCOPE.md').read_bytes())
            self.assertEqual((destination/'ONNXRuntime-ThirdPartyNotices.txt').read_bytes(), (ROOT/'vendor/onnxruntime-osx-arm64-1.31.1/ThirdPartyNotices.txt').read_bytes())
            attribution = (destination/'nlohmann-json-HEADER-NOTICES.txt').read_text()
            for author in ['Niels Lohmann', 'Evan Nemerson', 'Björn Hoehrmann', 'Florian Loitsch', 'The Abseil Authors']:
                self.assertIn(author, attribution)
            self.assertTrue((destination/'dependency-inventory.json').is_file())
            self.assertTrue((destination/'SOURCE_INFORMATION.md').is_file())

    def test_missing_inputs_fail_before_creating_destination(self):
        module = self.load()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)/'empty'; root.mkdir()
            target = Path(directory)/'output'
            with self.assertRaises((FileNotFoundError, ValueError)):
                module.copy_licences(root, target)
            self.assertFalse(target.exists())

    def test_existing_destination_is_not_overwritten(self):
        module = self.load()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)/'Licenses'; target.mkdir()
            sentinel = target/'GPL-3.0-only.txt'; sentinel.write_text('original')
            with self.assertRaises(FileExistsError):
                module.copy_licences(ROOT, target)
            self.assertEqual(sentinel.read_text(), 'original')

if __name__ == '__main__':
    unittest.main()
