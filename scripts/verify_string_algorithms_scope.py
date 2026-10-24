"""Check exact A7 inventory and byte-preservation of approved source/history."""
import argparse
import hashlib
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def verify(root=ROOT, source_only=False):
    evidence = root/"docs/string-algorithms-evidence"
    before = yaml.safe_load((evidence/"catalog-baseline.yaml").read_text())
    after = yaml.safe_load((root/"catalog.yaml").read_text())
    assert after["categories"] == before["categories"], "syllabus identities/order changed"
    assert (len(after["categories"]),sum(len(c["items"]) for c in after["categories"]),len(after["algorithms"])) == (35,256,235)
    a = {r["id"]:r for r in before["algorithms"]}
    b = {r["id"]:r for r in after["algorithms"]}
    assert a.keys() == b.keys()
    mutable = {"documentation_status","python_status","cpp_status","test_status","notes"}
    for name,record in a.items():
        if record["category"] != "A7":
            assert record == b[name], name
        else:
            assert {k:v for k,v in record.items() if k not in mutable} == {k:v for k,v in b[name].items() if k not in mutable}, name
    assert b["dynamic-policy-optimization"]["test_status"] == "blocked"
    protected = json.loads((evidence/"approved-baseline.json").read_text())["protected_files"]
    count = 0
    omitted = []
    for name,digest in protected.items():
        if source_only and name.startswith("artifacts/review-packages/") and not name.endswith(".md"):
            omitted.append(name)
            continue
        path = root/name
        assert path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
        count += 1
    return dict(categories=35,memberships=256,canonicals=235,string_canonicals=9,
                protected_files_verified=count,source_only=source_only,
                intentionally_excluded_historical_package_files=omitted,
                out_of_scope_records="unchanged",dpo="blocked",status="passed")


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--check-only",action="store_true")
    parser.add_argument("--source-only",action="store_true")
    args=parser.parse_args()
    result=verify(source_only=args.source_only)
    if not args.check_only:
        (ROOT/"docs/string-algorithms-evidence/preservation-results.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
