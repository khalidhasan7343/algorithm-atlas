"""Run Regression completion audit gates with bounded commands and preserved attempt transcripts."""
from datetime import datetime
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/regression-audit-evidence"
CATEGORY = "machine-learning/supervised-learning/regression"

def run(label, args, timeout=1200):
    attempts = sorted(EVIDENCE.glob(label + "-attempt*.json"))
    name = f"{label}-attempt{len(attempts) + 1}"
    started = time.monotonic()
    env = os.environ.copy()
    env.update(PYTHONHASHSEED="0", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", LOKY_MAX_CPU_COUNT="2")
    try:
        result = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True,
                                text=True, timeout=timeout, env=env)
        code, output, timed_out = result.returncode, result.stdout + result.stderr, False
    except subprocess.TimeoutExpired as error:
        code, timed_out = None, True
        output = "".join(x.decode(errors="replace") if isinstance(x, bytes) else x or "" for x in (error.stdout, error.stderr))
    record = dict(command=["python", *args], interpreter=sys.executable,
                  timestamp=datetime.now(ZoneInfo("Asia/Dhaka")).isoformat(),
                  elapsed_seconds=round(time.monotonic() - started, 3), returncode=code,
                  timed_out=timed_out, timeout_seconds=timeout,
                  environment={k: env.get(k) for k in ("CXX", "PYTHONHASHSEED", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS")},
                  log=f"docs/regression-audit-evidence/{name}.txt",
                  summary=output.strip().splitlines()[-1] if output.strip() else "no output")
    (EVIDENCE / (name + ".txt")).write_text(output)
    (EVIDENCE / (name + ".json")).write_text(json.dumps(record, indent=2) + "\n")
    print(label + ": " + record["summary"], flush=True)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("baseline", "targeted", "configuration", "final"), required=True)
    stage = parser.parse_args().stage
    EVIDENCE.mkdir(exist_ok=True)
    if stage == "baseline":
        jobs = [("baseline-B1", ["-m", "pytest", CATEGORY, "-q"]),
                ("baseline-catalog", ["scripts/validate_catalog.py"]),
                ("baseline-generated", ["scripts/generate_catalog_docs.py", "--check"])]
    elif stage == "targeted":
        jobs = [("B1", ["-m", "pytest", CATEGORY, "-q", "--junitxml=" + str(EVIDENCE / "B1.xml")]),
                ("numerical", ["-m", "pytest", CATEGORY, "-m", "numerical", "-q"]),
                ("reference", ["-m", "pytest", CATEGORY, "-m", "reference", "-q"])]
    elif stage == "configuration":
        jobs = [("catalog", ["scripts/validate_catalog.py"]), ("generated", ["scripts/generate_catalog_docs.py", "--check"]),
                ("infrastructure", ["-m", "pytest", "tests", "--require-cpp", "-q"])]
    else:
        jobs = [("B1", ["-m", "pytest", CATEGORY, "-q", "--junitxml=" + str(EVIDENCE / "B1.xml")]),
                ("numerical", ["-m", "pytest", CATEGORY, "-m", "numerical", "-q"]),
                ("reference", ["-m", "pytest", CATEGORY, "-m", "reference", "-q"]),
                ("classification", ["-m", "pytest", "machine-learning/supervised-learning/classification", "-q"]),
                ("full-suite", ["-m", "pytest", "--require-cpp", "-q", "--junitxml=" + str(EVIDENCE / "full-suite.xml")])]
    results = {}
    for label, args in jobs:
        results[label] = run(label, args)
        (EVIDENCE / (stage + "-results.json")).write_text(json.dumps(results, indent=2) + "\n")
        if results[label]["returncode"] != 0:
            raise SystemExit(1)
    versions = {name: importlib.metadata.version(name) for name in ("numpy", "scikit-learn", "scipy", "pytest", "PyYAML", "joblib", "threadpoolctl", "cloudpickle")}
    (EVIDENCE / "environment.json").write_text(json.dumps(dict(python=sys.version, platform=platform.platform(), dependencies=versions,
                                                               dependency_setup="Established Phase 13 environment reused; no installation or upgrade."), indent=2) + "\n")


if __name__ == "__main__":
    main()
