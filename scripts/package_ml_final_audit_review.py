"""Freeze the Phase26 repository and independently validate the final ML audit ZIP export."""
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

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/ml-final-audit-evidence'
REPORT = 'docs/reviews/machine-learning/ML-FINAL-COMPREHENSIVE-AUDIT-REPORT.md'
OUTPUT = ROOT / 'artifacts/review-packages/machine-learning/algorithm-atlas-ml-final-audit-review.zip'
PREFIX = 'algorithm-atlas/'
B_CATEGORIES = [f'B{i}' for i in range(1, 14)]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def latest(label):
    candidates = sorted(EVIDENCE.glob(label + '-[0-9][0-9].json'))
    assert candidates, 'missing evidence for ' + label
    return json.loads(candidates[-1].read_text())


def main():
    sidecar = OUTPUT.with_suffix('.json')
    checksum = OUTPUT.with_suffix('.zip.sha256')
    assert not any(p.exists() for p in (OUTPUT, sidecar, checksum)), 'Refusing to overwrite review artifacts'
    oracles = json.loads((EVIDENCE / 'oracle-results.json').read_text())
    assert oracles['all_passed'] and oracles['total_checks'] == oracles['passed_checks'] >= 200
    final = {label: latest(label) for label in ('final-validate-catalog', 'final-docs-check', 'final-full-suite')}
    assert all(r['returncode'] == 0 and not r['timed_out'] for r in final.values()), final
    suite_output = (ROOT / final['final-full-suite']['output']).read_text()
    summary = re.search(r'(\d+) passed in ([\d.]+)s', suite_output)
    assert summary and 'failed' not in suite_output.splitlines()[-1] and 'skipped' not in suite_output.splitlines()[-1]
    audit = json.loads((EVIDENCE / 'phase26-audit-evidence.json').read_text())
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
    assert state['phase_number'] == 26 and state['mode'] == 'final-ml-audit' and state['status'] == 'awaiting-review'
    assert state['completed_batches'] == list(range(1, 8)) and state['active_batch'] is None
    assert state['current_review']['owner_approval'] == state['phase_records']['26']['owner_approval'] == 'pending'
    assert all(state['phase_records'][str(p)]['owner_approval'] == 'approved' for p in range(13, 26))
    algorithms = {a['id']: a for a in catalog['algorithms']}
    b_track = [a for a in algorithms.values() if a['category'] in B_CATEGORIES]
    dpo = algorithms['dynamic-policy-optimization']
    assert all(dpo[k] == 'blocked' for k in ('documentation_status', 'python_status', 'cpp_status', 'test_status'))
    assert dpo['canonical_location'] == 'machine-learning/reinforcement-learning/dynamic-policy-optimization'
    implemented = [a for a in b_track if a['id'] != 'dynamic-policy-optimization']
    assert len(b_track) == 100 and len(implemented) == 99 and all(is_complete(a) for a in implemented)
    assert state['dpo_specification_decision']['decision'] == 'remain-blocked' and state['dpo_specification_decision']['owner_approval'] == 'approved'
    required = {REPORT, 'README.md', 'AGENTS.md', 'CONTRIBUTING.md', 'LICENSE', 'catalog.yaml',
                'requirements-dev.txt', 'requirements-ml.txt', 'requirements-ml-test.txt', 'pyproject.toml', 'conftest.py',
                '.github/workflows/ci.yml', 'scripts/validate_catalog.py', 'scripts/generate_catalog_docs.py',
                'scripts/track_policy.py', 'scripts/review_paths.py', 'scripts/package_bit_manipulation_review.py', 'scripts/package_tree_algorithms_review.py',
                'scripts/run_ml_final_audit_validation.py', 'scripts/run_ml_final_audit_oracles.py', 'scripts/package_ml_final_audit_review.py',
                'scripts/ml_final_audit_oracles/README.md', 'docs/ml-final-audit-scope.md', 'docs/ml-final-audit-checkpoints.md',
                'docs/development.md', 'docs/ml-development.md', 'docs/progress.md', 'docs/learning-roadmap.md', 'docs/algorithm-index.md',
                'docs/ml-final-audit-evidence/phase26-audit-evidence.json', 'docs/ml-final-audit-evidence/oracle-results.json',
                'docs/ml-final-audit-evidence/approval-evidence.json', 'docs/ml-final-audit-evidence/baseline.json',
                state['dpo_specification_decision']['report'], state['dpo_specification_decision']['evidence'],
                dpo['canonical_location'] + '/README.md', 'machine-learning/README.md'}
    required.update(f'scripts/ml_final_audit_oracles/oracle_b{i}.py' for i in range(1, 14))
    required.update(f'docs/ml-final-audit-evidence/{label}-01.json' for label in final)
    required.update(n for n in payload if n.startswith('docs/reviews/') and n.endswith('.md'))
    required.update(n for n in payload if n.startswith('machine-learning/') and (n.endswith('support.py') or n.endswith('conftest.py') or '/tests/' in n and n.endswith('.py')))
    required.update(c['path'] + '/README.md' for c in catalog['categories'])
    for a in catalog['algorithms']:
        required.add(a['canonical_location'] + '/README.md')
        if is_complete(a):
            required.update(a['canonical_location'] + '/' + part for part in ('python/solution.py', 'tests/test_python.py'))
            if cpp_required(a):
                required.update(a['canonical_location'] + '/' + part for part in ('cpp/solution.cpp', 'tests/test_cpp.py'))
    assert required <= payload.keys(), sorted(required - payload.keys())
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
    approval = json.loads((EVIDENCE / 'approval-evidence.json').read_text())
    inventory = audit['b_track_inventory']
    metadata = dict(
        phase_number=26, phase_name=state['phase'], track='machine-learning', mode='final-ml-audit', categories=B_CATEGORIES,
        catalog_counts=audit['catalog_counts'],
        b_track=dict(memberships=inventory['memberships'], distinct_canonicals=inventory['distinct_canonicals'], implemented=inventory['implemented'],
                     blocked=inventory['blocked'], missing_implementations=inventory['missing_implementations'],
                     per_category=[dict(category=r['cat'], entries=r['entries'], owned=r['owned'], implemented=r['implemented'], blocked=r['blocked'], shared_in=r['shared_in']) for r in inventory['categories']]),
        audit_verdict='CONDITIONAL PASS', owner_approval='pending', phase25_owner_approval='approved',
        phase25_approved_package_sha256=approval['approved_package_sha256'],
        category_owner_approvals={str(p): state['phase_records'][str(p)]['owner_approval'] for p in range(13, 26)},
        dpo=dict(id=dpo['id'], canonical_path=dpo['canonical_location'],
                 statuses={k: dpo[k] for k in ('documentation_status', 'python_status', 'cpp_status', 'test_status')},
                 specification_decision='owner-approved: remain blocked', substitution_authorized=False),
        independent_oracles=dict(total_checks=oracles['total_checks'], passed_checks=oracles['passed_checks'],
                                 per_script={k: dict(passed=v['passed'], total=v['total']) for k, v in oracles['scripts'].items()}),
        final_validation=final, full_suite_summary=summary.group(0),
        client_date='2026-11-14 Asia/Dhaka', execution_timestamp=datetime.now(ZoneInfo('Asia/Dhaka')).isoformat(),
        starting_revision=audit['repository_baseline']['head'], branch=audit['repository_baseline']['branch'],
        environment=audit['environment'], dependencies_changed=False,
        report=REPORT, report_tracking_status='tracked and unignored', archive=OUTPUT.name, bytes=OUTPUT.stat().st_size,
        files=len(payload), sha256=digest, file_sha256={n: sha(data) for n, data in payload.items()}, required_files=sorted(required),
        source_only=True, nested_archives=False, hosted_github_actions='not executed or verified',
        extraction_checks=[], extraction_validation_status='running')

    def save():
        sidecar.write_text(json.dumps(metadata, indent=2) + '\n')
    save()
    with tempfile.TemporaryDirectory(prefix='atlas-ml-final-export-') as temp:
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
        env = dict(os.environ, PYTHONPATH='', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONHASHSEED='0')
        commands = [['scripts/validate_catalog.py'], ['scripts/generate_catalog_docs.py', '--check'],
                    ['scripts/run_ml_final_audit_oracles.py'],
                    ['-m', 'pytest', 'machine-learning', '-q', '-p', 'no:cacheprovider'],
                    ['-m', 'pytest', '--require-cpp', '-q', '-p', 'no:cacheprovider']]
        for args in commands:
            print('Export check: python ' + ' '.join(args), flush=True)
            before = time.monotonic()
            try:
                r = subprocess.run([sys.executable, *args], cwd=exported, env=env, capture_output=True, text=True, timeout=1200)
                record = dict(command=['python', *args], returncode=r.returncode, timed_out=False, output=(r.stdout + r.stderr)[-6000:], elapsed_seconds=round(time.monotonic() - before, 3))
            except subprocess.TimeoutExpired as error:
                record = dict(command=['python', *args], returncode=None, timed_out=True, output=(str(error.stdout or '') + str(error.stderr or ''))[-6000:], elapsed_seconds=round(time.monotonic() - before, 3))
            metadata['extraction_checks'].append(record)
            save()
            if record['returncode'] != 0:
                metadata['extraction_validation_status'] = 'failed'
                save()
                raise AssertionError(record)
            print(record['output'][-400:], flush=True)
        # The oracle runner rewrites its evidence file inside the export; every other exported byte must be unchanged.
        for name, data in payload.items():
            if name != 'docs/ml-final-audit-evidence/oracle-results.json':
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
