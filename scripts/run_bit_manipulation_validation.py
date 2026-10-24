"""Record real Phase 10 commands without inferring owner approval or changing status."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/bit-manipulation-evidence"
BATCHES = (
    ("xor-unique-elements", "two-non-repeating-elements"),
    ("brian-kernighan-set-bit-counting", "subset-generation-bitmasking"),
)


def run(label, arguments, stage, timeout=900):
    command = [sys.executable, *arguments]
    started = time.monotonic()
    timed_out = False
    try:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        code, output = result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired as error:
        timed_out = True
        code = None
        output = (error.stdout or b"").decode() + (error.stderr or b"").decode()
    log = EVIDENCE / f"{stage}-{label}.txt"
    log.write_text(output)
    record = dict(command=["python",*arguments],returncode=code,timed_out=timed_out,
                  timeout_seconds=timeout,elapsed_seconds=round(time.monotonic()-started,2),
                  log=log.relative_to(ROOT).as_posix(),timestamp=datetime.now(timezone.utc).isoformat())
    print(label, code, output.strip().splitlines()[-1:] or ["no output"], flush=True)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("batch1","batch2","configuration","final"),required=True)
    args = parser.parse_args()
    EVIDENCE.mkdir(exist_ok=True)
    commands = {}
    if args.stage.startswith("batch"):
        paths = ["dsa/bit-manipulation/"+name for name in BATCHES[int(args.stage[-1])-1]]
        commands = {"algorithms":["-m","pytest",*paths,"--require-cpp","-q"]}
    elif args.stage == "configuration":
        commands = {"catalog":["scripts/validate_catalog.py"],
                    "generated-docs":["scripts/generate_catalog_docs.py","--check"],
                    "infrastructure":["-m","pytest","tests","--require-cpp","-q"]}
    else:
        commands = {"python":["-m","pytest","dsa/bit-manipulation","-m","not cpp","-q"],
                    "cpp17":["-m","pytest","dsa/bit-manipulation","-m","cpp","--cpp-standard=c++17","--require-cpp","-q"],
                    "cpp20":["-m","pytest","dsa/bit-manipulation","-m","cpp","--cpp-standard=c++20","--require-cpp","-q"],
                    "full-suite":["-m","pytest","--require-cpp","-q"]}
    records = {}
    for label, command in commands.items():
        records[label] = run(label,command,args.stage)
        (EVIDENCE / f"{args.stage}-results.json").write_text(json.dumps(records,indent=2)+"\n")
        if records[label]["returncode"] != 0:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
