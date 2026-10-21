"""Run bounded, separately logged Sorting verification commands.

Use --stage individual before extra audits, then --stage groups. Each command
has its own timeout; a failure or timeout is recorded and does not hide later
results. Logs use paths relative to the checkout and do not require Git.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
ALGORITHMS = (
    "bubble-sort", "selection-sort", "insertion-sort", "merge-sort",
    "quick-sort", "heap-sort", "counting-sort", "radix-sort",
    "bucket-sort", "shell-sort", "tim-sort",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("individual", "groups", "sanitizer"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("--timeout must be positive")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    pytest = ["-m", "pytest", "-q", "--require-cpp"]
    if args.stage == "individual":
        commands = [
            (name, [*pytest, f"dsa/sorting/{name}/tests"])
            for name in ALGORITHMS
        ]
    elif args.stage == "groups":
        commands = [
            ("sorting-python", [*pytest, "dsa/sorting", "-m", "not cpp"]),
            ("sorting-cpp17", [*pytest, "dsa/sorting", "-m", "cpp",
                               "--cpp-standard=c++17"]),
            ("sorting-cpp20", [*pytest, "dsa/sorting", "-m", "cpp",
                               "--cpp-standard=c++20"]),
            ("infrastructure", [*pytest, "tests"]),
            ("full-suite", pytest),
            ("catalog", ["scripts/validate_catalog.py"]),
            ("generated-docs", ["scripts/generate_catalog_docs.py", "--check"]),
        ]
    else:
        if "-fsanitize=address,undefined" not in shlex.split(os.environ.get("CXX", "")):
            parser.error("sanitizer stage requires CXX with -fsanitize=address,undefined")
        commands = [
            ("sanitizer", [*pytest, "dsa/sorting/tests", "dsa/sorting/tim-sort/tests",
                           "-m", "cpp", "--cpp-standard=c++20"]),
        ]
    results = []
    for label, arguments in commands:
        command = [sys.executable, *arguments]
        displayed = shlex.join(["python", *arguments])
        begin = time.monotonic()
        timed_out = False
        try:
            completed = subprocess.run(
                command, cwd=ROOT, capture_output=True, text=True,
                timeout=args.timeout, env=os.environ.copy(),
            )
            code = completed.returncode
            transcript = completed.stdout + completed.stderr
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            code = None
            chunks = [exc.stdout or b"", exc.stderr or b""]
            transcript = "".join(
                chunk.decode(errors="replace") if isinstance(chunk, bytes)
                else chunk for chunk in chunks
            )
        seconds = round(time.monotonic() - begin, 3)
        # Pytest prints its complete outcome before the trailing timing clause.
        summary = next((line.strip() for line in reversed(transcript.splitlines())
                        if re.search(r"\d+ (?:passed|failed|error|skipped)", line)), "")
        record = {
            "label": label, "command": displayed, "returncode": code,
            "timeout_seconds": args.timeout, "timed_out": timed_out,
            "elapsed_seconds": seconds, "summary": summary,
            "CXX": os.environ.get("CXX", "(automatic g++/clang++ discovery)"),
        }
        results.append(record)
        header = f"Command: {displayed}\nResult: {json.dumps(record)}\n\n"
        (output / f"{label}.txt").write_text(header + transcript, encoding="utf-8")
        (output / f"{args.stage}-results.json").write_text(
            json.dumps(results, indent=2) + "\n", encoding="utf-8",
        )
        print(json.dumps(record), flush=True)
    return int(any(row["returncode"] != 0 or row["timed_out"] for row in results))


if __name__ == "__main__":
    raise SystemExit(main())
