"""Freeze Phase20 source and independently validate the actual ZIP extraction.

No output overwrite, Git mutation, network installer or nested review archive.
Post-freeze extraction results live in external JSON to avoid recursive hashes.
"""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
import time
import zipfile
from zoneinfo import ZoneInfo

import yaml
from package_bit_manipulation_review import excluded
from package_tree_algorithms_review import PATTERNS
from track_policy import cpp_required, is_complete
from verify_reinforcement_learning_scope import verify, REPORT

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/reinforcement-learning-evidence'
OUTPUT = ROOT / 'artifacts/review-packages/reinforcement-learning/algorithm-atlas-reinforcement-learning-review.zip'
PREFIX = 'algorithm-atlas/'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    sidecar, checksum = OUTPUT.with_suffix('.json'), OUTPUT.with_suffix('.zip.sha256')
    assert not any(p.exists() for p in (OUTPUT, sidecar, checksum)), 'Refusing to overwrite review artifacts'
    preservation = verify(require_tracked=True)
    final = json.loads((EVIDENCE / 'final-results.json').read_text())
    config = json.loads((EVIDENCE / 'configuration-results.json').read_text())
    matrix = json.loads((EVIDENCE / 'test-matrix.json').read_text())
    assert all(r['returncode'] == 0 and not r['timed_out'] for r in [*final.values(), *config.values()])
    assert matrix['failures'] == matrix['errors'] == matrix['skipped'] == 0
    for batch in range(1, 6):
        gate = json.loads((EVIDENCE / f'batch{batch}-gate.json').read_text())
        assert gate['returncode'] == 0
    names = subprocess.check_output(['git', 'ls-files', '-c', '-o', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')
    paths = sorted({PurePosixPath(name) for name in names if name and (ROOT / name).is_file() and not excluded(PurePosixPath(name))})
    payload = {}
    for name in paths:
        path = ROOT / name
        assert not path.is_symlink() and not name.is_absolute() and '..' not in name.parts
        data = path.read_bytes()
        data.decode('utf-8')
        for label, pattern in PATTERNS.items():
            assert not re.search(pattern, data), f'Potential credential: {name} ({label})'
        payload[name.as_posix()] = data
    catalog = yaml.safe_load(payload['catalog.yaml'])
    state = catalog['development']
    assert state['status'] == 'awaiting-review' and state['phase_number'] == 20
    b8 = [a for a in catalog['algorithms'] if a['category'] == 'B8']
    assert len(b8) == 10 and sum(is_complete(a) for a in b8) == 9
    decision = state['dpo_specification_decision']
    assert decision['owner_approval'] == 'approved' and decision['decision'] == 'remain-blocked'
    assert state['current_review']['owner_approval'] == state['phase_records']['20']['owner_approval'] == 'pending'
    previous_package = json.loads((EVIDENCE / 'outcome3-history-moves.json').read_text())
    for move in previous_package['moves']:
        assert sha((ROOT / move['new']).read_bytes()) == move['sha256']
    required = {REPORT, 'README.md', 'AGENTS.md', 'CONTRIBUTING.md', 'LICENSE', 'catalog.yaml',
                'requirements-dev.txt', 'requirements-ml.txt', 'requirements-ml-test.txt',
                'pyproject.toml', 'conftest.py', '.github/workflows/ci.yml',
                'scripts/validate_catalog.py', 'scripts/generate_catalog_docs.py',
                'scripts/track_policy.py', 'scripts/verify_reinforcement_learning_scope.py',
                'scripts/verify_reinforcement_learning_examples.py', 'scripts/evaluate_reinforcement_learning.py',
                'scripts/run_reinforcement_learning_validation.py', 'scripts/package_reinforcement_learning_review.py',
                'docs/reinforcement-learning-scope.md', 'docs/reinforcement-learning-checkpoints.md',
                'docs/reinforcement-learning-conventions.md', 'docs/terminology-decisions.md',
                'machine-learning/reinforcement-learning/support.py', 'machine-learning/reinforcement-learning/conftest.py',
                'machine-learning/reinforcement-learning/tests/oracles.py',
                'machine-learning/reinforcement-learning/tests/test_contracts.py',
                'machine-learning/reinforcement-learning/dynamic-policy-optimization/README.md',
                'tests/test_b8_language_and_blocker_policy.py'}
    required.update({decision['report'], decision['evidence'],
                     'docs/reinforcement-learning-evidence/outcome3-finalization-baseline.json',
                     'docs/reinforcement-learning-evidence/outcome3-catalog-baseline.yaml',
                     'docs/reinforcement-learning-evidence/outcome3-history-moves.json'})
    # Include required source/tests of every completed canonical, not only B8.
    for a in catalog['algorithms']:
        required.add(a['canonical_location'] + '/README.md')
        if is_complete(a):
            required.update(a['canonical_location'] + '/' + part for part in ('python/solution.py', 'tests/test_python.py'))
            if cpp_required(a):
                required.update(a['canonical_location'] + '/' + part for part in ('cpp/solution.cpp', 'tests/test_cpp.py'))
    for a in b8:
        if is_complete(a):
            required.add(a['canonical_location'] + '/python/example.py')
    required.update(n for n in payload if n.startswith('docs/reviews/') and n.endswith('.md'))
    baseline = json.loads((EVIDENCE / 'baseline.json').read_text())
    required.update(n for n in baseline['hashes'] if n.startswith('docs/reviews/') and n.endswith('.md'))
    for name in ('baseline.json', 'catalog-baseline.yaml', 'approval-evidence.json', 'final-results.json',
                 'configuration-results.json', 'test-matrix.json', 'preservation-results.json',
                 'examples-results.json', 'educational-training-results.json', 'development-findings.json',
                 'reference-sources.json', 'changed-files.json', 'negative-validation-matrix.json'):
        required.add('docs/reinforcement-learning-evidence/' + name)
    assert required <= payload.keys(), sorted(required - payload.keys())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in payload.items():
            info = zipfile.ZipInfo(PREFIX + name, date_time=(2026, 10, 31, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, data)
    digest = sha(OUTPUT.read_bytes())
    checksum.write_text(f'{digest}  {OUTPUT.name}\n')
    metadata = dict(phase_number=20, phase_name=state['phase'], category_id='B8', category_name='Reinforcement Learning',
                    catalog_entries=10, implementation_count=9, blocked_count=1, blocked=['dynamic-policy-optimization'],
                    algorithm_ids=[a['id'] for a in b8], owner_approval='pending', phase19_owner_approval='approved',
                    dpo_owner_decision='owner-approved: remain blocked (Outcome 3); no substitute authorized',
                    dpo_specification_owner_approval='approved', dpo_specification_decision=decision,
                    implementation_completion=dict(defined_algorithms=9, completed_algorithms=9, complete=True),
                    catalog_completion=dict(entries=10, completed=9, intentionally_blocked=1, complete=False),
                    previous_phase20_package_preservation=previous_package,
                    client_review_date='2026-10-31 Asia/Dhaka', execution_timestamp=datetime.now(ZoneInfo('Asia/Dhaka')).isoformat(),
                    starting_revision=baseline['revision'], branch=baseline['branch'], dependencies_changed=False,
                    environment=baseline['environment'], report=REPORT, report_tracking_status='tracked and unignored',
                    archive=OUTPUT.name, bytes=OUTPUT.stat().st_size, files=len(payload), sha256=digest,
                    file_sha256={n: sha(data) for n, data in payload.items()}, required_files=sorted(required),
                    local_test_matrix=matrix, local_validation=final, configuration_validation=config,
                    prior_source_preservation=preservation, source_only=True, nested_archives=False,
                    hosted_github_actions='not executed or verified', extraction_checks=[], extraction_validation_status='running')

    def save():
        sidecar.write_text(json.dumps(metadata, indent=2) + '\n')
    save()
    with tempfile.TemporaryDirectory(prefix='atlas-b8-export-') as temp:
        folder = Path(temp)
        with zipfile.ZipFile(OUTPUT) as archive:
            assert archive.testzip() is None
            infos = archive.infolist()
            assert len(infos) == len({i.filename for i in infos}) == len(payload)
            for info in infos:
                path = PurePosixPath(info.filename)
                assert path.parts[0] == 'algorithm-atlas' and len(path.parts) > 1
                assert not path.is_absolute() and '..' not in path.parts and '\\' not in info.filename
                assert stat.S_ISREG(info.external_attr >> 16)
                relative = PurePosixPath(*path.parts[1:]).as_posix()
                assert relative in payload and not excluded(PurePosixPath(relative))
                assert sha(archive.read(info)) == metadata['file_sha256'][relative]
            archive.extractall(folder)
        exported = folder / 'algorithm-atlas'
        for name, data in payload.items():
            assert (exported / name).read_bytes() == data
        env = dict(os.environ, PYTHONPATH='', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONHASHSEED='0')
        commands = [
            ['scripts/validate_catalog.py'], ['scripts/generate_catalog_docs.py', '--check'],
            ['scripts/verify_reinforcement_learning_scope.py', '--check-only', '--source-only'],
            ['scripts/verify_reinforcement_learning_examples.py', '--check-only'],
            ['-m', 'pytest', 'machine-learning/reinforcement-learning', '-q'],
            ['-m', 'pytest', '--require-cpp', '-q'],
        ]
        for args in commands:
            print('Export check: python ' + ' '.join(args), flush=True)
            before = time.monotonic()
            try:
                result = subprocess.run([sys.executable, *args], cwd=exported, env=env,
                                        capture_output=True, text=True, timeout=1200)
                record = dict(command=['python', *args], returncode=result.returncode, timed_out=False,
                              output=result.stdout + result.stderr, elapsed_seconds=round(time.monotonic() - before, 3))
            except subprocess.TimeoutExpired as error:
                record = dict(command=['python', *args], returncode=None, timed_out=True,
                              output=str(error.stdout or '') + str(error.stderr or ''), elapsed_seconds=round(time.monotonic() - before, 3))
            metadata['extraction_checks'].append(record)
            save()
            if record['returncode'] != 0:
                metadata['extraction_validation_status'] = 'failed'
                save()
                raise AssertionError(record)
            print(record['output'][-400:], flush=True)
        for name, data in payload.items():
            assert (exported / name).read_bytes() == data, 'Export source mutated: ' + name
    assert sha(OUTPUT.read_bytes()) == digest == checksum.read_text().split()[0]
    for name, data in payload.items():
        assert (ROOT / name).read_bytes() == data, 'Working source changed after freeze: ' + name
    metadata.update(extraction_validation_status='passed', zip_crc='passed', safe_unique_regular_paths=True,
                    required_files_present=True, checksum_consistency='passed', source_bytes='identical',
                    credential_scan='no high-confidence matches', json_metadata_consistency='passed')
    save()
    check = json.loads(sidecar.read_text())
    assert check['sha256'] == digest and check['files'] == len(check['file_sha256'])
    assert check['implementation_count'] == 9 and check['blocked_count'] == 1
    print(f'Package verified: {OUTPUT.relative_to(ROOT)}; SHA256 {digest}', flush=True)


if __name__ == '__main__':
    main()
