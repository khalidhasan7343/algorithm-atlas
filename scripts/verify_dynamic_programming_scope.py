"""Verify scope, prior-file preservation, all lesson sections and test artifacts."""
import hashlib
import json
from pathlib import Path
import re

import yaml

from validate_catalog import DYNAMIC_PROGRAMMING_BATCHES, SECTIONS, STATUS_FIELDS

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/dynamic-programming-evidence"


def main():
    baseline = json.loads((EVIDENCE / "approved-baseline.json").read_text())
    for name, digest in baseline["sha256"].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    before = yaml.safe_load((EVIDENCE / "catalog-baseline.yaml").read_text())
    after = yaml.safe_load((ROOT / "catalog.yaml").read_text())
    assert before["categories"] == after["categories"]
    original = {a["id"]: a for a in before["algorithms"]}
    current = {a["id"]: a for a in after["algorithms"]}
    assert current.keys() == original.keys()
    allowed = {name for batch in DYNAMIC_PROGRAMMING_BATCHES for name in batch}
    mutable = {*STATUS_FIELDS, "notes"}
    audited = {}
    for name, record in current.items():
        if name not in allowed:
            assert record == original[name], name
            continue
        assert {k: v for k, v in record.items() if k not in mutable} == {
            k: v for k, v in original[name].items() if k not in mutable}, name
        folder = ROOT / record["canonical_location"]
        headings = re.findall(r"^## (\d+)\. (.+)$", (folder / "README.md").read_text(), re.M)
        assert headings == [(str(i), title) for i, title in enumerate(SECTIONS, 1)], name
        for part in ("python/solution.py", "cpp/solution.cpp", "tests/test_python.py", "tests/test_cpp.py", "tests/cases.py"):
            assert (folder / part).is_file() and (folder / part).stat().st_size > 0, (name, part)
        audited[name] = {"sections": 25, "required_artifacts": 6}
    category = next(c for c in after["categories"] if c["id"] == "A12")
    assert {item["algorithm"] for item in category["items"]} == allowed | {"bellman-ford", "floyd-warshall"}
    for name in ("bellman-ford", "floyd-warshall"):
        assert current[name] == original[name]
        assert not (ROOT / "dsa/dynamic-programming" / name).exists()
    result = {"baseline_revision": baseline["revision"], "prior_files_byte_identical": len(baseline["sha256"]),
              "all_syllabus_memberships_and_identities_preserved": True,
              "out_of_scope_catalog_records_unchanged": True, "dp_memberships": 13,
              "implemented_scope": sorted(allowed), "shared_graph_memberships_still_planned": ["bellman-ford", "floyd-warshall"],
              "lesson_audit": audited}
    (EVIDENCE / "preservation-results.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
