"""Verify Phase 4 preserves canonical scope and all prior algorithm files."""
import argparse
import hashlib
import json
from pathlib import Path
import yaml

from review_paths import assert_preserved

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/divide-conquer-evidence"
NEW = {"maximum-subarray-divide-and-conquer", "karatsuba-multiplication",
       "closest-pair-of-points", "strassen-matrix-multiplication"}
REUSED = {"merge-sort", "quick-sort", "binary-search"}
MUTABLE = {"documentation_status", "python_status", "cpp_status", "test_status", "notes"}


def main(write_evidence=True):
    baseline = json.loads((EVIDENCE / "approved-baseline.json").read_text())
    for name, digest in baseline["files_sha256"].items():
        assert_preserved(ROOT, name, digest)
    original = (EVIDENCE / baseline['catalog_baseline_file']).read_bytes()
    assert hashlib.sha256(original).hexdigest() == baseline['catalog_sha256']
    before = yaml.safe_load(original)
    after = yaml.safe_load((ROOT / "catalog.yaml").read_text())
    assert before["categories"] == after["categories"], "Syllabus memberships changed"
    old = {a["id"]: a for a in before["algorithms"]}
    current = {a["id"]: a for a in after["algorithms"]}
    assert old.keys() == current.keys()
    for name, record in current.items():
        if name in NEW:
            assert {k:v for k,v in old[name].items() if k not in MUTABLE} == {
                k:v for k,v in record.items() if k not in MUTABLE}, name
        else:
            assert record == old[name], name
    category = next(c for c in after["categories"] if c["id"] == "A4")
    assert {m["algorithm"] for m in category["items"]} == NEW | REUSED
    for name in REUSED:
        assert not (ROOT / "dsa/divide-and-conquer" / name).exists(), name
    report = {"baseline_HEAD":baseline["baseline_HEAD"],
              "prior_files_baseline_bytes_verified":len(baseline["files_sha256"]),
              "syllabus_and_all_canonical_identities_unchanged":True,
              "out_of_scope_catalog_records_unchanged":True,
              "category_memberships":len(category["items"]),
              "new_topics":sorted(NEW), "reused_topics":sorted(REUSED),
              "duplicate_reused_folders":0}
    if write_evidence:
        (EVIDENCE / "preservation-results.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Verify without replacing historical execution evidence.")
    main(write_evidence=not parser.parse_args().check_only)
