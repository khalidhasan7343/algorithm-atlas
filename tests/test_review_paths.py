"""Report moves must retain strict historical hashes and safe package locations."""
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath

import pytest

from scripts.review_paths import REPORT_LOCATIONS, assert_preserved, preserved_bytes, report_paths


def sha(value):
    return hashlib.sha256(value).hexdigest()


@pytest.fixture
def relocated_report(tmp_path):
    old = 'GRAPH-ALGORITHMS-REVIEW-REPORT.md'
    new = REPORT_LOCATIONS[old]
    before = 'Evidence: [catalog](catalog.yaml).\nTests: 1548 passed.\n'
    after = 'Evidence: [catalog](../../../catalog.yaml).\nTests: 1548 passed.\n'
    start = before.index('catalog.yaml')
    record = dict(old=old, new=new, sha256_before=sha(before.encode()), sha256_after=sha(after.encode()),
                  text_edits=[dict(after_start=start, after_end=start+len('../../../catalog.yaml'),
                                   before='catalog.yaml', after='../../../catalog.yaml')])
    path = tmp_path/new
    path.parent.mkdir(parents=True)
    path.write_text(after)
    manifest = tmp_path/'docs/maintenance/root-cleanup/manifest.json'
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps(dict(moves=[record])))
    return tmp_path, old, before.encode(), path, manifest


def test_relocated_link_edit_still_verifies_the_original_digest(relocated_report):
    root, old, original, _, _ = relocated_report
    assert preserved_bytes(root, old) == original
    assert_preserved(root, old, sha(original))


def test_report_findings_tamper_is_rejected(relocated_report):
    root, old, original, path, _ = relocated_report
    path.write_text(path.read_text().replace('1548 passed', 'all tests failed'))
    with pytest.raises(AssertionError):
        assert_preserved(root, old, sha(original))


def test_wrong_original_hash_or_edit_coordinates_are_rejected(relocated_report):
    root, old, original, _, manifest = relocated_report
    with pytest.raises(AssertionError):
        assert_preserved(root, old, '0'*64)
    data = json.loads(manifest.read_text())
    data['moves'][0]['text_edits'][0]['after_start'] += 1
    manifest.write_text(json.dumps(data))
    with pytest.raises(AssertionError):
        assert_preserved(root, old, sha(original))


def test_no_relocation_exception_for_algorithm_code(tmp_path):
    path = tmp_path/'dsa/example/python/solution.py'
    path.parent.mkdir(parents=True)
    path.write_bytes(b'return 1\n')
    assert_preserved(tmp_path, str(path.relative_to(tmp_path)), sha(path.read_bytes()))
    path.write_bytes(b'return 2\n')
    with pytest.raises(AssertionError):
        assert_preserved(tmp_path, str(path.relative_to(tmp_path)), sha(b'return 1\n'))
    with pytest.raises(FileNotFoundError):
        preserved_bytes(tmp_path, 'dsa/missing.py')


def test_report_discovery_cannot_silently_omit_a_missing_historical_report(tmp_path):
    new = tmp_path/'docs/reviews/future/FUTURE-REVIEW-REPORT.md'
    new.parent.mkdir(parents=True)
    new.write_text('Future report')
    assert set(REPORT_LOCATIONS.values()) < set(report_paths(tmp_path))
    assert new.relative_to(tmp_path).as_posix() in report_paths(tmp_path)


@pytest.mark.parametrize('script,phase', [
    ('package_backtracking_review','recursion-backtracking'),
    ('package_divide_conquer_review','divide-conquer'),
    ('package_dynamic_programming_review','dynamic-programming'),
    ('package_greedy_review','greedy'),
    ('package_graph_algorithms_review','graph-algorithms'),
])
def test_package_output_and_nested_archive_exclusions(script,phase):
    source=Path(__file__).resolve().parents[1]/'scripts'/f'{script}.py'
    spec=importlib.util.spec_from_file_location(script,source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    assert module.OUTPUT.parent==module.ROOT/'artifacts/review-packages'/phase
    for suffix in ('.zip','.zip.sha256','.zip.verification.json'):
        assert module.excluded(PurePosixPath(f'artifacts/review-packages/{phase}/old{suffix}'))
    assert not module.excluded(PurePosixPath('docs/reviews/graph-algorithms/GRAPH-ALGORITHMS-REVIEW-REPORT.md'))
