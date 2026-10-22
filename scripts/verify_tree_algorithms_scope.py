"""Audit Phase 8 artifacts, scope counts, classification and prior-file preservation."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

import yaml

from validate_catalog import TREE_BATCHES, SECTIONS, STATUS_FIELDS



ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/tree-algorithms-evidence"


def main(write_evidence=True, source_only=False):
    baseline = json.loads((EVIDENCE / "approved-baseline.json").read_text())
    checked=0;excluded=[]
    for name,digest in baseline["sha256"].items():
        path=ROOT/name
        if source_only and name.startswith('artifacts/review-packages/') and not path.exists():
            assert name.endswith(('.zip','.zip.sha256','.zip.verification.json')),name
            excluded.append(name);continue
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==digest,name
        checked+=1
    source_catalog = (EVIDENCE / "catalog-baseline.yaml").read_bytes()
    assert hashlib.sha256(source_catalog).hexdigest() == baseline["catalog_sha256"]
    before = yaml.safe_load(source_catalog)
    after = yaml.safe_load((ROOT / "catalog.yaml").read_text())
    assert before["categories"] == after["categories"], "syllabus memberships changed"
    original = {a["id"]: a for a in before["algorithms"]}
    current = {a["id"]: a for a in after["algorithms"]}
    assert original.keys() == current.keys() and len(current) == 235
    assert sum(len(c["items"]) for c in after["categories"]) == 256
    owned = {name for batch in TREE_BATCHES for name in batch}
    mutable = {*STATUS_FIELDS, "notes", "related_algorithms"}
    audit, inventory = {}, {}
    for name, record in current.items():
        if name not in owned:
            assert record == original[name], name
            continue
        assert {k: v for k, v in record.items() if k not in mutable} == {
            k: v for k, v in original[name].items() if k not in mutable}, name
        assert record["documentation_status"]=="implemented" and all(record[k]=="tested" for k in ("python_status","cpp_status","test_status")), name
        folder = ROOT / record["canonical_location"]
        headings = re.findall(r"^## (\d+)\. (.+)$", (folder / "README.md").read_text(), re.M)
        assert headings == [(str(i), title) for i, title in enumerate(SECTIONS, 1)], name
        for part in ("python/solution.py", "cpp/solution.cpp", "tests/test_python.py", "tests/test_cpp.py", "tests/cases.py"):
            assert (folder / part).is_file() and (folder / part).stat().st_size, (name, part)
        audit[name] = {"sections": 25, "required_artifacts": 6}
        spec = importlib.util.spec_from_file_location("tree_oracle_"+name, folder / "tests/cases.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        inventory[name] = {"independently_expected_vectors": len(module.vectors()), "seed": module.SEED}
    category = next(c for c in after["categories"] if c["id"] == "A6")
    assert {m["algorithm"] for m in category["items"]} == owned and len(owned)==14
    assert {p.parent.name for p in (ROOT/'dsa/tree-algorithms').glob('*/README.md')}==owned
    for name in owned:
        locations=[(ROOT/c['path']/name/'README.md') for c in after['categories'] if (ROOT/c['path']/name/'README.md').is_file()]
        assert locations==[ROOT/current[name]['canonical_location']/'README.md'],name
        assert current[name]["canonical_location"]=="dsa/tree-algorithms/"+name
    assert after['algorithms'][next(i for i,a in enumerate(after['algorithms']) if a['id']=='dynamic-policy-optimization')]['test_status']=='blocked'
    result = {"baseline_revision": baseline["revision"], "prior_files_baseline_bytes_verified": checked,"excluded_old_package_files":excluded,
              "syllabus_memberships": 256, "canonical_topics": 235, "categories":35,"tree_memberships":len(category["items"]),
              "all_memberships_identities_and_out_of_scope_records_preserved": True,
              "implemented_scope": sorted(owned),"duplicate_cross_category_folders":0,
              "lesson_audit": audit}
    if write_evidence:
        (EVIDENCE / "preservation-results.json").write_text(json.dumps(result, indent=2)+"\n")
    if write_evidence:
        (EVIDENCE / "oracle-inventory.json").write_text(json.dumps(inventory, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Verify without replacing historical execution evidence.")
    parser.add_argument("--source-only",action="store_true",help="Permit omitted historical package files in a source-only ZIP export.")
    args=parser.parse_args()
    main(write_evidence=not args.check_only,source_only=args.source_only)
