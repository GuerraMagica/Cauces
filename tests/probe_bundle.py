"""Prepare a private test copy; never trust paths embedded in a supplied app.

Only use authenticated Cauces builds: these probes later run packaged code.
The caller owns the private mkdtemp parent. This is not isolation against a
concurrent writer running as the same user.
"""
import os
import plistlib
import stat
import subprocess
from pathlib import Path


def validate_bundle(app):
    app = Path(app)
    if not stat.S_ISDIR(app.lstat().st_mode):
        raise ValueError('The probe input must be a real app directory.')
    for directory, folders, files in os.walk(app, followlinks=False):
        for name in folders + files:
            mode = (Path(directory)/name).lstat().st_mode
            if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise ValueError('Probe bundles must contain only regular files and directories, without symlinks.')
    for relative in ('Contents', 'Contents/MacOS', 'Contents/Resources'):
        if not stat.S_ISDIR((app/relative).lstat().st_mode):
            raise ValueError('The probe app is missing a required real directory.')
    plist = app/'Contents/Info.plist'
    if not stat.S_ISREG(plist.lstat().st_mode):
        raise ValueError('The probe Info.plist must be a regular file.')
    info = plistlib.loads(plist.read_bytes())
    if not isinstance(info, dict) or info.get('CFBundleExecutable') != 'Cauces':
        raise ValueError('The probe app must declare the expected executable name Cauces.')
    if not stat.S_ISREG((app/'Contents/MacOS/Cauces').lstat().st_mode):
        raise ValueError('The Cauces executable must be a regular file.')
    return info


def prepare_probe_copy(app, probe, bundle_identifier, executable):
    """Validate before copying and again before any mutation of the private copy."""
    probe = Path(probe)
    if executable not in ('CaucesAudit', 'CaucesOutputAudit'):
        raise ValueError('Unknown probe executable.')
    parent = probe.parent.lstat()
    if not stat.S_ISDIR(parent.st_mode) or parent.st_uid != os.getuid() or parent.st_mode & 0o077:
        raise ValueError('The probe requires an owned private temporary parent.')
    if probe.exists() or probe.is_symlink():
        raise FileExistsError(probe)
    validate_bundle(app)
    # -P preserves links as links rather than following a source changed during
    # copying. The second validation rejects them before plist/file mutations.
    subprocess.run(['cp', '-cRP', str(app), str(probe)], check=True)
    info = validate_bundle(probe)
    (probe/'Contents/MacOS/Cauces').unlink()
    info.update(CFBundleIdentifier=bundle_identifier, CFBundleExecutable=executable)
    (probe/'Contents/Info.plist').write_bytes(plistlib.dumps(info))
