"""Freeze the Phase27 repository and independently validate the actual ZIP export."""
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
from verify_uninformed_search_scope import CATEGORY, REPORT, SHARED, TOPICS, verify

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/uninformed-search-evidence'
OUTPUT = ROOT / 'artifacts/review-packages/uninformed-search/algorithm-atlas-uninformed-search-review.zip'
PREFIX = 'algorithm-atlas/'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    sidecar, checksum = OUTPUT.with_suffix('.json'), OUTPUT.with_suffix('.zip.sha256')
    assert not any(p.exists() for p in (OUTPUT, sidecar, checksum)), 'Refusing to overwrite review artifacts'
    preservation = verify(require_tracked=True)
    final = json.loads((EVIDENCE / 'final-results.json').read_text())
    assert {'full-suite', 'c1-targeted', 'c1-policy', 'catalog', 'generated', 'scope', 'examples'} <= final.keys()
    assert all(r['returncode'] == 0 and not r['timed_out'] for r in final.values())
    for batch in range(1, 5):
        record = json.loads(next(EVIDENCE.glob(f'batch{batch}-*-01.json')).read_text())
        assert record['returncode'] == 0
    names = subprocess.check_output(['git', 'ls-files', '-c', '-o', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')
    paths = sorted({PurePosixPath(n) for n in names if n and (ROOT / n).is_file() and not excluded(PurePosixPath(n))})
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
    assert state['phase_number'] == 27 and state['status'] == 'awaiting-review' and state['category'] == 'C1'
    assert state['current_review']['owner_approval'] == state['phase_records']['27']['owner_approval'] == 'pending'
    assert state['phase_records']['26']['owner_approval'] == 'approved'
    assert state['phase_records']['26']['audit_verdict'] == 'CONDITIONAL PASS'
    records = {a['id']: a for a in catalog['algorithms']}
    assert all(is_complete(records[t]) and cpp_required(records[t]) for t in TOPICS)
    assert all(records[s]['category'] == 'A5' and is_complete(records[s]) for s in SHARED)
    dpo = records['dynamic-policy-optimization']
    assert all(dpo[k] == 'blocked' for k in ('documentation_status', 'python_status', 'cpp_status', 'test_status'))
    required = {REPORT, 'README.md', 'AGENTS.md', 'CONTRIBUTING.md', 'LICENSE', 'catalog.yaml', 'requirements-dev.txt',
                'requirements-ml.txt', 'requirements-ml-test.txt', 'pyproject.toml', 'conftest.py', '.gitignore',
                '.github/workflows/ci.yml', 'scripts/validate_catalog.py', 'scripts/generate_catalog_docs.py',
                'scripts/track_policy.py', 'scripts/package_bit_manipulation_review.py', 'scripts/package_tree_algorithms_review.py',
                'scripts/run_uninformed_search_validation.py', 'scripts/verify_uninformed_search_scope.py',
                'scripts/verify_uninformed_search_examples.py', 'scripts/package_uninformed_search_review.py',
                'tests/test_c1_language_and_scope_policy.py', 'docs/uninformed-search-scope.md',
                'docs/uninformed-search-conventions.md', 'docs/uninformed-search-checkpoints.md',
                f'{CATEGORY}/README.md', f'{CATEGORY}/support.py', f'{CATEGORY}/common.hpp', f'{CATEGORY}/conftest.py',
                f'{CATEGORY}/tests/oracles.py', f'{CATEGORY}/tests/encoding.py', f'{CATEGORY}/tests/test_shared_canonicals.py',
                f'{CATEGORY}/examples/shared_bfs_dfs.py', f'{CATEGORY}/examples/compare_uninformed.py',
                'dsa/graph-algorithms/README.md', 'dsa/graph-algorithms/support.py', 'dsa/graph-algorithms/common.hpp',
                'dsa/graph-algorithms/oracles.py', 'dsa/graph-algorithms/conftest.py',
                state['dpo_specification_decision']['report'], state['dpo_specification_decision']['evidence']}
    for topic in TOPICS:
        required.update(f'{CATEGORY}/{topic}/{part}' for part in ('README.md', 'python/solution.py', 'python/example.py',
                                                                  'cpp/solution.cpp', 'tests/test_python.py', 'tests/test_cpp.py'))
    for shared in (*SHARED, 'dijkstra'):
        required.update(f'dsa/graph-algorithms/{shared}/{part}' for part in ('README.md', 'python/solution.py', 'cpp/solution.cpp',
                                                                              'tests/cases.py', 'tests/test_python.py', 'tests/test_cpp.py'))
    for a in catalog['algorithms']:
        required.add(a['canonical_location'] + '/README.md')
        if is_complete(a):
            required.update(a['canonical_location'] + '/' + part for part in ('python/solution.py', 'tests/test_python.py'))
            if cpp_required(a):
                required.update(a['canonical_location'] + '/' + part for part in ('cpp/solution.cpp', 'tests/test_cpp.py'))
    required.update(n for n in payload if n.startswith('docs/reviews/') and n.endswith('.md'))
    for name in ('baseline.json', 'catalog-baseline.yaml', 'phase27-request.md', 'approval-evidence.json',
                 'final-results.json', 'preservation-results.json', 'examples-results.json'):
        required.add('docs/uninformed-search-evidence/' + name)
    assert required <= payload.keys(), sorted(required - payload.keys())
    assert not any(n.startswith(f'{CATEGORY}/{s}/') for n in payload for s in SHARED), 'Duplicate shared canonical'
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in payload.items():
            info = zipfile.ZipInfo(PREFIX + name, date_time=(2026, 11, 14, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            z.writestr(info, data)
    digest = sha(OUTPUT.read_bytes())
    checksum.write_text(f'{digest}  {OUTPUT.name}\n')
    baseline = json.loads((EVIDENCE / 'baseline.json').read_text())
    approval = json.loads((EVIDENCE / 'approval-evidence.json').read_text())
    metadata = dict(
        phase_number=27, phase_name=state['phase'], track='C — Artificial Intelligence', category_id='C1',
        category_name='Uninformed Search', syllabus_entries=6, new_canonical_implementations=list(TOPICS),
        shared_a5_canonical_entries=list(SHARED), duplicate_shared_implementations=0, completed_batches=[1, 2, 3, 4, 5],
        batch_names=state['batch_names'], incomplete_algorithms=[], language_policy='Python and C++ (C++17 and C++20) required for AI',
        owner_approval='pending', phase26_owner_approval='approved', phase26_audit_verdict='CONDITIONAL PASS (preserved)',
        phase26_approved_package_sha256=approval['approved_package_sha256'],
        dpo=dict(id=dpo['id'], canonical_path=dpo['canonical_location'],
                 statuses={k: dpo[k] for k in ('documentation_status', 'python_status', 'cpp_status', 'test_status')},
                 specification_decision='owner-approved: remain blocked', substitution_authorized=False),
        client_date='2026-11-14 Asia/Dhaka', execution_timestamp=datetime.now(ZoneInfo('Asia/Dhaka')).isoformat(),
        starting_revision=baseline['revision'], branch=baseline['branch'], environment=baseline['environment'],
        dependencies_changed=False, report=REPORT, report_tracking_status=preservation['report_tracking'],
        archive=OUTPUT.name, bytes=OUTPUT.stat().st_size, files=len(payload), sha256=digest,
        file_sha256={n: sha(data) for n, data in payload.items()}, required_files=sorted(required),
        local_validation=final, prior_source_preservation=preservation, source_only=True, nested_archives=False,
        hosted_github_actions='not executed or verified', extraction_checks=[], extraction_validation_status='running')

    def save():
        sidecar.write_text(json.dumps(metadata, indent=2) + '\n')
    save()
    with tempfile.TemporaryDirectory(prefix='atlas-c1-export-') as temp:
        folder = Path(temp)
        with zipfile.ZipFile(OUTPUT) as z:
            assert z.testzip() is None
            assert len(z.infolist()) == len(set(z.namelist())) == len(payload)
            for info in z.infolist():
                path = PurePosixPath(info.filename)
                assert path.parts[0] == 'algorithm-atlas' and len(path.parts) > 1 and not path.is_absolute()
                assert '..' not in path.parts and '\\' not in info.filename and stat.S_ISREG(info.external_attr >> 16)
                name = PurePosixPath(*path.parts[1:]).as_posix()
                assert name in payload and not excluded(PurePosixPath(name)) and sha(z.read(info)) == metadata['file_sha256'][name]
            z.extractall(folder)
        exported = folder / 'algorithm-atlas'
        for name, data in payload.items():
            assert (exported / name).read_bytes() == data
        env = dict(os.environ, PYTHONPATH='', PYTHONHASHSEED='0', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
        commands = [['scripts/validate_catalog.py'], ['scripts/generate_catalog_docs.py', '--check'],
                    ['scripts/verify_uninformed_search_scope.py', '--source-only', '--check-only'],
                    ['scripts/verify_uninformed_search_examples.py', '--check-only'],
                    ['-m', 'pytest', '-p', 'no:cacheprovider', '--require-cpp', '-q', CATEGORY,
                     'dsa/graph-algorithms/breadth-first-search', 'dsa/graph-algorithms/depth-first-search',
                     'dsa/graph-algorithms/dijkstra', 'tests/test_c1_language_and_scope_policy.py'],
                    ['-m', 'pytest', '-p', 'no:cacheprovider', '--require-cpp', '-q']]
        for args in commands:
            print('Export check: python ' + ' '.join(args), flush=True)
            before = time.monotonic()
            try:
                r = subprocess.run([sys.executable, *args], cwd=exported, env=env, capture_output=True, text=True, timeout=1500)
                record = dict(command=['python', *args], returncode=r.returncode, timed_out=False, output=r.stdout + r.stderr,
                              elapsed_seconds=round(time.monotonic() - before, 3))
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
            assert (exported / name).read_bytes() == data, 'Export source changed: ' + name
    for name, data in payload.items():
        assert (ROOT / name).read_bytes() == data, 'Working source changed after freeze: ' + name
    assert sha(OUTPUT.read_bytes()) == digest == checksum.read_text().split()[0]
    metadata.update(extraction_validation_status='passed', zip_crc='passed', safe_unique_regular_paths=True,
                    required_files_present=True, checksum_consistency='passed', source_bytes='identical',
                    credential_scan='no high-confidence matches', json_metadata_consistency='passed')
    save()
    check = json.loads(sidecar.read_text())
    assert check['sha256'] == digest and check['files'] == len(check['file_sha256'])
    print(f'Package verified: {OUTPUT.relative_to(ROOT)}; SHA256 {digest}', flush=True)


if __name__ == '__main__':
    main()
