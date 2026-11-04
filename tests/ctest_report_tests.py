"""A partial CTest report must never count as the public contract suite passing."""
from pathlib import Path
import subprocess
import tempfile
import unittest


CHECKER = Path(__file__).with_name('check_ctest_report.py')
# The eight published contracts are the public requirement, independent of a
# particular generated build directory or the checker's implementation.
CONTRACTS = ('dsp_contracts', 'pipeline_contracts', 'wav_contracts', 'api_contracts',
             'cleanup_identity', 'storage_bounds', 'nonregular_copy', 'wav_without_dev_fd')


class CTestReportContracts(unittest.TestCase):
    def check_report(self, names=CONTRACTS, status='', malformed=False):
        with tempfile.TemporaryDirectory(prefix='cauces-ctest-report-') as directory:
            path = Path(directory) / 'report.xml'
            cases = ''.join(f'<testcase name="{name}">{status if i == 0 else ""}</testcase>'
                            for i, name in enumerate(names))
            path.write_text('<testsuite>' + cases + '</testsuite>' if not malformed else '<broken')
            return subprocess.run(['/usr/bin/python3', str(CHECKER), str(path)],
                                  capture_output=True, text=True, timeout=10)

    def test_complete_passing_report_is_accepted(self):
        result = self.check_report()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_registered_contract_is_rejected(self):
        result = self.check_report(names=CONTRACTS[:-1])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('wav_without_dev_fd', result.stderr)

    def test_disabled_contract_is_rejected(self):
        result = self.check_report(status='<skipped message="disabled"/>')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('dsp_contracts', result.stderr)

    def test_failed_contract_is_rejected(self):
        result = self.check_report(status='<failure message="failed"/>')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('dsp_contracts', result.stderr)

    def test_additional_passing_contracts_remain_supported(self):
        result = self.check_report(names=CONTRACTS + ('new_contract',))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_malformed_report_is_an_explicit_error(self):
        result = self.check_report(malformed=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Cannot read CTest report', result.stderr)


if __name__ == '__main__':
    unittest.main()
