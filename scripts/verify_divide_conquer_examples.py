"""Compile and execute the four documented README examples without a shell."""

import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    catalog = yaml.safe_load((ROOT / "catalog.yaml").read_text())
    compiler = shlex.split(os.environ.get("CXX", ""))
    if not compiler:
        compiler = [shutil.which("g++") or shutil.which("clang++") or "g++"]
    records = []
    with tempfile.TemporaryDirectory(prefix="atlas-divide_conquer-examples-") as temporary:
        for record in catalog["algorithms"]:
            if record["category"] != "A4":
                continue
            folder = ROOT / record["canonical_location"]
            text = (folder / "README.md").read_text()
            example = text.split("## 15. Input and Output Examples\n", 1)[1].split("## 16.", 1)[0]
            sample = re.search(r"printf '([^']*)\\n'", example)
            output = re.search(r"```json\n(.*?)\n```", example, re.S)
            assert sample and output, record["id"]
            expected = json.dumps(json.loads(output[1]), separators=(",", ":")) + "\n"
            executable = Path(temporary) / record["id"]
            compile_command = [*compiler, "-std=c++20", "-Wall", "-Wextra", "-pedantic",
                               str(folder / "cpp/solution.cpp"), "-o", str(executable)]
            subprocess.run(compile_command, capture_output=True, text=True,
                           timeout=60, check=True)
            for language, command in (
                ("python", [sys.executable, str(folder / "python/solution.py")]),
                ("cpp20", [str(executable)]),
            ):
                result = subprocess.run(command, input=sample[1] + "\n", text=True,
                                        capture_output=True, timeout=20, check=True)
                assert result.stdout == expected and result.stderr == "", record["id"]
                records.append({"algorithm": record["id"], "language": language,
                                "input": sample[1], "expected_stdout": expected,
                                "returncode": result.returncode, "passed": True})
    destination = ROOT / "docs/divide-conquer-evidence/examples-results.json"
    destination.write_text(json.dumps(records, indent=2) + "\n")
    print(f"All {len(records)} documented Python/C++20 example executions passed.")


if __name__ == "__main__":
    main()
