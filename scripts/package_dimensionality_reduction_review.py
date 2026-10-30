"""Freeze the Phase 17 B5 Dimensionality Reduction source, inspect the actual ZIP and execute its exported checks.

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
EVIDENCE = ROOT / "docs/dimensionality-reduction-evidence"
REPORT = "docs/reviews/dimensionality-reduction/DIMENSIONALITY-REDUCTION-REVIEW-REPORT.md"
OUTPUT = ROOT / "artifacts/review-packages/dimensionality-reduction/algorithm-atlas-dimensionality-reduction-review.zip"
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
    assert set(final) == {"B5", "numerical", "oracle", "reference", "B1", "B2", "B3", "B4", "full-suite"}
    assert all(r["returncode"] == 0 and not r["timed_out"] for r in [*final.values(), *configuration.values()])
    assert matrix["failures"] == matrix["errors"] == matrix["skipped"] == 0
    assert preservation["status"] == "passed" and preservation["phase16_owner_approval"] == "approved"
    assert preservation["phase17_owner_approval"] == "pending"
    assert preservation["report_tracking"] == "tracked and unignored"
    for batch in range(1, 5):
        records = json.loads((EVIDENCE / f"batch{batch}-results.json").read_text())
        assert records[f"batch{batch}"]["returncode"] == 0
    subprocess.run([sys.executable, "scripts/verify_dimensionality_reduction_scope.py", "--check-only"], cwd=ROOT, check=True)
    subprocess.run(["git", "ls-files", "--error-unmatch", REPORT], cwd=ROOT, check=True, capture_output=True)
    assert subprocess.run(["git", "check-ignore", "-q", REPORT], cwd=ROOT).returncode == 1
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
    assert state["category"] == "B5" and state["phase_number"] == 17
    assert state["status"] == "awaiting-review" and state["completed_batches"] == [1, 2, 3, 4]
    assert state["current_review"]["owner_approval"] == state["phase_records"]["17"]["owner_approval"] == "pending"
    assert state["phase_records"]["16"]["owner_approval"] == "approved"
    member_ids={i["algorithm"] for i in next(c for c in catalog["categories"] if c["id"]=="B5")["items"]}
    algorithms = [a for a in catalog["algorithms"] if a["id"] in member_ids]
    assert len(algorithms) == 7 and all(is_complete(a) and a["cpp_status"] == "planned" for a in algorithms)
    category = "machine-learning/unsupervised-learning/dimensionality-reduction/"
    required = {REPORT, "README.md", "AGENTS.md", "CONTRIBUTING.md", "LICENSE", "catalog.yaml", "conftest.py", "pyproject.toml",
                "requirements-dev.txt", "requirements-ml.txt", "requirements-ml-test.txt", ".github/workflows/ci.yml",
                "docs/ml-development.md", "docs/dimensionality-reduction-scope.md", "docs/dimensionality-reduction-conventions.md", "docs/dimensionality-reduction-checkpoints.md",
                "scripts/track_policy.py", "scripts/validate_catalog.py", "scripts/generate_catalog_docs.py",
                "scripts/verify_dimensionality_reduction_scope.py", "scripts/verify_dimensionality_reduction_examples.py", "scripts/run_dimensionality_reduction_validation.py",
                "scripts/package_dimensionality_reduction_review.py", "tests/test_track_policy.py", "tests/test_validate_catalog.py", "tests/test_generate_catalog_docs.py",
                category + "support.py", category + "conftest.py", category + "tests/test_contracts.py",
                "tests/test_b5_shared_canonical_policy.py", "machine-learning/deep-learning/vanilla-autoencoders/conftest.py"}
    for algorithm in catalog["algorithms"]:
        folder = algorithm["canonical_location"]
        required.add(folder + "/README.md")
        if algorithm["test_status"] in ("tested", "reviewed"):
            required.update(folder + "/" + name for name in ("python/solution.py", "tests/test_python.py"))
            if cpp_required(algorithm):
                required.update(folder + "/" + name for name in ("cpp/solution.cpp", "tests/test_cpp.py"))
    required.update(a["canonical_location"] + "/python/example.py" for a in algorithms)
    required.update(name for name in baseline["hashes"] if name.startswith("docs/reviews/") and name.endswith(".md"))
    required.update("docs/dimensionality-reduction-evidence/" + name for name in ("baseline.json", "catalog-baseline.yaml", "baseline-results.json",
        "test-matrix.json", "environment.json", "preservation-results.json", "final-results.json", "configuration-results.json",
        "reference-sources.json", "changed-files.json", "development-findings.json", "approval-evidence.json", "examples-results.json",
        "negative-validation-matrix.json"))
    assert required <= payload.keys(), sorted(required - payload.keys())
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "x", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in payload.items():
            entry = zipfile.ZipInfo(PREFIX + name, date_time=(2026, 10, 30, 0, 0, 0))
            entry.create_system = 3
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(entry, data)
    digest = sha(OUTPUT.read_bytes())
    checksum.write_text(f"{digest}  {OUTPUT.name}\n")
    metadata = dict(phase_number=17, phase_name=state["phase"], category_id="B5", category_name="Dimensionality Reduction",
                    category_slug="dimensionality-reduction", algorithm_count=7, implementation_count=7,
                    algorithm_ids=[a["id"] for a in algorithms],
                    client_review_date="2026-10-30 Asia/Dhaka", timestamp=datetime.now(ZoneInfo("Asia/Dhaka")).isoformat(),
                    starting_revision=baseline["revision"], branch=baseline["branch"],
                    python_test_status=final["B5"], optional_cpp_status="Optional, absent for all seven B5 members; DSA both languages/C++17/C++20 unchanged",
                    mathematical_correctness_status="passed Jacobi reconstruction, PCA covariance, Fisher scatter/eigenspaces, ICA whitening/recovery, t-SNE KL/gradient, UMAP fuzzy graph/gradient and autoencoder backprop oracles",
                    numerical_validation_status=final["numerical"], independent_oracle_status=final["oracle"], independent_reference_status=final["reference"],
                    B1_regression_status=final["B1"], B2_classification_status=final["B2"], B3_ensemble_status=final["B3"], B4_clustering_status=final["B4"],
                    DSA_regression_status=matrix["dsa"], cpp17_status=matrix["dsa"]["cpp17"], cpp20_status=matrix["dsa"]["cpp20"], full_suite=matrix,
                    catalog_validation_status=configuration["catalog"], documentation_validation_status=configuration["generated"],
                    negative_validation=json.loads((EVIDENCE / "negative-validation-matrix.json").read_text()),
                    dependency_information=json.loads((EVIDENCE / "environment.json").read_text()), dependencies_changed=False,
                    canonical_ownership={a['id']:dict(owner=a['category'],path=a['canonical_location']) for a in algorithms},
                    shared_memberships={'vanilla-autoencoders':['B5','B7']},
                    known_limitations=["Dense finite arrays n<=512,p<=32; manifold n<=128; explicit input/resource and numerical resolution bounds.",
                        "Reduced Jacobi SVD truncates unresolved directions; PCA does not standardize and physical tiny variances can underflow.",
                        "LDA requires labels and at most classes-1 directions; singular Sw needs explicit normalized-unit regularization.",
                        "FastICA assumes resolved non-Gaussian independent sources, sign/scale/permutation ambiguity; convergence not guaranteed.",
                        "t-SNE is exact transductive KL, no exaggeration or transform; nearest-distance ties can make perplexity unattainable.",
                        "UMAP exact self-excluding kNN, local_connectivity1, fixed rational b1 kernel, smoothed full cross-entropy rather than negative sampling; saturated local scales exposed.",
                        "t-SNE/UMAP/autoencoder finite budgets expose convergence status; no global optimum or reference-coordinate parity claimed.",
                        "Canonical shared autoencoder has one tanh/linear bottleneck and linear decoder, full-batch MSE/backprop; no superiority over PCA or other B7 authorization.",
                        "Hosted GitHub Actions and other OS/Python/compiler matrices were not run or verified."],
                    development_findings=json.loads((EVIDENCE / "development-findings.json").read_text()),
                    owner_approval="pending", phase16_owner_approval="approved", prior_package_preservation="all previous package bytes unchanged",
                    report=REPORT, report_tracking_status="tracked and unignored; unrelated staged contents preserved",
                    starting_staged_diff_sha256=baseline["staged_diff_sha256"],
                    archive=OUTPUT.name, bytes=OUTPUT.stat().st_size, sha256=digest, files=len(payload),
                    file_sha256={name: sha(data) for name, data in payload.items()},
                    extraction_checks=[], extraction_validation_status="running",
                    dependency_environment="Existing external installed ML interpreter; no bundled environment or network installer",
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
        with tempfile.TemporaryDirectory(prefix="atlas-dimensionality-reduction-export-") as temporary:
            archive.extractall(temporary)
            exported = Path(temporary) / "algorithm-atlas"
            commands = [["scripts/validate_catalog.py"], ["scripts/generate_catalog_docs.py", "--check"],
                        ["scripts/verify_dimensionality_reduction_scope.py", "--check-only", "--source-only"],
                        ["scripts/verify_dimensionality_reduction_examples.py", "--check-only"],
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
                if args[:2] == ["-m", "pytest"] and record["returncode"] == 0:
                    assert re.search(r"\b" + str(matrix["tests"]) + r" passed\b", record["output"]), "Extracted test count differs"
                    assert not re.search(r"\b\d+ (?:failed|skipped|errors?)\b", record["output"]), "Extracted suite has failures/skips"
                if record["returncode"] != 0:
                    raise SystemExit(1)
    subprocess.run([sys.executable, "scripts/verify_dimensionality_reduction_scope.py", "--check-only"], cwd=ROOT, check=True)
    assert checksum.read_text().split()[0] == sha(OUTPUT.read_bytes()) == digest
    assert all((ROOT / name).read_bytes() == data for name, data in payload.items()), "Source changed during packaging"
    metadata.update(extraction_validation_status="passed", zip_crc="passed", source_bytes="identical", checksum_consistency="passed",
                    safe_unique_regular_paths=True, required_files_present=True, credential_scan="no high-confidence matches")
    sidecar.write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Verified {OUTPUT.relative_to(ROOT)} ({len(payload)} files); SHA-256 {digest}")


if __name__ == "__main__":
    main()
