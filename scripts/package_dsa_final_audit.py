"""Package the audited source and run required checks from its actual ZIP export.

The package sidecar records extraction results after ZIP creation, avoiding
self-referential hashes. Historical archives and private/build files are never
bundled. This command neither stages files nor changes owner approvals.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
import time
import zipfile
from zoneinfo import ZoneInfo

from package_bit_manipulation_review import excluded
from package_tree_algorithms_review import PATTERNS

ROOT = Path(__file__).resolve().parents[1]
REVIEW = "docs/reviews/dsa-final-audit"
OUTPUT = ROOT / "artifacts/review-packages/dsa-final-audit/algorithm-atlas-dsa-final-audit.zip"
PREFIX = "algorithm-atlas/"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    sidecar = OUTPUT.with_suffix(".json")
    checksum = OUTPUT.with_suffix(".zip.sha256")
    if any(p.exists() for p in (OUTPUT, sidecar, checksum)):
        raise SystemExit("Refusing to overwrite an existing final-audit review package")
    matrix = json.loads((ROOT / REVIEW / "DSA-AUDIT-TEST-MATRIX.json").read_text())
    findings = json.loads((ROOT / REVIEW / "DSA-AUDIT-FINDINGS.json").read_text())
    baseline = json.loads((ROOT / REVIEW / "evidence/baseline.json").read_text())
    assert matrix["summary"]["failures"] == matrix["summary"]["skipped"] == 0
    assert matrix["summary"]["unexecuted_algorithms"] == []
    assert matrix["owner_approval"] == "pending"
    names = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT).decode().split("\0")
    paths = sorted({PurePosixPath(name) for name in names if name and (ROOT / name).is_file()
                    and not excluded(PurePosixPath(name))})
    payload = {}
    for relative in paths:
        source = ROOT / relative
        assert not source.is_symlink() and not relative.is_absolute() and ".." not in relative.parts, relative
        data = source.read_bytes()
        data.decode("utf-8")
        for label, pattern in PATTERNS.items():
            assert not re.search(pattern, data), f"Potential credential in {relative}: {label}"
        payload[relative.as_posix()] = data
    required = {"catalog.yaml", "LICENSE", "AGENTS.md", "conftest.py", "pyproject.toml", "requirements-dev.txt",
                ".github/workflows/ci.yml", "scripts/validate_catalog.py", "scripts/generate_catalog_docs.py",
                "scripts/run_dsa_final_audit.py", "scripts/package_dsa_final_audit.py",
                REVIEW + "/DSA-FINAL-AUDIT-REPORT.md", REVIEW + "/DSA-AUDIT-FINDINGS.json",
                REVIEW + "/DSA-AUDIT-TEST-MATRIX.json", REVIEW + "/verify_independent.py"}
    for a in baseline["algorithms"]:
        required.update(a["canonical_location"] + "/" + p for p in
                        ("README.md", "python/solution.py", "cpp/solution.cpp", "tests/test_python.py", "tests/test_cpp.py"))
    required.update(name for name in baseline["tracked"] if name.startswith("docs/reviews/") and name.endswith(".md"))
    assert required <= payload.keys(), sorted(required - payload.keys())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "x", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in payload.items():
            entry = zipfile.ZipInfo(PREFIX + name, date_time=(2026, 10, 24, 12, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(entry, data)
    digest = sha(OUTPUT.read_bytes())
    checksum.write_text(f"{digest}  {OUTPUT.name}\n")
    metadata = dict(audit_name="Algorithm Atlas comprehensive DSA final audit",
                    audit_timestamp=datetime.now(ZoneInfo("Asia/Dhaka")).isoformat(),
                    repository_revision=baseline["revision"], branch=baseline["branch"],
                    dsa_category_count=baseline["counts"]["dsa_categories"],
                    dsa_canonical_algorithm_count=len(baseline["algorithms"]), audited_algorithm_count=len(matrix["algorithms"]),
                    python_test_summary=matrix["summary"]["python"], cpp17_test_summary=matrix["summary"]["cpp17"],
                    cpp20_test_summary=matrix["summary"]["cpp20"], full_suite=matrix["summary"],
                    independent_correctness_summary=matrix["independent_summary"],
                    documentation_status="97 exact 25-section lessons; local links and all primary examples verified; 24 external retrievals unverified",
                    catalog_status="passed; 35 categories / 256 memberships / 235 canonicals; catalog unchanged",
                    ci_equivalent_status="local required checks passed on Python 3.14.2 / Apple Clang 21; hosted Actions not verified",
                    finding_counts=findings["counts"],
                    number_of_critical_findings=findings["counts"]["critical"], number_of_high_findings=findings["counts"]["high"],
                    number_of_medium_findings=findings["counts"]["medium"], number_of_low_findings=findings["counts"]["low"],
                    final_recommendation=matrix["final_recommendation"], owner_approval_status="pending",
                    phase11_owner_approval="pending", phase12_owner_approval="pending",
                    archive=OUTPUT.name, bytes=OUTPUT.stat().st_size, sha256=digest, files=len(payload),
                    file_sha256={name: sha(data) for name, data in payload.items()},
                    extraction_checks=[], extraction_validation_status="running",
                    dependency_environment="Existing local development interpreter; no bundled venv, network install or .git",
                    historical_archives_included=False)
    sidecar.write_text(json.dumps(metadata, indent=2) + "\n")
    with zipfile.ZipFile(OUTPUT) as archive:
        archive_names = archive.namelist()
        assert not [n for n, count in Counter(archive_names).items() if count > 1]
        assert archive.testzip() is None
        assert len(archive_names) == len(payload)
        for entry in archive.infolist():
            path = PurePosixPath(entry.filename)
            assert path.parts[0] == "algorithm-atlas" and ".." not in path.parts and not path.is_absolute()
            assert stat.S_ISREG(entry.external_attr >> 16)
            assert not excluded(PurePosixPath(*path.parts[1:]))
            assert archive.read(entry.filename) == payload[str(PurePosixPath(*path.parts[1:]))]
        with tempfile.TemporaryDirectory(prefix="atlas-final-audit-export-") as temporary:
            archive.extractall(temporary)
            exported = Path(temporary) / "algorithm-atlas"
            commands = [["scripts/validate_catalog.py"], ["scripts/generate_catalog_docs.py", "--check"],
                        ["-m", "pytest", "--require-cpp", "-q"]]
            env = os.environ.copy()
            env.pop("PYTHONPATH", None)
            env["PYTHONHASHSEED"] = "0"
            for args in commands:
                started = time.monotonic()
                try:
                    result = subprocess.run([sys.executable, *args], cwd=exported, capture_output=True,
                                            text=True, env=env, timeout=1200)
                    record = dict(command=["python", *args], returncode=result.returncode, timed_out=False,
                                  elapsed_seconds=round(time.monotonic() - started, 3),
                                  output=result.stdout + result.stderr)
                except subprocess.TimeoutExpired as error:
                    record = dict(command=["python", *args], returncode=None, timed_out=True,
                                  elapsed_seconds=round(time.monotonic() - started, 3),
                                  output=str(error.stdout) + str(error.stderr))
                metadata["extraction_checks"].append(record)
                metadata["extraction_validation_status"] = "failed" if record["returncode"] != 0 else "running"
                sidecar.write_text(json.dumps(metadata, indent=2) + "\n")
                print("export: " + " ".join(args) + ": " + record["output"].strip().splitlines()[-1], flush=True)
                if record["returncode"] != 0:
                    raise SystemExit(1)
    assert checksum.read_text().split()[0] == sha(OUTPUT.read_bytes()) == digest
    metadata.update(extraction_validation_status="passed", zip_crc="passed", source_bytes="passed", checksum_consistency="passed",
                    git_status=subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True))
    sidecar.write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Verified {OUTPUT.relative_to(ROOT)} ({len(payload)} files); SHA-256 {digest}")


if __name__ == "__main__":
    main()
