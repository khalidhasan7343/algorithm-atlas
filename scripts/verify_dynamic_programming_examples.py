"""Execute every lesson's documented CLI example against its exact expectation."""
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = {
    "fibonacci": ("10\n", "55"),
    "zero-one-knapsack": ("5 3 2 3 3 4 4 5\n", "7"),
    "coin-change": ("6 3 1 3 4\n", "[2,4]"),
    "rod-cutting": ("4 4 2 5 7 8\n", "10"),
    "longest-common-subsequence": ("abc\nac\n", "2"),
    "longest-increasing-subsequence": ("8 10 9 2 5 3 7 101 18\n", "4"),
    "edit-distance": ("kitten\nsitting\n", "3"),
    "matrix-chain-multiplication": ("4 10 30 5 60\n", "4500"),
    "subset-sum": ("9 6 3 34 4 12 5 2\n", "true"),
    "palindrome-partitioning": ("aab\n", "1"),
    "kadane": ("9 -2 1 -3 4 -1 2 1 -5 4\n", '["6",3,7]'),
}


def main():
    compiler = shlex.split(os.environ.get("CXX", "")) or [shutil.which("g++") or shutil.which("clang++")]
    assert compiler[0], "C++ compiler required"
    records = []
    with tempfile.TemporaryDirectory(prefix="atlas-dp-examples-") as temp:
        for name, (text, expected) in EXAMPLES.items():
            folder = ROOT / "dsa/dynamic-programming" / name
            lesson = (folder / "README.md").read_text()
            assert "\n"+expected+"\n" in lesson
            binary = Path(temp) / name
            command = [*compiler, "-std=c++20", "-Wall", "-Wextra", "-pedantic", str(folder / "cpp/solution.cpp"), "-o", str(binary)]
            compiled = subprocess.run(command, capture_output=True, text=True, timeout=60)
            assert compiled.returncode == 0, compiled.stderr
            for language, invocation in (("python", [sys.executable, str(folder / "python/solution.py")]), ("cpp20", [str(binary)])):
                result = subprocess.run(invocation, input=text, text=True, capture_output=True, timeout=10)
                assert result.returncode == 0 and result.stdout == expected+"\n" and not result.stderr, (name, language, result)
                records.append({"topic": name, "language": language, "input": text, "expected": expected,
                                "returncode": result.returncode, "stdout": result.stdout})
    (ROOT / "docs/dynamic-programming-evidence/examples-results.json").write_text(json.dumps(records, indent=2)+"\n")
    print(f"{len(records)}/{len(EXAMPLES)*2} documented examples matched exact output")


if __name__ == "__main__":
    main()
