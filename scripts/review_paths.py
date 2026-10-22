"""Review locations and strict verification of reports relocated during maintenance.

Historical manifests keep the exact paths/hashes of their original snapshots.
For a relocated report, replay only the recorded path edits in reverse, verify
both byte hashes, then let the caller compare its own historical digest.
Algorithm files have no relocation or hash exception.
"""
import hashlib
import json
from pathlib import Path

REPORT_PHASES = {
    "PHASE-0-REPORT.md": "phase-0",
    "SORTING-REVIEW-REPORT.md": "sorting",
    "SORTING-FINAL-AUDIT-REPORT.md": "sorting",
    "SEARCHING-REVIEW-REPORT.md": "searching",
    "RECURSION-BACKTRACKING-REVIEW-REPORT.md": "recursion-backtracking",
    "DIVIDE-CONQUER-REVIEW-REPORT.md": "divide-conquer",
    "DYNAMIC-PROGRAMMING-REVIEW-REPORT.md": "dynamic-programming",
    "GREEDY-REVIEW-REPORT.md": "greedy",
    "GRAPH-ALGORITHMS-REVIEW-REPORT.md": "graph-algorithms",
}
REPORT_LOCATIONS = {name: f"docs/reviews/{phase}/{name}" for name, phase in REPORT_PHASES.items()}
MAINTENANCE_MANIFEST = "docs/maintenance/root-cleanup/manifest.json"


def preserved_bytes(root: Path, original_name: str) -> bytes:
    """Read original bytes, verifying any explicitly recorded report path edits."""
    path = root / original_name
    if path.is_file():
        return path.read_bytes()
    if original_name not in REPORT_LOCATIONS:
        raise FileNotFoundError(path)
    manifest = json.loads((root / MAINTENANCE_MANIFEST).read_text())
    entries = [record for record in manifest['moves'] if record['old'] == original_name]
    assert len(entries) == 1, original_name
    record = entries[0]
    assert record['new'] == REPORT_LOCATIONS[original_name], original_name
    data = (root / record['new']).read_bytes()
    assert hashlib.sha256(data).hexdigest() == record['sha256_after'], original_name
    text = data.decode('utf-8')
    previous_end = 0
    for edit in record['text_edits']:
        start, end = edit['after_start'], edit['after_end']
        assert previous_end <= start <= end <= len(text), original_name
        assert text[start:end] == edit['after'], original_name
        previous_end = end
    for edit in reversed(record['text_edits']):
        text = text[:edit['after_start']] + edit['before'] + text[edit['after_end']:]
    original = text.encode('utf-8')
    assert hashlib.sha256(original).hexdigest() == record['sha256_before'], original_name
    return original


def assert_preserved(root: Path, original_name: str, digest: str) -> None:
    assert hashlib.sha256(preserved_bytes(root, original_name)).hexdigest() == digest, original_name


def report_paths(root: Path) -> list[str]:
    """Discover current reports, retaining checks for all known historical reports."""
    paths = set(REPORT_LOCATIONS.values())
    paths.update(p.relative_to(root).as_posix() for p in (root / 'docs/reviews').rglob('*REPORT*.md'))
    return sorted(paths)
