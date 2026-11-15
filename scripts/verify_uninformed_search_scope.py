"""Phase27 identity, approval, ownership and byte-preservation audit against the baseline."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

import yaml

from package_bit_manipulation_review import excluded
from track_policy import cpp_required, is_complete
from validate_catalog import SECTIONS

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/uninformed-search-evidence'
REPORT = 'docs/reviews/uninformed-search/UNINFORMED-SEARCH-REVIEW-REPORT.md'
CATEGORY = 'artificial-intelligence/uninformed-search'
TOPICS = ('depth-limited-search', 'iterative-deepening-dfs', 'uniform-cost-search', 'bidirectional-search')
SHARED = ('breadth-first-search', 'depth-first-search')
STATUS = ('documentation_status', 'python_status', 'cpp_status', 'test_status')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify(source_only=False, require_tracked=False):
    baseline = json.loads((EVIDENCE / 'baseline.json').read_text())
    old = yaml.safe_load((EVIDENCE / 'catalog-baseline.yaml').read_text())
    current = yaml.safe_load((ROOT / 'catalog.yaml').read_text())
    assert current['categories'] == old['categories'], 'Category inventory changed'
    assert [a['id'] for a in current['algorithms']] == [a['id'] for a in old['algorithms']]
    assert len(current['categories']) == 35 and len(current['algorithms']) == 235
    assert sum(len(c['items']) for c in current['categories']) == 256
    c1 = next(c for c in current['categories'] if c['id'] == 'C1')
    assert [i['algorithm'] for i in c1['items']] == [*SHARED, *TOPICS]
    for before, now in zip(old['algorithms'], current['algorithms']):
        if before['id'] in TOPICS:
            assert is_complete(now) and cpp_required(now) and all(now[k] in ('implemented', 'tested') for k in STATUS)
            for key in before.keys() - {'notes', *STATUS}:
                assert before[key] == now[key], (before['id'], key)
        else:
            assert before == now, 'Unapproved canonical record mutation: ' + before['id']
    for shared in SHARED:
        record = next(a for a in current['algorithms'] if a['id'] == shared)
        assert record['category'] == 'A5' and record['canonical_location'] == 'dsa/graph-algorithms/' + shared
        assert not (ROOT / CATEGORY / shared).exists(), 'Duplicate shared canonical folder'
    state, previous = current['development'], old['development']
    assert state['phase_number'] == 27 and state['track'] == 'artificial-intelligence' and state['category'] == 'C1'
    assert state['category_memberships'] == [*SHARED, *TOPICS]
    for key, record in previous['phase_records'].items():
        if key != '26':
            assert state['phase_records'][key] == record, key
    r26, o26 = state['phase_records']['26'], previous['phase_records']['26']
    assert r26['audit_verdict'] == o26['audit_verdict'] == 'CONDITIONAL PASS', 'Phase26 verdict changed'
    assert r26['owner_approval'] == 'approved' and o26['owner_approval'] == 'pending'
    for key in o26.keys() - {'owner_approval', 'status'}:
        assert r26[key] == o26[key], ('phase26', key)
    assert state['phase_records']['27']['owner_approval'] == state['current_review']['owner_approval'] == 'pending'
    assert state['dpo_specification_decision'] == previous['dpo_specification_decision']
    assert state['blocker_reviews'] == previous['blocker_reviews']
    dpo = next(a for a in current['algorithms'] if a['id'] == 'dynamic-policy-optimization')
    assert all(dpo[k] == 'blocked' for k in STATUS) and not (ROOT / dpo['canonical_location'] / 'python').exists()
    approval = json.loads((EVIDENCE / 'approval-evidence.json').read_text())
    assert approval['phase26_audit_verdict'] == 'CONDITIONAL PASS' and approval['phase27_owner_approval'] == 'pending'
    assert approval['approved_package_sha256'] == r26['approved_package_sha256']
    allowed = {'AGENTS.md', 'CONTRIBUTING.md', 'README.md', 'catalog.yaml', 'docs/development.md',
               'docs/ml-development.md', 'docs/getting-started.md', 'docs/learning-roadmap.md',
               'docs/algorithm-index.md', 'docs/progress.md', 'docs/reviews/README.md',
               'artifacts/review-packages/README.md', 'scripts/generate_catalog_docs.py',
               'scripts/validate_catalog.py', 'scripts/track_policy.py'}
    allowed.update(c['path'] + '/README.md' for c in current['categories'])
    allowed.update(f'{CATEGORY}/{t}/README.md' for t in TOPICS)
    protected, changed, omitted = 0, [], []
    for name, expected in baseline['hashes'].items():
        path = ROOT / name
        if source_only and not path.exists() and excluded(PurePosixPath(name)):
            omitted.append(name)
            continue
        assert path.is_file(), 'Missing prior file: ' + name
        if sha(path.read_bytes()) != expected:
            assert name in allowed, 'Unapproved prior-file mutation: ' + name
            changed.append(name)
        else:
            protected += 1
    for name in ('dsa/graph-algorithms/breadth-first-search/python/solution.py', 'dsa/graph-algorithms/depth-first-search/python/solution.py',
                 'dsa/graph-algorithms/dijkstra/python/solution.py', 'dsa/graph-algorithms/support.py'):
        assert sha((ROOT / name).read_bytes()) == baseline['hashes'][name], 'A5 source changed: ' + name
    if (ROOT / '.git').exists() and not source_only:
        names = subprocess.check_output(['git', 'ls-files', '-c', '-o', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')
    else:
        names = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()]
    new_scripts = {f'scripts/{stem}_uninformed_search{tail}.py' for stem, tail in
                   (('run', '_validation'), ('verify', '_scope'), ('verify', '_examples'), ('package', '_review'))}
    added = []
    for name in names:
        if not name or name in baseline['hashes'] or excluded(PurePosixPath(name)):
            continue
        added.append(name)
        if PurePosixPath(name).suffix in {'.py', '.cpp', '.hpp', '.h'}:
            assert name.startswith(CATEGORY + '/') or name in new_scripts or name == 'tests/test_c1_language_and_scope_policy.py', \
                'Out-of-scope new source: ' + name
    for topic in TOPICS:
        folder = ROOT / CATEGORY / topic
        assert re.findall(r'^## (.+)$', (folder / 'README.md').read_text(), re.M) == [f'{i}. {v}' for i, v in enumerate(SECTIONS, 1)]
        for part in ('python/solution.py', 'python/example.py', 'cpp/solution.cpp', 'tests/test_python.py', 'tests/test_cpp.py'):
            assert (folder / part).is_file() and (folder / part).stat().st_size > 0, (topic, part)
    guide = (ROOT / CATEGORY / 'README.md').read_text()
    assert guide.count('<!-- algorithm-atlas:authored-category-guide -->') == 1
    assert [h for h in re.findall(r'^## (\d+)\. ', guide.split('authored-category-guide')[1], re.M)] == [str(i) for i in range(1, 26)]
    tracking = 'source export; Git index omitted'
    if (ROOT / '.git').exists() and not source_only:
        assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == baseline['revision']
        staged = subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=ROOT, text=True).splitlines()
        assert set(staged) <= {REPORT}, 'Unexpected staged paths: ' + ', '.join(staged)
        tracked = subprocess.run(['git', 'ls-files', '--error-unmatch', REPORT], cwd=ROOT, capture_output=True).returncode == 0
        unignored = subprocess.run(['git', 'check-ignore', '-q', REPORT], cwd=ROOT).returncode == 1
        tracking = 'tracked and unignored' if tracked and unignored else 'awaiting report tracking'
        if require_tracked:
            assert tracked and unignored, tracking
    assert (ROOT / REPORT).is_file() and (ROOT / REPORT).stat().st_size > 0
    return dict(status='passed', counts=baseline['counts'], new_canonicals=list(TOPICS), shared_a5=list(SHARED),
                duplicate_shared_folders=0, phase26='owner-approved; CONDITIONAL PASS verdict unchanged',
                phase27_owner_approval='pending', dpo='canonical ID/path/four blocked statuses/decision unchanged',
                protected_preexisting_files=protected, changed_preexisting_files=sorted(changed),
                added_files=sorted(added), historical_artifacts_omitted_from_export=omitted, report_tracking=tracking,
                a5_bfs_dfs_dijkstra_sources='byte-identical', runtime_dependencies='Python/C++ standard libraries only; no new packages')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-only', action='store_true')
    parser.add_argument('--require-tracked', action='store_true')
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    result = verify(args.source_only, args.require_tracked)
    if not args.check_only:
        (EVIDENCE / 'preservation-results.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f"Phase27 scope passed: 4 new canonicals, 2 shared A5 entries; {result['protected_preexisting_files']} "
          f"protected prior files; {len(result['changed_preexisting_files'])} allowed changes; {result['report_tracking']}")


if __name__ == '__main__':
    main()
