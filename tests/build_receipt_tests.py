"""Receipts must reject stale code, replaced outputs and missing records."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class BuildReceiptTests(unittest.TestCase):
    def module(self):
        spec=importlib.util.spec_from_file_location('build_receipt',ROOT/'scripts/build_receipt.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

    def fixture(self,root):
        names=['src/example.cpp','CMakeLists.txt','scripts/build.sh','scripts/build_receipt.py',
               'vendor/json/include/example.hpp','vendor/onnxruntime-osx-arm64-1.31.1/include/example.h',
               'vendor/onnxruntime-osx-arm64-1.31.1/lib/libonnxruntime.1.31.1.dylib',
               'build/arm64/Cauces','build/arm64/dialogue-worker','build/arm64/libdialogue_separator.dylib']
        for name in names:
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(name.encode())

    def test_valid_record_then_changed_source_is_rejected(self):
        module=self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root);module.begin(root,'arm64');module.record(root,'arm64');module.verify(root,'arm64')
            (root/'src/example.cpp').write_text('changed code')
            with self.assertRaises(ValueError):module.verify(root,'arm64')

    def test_replaced_binary_and_runtime_are_rejected(self):
        module=self.module()
        for name in ['build/arm64/Cauces','vendor/onnxruntime-osx-arm64-1.31.1/lib/libonnxruntime.1.31.1.dylib']:
            with self.subTest(name=name),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);self.fixture(root);module.begin(root,'arm64');module.record(root,'arm64')
                (root/name).write_text('replacement')
                with self.assertRaises(ValueError):module.verify(root,'arm64')

    def test_change_during_build_is_rejected(self):
        module=self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root);module.begin(root,'arm64')
            (root/'src/example.cpp').write_text('changed during build')
            with self.assertRaises(ValueError):module.record(root,'arm64')

    def test_missing_receipt_fails(self):
        module=self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);self.fixture(root)
            with self.assertRaises(FileNotFoundError):module.verify(root,'arm64')

if __name__=='__main__':unittest.main()
