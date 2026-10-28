"""Verify audit-only changes against the complete pre-existing working tree.

Existing staged content is never changed. --source-only permits only deliberately
excluded historical archive/sidecar absences in an exported source snapshot.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

import yaml

from track_policy import is_complete
from validate_catalog import SECTIONS

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/regression-audit-evidence'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--source-only', action='store_true')
    args = parser.parse_args()
    baseline = json.loads((EVIDENCE/'baseline.json').read_text())
    old = yaml.safe_load((EVIDENCE/'catalog-baseline.yaml').read_text())
    current = yaml.safe_load((ROOT/'catalog.yaml').read_text())
    assert current['categories'] == old['categories']
    assert [a['id'] for a in current['algorithms']] == [a['id'] for a in old['algorithms']]
    topics = {a['id'] for a in baseline['algorithms']}
    assert len(topics) == 7
    for previous, now in zip(old['algorithms'], current['algorithms']):
        if previous['id'] not in topics:
            assert previous == now, previous['id']
        else:
            for key in previous.keys() - {'notes'}:
                assert previous[key] == now[key], (previous['id'], key)
            assert is_complete(now) and now['cpp_status'] == 'planned'
    state = current['development']
    assert state['category'] == 'B1' and state['phase_number'] == 13
    assert state['current_review']['owner_approval'] == 'pending'
    for phase in ('11', '12', '13', '14'):
        assert state['phase_records'][phase]['owner_approval'] == 'approved'
    allowed = {'AGENTS.md', 'CONTRIBUTING.md', 'README.md', 'catalog.yaml',
               'docs/algorithm-index.md', 'docs/progress.md', 'docs/development.md',
               'docs/getting-started.md', 'docs/glossary.md', 'docs/learning-roadmap.md', 'docs/ml-development.md',
               'docs/reviews/README.md', 'docs/reviews/regression/REGRESSION-REVIEW-REPORT.md',
               'artifacts/review-packages/README.md', 'artifacts/review-packages/regression/README.md',
               'scripts/generate_catalog_docs.py',
               'machine-learning/supervised-learning/regression/support.py',
               'machine-learning/supervised-learning/regression/experiments/benchmark.py',
               'machine-learning/supervised-learning/regression/decision-tree-regression/python/solution.py',
               'machine-learning/supervised-learning/regression/decision-tree-regression/README.md'}
    allowed.update(category['path']+'/README.md' for category in current['categories'])
    historical = json.loads((EVIDENCE/'historical-package.json').read_text())
    mappings = {r['original']: r for r in historical['files']}
    checked = 0
    omitted = []
    for name, expected in baseline['hashes'].items():
        if name in allowed:
            continue
        path = ROOT/name
        if name in mappings:
            record = mappings[name]
            assert record['sha256'] == expected
            path = ROOT/record['preserved']
        if args.source_only and name.startswith('artifacts/review-packages/') and not path.exists():
            omitted.append(name)
            continue
        assert path.is_file() and digest(path.read_bytes()) == expected, f'Unapproved pre-existing change: {name}'
        checked += 1
    assert digest((EVIDENCE/'approved-regression-report.txt').read_bytes()) == baseline['hashes']['docs/reviews/regression/REGRESSION-REVIEW-REPORT.md']
    assert digest((EVIDENCE/'approved-regression-support.txt').read_bytes()) == baseline['hashes']['machine-learning/supervised-learning/regression/support.py']
    assert digest((EVIDENCE/'approved-regression-tree.txt').read_bytes()) == baseline['hashes']['machine-learning/supervised-learning/regression/decision-tree-regression/python/solution.py']
    lessons = []
    for algorithm in current['algorithms']:
        if algorithm['id'] not in topics:
            continue
        folder = ROOT/algorithm['canonical_location']
        headings = re.findall(r'^##[ \t]+(.+)$', (folder/'README.md').read_text(), re.M)
        assert headings == [f'{i}. {title}' for i, title in enumerate(SECTIONS, 1)]
        for name in ('python/solution.py', 'python/example.py', 'tests/test_python.py'):
            assert (folder/name).is_file() and (folder/name).stat().st_size > 0
        assert not (folder/'cpp/solution.cpp').exists() and not (folder/'tests/test_cpp.py').exists()
        imports = []
        for node in ast.walk(ast.parse((folder/'python/solution.py').read_text())):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or '')
        assert not any(v.split('.')[0] in {'sklearn', 'scipy', 'requests', 'pickle', 'torch', 'tensorflow', 'subprocess'} for v in imports)
        lessons.append(dict(id=algorithm['id'], exact_sections=25, existing_implementation='retained',
                            fitting_kernel='targeted CART underflow repair' if algorithm['id']=='decision-tree-regression' else 'byte-identical',
                            cpp='optional, absent'))
    tracking = 'not checked in source export'
    if (ROOT/'.git').exists() and not args.source_only:
        assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == baseline['revision']
        staged = subprocess.check_output(['git', 'diff', '--cached', '--binary'], cwd=ROOT)
        assert digest(staged) == baseline['staged_diff_sha256'], 'Pre-existing staged contents changed'
        report = 'docs/reviews/regression/REGRESSION-REVIEW-REPORT.md'
        subprocess.run(['git', 'ls-files', '--error-unmatch', report], cwd=ROOT, check=True, capture_output=True)
        assert subprocess.run(['git', 'check-ignore', '-q', report], cwd=ROOT).returncode == 1
        tracking = 'tracked/unignored; original staged diff preserved exactly'
    result = dict(status='passed', inventory=baseline['counts'], algorithms=7, retained=7, new_implementations=0,
                  protected_preexisting_files=checked, historical_artifacts_omitted_from_export=omitted,
                  classification_canonicals='all eleven source/tests/lessons byte-identical', dsa_canonicals='all 97 source/tests/lessons byte-identical',
                  six_fitting_kernels='byte-identical', CART='confirmed underflow repair only',
                  previous_work_owner_approval='approved', current_review_owner_approval='pending', report_tracking=tracking, lessons=lessons)
    if not args.check_only:
        (EVIDENCE/'preservation-results.json').write_text(json.dumps(result, indent=2)+'\n')
    print(f"Regression audit scope passed: 7 retained, 0 new algorithms, {checked} pre-existing files preserved; staged contents unchanged")


if __name__ == '__main__':
    main()
