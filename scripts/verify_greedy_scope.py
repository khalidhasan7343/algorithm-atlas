"""Audit Phase 6 artifacts, scope counts, classification and prior-file preservation."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

import yaml

from validate_catalog import GREEDY_BATCHES, SECTIONS, STATUS_FIELDS

from review_paths import assert_preserved

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/greedy-evidence"


def main(write_evidence=True):
    baseline = json.loads((EVIDENCE / "approved-baseline.json").read_text())
    for name, digest in baseline["sha256"].items():
        assert_preserved(ROOT, name, digest)
    source_catalog = (EVIDENCE / "catalog-baseline.yaml").read_bytes()
    assert hashlib.sha256(source_catalog).hexdigest() == baseline["catalog_sha256"]
    before = yaml.safe_load(source_catalog)
    after = yaml.safe_load((ROOT / "catalog.yaml").read_text())
    assert before["categories"] == after["categories"], "syllabus memberships changed"
    original = {a["id"]: a for a in before["algorithms"]}
    current = {a["id"]: a for a in after["algorithms"]}
    assert original.keys() == current.keys() and len(current) == 235
    assert sum(len(c["items"]) for c in after["categories"]) == 256
    owned = {name for batch in GREEDY_BATCHES for name in batch}
    graph = {"dijkstra", "prim", "kruskal"}
    mutable = {*STATUS_FIELDS, "notes", "related_algorithms"}
    audit, inventory = {}, {}
    for name, record in current.items():
        if name not in owned:
            assert record == original[name], name
            continue
        assert {k: v for k, v in record.items() if k not in mutable} == {
            k: v for k, v in original[name].items() if k not in mutable}, name
        folder = ROOT / record["canonical_location"]
        headings = re.findall(r"^## (\d+)\. (.+)$", (folder / "README.md").read_text(), re.M)
        assert headings == [(str(i), title) for i, title in enumerate(SECTIONS, 1)], name
        for part in ("python/solution.py", "cpp/solution.cpp", "tests/test_python.py", "tests/test_cpp.py", "tests/cases.py"):
            assert (folder / part).is_file() and (folder / part).stat().st_size, (name, part)
        audit[name] = {"sections": 25, "required_artifacts": 6}
        spec = importlib.util.spec_from_file_location("greedy_oracle_"+name, folder / "tests/cases.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        inventory[name] = {"independently_expected_vectors": len(module.vectors())}
    category = next(c for c in after["categories"] if c["id"] == "A11")
    assert {m["algorithm"] for m in category["items"]} == owned | graph
    for name in graph:
        assert current[name] == original[name]
        assert not (ROOT / "dsa/greedy" / name).exists(), name
        assert all(current[name][field] == "planned" for field in STATUS_FIELDS)
    category_text = (ROOT / "dsa/greedy/README.md").read_text()
    assert "Greedy algorithms implemented in Phase 6" in category_text
    left, right = category_text.split("Graph algorithms that also use the Greedy paradigm")
    roadmap = (ROOT / "docs/learning-roadmap.md").read_text()
    for name in owned:
        assert "]("+name+"/README.md)" in left
    for name in graph:
        assert "](../graph-algorithms/"+name+"/README.md)" in right
        assert "../dsa/graph-algorithms/"+name+"/" in roadmap
    assert graph <= set(current["activity-selection"]["related_algorithms"])
    result = {"baseline_revision": baseline["revision"], "prior_files_baseline_bytes_verified": len(baseline["sha256"]),
              "syllabus_memberships": 256, "canonical_topics": 235, "greedy_memberships": 7,
              "all_memberships_identities_and_out_of_scope_records_preserved": True,
              "implemented_scope": sorted(owned), "graph_conceptual_references_only": sorted(graph),
              "graph_paths_statuses_unchanged": True, "duplicate_graph_folders": 0,
              "schema_supported_conceptual_metadata": "activity-selection.related_algorithms",
              "lesson_audit": audit}
    if write_evidence:
        (EVIDENCE / "preservation-results.json").write_text(json.dumps(result, indent=2)+"\n")
    if write_evidence:
        (EVIDENCE / "oracle-inventory.json").write_text(json.dumps(inventory, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Verify without replacing historical execution evidence.")
    main(write_evidence=not parser.parse_args().check_only)
