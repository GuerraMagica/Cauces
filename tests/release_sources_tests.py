"""Source preflight must reject missing, changed and unexpected dependency trees."""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import audit_dependencies

class ReleaseSourceTests(unittest.TestCase):
    def test_pinned_tree_checks_reject_tampering_and_missing_dependencies(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);tree=root/'build/ort-intel-1.31.1/_deps/example-src';tree.mkdir(parents=True)
            (tree/'LICENSE').write_text('upstream notice')
            inventory={'local_source_trees':{'example-src':audit_dependencies.tree_hash(tree)}}
            audit_dependencies.verify_dependency_trees(root,inventory)
            (tree/'LICENSE').write_text('altered')
            with self.assertRaises(ValueError):audit_dependencies.verify_dependency_trees(root,inventory)
            (tree/'LICENSE').unlink();tree.rmdir()
            with self.assertRaises(ValueError):audit_dependencies.verify_dependency_trees(root,inventory)

    def test_internal_links_are_hashed_and_external_links_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);tree=root/'tree';tree.mkdir();(tree/'file').write_text('source')
            (tree/'link').symlink_to('file')
            self.assertTrue(audit_dependencies.tree_hash(tree))
            (tree/'link').unlink();(tree/'link').symlink_to('../outside')
            with self.assertRaises(ValueError):audit_dependencies.tree_hash(tree)

    def test_unreviewed_extra_tree_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'build/ort-intel-1.31.1/_deps/extra-src').mkdir(parents=True)
            with self.assertRaises(ValueError):audit_dependencies.verify_dependency_trees(root,{'local_source_trees':{}})

if __name__=='__main__':unittest.main()
