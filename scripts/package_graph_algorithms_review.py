"""Build and independently inspect the requested local review snapshot."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'artifacts/review-packages/graph-algorithms/algorithm-atlas-graph-algorithms-review.zip'
PREFIX = 'algorithm-atlas/'
EXCLUDED_DIRS = {
    '.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache', '.mypy_cache',
    '.ruff_cache', '.tox', '.nox', 'htmlcov', 'build', 'dist', 'CMakeFiles',
    '.aws', '.ssh', '.gnupg', '.codex', '.agents', '.idea', '.vscode',
    'node_modules', '.cache', 'data', 'datasets', 'models', 'checkpoints',
}
EXCLUDED_SUFFIXES = {
    '.zip', '.pyc', '.pyo', '.o', '.obj', '.a', '.so', '.dylib', '.dll',
    '.exe', '.out', '.pem', '.key', '.p12', '.pfx', '.log', '.tmp', '.temp',
    '.swp', '.swo', '.pt', '.pth', '.ckpt', '.onnx', '.h5',
}
EXCLUDED_NAMES = {
    '.DS_Store', 'Thumbs.db', '.coverage', '.git-credentials', '.netrc',
    '.npmrc', '.pypirc', 'credentials', 'credentials.json', 'secrets.json',
    'secrets.yaml', 'secrets.yml', 'id_rsa', 'id_ed25519', 'CMakeCache.txt',
    'compile_commands.json',
}
PATTERNS = {
    'private-key': rb'-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----',
    'aws-access-key': rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'github-token': rb'\bgh[pousr]_[A-Za-z0-9]{30,}\b',
    'github-fine-token': rb'\bgithub_pat_[A-Za-z0-9_]{50,}\b',
    'openai-key': rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b',
    'credential-url': rb'https?://[^\s/:]+:[^\s/@]+@',
}


def excluded(path):
    return (
        bool(set(path.parts) & EXCLUDED_DIRS)
        or any(part.startswith('cmake-build-') or part.endswith(('.egg-info', '.dSYM')) for part in path.parts)
        or path.suffix.lower() in EXCLUDED_SUFFIXES
        or path.name in EXCLUDED_NAMES
        or '.zip.' in path.name
        or (path.name.startswith('.env') and path.name != '.env.example')
    )


def run(command, cwd):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stdout + result.stderr
    return {'command': ['python' if arg == sys.executable else arg for arg in command],
            'returncode': result.returncode, 'timeout_seconds': 120,
            'timed_out': False, 'output': result.stdout + result.stderr}


def main():
    listed = subprocess.run(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
        cwd=ROOT, capture_output=True, check=True,
    ).stdout.decode().split('\0')
    paths = sorted({PurePosixPath(value) for value in listed if value
                    and (ROOT / value).exists() and not excluded(PurePosixPath(value))})
    payload = {}
    for relative in paths:
        source = ROOT / relative
        assert not source.is_symlink() and source.is_file(), relative
        assert not relative.is_absolute() and '..' not in relative.parts, relative
        data = source.read_bytes()
        # This repository contains text deliverables; do not silently ship binaries.
        data.decode('utf-8')
        for label, pattern in PATTERNS.items():
            assert not re.search(pattern, data), f'Potential credential: {relative} ({label})'
        payload[relative.as_posix()] = data

    import yaml
    catalog = yaml.safe_load(payload['catalog.yaml'])
    required = {'README.md','LICENSE','AGENTS.md','CONTRIBUTING.md','catalog.yaml',
                'docs/reviews/graph-algorithms/GRAPH-ALGORITHMS-REVIEW-REPORT.md','docs/progress.md',
                'docs/graph-algorithms-checkpoints.md','scripts/run_graph_algorithms_validation.py',
                'scripts/verify_graph_algorithms_scope.py','scripts/verify_graph_algorithms_examples.py',
                'scripts/verify_graph_algorithms_tracking.py',
                'scripts/package_graph_algorithms_review.py',
                'docs/graph-algorithms-evidence/final-results.json',
                'docs/graph-algorithms-evidence/sanitizer-results.json',
                'docs/graph-algorithms-evidence/configuration-results.json',
                'docs/graph-algorithms-evidence/batch1-results.json',
                'docs/graph-algorithms-evidence/batch2-results.json',
                'docs/graph-algorithms-evidence/batch3-results.json',
                'docs/graph-algorithms-evidence/batch4-results.json',
                'docs/graph-algorithms-evidence/batch5-results.json',
                'docs/graph-algorithms-evidence/cross-matrix-batch5.json',
                'docs/graph-conventions.md',
                'scripts/verify_graph_cross_algorithms.py',
                'docs/graph-algorithms-evidence/tracking-results.json',
                'docs/graph-algorithms-evidence/preservation-results.json',
                'docs/graph-algorithms-evidence/catalog-baseline.yaml',
                'docs/graph-algorithms-evidence/approved-baseline.json',
                'docs/graph-algorithms-evidence/oracle-inventory.json',
                'docs/graph-algorithms-evidence/examples-results.json',
                'docs/graph-algorithms-evidence/changed-files.txt',
                'dsa/graph-algorithms/common.hpp','dsa/graph-algorithms/conftest.py','.github/workflows/ci.yml'}
    for algorithm in catalog['algorithms']:
        folder = algorithm['canonical_location']
        required.add(folder+'/README.md')
        if algorithm['test_status'] in ('tested','reviewed'):
            required.update(folder+'/'+part for part in (
                'python/solution.py','cpp/solution.cpp','tests/test_python.py','tests/test_cpp.py'))
    from validate_catalog import GRAPH_BATCHES
    for batch in GRAPH_BATCHES:
        for name in batch:
            required.add('dsa/graph-algorithms/'+name+'/tests/cases.py')
    required.update({'scripts/review_paths.py', 'docs/maintenance/root-cleanup/manifest.json'})
    assert required <= payload.keys(), sorted(required-payload.keys())

    directories = {PREFIX}
    for name in payload:
        for parent in PurePosixPath(name).parents:
            if parent.as_posix() != '.':
                directories.add(PREFIX + parent.as_posix() + '/')

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    assert not OUTPUT.exists(), 'Refusing to overwrite an existing review artifact'
    with zipfile.ZipFile(OUTPUT, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(directories):
            info = zipfile.ZipInfo(name, (2026, 10, 23, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFDIR | 0o755) << 16 | 0x10
            archive.writestr(info, b'')
        for name, data in payload.items():
            info = zipfile.ZipInfo(PREFIX + name, (2026, 10, 23, 0, 0, 0))
            info.create_system = 3
            mode = 0o755 if os.access(ROOT / name, os.X_OK) else 0o644
            info.external_attr = (stat.S_IFREG | mode) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data, compresslevel=9)

    with zipfile.ZipFile(OUTPUT) as archive:
        assert archive.testzip() is None
        entries = archive.infolist()
        assert len({entry.filename for entry in entries}) == len(entries)
        assert {entry.filename for entry in entries if not entry.is_dir()} == {PREFIX + name for name in payload}
        assert {entry.filename for entry in entries if entry.is_dir()} == directories
        for entry in entries:
            path = PurePosixPath(entry.filename)
            assert entry.filename.startswith(PREFIX) and not path.is_absolute() and '..' not in path.parts
            assert not stat.S_ISLNK(entry.external_attr >> 16)
            if not entry.is_dir():
                relative = entry.filename[len(PREFIX):]
                assert not excluded(PurePosixPath(relative))
                assert archive.read(entry) == payload[relative]
        with tempfile.TemporaryDirectory(prefix='atlas-final-extracted-') as temporary:
            archive.extractall(temporary)
            extracted = Path(temporary) / 'algorithm-atlas'
            checks = [run([sys.executable, 'scripts/validate_catalog.py'], extracted),
                      run([sys.executable, 'scripts/generate_catalog_docs.py', '--check'], extracted),
                      run([sys.executable, 'scripts/verify_graph_algorithms_scope.py', '--check-only'], extracted)]

    digest = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    OUTPUT.with_suffix('.zip.sha256').write_text(f'{digest}  {OUTPUT.name}\n')
    verification = {
        'archive': OUTPUT.name, 'sha256': digest, 'bytes': OUTPUT.stat().st_size,
        'regular_files': len(payload), 'directory_entries': len(directories),
        'total_entries': len(payload) + len(directories), 'crc_test': 'passed',
        'unique_safe_relative_paths': True, 'symlinks': 0,
        'source_byte_comparison': 'all regular files identical',
        'required_paths_present': True, 'excluded_artifacts_present': False,
        'high_confidence_credential_scan': 'no matches',
        'credential_pattern_labels': list(PATTERNS),
        'extracted_configuration_checks': checks,
        'files': {name: hashlib.sha256(data).hexdigest() for name, data in payload.items()},
    }
    OUTPUT.with_suffix('.zip.verification.json').write_text(json.dumps(verification, indent=2) + '\n')
    print(json.dumps({key: value for key, value in verification.items() if key != 'files'}, indent=2))


if __name__ == "__main__":
    main()
