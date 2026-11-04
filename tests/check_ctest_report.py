"""Require all published CTest contracts and reject partial/failed test reports."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


REQUIRED_CONTRACTS = {
    'dsp_contracts', 'pipeline_contracts', 'wav_contracts', 'api_contracts',
    'cleanup_identity', 'storage_bounds', 'nonregular_copy', 'wav_without_dev_fd',
}


def validate_report(path):
    try:
        cases = ET.parse(path).findall('.//testcase')
    except (OSError, ET.ParseError) as error:
        raise ValueError(f'Cannot read CTest report: {error}') from error
    missing = REQUIRED_CONTRACTS - {case.get('name') for case in cases}
    if missing:
        raise ValueError('Missing CTest contracts: ' + ', '.join(sorted(missing))
                         + '. Reconfigure and rebuild this architecture.')
    incomplete = [case.get('name', '<unnamed>') for case in cases
                  if any(case.find(tag) is not None for tag in ('skipped', 'failure', 'error'))]
    if incomplete:
        raise ValueError('CTest contracts did not pass: ' + ', '.join(incomplete))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python3 tests/check_ctest_report.py <report.xml>')
    try:
        validate_report(Path(sys.argv[1]))
    except ValueError as error:
        print(f'Cauces tests: {error} No public PASS is reported.', file=sys.stderr)
        raise SystemExit(1)
