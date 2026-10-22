"""Run bounded Divide/conquer batch gates and retain actual local evidence.

Examples: python scripts/run_divide_conquer_validation.py --stage batch1
          python scripts/run_divide_conquer_validation.py --stage final
Every child command has its own timeout and a separate transcript.
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
BATCHES = (
    ("maximum-subarray-divide-and-conquer", "karatsuba-multiplication"),
    ("closest-pair-of-points", "strassen-matrix-multiplication"),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", required=True,
                        choices=("batch1", "batch2", "final", "sanitizer", "configuration"))
    parser.add_argument("--output", type=Path, default=Path("docs/divide-conquer-evidence"))
    parser.add_argument("--timeout", type=int, default=240)
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("--timeout must be positive")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    pytest = ["-m", "pytest", "-q", "--require-cpp"]
    configuration = [
        ("catalog", ["scripts/validate_catalog.py"]),
        ("generated-docs", ["scripts/generate_catalog_docs.py", "--check"]),
    ]
    if args.stage in ("batch1", "batch2"):
        index = int(args.stage[-1]) - 1
        commands = [(name, [*pytest, f"dsa/divide-and-conquer/{name}/tests"])
                    for name in BATCHES[index]] + configuration
        if index == 0:
            commands.append(("full-suite", pytest))
    elif args.stage == "final":
        commands = [
            ("divide-conquer-python", [*pytest, "dsa/divide-and-conquer", "-m", "not cpp"]),
            ("divide-conquer-cpp17", [*pytest, "dsa/divide-and-conquer", "-m", "cpp", "--cpp-standard=c++17"]),
            ("divide-conquer-cpp20", [*pytest, "dsa/divide-and-conquer", "-m", "cpp", "--cpp-standard=c++20"]),
            ("infrastructure", [*pytest, "tests"]),
            ("full-suite", pytest),
            *configuration,
        ]
    elif args.stage == "sanitizer":
        flags = shlex.split(os.environ.get("CXX", ""))
        if not {"-fsanitize=address,undefined", "-fno-sanitize-recover=all"} <= set(flags):
            parser.error("set CXX to a sanitizer compiler with recovery disabled")
        commands = [("divide-conquer-sanitizer", [*pytest, "dsa/divide-and-conquer", "-m", "cpp",
                                               "--cpp-standard=c++20"])]
    else:
        commands = [*configuration, ("infrastructure", [*pytest, "tests"])]
    records = []
    for label, arguments in commands:
        command = [sys.executable, *arguments]
        display = shlex.join(["python", *arguments])
        begin = time.monotonic()
        timed_out = False
        try:
            result = subprocess.run(command, cwd=ROOT, capture_output=True,
                                    text=True, timeout=args.timeout)
            code = result.returncode
            transcript = result.stdout + result.stderr
        except subprocess.TimeoutExpired as error:
            code = None
            timed_out = True
            transcript = "".join(
                chunk.decode(errors="replace") if isinstance(chunk, bytes) else chunk
                for chunk in (error.stdout or "", error.stderr or "")
            )
        summary = next((line.strip() for line in reversed(transcript.splitlines())
                        if re.search(r"\d+ (?:passed|failed|skipped|error)", line)), "")
        row = {
            "label": label, "command": display, "returncode": code,
            "timeout_seconds": args.timeout, "timed_out": timed_out,
            "elapsed_seconds": round(time.monotonic() - begin, 3),
            "summary": summary, "CXX": os.environ.get("CXX", "automatic discovery"),
        }
        records.append(row)
        (output / f"{args.stage}-{label}.txt").write_text(
            f"Command: {display}\nResult: {json.dumps(row)}\n\n{transcript}",
            encoding="utf-8",
        )
        (output / f"{args.stage}-results.json").write_text(
            json.dumps(records, indent=2) + "\n", encoding="utf-8",
        )
        print(json.dumps(row), flush=True)
        if code != 0 or timed_out:
            # A batch gate must never advance after a failed/incomplete check.
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
