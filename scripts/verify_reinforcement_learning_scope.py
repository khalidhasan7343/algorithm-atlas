"""Verify Phase20 identities, nine implementations, DPO and byte preservation."""
import argparse
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

import yaml
from package_bit_manipulation_review import excluded
from track_policy import is_complete
from validate_catalog import SECTIONS

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/reinforcement-learning-evidence'
REPORT = 'docs/reviews/reinforcement-learning/REINFORCEMENT-LEARNING-REVIEW-REPORT.md'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify(source_only=False, require_tracked=False):
    baseline = json.loads((EVIDENCE / 'baseline.json').read_text())
    old = yaml.safe_load((EVIDENCE / 'catalog-baseline.yaml').read_text())
    current = yaml.safe_load((ROOT / 'catalog.yaml').read_text())
    assert current['categories'] == old['categories']
    assert [a['id'] for a in current['algorithms']] == [a['id'] for a in old['algorithms']]
    topics = {a['id'] for a in old['algorithms'] if a['category'] == 'B8'}
    assert len(topics) == 10
    for before, now in zip(old['algorithms'], current['algorithms']):
        if before['category'] != 'B8' or before['id'] == 'dynamic-policy-optimization':
            assert before == now, before['id']
        else:
            for key in before.keys() - {'notes', 'documentation_status', 'python_status', 'test_status'}:
                assert before[key] == now[key], (before['id'], key)
            assert is_complete(now) and now['cpp_status'] == 'planned'
    state = current['development']
    assert state['phase_number'] == 20 and state['category'] == 'B8'
    assert state['status'] == 'awaiting-review' and state['completed_batches'] == list(range(1, 6)) and state['active_batch'] is None
    assert state['phase_records']['19']['owner_approval'] == 'approved'
    assert state['current_review']['owner_approval'] == state['phase_records']['20']['owner_approval'] == 'pending'
    assert state['blocker_reviews'] == {'dynamic-policy-optimization': 'verified-blocked'}
    assert state['completion_report'] == REPORT
    decision = state['dpo_specification_decision']
    assert decision['owner_approval'] == 'approved' and decision['outcome'] == 3
    assert decision['decision'] == 'remain-blocked' and decision['substitution_authorized'] is False
    assert decision['canonical_id'] == 'dynamic-policy-optimization'
    assert decision['canonical_path'] == 'machine-learning/reinforcement-learning/dynamic-policy-optimization'
    assert state['phase_records']['20']['full_catalog_completion'] is False
    approval = json.loads((ROOT / decision['evidence']).read_text())
    assert approval['dpo_specification_owner_approval'] == 'approved'
    assert approval['phase20_implementation_owner_approval'] == 'pending'
    research_text = (ROOT / decision['report']).read_text()
    research_body = research_text[research_text.index('## Evidence and confidence'):research_text.index('## Decision for the owner')]
    assert sha(research_body.encode()) == approval['research_body_sha256_before'] == approval['research_body_sha256_after']
    allowed = {'AGENTS.md', 'CONTRIBUTING.md', 'README.md', 'catalog.yaml',
               'docs/development.md', 'docs/ml-development.md', 'docs/algorithm-index.md',
               'docs/progress.md', 'docs/learning-roadmap.md', 'docs/reviews/README.md',
               'artifacts/review-packages/README.md', 'scripts/generate_catalog_docs.py',
               'scripts/validate_catalog.py'}
    allowed.update(c['path'] + '/README.md' for c in current['categories'])
    allowed.update(a['canonical_location'] + '/README.md' for a in current['algorithms']
                   if a['id'] in topics and a['id'] != 'dynamic-policy-optimization')
    protected, omitted = 0, []
    changed = []
    for name, expected in baseline['hashes'].items():
        path = ROOT / name
        if source_only and not path.exists() and name.startswith('artifacts/review-packages/') and excluded(PurePosixPath(name)):
            omitted.append(name)
            continue
        assert path.is_file(), name
        digest = sha(path.read_bytes())
        if digest != expected:
            assert name in allowed, 'Unapproved prior-file mutation: ' + name
            changed.append(name)
        elif name not in allowed:
            protected += 1
    forbidden = {'torch', 'tensorflow', 'gymnasium', 'stable_baselines3', 'ray', 'sklearn',
                 'requests', 'urllib', 'pickle', 'subprocess'}
    lessons = []
    core = [ROOT / 'machine-learning/reinforcement-learning/support.py']
    for a in current['algorithms']:
        if a['id'] not in topics:
            continue
        folder = ROOT / a['canonical_location']
        if a['id'] == 'dynamic-policy-optimization':
            assert all(a[f] == 'blocked' for f in ('documentation_status', 'python_status', 'cpp_status', 'test_status'))
            assert not (folder / 'python').exists() and not (folder / 'tests').exists()
            continue
        assert re.findall(r'^##[ \t]+(.+)$', (folder / 'README.md').read_text(), re.M) == [f'{i}. {title}' for i, title in enumerate(SECTIONS, 1)]
        for part in ('python/solution.py', 'python/example.py', 'tests/test_python.py'):
            assert (folder / part).is_file() and (folder / part).stat().st_size > 0
        assert not (folder / 'cpp/solution.cpp').exists() and not (folder / 'tests/test_cpp.py').exists()
        core.append(folder / 'python/solution.py')
        lessons.append(a['id'])
    for path in core:
        for node in ast.walk(ast.parse(path.read_text())):
            names = [n.name for n in node.names] if isinstance(node, ast.Import) else [node.module or ''] if isinstance(node, ast.ImportFrom) else []
            assert not any(n.split('.')[0] in forbidden for n in names), path
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in {'eval', 'exec', 'compile'}, path
    tracking = 'source export; Git index deliberately omitted'
    if (ROOT / '.git').exists() and not source_only:
        assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == baseline['revision']
        staged = subprocess.check_output(['git', 'diff', '--cached', '--binary', '--', '.', ':(exclude)' + REPORT], cwd=ROOT)
        assert sha(staged) == baseline['staged_diff_sha256'], 'Pre-existing staged contents changed'
        staged_paths = subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=ROOT, text=True).splitlines()
        assert set(staged_paths) <= set(baseline['staged_paths']) | {REPORT}
        tracked = subprocess.run(['git', 'ls-files', '--error-unmatch', REPORT], cwd=ROOT, capture_output=True).returncode == 0
        unignored = subprocess.run(['git', 'check-ignore', '-q', REPORT], cwd=ROOT).returncode == 1
        tracking = 'tracked and unignored' if tracked and unignored else 'awaiting final report tracking'
        if require_tracked:
            assert tracked and unignored, tracking
    report = ROOT / REPORT
    assert report.is_file() and report.stat().st_size > 0
    # Re-finalization may update approval/progress evidence, never algorithm bytes.
    finalization = json.loads((EVIDENCE / 'outcome3-finalization-baseline.json').read_text())
    finalization_catalog = yaml.safe_load((EVIDENCE / 'outcome3-catalog-baseline.yaml').read_text())
    assert current['algorithms'] == finalization_catalog['algorithms']
    assert current['categories'] == finalization_catalog['categories']
    moves = json.loads((EVIDENCE / 'outcome3-history-moves.json').read_text())['moves']
    relocated = {move['old']: move['new'] for move in moves}
    finalization_allowed = (allowed - {a['canonical_location'] + '/README.md'
                                      for a in current['algorithms'] if a['category'] == 'B8'}) | {
        REPORT, decision['report'], 'docs/reinforcement-learning-checkpoints.md',
        'docs/reinforcement-learning-scope.md', 'docs/reinforcement-learning-conventions.md',
        'artifacts/review-packages/reinforcement-learning/README.md',
        'scripts/package_reinforcement_learning_review.py',
        'scripts/verify_reinforcement_learning_scope.py',
    }
    finalization_allowed.update('docs/reinforcement-learning-evidence/' + name for name in (
        'final-results.json', 'configuration-results.json', 'test-matrix.json',
        'preservation-results.json', 'changed-files.json', 'negative-validation-matrix.json'))
    finalization_protected = 0
    for name, expected in finalization['hashes'].items():
        location = relocated.get(name, name)
        path = ROOT / location
        if source_only and not path.exists() and excluded(PurePosixPath(location)):
            continue
        assert path.is_file(), location
        if name in relocated or name not in finalization_allowed:
            assert sha(path.read_bytes()) == expected, 'Unapproved finalization mutation: ' + name
            finalization_protected += 1
    if (ROOT / '.git').exists() and not source_only:
        assert sha(subprocess.check_output(['git', 'diff', '--cached', '--binary'], cwd=ROOT)) == finalization['staged_sha256']
    return dict(status='passed', counts=baseline['counts'], implemented=9, blocked=['dynamic-policy-optimization'],
                phase19_owner_approval='approved', phase20_owner_approval='pending', report_tracking=tracking,
                dpo_specification_owner_approval='approved: remain blocked', full_catalog_complete=False,
                finalization_protected_files=finalization_protected,
                prior_phase20_package='relocated byte-for-byte; original internal snapshot metadata unchanged',
                decision_research_body='byte-identical',
                protected_preexisting_files=protected, historical_artifacts_omitted_from_export=omitted,
                changed_preexisting_files=sorted(changed), exact25_section_lessons=sorted(lessons),
                approved_B1_B7_DSA_sources_tests_lessons_and_historical_artifacts='byte-identical',
                runtime_dependency_audit='NumPy/stdlib/local source only; no downloads/framework/pickle/eval/exec')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-only', action='store_true')
    parser.add_argument('--require-tracked', action='store_true')
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    result = verify(args.source_only, args.require_tracked)
    if not args.check_only:
        (EVIDENCE / 'preservation-results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f"Phase20 scope passed:9 implemented+1 blocked; {result['protected_preexisting_files']} protected prior files; {result['report_tracking']}")


if __name__ == '__main__':
    main()
