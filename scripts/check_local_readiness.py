"""Read-only environment/Day10 integrity check; never trains or evaluates."""
import hashlib
import importlib.metadata
import json
import platform
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    failures = []
    packages = {}
    for line in (ROOT / 'requirements.txt').read_text().splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        match = re.fullmatch(r'([\w-]+)(?:\[[\w,-]+\])?==([^\s]+)', line.strip())
        if not match:
            raise ValueError('Unsupported requirement format')
        name, expected = match.groups()
        names = [name, 'psycopg-binary'] if name == 'psycopg' else [name]
        for package in names:
            try:
                actual = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                actual = None
            packages[package] = {'expected': expected, 'installed': actual}
            if actual != expected:
                failures.append('package: ' + package)
    if sys.version_info[:2] != (3, 11):
        failures.append('Python 3.11 required by local baseline')
    folder = ROOT / 'reports/day10/final_20261123'
    lock = json.loads((folder / 'selection_lock.json').read_text())
    manifest = json.loads((folder / 'manifest.json').read_text())
    audit = json.loads((folder / 'validation.json').read_text())
    groups = {'locked': lock['hashes'], 'inputs': manifest['inputs'],
              'outputs': manifest['outputs'], 'evidence': {
                  'reports/day10/final_20261123/metrics.json': manifest['metrics_sha256'],
                  'reports/day10/final_20261123/selection_lock.json': manifest['selection_lock_sha256'],
                  'reports/day10/final_20261123/manifest.json': audit['manifest_sha256'],
                  'scripts/day10_evaluate.py': manifest['script_sha256'],
                  'scripts/verify_day10.py': audit['verifier_sha256']}}
    verified = {}
    for group, entries in groups.items():
        verified[group] = 0
        for relative, expected in entries.items():
            path = (ROOT / relative.replace('\\', '/')).resolve()
            if not path.is_relative_to(ROOT):
                raise ValueError('Manifest path outside project')
            if not path.is_file() or digest(path) != expected:
                failures.append('hash: ' + relative)
            else:
                verified[group] += 1
    print(json.dumps({'checked_at_utc': datetime.now(timezone.utc).isoformat(),
                     'python': platform.python_version(), 'platform': platform.system(),
                     'packages': packages, 'verified_hashes': verified,
                     'failures': failures, 'passed': not failures,
                     'scope': 'Existing local environment and Day10 file integrity only',
                     'training_or_metric_recalculation': False,
                     'clean_environment_rebuild': False}, indent=2))
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
