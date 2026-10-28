"""Freeze Phase 14 source, inspect the actual ZIP and execute its exported checks.

Extraction output goes into the external JSON sidecar after ZIP creation, avoiding
recursive hashes. Existing outputs are never overwritten, and historical binary
archives/sidecars stay outside source payloads. No Git mutations or downloads.
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
from track_policy import cpp_required, is_complete

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/classification-evidence"
REPORT = "docs/reviews/classification/CLASSIFICATION-REVIEW-REPORT.md"
OUTPUT = ROOT / "artifacts/review-packages/classification/algorithm-atlas-classification-review.zip"
PREFIX = "algorithm-atlas/"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    sidecar, checksum = OUTPUT.with_suffix(".json"), OUTPUT.with_suffix(".zip.sha256")
    assert not any(path.exists() for path in (OUTPUT, sidecar, checksum)), "Refusing to overwrite an existing review artifact"
    final = json.loads((EVIDENCE / "final-results.json").read_text())
    configuration = json.loads((EVIDENCE / "configuration-results.json").read_text())
    matrix = json.loads((EVIDENCE / "test-matrix.json").read_text())
    baseline = json.loads((EVIDENCE / "baseline.json").read_text())
    preservation = json.loads((EVIDENCE / "preservation-results.json").read_text())
    assert set(final) == {"ml", "numerical", "reference", "B1", "full-suite"}
    assert all(r["returncode"] == 0 and not r["timed_out"] for r in [*final.values(), *configuration.values()])
    assert matrix["failures"] == matrix["errors"] == matrix["skipped"] == 0
    assert preservation["status"] == "passed" and preservation["phase13_owner_approval"] == "approved"
    for batch in (1, 2, 3, 4):
        records = json.loads((EVIDENCE / f"batch{batch}-results.json").read_text())
        assert records[f"batch{batch}"]["returncode"] == 0
    names = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT).decode().split("\0")
    paths = sorted({PurePosixPath(name) for name in names if name and (ROOT / name).is_file() and not excluded(PurePosixPath(name))})
    payload = {}
    for relative in paths:
        source = ROOT / relative
        assert not source.is_symlink() and not relative.is_absolute() and ".." not in relative.parts
        data = source.read_bytes()
        data.decode("utf-8")
        for label, pattern in PATTERNS.items():
            assert not re.search(pattern, data), f"Potential credential: {relative} ({label})"
        payload[relative.as_posix()] = data
    catalog = yaml.safe_load(payload["catalog.yaml"])
    state = catalog["development"]
    assert state["category"] == "B2" and state["phase_number"] == 14
    assert state["status"] == "awaiting-review" and state["completed_batches"] == [1, 2, 3, 4]
    assert state["phase_records"]["13"]["owner_approval"] == "approved"
    assert state["phase_records"]["14"]["owner_approval"] == "pending"
    algorithms = [a for a in catalog["algorithms"] if a["category"] == "B2"]
    assert len(algorithms) == 11 and all(is_complete(a) and a["cpp_status"] == "planned" for a in algorithms)
    category = "machine-learning/supervised-learning/classification/"
    required = {REPORT, "README.md", "AGENTS.md", "CONTRIBUTING.md", "LICENSE", "catalog.yaml", "conftest.py", "pyproject.toml",
                "requirements-dev.txt", "requirements-ml.txt", "requirements-ml-test.txt", ".github/workflows/ci.yml",
                "docs/ml-development.md", "docs/classification-scope.md", "docs/classification-conventions.md", "docs/classification-checkpoints.md",
                "scripts/track_policy.py", "scripts/validate_catalog.py", "scripts/generate_catalog_docs.py",
                "scripts/verify_classification_scope.py", "scripts/verify_classification_examples.py", "scripts/run_classification_validation.py",
                "scripts/package_classification_review.py", "tests/test_track_policy.py",
                category + "support.py", category + "metrics.py", category + "conftest.py",
                category + "tests/test_contracts.py", category + "tests/test_metrics_and_cross_models.py", category + "experiments/benchmark.py"}
    for algorithm in catalog["algorithms"]:
        folder = algorithm["canonical_location"]
        required.add(folder + "/README.md")
        if algorithm["test_status"] in ("tested", "reviewed"):
            required.update(folder + "/" + name for name in ("python/solution.py", "tests/test_python.py"))
            if cpp_required(algorithm):
                required.update(folder + "/" + name for name in ("cpp/solution.cpp", "tests/test_cpp.py"))
    required.update(a["canonical_location"] + "/python/example.py" for a in algorithms)
    required.update(name for name in baseline["tracked"] if name.startswith("docs/reviews/") and name.endswith(".md"))
    required.update("docs/classification-evidence/" + name for name in ("baseline.json", "catalog-baseline.yaml", "baseline-validation.json",
        "test-matrix.json", "environment.json", "preservation-results.json", "final-results.json", "configuration-results.json", "benchmark.json",
        "reference-sources.json", "changed-files.json"))
    assert required <= payload.keys(), sorted(required - payload.keys())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "x", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in payload.items():
            entry = zipfile.ZipInfo(PREFIX + name, date_time=(2026, 10, 28, 0, 0, 0))
            entry.create_system = 3
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(entry, data)
    digest = sha(OUTPUT.read_bytes())
    checksum.write_text(f"{digest}  {OUTPUT.name}\n")
    metadata = dict(phase_number=14, phase_name=state["phase"], category_id="B2", category_name="Supervised Learning — Classification",
                    category_slug="classification", algorithm_count=11, implementation_count=11,
                    timestamp=datetime.now(ZoneInfo("Asia/Dhaka")).isoformat(), starting_revision=baseline["revision"], branch=baseline["branch"],
                    python_test_status=final["ml"], optional_cpp_status="Optional, absent for all eleven B2 topics; DSA C++17/C++20 unchanged",
                    mathematical_correctness_status="passed analytical gradients, event likelihoods, dual feasibility/gap, exhaustive tree splits and Gaussian discriminants",
                    numerical_validation_status=final["numerical"], independent_reference_status=final["reference"],
                    B1_regression_status=final["B1"], DSA_regression_status=matrix["dsa"], cpp17_status=matrix["dsa"]["cpp17"],
                    cpp20_status=matrix["dsa"]["cpp20"], full_suite=matrix,
                    catalog_validation_status=configuration["catalog"], documentation_validation_status=configuration["generated"],
                    dependency_information=json.loads((EVIDENCE / "environment.json").read_text()), dependencies_changed=False,
                    known_limitations=["Dense finite numeric arrays and explicit sample/feature/cell/magnitude caps; no sparse inputs or sample weights.",
                        "Labels are homogeneous int64-compatible integers or nonempty strings; no arbitrary/mixed-label coercion.",
                        "Logistic and SVM are binary; SVM is linear, n<=256, with no calibrated probability output.",
                        "Newton/ADMM are bounded and can report non-convergence; numerical gaps are approximate floating-point evidence.",
                        "ID3 uses integer-coded categories. C4.5 is the documented gain-ratio/MDL/filter subset; no pruning or missing-value routing.",
                        "Trees are greedy; node/vote probabilities are empirical and not guaranteed calibrated.",
                        "LDA has no transform; QDA requires at least two rows/class; unresolved covariance directions fail explicitly.",
                        "Fixed synthetic cohorts/splits and observational timing do not establish universal model superiority.",
                        "Local Python 3.14.2/macOS Apple Clang results; hosted CI matrix and other platforms unverified."],
                    owner_approval="pending", phase13_owner_approval="approved", phase11_owner_approval="pending", phase12_owner_approval="pending",
                    report=REPORT, report_tracking_status="pending final working-tree check",
                    archive=OUTPUT.name, bytes=OUTPUT.stat().st_size, sha256=digest, files=len(payload),
                    file_sha256={name: sha(data) for name, data in payload.items()},
                    extraction_checks=[], extraction_validation_status="running",
                    dependency_environment="Existing external local ML development interpreter; no bundled environment or network installation",
                    historical_archives_included=False, nested_archives=False, hosted_github_actions="not run or verified")
    sidecar.write_text(json.dumps(metadata, indent=2) + "\n")
    with zipfile.ZipFile(OUTPUT) as archive:
        assert all(count == 1 for count in Counter(archive.namelist()).values())
        assert archive.testzip() is None and len(archive.namelist()) == len(payload)
        for entry in archive.infolist():
            path = PurePosixPath(entry.filename)
            assert path.parts[0] == "algorithm-atlas" and ".." not in path.parts and not path.is_absolute()
            relative = PurePosixPath(*path.parts[1:])
            assert stat.S_ISREG(entry.external_attr >> 16) and not excluded(relative)
            assert archive.read(entry) == payload[relative.as_posix()]
        with tempfile.TemporaryDirectory(prefix="atlas-classification-export-") as temporary:
            archive.extractall(temporary)
            exported = Path(temporary) / "algorithm-atlas"
            commands = [["scripts/validate_catalog.py"], ["scripts/generate_catalog_docs.py", "--check"],
                        ["scripts/verify_classification_scope.py", "--check-only", "--source-only"],
                        ["scripts/verify_classification_examples.py", "--check-only"],
                        ["-m", "pytest", "--require-cpp", "-q"]]
            env = os.environ.copy()
            env.pop("PYTHONPATH", None)
            env.update(PYTHONHASHSEED="0", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", LOKY_MAX_CPU_COUNT="2")
            for args in commands:
                started = time.monotonic()
                try:
                    result = subprocess.run([sys.executable, *args], cwd=exported, capture_output=True, text=True, env=env, timeout=1200)
                    record = dict(command=["python", *args], returncode=result.returncode, timed_out=False,
                                  elapsed_seconds=round(time.monotonic() - started, 3), output=result.stdout + result.stderr)
                except subprocess.TimeoutExpired as error:
                    record = dict(command=["python", *args], returncode=None, timed_out=True,
                                  elapsed_seconds=round(time.monotonic() - started, 3), output=str(error.stdout) + str(error.stderr))
                metadata["extraction_checks"].append(record)
                metadata["extraction_validation_status"] = "failed" if record["returncode"] != 0 else "running"
                sidecar.write_text(json.dumps(metadata, indent=2) + "\n")
                print("export: " + " ".join(args) + ": " + record["output"].strip().splitlines()[-1], flush=True)
                if record["returncode"] != 0:
                    raise SystemExit(1)
    assert checksum.read_text().split()[0] == sha(OUTPUT.read_bytes()) == digest
    assert all((ROOT / name).read_bytes() == data for name, data in payload.items()), "Source changed during packaging"
    metadata.update(extraction_validation_status="passed", zip_crc="passed", source_bytes="identical", checksum_consistency="passed",
                    safe_unique_regular_paths=True, required_files_present=True, credential_scan="no high-confidence matches")
    sidecar.write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Verified {OUTPUT.relative_to(ROOT)} ({len(payload)} files); SHA-256 {digest}")


if __name__ == "__main__":
    main()
