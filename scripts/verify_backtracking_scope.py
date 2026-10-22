"""Verify Phase 3 catalog identity and byte preservation against its checkpoint."""

import hashlib
import json
from pathlib import Path
import subprocess

import yaml

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/recursion-backtracking-evidence"
EXPECTED = {
    "permutations", "combinations", "power-set-generation", "n-queens",
    "sudoku-solver", "rat-in-a-maze", "graph-coloring", "hamiltonian-path",
    "subset-sum-backtracking",
}
MUTABLE_FIELDS = {
    "documentation_status", "python_status", "cpp_status", "test_status", "notes",
}


def main() -> None:
    baseline = json.loads((EVIDENCE / "approved-baseline.json").read_text())
    changed = [
        name for name, digest in baseline["files_sha256"].items()
        if not (ROOT / name).is_file()
        or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest
    ]
    assert not changed, f"Approved files changed: {changed}"
    original = subprocess.run(
        ["git", "show", baseline["baseline_HEAD"] + ":catalog.yaml"],
        cwd=ROOT, check=True, capture_output=True, text=True, timeout=30,
    )
    before = yaml.safe_load(original.stdout)
    after = yaml.safe_load((ROOT / "catalog.yaml").read_text())
    assert before["categories"] == after["categories"], "Syllabus changed"
    previous = {a["id"]: a for a in before["algorithms"]}
    current = {a["id"]: a for a in after["algorithms"]}
    assert previous.keys() == current.keys(), "Canonical IDs changed"
    assert {a["id"] for a in after["algorithms"] if a["category"] == "A3"} == EXPECTED
    for name, record in current.items():
        if name in EXPECTED:
            assert {k: v for k, v in record.items() if k not in MUTABLE_FIELDS} == {
                k: v for k, v in previous[name].items() if k not in MUTABLE_FIELDS
            }, name
        else:
            assert record == previous[name], f"Out-of-scope catalog record changed: {name}"
    result = {
        "baseline_HEAD": baseline["baseline_HEAD"],
        "approved_files_checked": len(baseline["files_sha256"]),
        "approved_files_unchanged": True,
        "syllabus_categories_unchanged": True,
        "canonical_ids_names_paths_metadata_preserved": True,
        "out_of_scope_catalog_records_unchanged": True,
        "phase3_catalog_ids": sorted(EXPECTED),
    }
    (EVIDENCE / "preservation-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
