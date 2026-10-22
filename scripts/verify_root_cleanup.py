"""Verify the root-cleanup snapshot without changing historical phase evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

import yaml

try:
    from .review_paths import assert_preserved
except ImportError:  # Direct execution from scripts/.
    from review_paths import assert_preserved

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'docs/maintenance/root-cleanup/manifest.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify(root, *, tracked_only=False, check_git=False):
    manifest = json.loads((root / MANIFEST).read_text())
    for group in ('algorithm_files_sha256', 'unchanged_root_files_sha256', 'historical_evidence_sha256'):
        for name, expected in manifest[group].items():
            assert digest((root / name).read_bytes()) == expected, name
    catalog = yaml.safe_load((root / 'catalog.yaml').read_text())
    assert digest(json.dumps(catalog['categories'], sort_keys=True).encode()) == manifest['catalog_categories_sha256']
    assert digest(json.dumps(catalog['algorithms'], sort_keys=True).encode()) == manifest['catalog_algorithms_sha256']
    expected_development = dict(manifest['development_before'])
    moves = {record['old']: record['new'] for record in manifest['moves']}
    expected_development['completion_report'] = moves[expected_development['completion_report']]
    assert catalog['development'] == expected_development, 'Phase status or approval changed'
    for name in manifest['essential_root_files']:
        assert (root / name).is_file() and (root / name).stat().st_size, name
    for name in ('.github', 'dsa', 'machine-learning', 'artificial-intelligence', 'docs', 'scripts', 'tests'):
        assert (root / name).is_dir(), name
    reports, packages, local_omissions = [], [], []
    for record in manifest['moves']:
        old, new = root / record['old'], root / record['new']
        assert not old.exists(), f'Old root path remains: {record["old"]}'
        if tracked_only and not record['tracked_before'] and not new.exists():
            local_omissions.append(record['new'])
            continue
        assert new.is_file() and new.stat().st_size, record['new']
        assert digest(new.read_bytes()) == record['sha256_after'], record['new']
        if new.suffix == '.md':
            assert_preserved(root, record['old'], record['sha256_before'])
            reports.append(record['new'])
        else:
            assert record['sha256_before'] == record['sha256_after'], record['new']
        if new.suffix == '.zip':
            checksum = new.with_suffix('.zip.sha256').read_text().split()
            assert len(checksum) == 2 and checksum[1] == new.name, new
            assert checksum[0] == digest(new.read_bytes()), new
            metadata = json.loads(new.with_suffix('.zip.verification.json').read_text())
            assert metadata['sha256'] == checksum[0] and metadata['bytes'] == new.stat().st_size
            assert metadata['archive'] == new.name
            with zipfile.ZipFile(new) as archive:
                assert archive.testzip() is None, new
            packages.append(dict(path=record['new'], sha256=checksum[0], crc='passed'))
    assert len(catalog['categories']) == 35 and len(catalog['algorithms']) == 235
    assert sum(len(c['items']) for c in catalog['categories']) == 256
    if check_git:
        tracked = set(subprocess.run(['git', 'ls-files', '-z'], cwd=root, capture_output=True,
                                     text=True, check=True, timeout=30).stdout.split('\0'))
        for record in manifest['moves']:
            assert record['old'] not in tracked, record['old']
            assert (record['new'] in tracked) == record['tracked_before'], record['new']
        for name in reports:
            ignored = subprocess.run(['git', 'check-ignore', '--no-index', '--', name], cwd=root,
                                     capture_output=True, text=True, timeout=10)
            assert ignored.returncode == 1 and not ignored.stdout, name
    return dict(reports_moved=len(reports), packages_verified=packages,
                package_files_moved=len(manifest['moves'])-len(reports),
                algorithm_files_byte_identical=len(manifest['algorithm_files_sha256']),
                historical_evidence_files_byte_identical=len(manifest['historical_evidence_sha256']),
                inventory=dict(categories=35, memberships=256, canonical_topics=235),
                development_status=catalog['development']['status'],
                completion_report=catalog['development']['completion_report'],
                tracked_only=tracked_only, local_untracked_files_absent=local_omissions,
                git_tracking_checked=check_git, hosted_github_actions='not triggered or verified')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tracked-only', action='store_true', help='Allow explicitly recorded local untracked package files to be absent.')
    parser.add_argument('--git', action='store_true', help='Require relocated tracking/ignore status to match the pre-cleanup index.')
    parser.add_argument('--output', type=Path, help='Write new maintenance evidence, never old phase evidence.')
    args = parser.parse_args()
    result = verify(ROOT, tracked_only=args.tracked_only, check_git=args.git)
    text = json.dumps(result, indent=2)+'\n'
    if args.output:
        args.output.write_text(text)
    print(text, end='')


if __name__ == '__main__':
    main()
