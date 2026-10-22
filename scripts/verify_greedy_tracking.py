"""Check report tracking and validate a clean export of the actual Git index."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import yaml

from review_paths import report_paths

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/greedy-evidence"


def checked(command, cwd=ROOT):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stdout + result.stderr
    return {"command": [".venv/bin/python" if arg == sys.executable else arg for arg in command],
            "returncode": result.returncode, "output": result.stdout+result.stderr}


def main():
    catalog = yaml.safe_load((ROOT / "catalog.yaml").read_text())
    reports = sorted(set(report_paths(ROOT)) | {catalog["development"]["completion_report"]})
    for name in reports:
        assert (ROOT / name).is_file() and (ROOT / name).read_text().strip(), name
        checked(["git", "ls-files", "--error-unmatch", "--", name])
        ignored = subprocess.run(["git", "check-ignore", "--no-index", "--", name], cwd=ROOT, capture_output=True, text=True, timeout=10)
        assert ignored.returncode == 1 and not ignored.stdout, name
    staged_catalog = checked(["git", "show", ":catalog.yaml"])["output"]
    assert staged_catalog == (ROOT / "catalog.yaml").read_text(), "catalog has unstaged changes"
    with tempfile.TemporaryDirectory(prefix="atlas-greedy-tracked-") as directory:
        target = Path(directory) / "algorithm-atlas"
        target.mkdir()
        checked(["git", "checkout-index", "--all", "--prefix="+str(target)+"/"])
        validations = [checked([sys.executable, "scripts/validate_catalog.py"], target),
                       checked([sys.executable, "scripts/generate_catalog_docs.py", "--check"], target),
                       checked([sys.executable, "scripts/verify_greedy_scope.py"], target)]
    result = {"reports_nonempty_and_tracked": reports, "required_reports_ignored": False,
              "completion_report": catalog["development"]["completion_report"],
              "snapshot": "clean export of the actual staged Git index; no commit created",
              "clean_tracked_checkout_validations": validations,
              "hosted_github_actions": "not triggered or verified"}
    (EVIDENCE / "tracking-results.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="clean_tracked_checkout_validations"}, indent=2))


if __name__ == "__main__":
    main()
