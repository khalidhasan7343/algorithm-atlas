"""Freeze Phase 13 source and verify required checks from the actual review ZIP.

Post-extraction results live in the external JSON sidecar to avoid a recursive
archive hash. Historical artifacts are preserved locally and excluded from ZIPs.
No Git mutation, publication, downloads or dependency installation is performed.
"""
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

import yaml

from package_bit_manipulation_review import excluded
from package_tree_algorithms_review import PATTERNS
from track_policy import is_complete

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/regression-evidence"
REPORT = "docs/reviews/regression/REGRESSION-REVIEW-REPORT.md"
OUTPUT = ROOT / "artifacts/review-packages/regression/algorithm-atlas-regression-review.zip"
PREFIX = "algorithm-atlas/"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    sidecar, checksum = OUTPUT.with_suffix(".json"), OUTPUT.with_suffix(".zip.sha256")
    assert not any(path.exists() for path in (OUTPUT, sidecar, checksum)), "Refusing to overwrite existing package"
    final = json.loads((EVIDENCE/"final-results.json").read_text())
    configuration = json.loads((EVIDENCE/"configuration-results.json").read_text())
    matrix = json.loads((EVIDENCE/"test-matrix.json").read_text())
    baseline = json.loads((EVIDENCE/"baseline.json").read_text())
    assert set(final) == {"ml", "numerical", "reference", "full-suite"}
    assert all(r["returncode"] == 0 and not r["timed_out"] for r in [*final.values(), *configuration.values()])
    assert matrix["failures"] == matrix["errors"] == matrix["skipped"] == 0
    for batch in (1, 2, 3):
        assert json.loads((EVIDENCE/f"batch{batch}-results.json").read_text())[f"batch{batch}"]["returncode"] == 0
    names = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT).decode().split("\0")
    paths = sorted({PurePosixPath(name) for name in names if name and (ROOT/name).is_file() and not excluded(PurePosixPath(name))})
    payload = {}
    for relative in paths:
        source = ROOT/relative
        assert not source.is_symlink() and not relative.is_absolute() and ".." not in relative.parts
        data = source.read_bytes()
        data.decode("utf-8")
        for label, pattern in PATTERNS.items():
            assert not re.search(pattern, data), f"Potential credential: {relative} ({label})"
        payload[relative.as_posix()] = data
    catalog = yaml.safe_load(payload["catalog.yaml"])
    development = catalog["development"]
    assert development["status"] == "awaiting-review" and development["completed_batches"] == [1, 2, 3]
    algorithms = [a for a in catalog["algorithms"] if a["category"] == "B1"]
    assert len(algorithms) == 7 and all(is_complete(a) and a["cpp_status"] == "planned" for a in algorithms)
    required = {REPORT, "README.md", "AGENTS.md", "CONTRIBUTING.md", "LICENSE", "catalog.yaml", "conftest.py", "pyproject.toml",
                "requirements-dev.txt", "requirements-ml.txt", "requirements-ml-test.txt", ".github/workflows/ci.yml",
                "docs/ml-development.md", "docs/regression-scope.md", "docs/regression-checkpoints.md",
                "scripts/track_policy.py", "scripts/validate_catalog.py", "scripts/generate_catalog_docs.py",
                "scripts/verify_regression_scope.py", "scripts/verify_regression_examples.py", "scripts/run_regression_validation.py",
                "scripts/package_regression_review.py", "tests/test_track_policy.py",
                "machine-learning/supervised-learning/regression/support.py",
                "machine-learning/supervised-learning/regression/conftest.py",
                "machine-learning/supervised-learning/regression/tests/test_contracts.py",
                "machine-learning/supervised-learning/regression/experiments/benchmark.py"}
    for algorithm in catalog["algorithms"]:
        folder = algorithm["canonical_location"]
        required.add(folder+"/README.md")
        if algorithm["test_status"] in ("tested", "reviewed"):
            required.update(folder+"/"+part for part in ("python/solution.py", "tests/test_python.py"))
            if algorithm["category"] != "B1":
                required.update(folder+"/"+part for part in ("cpp/solution.cpp", "tests/test_cpp.py"))
    required.update(a["canonical_location"]+"/python/example.py" for a in algorithms)
    required.update(name for name in baseline["tracked"] if name.startswith("docs/reviews/") and name.endswith(".md"))
    required.update("docs/regression-evidence/"+name for name in ("baseline.json", "catalog-baseline.yaml", "test-matrix.json",
        "environment.json", "preservation-results.json", "final-results.json", "configuration-results.json", "benchmark.json"))
    assert required <= payload.keys(), sorted(required-payload.keys())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "x", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in payload.items():
            entry = zipfile.ZipInfo(PREFIX+name, date_time=(2026, 10, 27, 0, 0, 0))
            entry.create_system = 3
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(entry, data)
    digest = sha(OUTPUT.read_bytes())
    checksum.write_text(f"{digest}  {OUTPUT.name}\n")
    metadata = dict(phase_number=13, phase_name=development["phase"], category_id="B1", category_name="Supervised Learning — Regression",
                    category_slug="regression", algorithm_count=7, implementation_count=7,
                    timestamp=datetime.now(ZoneInfo("Asia/Dhaka")).isoformat(), starting_revision=baseline["revision"], branch=baseline["branch"],
                    python_test_status=final["ml"], optional_cpp_status="Optional, absent for all seven; no dummy files; DSA requirements unchanged",
                    mathematical_correctness_status="passed analytical identities, finite differences, KKT/gap/feasibility and brute-force split tests",
                    numerical_validation_status=final["numerical"], independent_reference_status=final["reference"],
                    dsa_regression_status=matrix["dsa"], full_suite=matrix,
                    catalog_validation_status=configuration["catalog"], documentation_validation_status=configuration["generated"],
                    dependency_information=json.loads((EVIDENCE/"environment.json").read_text()),
                    known_limitations=["Dense single-output float64 with documented magnitude/sample/feature budgets; no weights, missing-data handling or sparse matrices.",
                        "Numerical rank cutoffs and ill conditioning limit coefficient accuracy; no universal parameter-error bound.",
                        "Coordinate descent and fixed-rho ADMM can fail to converge within a bounded budget; failure is explicit.",
                        "SVR uses dense kernels, at most 256 training rows, approximate floating-point feasibility/gap checks.",
                        "CART is greedy and may differ from other libraries on ties; no global optimum guarantee.",
                        "Synthetic held-out experiment is illustrative, with no general superiority claim.",
                        "Local Python 3.14.2/macOS Apple Clang results; hosted Linux/Python CI matrix not verified.",
                        "New work is pending owner approval; historical DSA checkpoints retain their recorded statuses."],
                    owner_approval="pending", phase11_owner_approval="pending", phase12_owner_approval="pending",
                    archive=OUTPUT.name, bytes=OUTPUT.stat().st_size, sha256=digest, files=len(payload),
                    file_sha256={name: sha(data) for name, data in payload.items()},
                    extraction_checks=[], extraction_validation_status="running", report=REPORT,
                    dependency_environment="Existing local ML development interpreter; dependencies external, no bundled venv or network install",
                    historical_archives_included=False, nested_archives=False, hosted_github_actions="not run or verified")
    sidecar.write_text(json.dumps(metadata, indent=2)+"\n")
    with zipfile.ZipFile(OUTPUT) as archive:
        assert all(count == 1 for count in Counter(archive.namelist()).values())
        assert archive.testzip() is None and len(archive.namelist()) == len(payload)
        for entry in archive.infolist():
            path = PurePosixPath(entry.filename)
            assert path.parts[0] == "algorithm-atlas" and ".." not in path.parts and not path.is_absolute()
            relative = PurePosixPath(*path.parts[1:])
            assert stat.S_ISREG(entry.external_attr >> 16) and not excluded(relative)
            assert archive.read(entry) == payload[relative.as_posix()]
        with tempfile.TemporaryDirectory(prefix="atlas-regression-export-") as temporary:
            archive.extractall(temporary)
            exported = Path(temporary)/"algorithm-atlas"
            commands = [["scripts/validate_catalog.py"], ["scripts/generate_catalog_docs.py", "--check"],
                        ["scripts/verify_regression_scope.py", "--check-only", "--source-only"],
                        ["scripts/verify_regression_examples.py", "--check-only"],
                        ["-m", "pytest", "--require-cpp", "-q"]]
            env = os.environ.copy()
            env.pop("PYTHONPATH", None)
            env.update(PYTHONHASHSEED="0", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
            for args in commands:
                started = time.monotonic()
                try:
                    result = subprocess.run([sys.executable, *args], cwd=exported, capture_output=True, text=True, env=env, timeout=1200)
                    record = dict(command=["python", *args], returncode=result.returncode, timed_out=False,
                                  elapsed_seconds=round(time.monotonic()-started, 3), output=result.stdout+result.stderr)
                except subprocess.TimeoutExpired as error:
                    record = dict(command=["python", *args], returncode=None, timed_out=True,
                                  elapsed_seconds=round(time.monotonic()-started, 3), output=str(error.stdout)+str(error.stderr))
                metadata["extraction_checks"].append(record)
                metadata["extraction_validation_status"] = "failed" if record["returncode"] != 0 else "running"
                sidecar.write_text(json.dumps(metadata, indent=2)+"\n")
                print("export: " + " ".join(args) + ": " + record["output"].strip().splitlines()[-1], flush=True)
                if record["returncode"] != 0:
                    raise SystemExit(1)
    assert checksum.read_text().split()[0] == sha(OUTPUT.read_bytes()) == digest
    assert all((ROOT/name).read_bytes() == data for name, data in payload.items()), "Source changed during packaging"
    metadata.update(extraction_validation_status="passed", zip_crc="passed", source_bytes="identical", checksum_consistency="passed",
                    safe_unique_regular_paths=True, required_files_present=True, credential_scan="no high-confidence matches")
    sidecar.write_text(json.dumps(metadata, indent=2)+"\n")
    print(f"Verified {OUTPUT.relative_to(ROOT)} ({len(payload)} files); SHA-256 {digest}")


if __name__ == "__main__":
    main()
