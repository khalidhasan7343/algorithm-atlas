"""Run bounded sequential gates and save actual outputs, including failures."""
import argparse
import json
import os
import platform
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/dynamic-programming-evidence"
BATCHES = (
    ("fibonacci", "zero-one-knapsack", "coin-change", "rod-cutting"),
    ("longest-common-subsequence", "longest-increasing-subsequence", "edit-distance"),
    ("matrix-chain-multiplication", "subset-sum", "palindrome-partitioning"),
    ("kadane",),
)


def run(label, arguments, timeout=300):
    start = time.monotonic()
    command = [sys.executable, *arguments]
    try:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        output, code, timed_out = result.stdout + result.stderr, result.returncode, False
    except subprocess.TimeoutExpired as error:
        output = (error.stdout or b"") + (error.stderr or b"")
        if isinstance(output, bytes):
            output = output.decode(errors="replace")
        code, timed_out = None, True
    record = {"command": [".venv/bin/python", *arguments], "returncode": code,
              "CXX": os.environ.get("CXX", "automatic discovery"),
              "timed_out": timed_out, "timeout_seconds": timeout,
              "elapsed_seconds": round(time.monotonic()-start, 3), "output": output}
    (EVIDENCE / (label + ".txt")).write_text(output)
    print(label + ": " + output.strip().splitlines()[-1] if output.strip() else label + ": no output", flush=True)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["batch1", "batch2", "batch3", "batch4", "final", "configuration", "sanitizer"], required=True)
    stage = parser.parse_args().stage
    EVIDENCE.mkdir(exist_ok=True)
    if stage.startswith("batch"):
        names = BATCHES[int(stage[-1])-1]
        jobs = [(name, ["-m", "pytest", "dsa/dynamic-programming/"+name, "--require-cpp", "-q"]) for name in names]
    elif stage == "final":
        jobs = [("python", ["-m", "pytest", "dsa/dynamic-programming", "-m", "not cpp", "-q"]),
                ("cpp17", ["-m", "pytest", "dsa/dynamic-programming", "-m", "cpp", "--cpp-standard=c++17", "--require-cpp", "-q"]),
                ("cpp20", ["-m", "pytest", "dsa/dynamic-programming", "-m", "cpp", "--cpp-standard=c++20", "--require-cpp", "-q"]),
                ("full-suite", ["-m", "pytest", "--require-cpp", "-q"])]
    elif stage == "sanitizer":
        if not all(flag in os.environ.get("CXX", "").split() for flag in
                   ("-fsanitize=address,undefined", "-fno-sanitize-recover=all")):
            parser.error("sanitizer stage requires CXX sanitizer flags with recovery disabled")
        jobs = [("sanitizer", ["-m", "pytest", "dsa/dynamic-programming", "-m", "cpp", "--cpp-standard=c++20", "--require-cpp", "-q"])]
    else:
        jobs = [("catalog", ["scripts/validate_catalog.py"]),
                ("generated-docs", ["scripts/generate_catalog_docs.py", "--check"]),
                ("infrastructure", ["-m", "pytest", "tests", "--require-cpp", "-q"])]
    results = {}
    for label, args in jobs:
        results[label] = run(stage+"-"+label, args)
        (EVIDENCE / (stage+"-results.json")).write_text(json.dumps(results, indent=2)+"\n")
        if results[label]["returncode"] != 0:
            raise SystemExit(1)
    compiler = subprocess.run(["g++", "--version"], capture_output=True, text=True, timeout=10)
    (EVIDENCE / "environment.json").write_text(json.dumps({"python": sys.version, "platform": platform.platform(), "default_compiler": compiler.stdout}, indent=2)+"\n")


if __name__ == "__main__":
    main()
