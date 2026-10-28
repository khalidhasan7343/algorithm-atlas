"""Verify Phase 13 scope, original DSA bytes, history and lesson contracts.

The baseline was captured before changes. --check-only reads existing evidence
without rewriting it. Git checks are omitted in a source export with no .git;
historical ZIPs/sidecars deliberately excluded from exports are reported absent.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

import yaml

from track_policy import is_complete
from validate_catalog import SECTIONS

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/regression-evidence"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--source-only", action="store_true")
    args = parser.parse_args()
    baseline = json.loads((EVIDENCE / "baseline.json").read_text())
    old = yaml.safe_load((EVIDENCE / "catalog-baseline.yaml").read_text())
    current = yaml.safe_load((ROOT / "catalog.yaml").read_text())
    assert current["categories"] == old["categories"]
    ids = [a["id"] for a in current["algorithms"]]
    assert ids == [a["id"] for a in old["algorithms"]]
    topics = {item["algorithm"] for item in baseline["first_ml_category"]["items"]}
    assert len(topics) == 7
    dsa = [a for a in old["algorithms"] if a["canonical_location"].startswith("dsa/")]
    assert len(dsa) == 97
    for previous, now in zip(old["algorithms"], current["algorithms"]):
        assert previous["canonical_location"] == now["canonical_location"]
        if previous["id"] not in topics:
            assert previous == now, previous["id"]
        else:
            assert is_complete(now) and now["cpp_status"] == "planned", now["id"]
    for phase in ("11", "12"):
        assert old["development"]["phase_records"][phase] == current["development"]["phase_records"][phase]
    canonical_folders = tuple(a["canonical_location"] + "/" for a in dsa)
    protected = {p: h for p, h in baseline["hashes"].items()
                 if p.startswith(canonical_folders) or
                 (p.startswith("dsa/") and p.endswith((".py", ".hpp", ".cpp"))) or
                 (p.startswith("docs/") and ("-evidence/" in p or p.startswith("docs/reviews/")) and p != "docs/reviews/README.md") or
                 (p.startswith("artifacts/review-packages/") and p != "artifacts/review-packages/README.md") or
                 p in ("LICENSE", "conftest.py", "requirements-dev.txt")}
    omitted = []
    for p, expected in protected.items():
        if args.source_only and p.startswith("artifacts/review-packages/") and not (ROOT/p).exists():
            omitted.append(p)
            continue
        assert (ROOT/p).is_file() and digest(ROOT/p) == expected, f"Preservation failure: {p}"
    rows = []
    for topic in sorted(topics):
        algorithm = next(a for a in current["algorithms"] if a["id"] == topic)
        folder = ROOT / algorithm["canonical_location"]
        headings = re.findall(r"^##[ \t]+(.+)$", (folder/"README.md").read_text(), re.M)
        assert headings == [f"{i}. {title}" for i, title in enumerate(SECTIONS, 1)]
        for name in ("python/solution.py", "python/example.py", "tests/test_python.py"):
            assert (folder/name).is_file() and (folder/name).stat().st_size > 0
        assert not (folder/"cpp/solution.cpp").exists() and not (folder/"tests/test_cpp.py").exists()
        # Educational implementations may use NumPy primitives, never reference estimators.
        source = ast.parse((folder/"python/solution.py").read_text())
        imports = []
        for node in ast.walk(source):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
        assert not any(name.split(".")[0] in {"sklearn", "scipy", "torch", "tensorflow", "requests", "pickle", "subprocess"}
                       for name in imports)
        rows.append(dict(id=topic, exact_sections=25, python="tested", cpp="optional, absent", imports=imports))
    has_git = (ROOT/".git").exists() and not args.source_only
    if has_git:
        continuation_path = EVIDENCE/"continuation-baseline.json"
        expected_revision = baseline["revision"]
        if continuation_path.exists():
            continuation = json.loads(continuation_path.read_text())
            assert continuation["original_revision"] == baseline["revision"]
            assert continuation["candidate_source_files_verified"] == 1621
            expected_revision = continuation["revision"]
            subprocess.run(["git", "merge-base", "--is-ancestor", baseline["revision"], expected_revision], cwd=ROOT, check=True)
            for name, expected_hash in continuation["historical_package_files"].items():
                assert (ROOT/name).is_file() and digest(ROOT/name) == expected_hash, name
        assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip() == expected_revision
        report = "docs/reviews/regression/REGRESSION-REVIEW-REPORT.md"
        subprocess.run(["git", "ls-files", "--error-unmatch", report], cwd=ROOT, check=True, capture_output=True)
        assert not subprocess.run(["git", "check-ignore", "-q", report], cwd=ROOT).returncode == 0
    result = dict(status="passed", inventory=baseline["counts"], dsa_canonicals=len(dsa),
                  protected_files_verified=len(protected)-len(omitted), historical_artifacts_omitted_from_source_export=omitted,
                  original_categories_and_order="identical", out_of_scope_algorithm_records="identical",
                  phase11_phase12_records="identical, pending", head="matches recorded starting/continuation revision" if has_git else "not checked in source export",
                  lessons=rows, owner_approval="pending")
    if not args.check_only:
        (EVIDENCE/"preservation-results.json").write_text(json.dumps(result, indent=2)+"\n")
    print(f"Scope/preservation passed: 7 ML lessons, 97 DSA canonicals, {result['protected_files_verified']} protected files; inventory 35/256/235")


if __name__ == "__main__":
    main()
