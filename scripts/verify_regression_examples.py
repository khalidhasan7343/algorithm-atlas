"""Execute authored examples and JSON CLIs without rewriting historical evidence."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "machine-learning/supervised-learning/regression"
CASES = {
    "linear-regression": dict(X=[[0], [1], [2]], y=[1, 3, 5], predict=[[3]], expected=[7.0]),
    "ridge-regression": dict(X=[[-1], [0], [1]], y=[-2, 0, 2], predict=[[2]], parameters=dict(alpha=2), expected=[2.0]),
    "polynomial-regression": dict(X=[[-2], [-1], [0], [1], [2]], y=[4, 1, 0, 1, 4], predict=[[3]], expected=[9.0]),
    "lasso-regression": dict(X=[[-1], [0], [1]], y=[-2, 0, 2], predict=[[2]], parameters=dict(alpha=1/3), expected=[3.0]),
    "elastic-net": dict(X=[[-1], [0], [1]], y=[-2, 0, 2], predict=[[2]], parameters=dict(alpha=0.5, l1_ratio=0.5), expected=[26/11]),
    "support-vector-regression": dict(X=[[-1], [0], [1]], y=[-1, 0, 1], predict=[[2]], parameters=dict(C=10, epsilon=0.1, kernel="linear", tol=1e-9), expected=[1.8]),
    "decision-tree-regression": dict(X=[[0], [1], [2], [3]], y=[1, 1, 5, 5], predict=[[0.5], [2.5]], parameters=dict(max_depth=1), expected=[1.0, 5.0]),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="execute without writing another evidence attempt")
    args = parser.parse_args()
    catalog = yaml.safe_load((ROOT / "catalog.yaml").read_text())
    names = [a["id"] for a in catalog["algorithms"] if a["category"] == "B1" and a["test_status"] == "tested"]
    records = []
    for name in names:
        case = CASES[name].copy()
        expected = case.pop("expected")
        for kind, filename, input_text in (("authored example", "example.py", None), ("JSON CLI", "solution.py", json.dumps(case))):
            result = subprocess.run([sys.executable, str(BASE / name / "python" / filename)], input=input_text,
                                    capture_output=True, text=True, timeout=60, check=True)
            assert not result.stderr, result.stderr
            observed = json.loads(result.stdout)
            if kind == "JSON CLI":
                observed = observed["predictions"]
            np.testing.assert_allclose(observed, expected, atol=1e-6, rtol=1e-6)
            records.append(dict(algorithm=name, kind=kind, expected=expected, observed=observed, status="passed"))
        bad = subprocess.run([sys.executable, str(BASE / name / "python/solution.py")], input='{"X":[[1]],"y":[1,2],"predict":[[1]]}',
                             capture_output=True, text=True, timeout=60)
        assert bad.returncode == 2 and not bad.stdout and bad.stderr.startswith("error:"), name
        records.append(dict(algorithm=name, kind="invalid JSON CLI dimensions", returncode=bad.returncode, status="passed"))
    path = ROOT / "docs/regression-evidence"
    attempt = len(list(path.glob("examples-attempt*.json"))) + 1
    if not args.check_only:
        (path / f"examples-attempt{attempt}.json").write_text(json.dumps(records, indent=2) + "\n")
    print(f"{len(names)} lessons; {2*len(names)} numerical example/CLI executions and {len(names)} invalid-input CLI checks passed")


if __name__ == "__main__":
    main()
