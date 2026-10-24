"""Reproduce DSA final-audit checks without rewriting historical evidence.

Use the repository's development interpreter. Outputs belong to the new audit
directory only; no command changes catalog statuses or owner approvals.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import subprocess
import sys
import time
import tempfile
import zipfile
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs/reviews/dsa-final-audit"
EVIDENCE = REVIEW / "evidence"


def save(name, value):
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / name).write_text(json.dumps(value, indent=2) + "\n")


def run(label, arguments, *, environment=None, timeout=1200, cwd=ROOT):
    """Record every exit, timeout and full transcript, including failures."""
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    command = [sys.executable, *arguments]
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                                env=environment, timeout=timeout)
        output, code, timed_out = result.stdout + result.stderr, result.returncode, False
    except subprocess.TimeoutExpired as error:
        output = "".join(p.decode(errors="replace") if isinstance(p, bytes) else p or ""
                         for p in (error.stdout, error.stderr))
        code, timed_out = None, True
    log = EVIDENCE / (label + ".txt")
    log.write_text(output)
    record = dict(command=["python", *arguments], interpreter=sys.executable,
                  timestamp=datetime.now(ZoneInfo("Asia/Dhaka")).isoformat(),
                  returncode=code, timed_out=timed_out, timeout_seconds=timeout,
                  execution_context="working repository" if cwd == ROOT else "isolated source copy",
                  elapsed_seconds=round(time.monotonic() - start, 3),
                  CXX=(environment or os.environ).get("CXX", "automatic discovery"),
                  ASAN_OPTIONS=(environment or os.environ).get("ASAN_OPTIONS"),
                  UBSAN_OPTIONS=(environment or os.environ).get("UBSAN_OPTIONS"),
                  log=log.relative_to(ROOT).as_posix(),
                  summary=output.strip().splitlines()[-1] if output.strip() else "no output")
    save(label + ".json", record)
    print(label + ": " + record["summary"], flush=True)
    return record


def inventory():
    """Inspect all canonical sources, all lesson sections, and historical archives."""
    from validate_catalog import SECTIONS
    catalog = yaml.safe_load((ROOT / "catalog.yaml").read_text())
    categories = [c for c in catalog["categories"] if c["path"].startswith("dsa/")]
    ids = {i["algorithm"] for c in categories for i in c["items"]}
    algorithms = [a for a in catalog["algorithms"] if a["id"] in ids]
    tracked = set(subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines())
    rows, issues, imports, hashes = [], [], {}, {}
    for a in algorithms:
        folder = ROOT / a["canonical_location"]
        required = [folder / p for p in ("README.md", "python/solution.py", "cpp/solution.cpp",
                                        "tests/test_python.py", "tests/test_cpp.py")]
        missing = [p.relative_to(ROOT).as_posix() for p in required
                   if not p.is_file() or not p.read_text().strip()]
        text = (folder / "README.md").read_text()
        headings = re.findall(r"^## (\d+)\. (.+)$", text, re.M)
        expected = [(str(i), title) for i, title in enumerate(SECTIONS, 1)]
        sections = re.split(r"^## \d+\. .+$", text, flags=re.M)[1:]
        sparse = [i for i, body in enumerate(sections, 1) if len(body.split()) < 8]
        py = (folder / "python/solution.py").read_text()
        cpp = (folder / "cpp/solution.cpp").read_text()
        tree = ast.parse(py)
        imports[a["id"]] = sorted({n.names[0].name if isinstance(n, ast.Import) else n.module or ""
                                    for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))})
        placeholders = bool(re.search(r"\b(?:TODO|FIXME|NotImplementedError)\b", py + cpp + text))
        for p in required:
            hashes[p.relative_to(ROOT).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
        problems = dict(missing=missing, headings_correct=headings == expected,
                        sparse_sections=sparse, placeholders=placeholders)
        if missing or headings != expected or placeholders:
            issues.append(dict(algorithm=a["id"], **problems))
        rows.append(dict(category=a["category"], algorithm_id=a["id"], name=a["name"],
                         canonical_path=a["canonical_location"], canonical_owner=a["category"],
                         maintainer="MD.Khalid Hasan",
                         memberships=[c["id"] for c in categories
                                      if any(i["algorithm"] == a["id"] for i in c["items"])],
                         catalog_status={k: a[k] for k in ("documentation_status", "python_status", "cpp_status", "test_status")},
                         source_lines=dict(python=len(py.splitlines()), cpp=len(cpp.splitlines())),
                         documentation_structure=problems,
                         tests_tracked=all(p.relative_to(ROOT).as_posix() in tracked for p in required)))
    known = {a["canonical_location"] for a in algorithms}
    actual = {p.parents[1].relative_to(ROOT).as_posix() for p in (ROOT / "dsa").glob("*/*/python/solution.py")}
    assert known == actual, (known - actual, actual - known)
    assert len(ids) == len(algorithms) == len({a["canonical_location"] for a in algorithms})
    archives = []
    for p in sorted((ROOT / "artifacts/review-packages").glob("*/*.zip")):
        if p.parent.name == "dsa-final-audit":
            continue
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        sidecar = p.with_suffix(".zip.sha256")
        with zipfile.ZipFile(p) as z:
            names = z.namelist()
            unsafe = [n for n in names if PurePosixPath(n).is_absolute() or ".." in PurePosixPath(n).parts]
            archives.append(dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size,
                                 sha256=digest, checksum_matches=sidecar.is_file() and sidecar.read_text().split()[0] == digest,
                                 crc_error=z.testzip(), entries=len(names), unsafe=unsafe,
                                 duplicate_entries=[n for n, count in Counter(names).items() if count > 1],
                                 nested_archives=[n for n in names if n.lower().endswith((".zip", ".tar", ".gz"))]))
    save("inventory.json", dict(counts=dict(categories=len(catalog["categories"]),
                                           memberships=sum(len(c["items"]) for c in catalog["categories"]),
                                           canonicals=len(catalog["algorithms"]), dsa_categories=len(categories),
                                           dsa_memberships=sum(len(c["items"]) for c in categories),
                                           dsa_canonicals=len(algorithms)),
                                categories=categories, algorithms=rows, structural_issues=issues,
                                imports=imports, artifact_hashes=hashes, historical_archives=archives))
    print(f"inventory: {len(categories)} DSA categories, {len(algorithms)} canonicals; {len(issues)} structural issues", flush=True)


def examples():
    # Older example scripts save results unconditionally. Execute their actual
    # commands in an isolated source copy so historical transcripts stay intact.
    names = ("backtracking", "divide_conquer", "dynamic_programming", "greedy",
             "graph_algorithms", "tree_algorithms", "string", "bit")
    jobs = [(name, ["scripts/verify_" + name + "_examples.py"]) for name in names]
    jobs += [(category, ["scripts/verify_number_window_examples.py", "--category", category])
             for category in ("number-theory", "two-pointers-sliding-window")]
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    with tempfile.TemporaryDirectory(prefix="atlas-audit-examples-") as temporary:
        exported = Path(temporary)
        for name in tracked:
            source = ROOT / name
            if not name or not source.is_file() or name.startswith("artifacts/"):
                continue
            target = exported / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        results = {}
        for label, command in jobs:
            record = run("examples-" + label, command, cwd=exported)
            results[label] = record
            save("examples-results.json", results)
            if record["returncode"] != 0:
                raise SystemExit(1)
        fresh = {p.relative_to(exported).as_posix(): json.loads(p.read_text())
                 for p in exported.glob("docs/*-evidence/examples-results.json")}
        save("examples-details.json", fresh)


def early_examples():
    """Execute the literal primary examples in all Sorting/Searching lessons."""
    catalog = yaml.safe_load((ROOT / "catalog.yaml").read_text())
    records = []
    with tempfile.TemporaryDirectory(prefix="atlas-audit-early-examples-") as temporary:
        for a in catalog["algorithms"]:
            if a["category"] not in ("A1", "A2"):
                continue
            folder = ROOT / a["canonical_location"]
            lesson = (folder / "README.md").read_text()
            section = re.search(r"^## 15\..*?(?=^## 16\.)", lesson, re.M | re.S).group()
            command = re.search(r"^printf (.+?) \| .*python[^\n]*", section, re.M).group(1)
            parts = shlex.split(command)
            payload = (parts[1] + "\n") if parts[0] == "%s\\n" else parts[0].replace("\\n", "\n")
            if a["category"] == "A2":
                expected = "1\n"
                assert "exactly `1`" in section
            else:
                block = re.search(r"```text\n(.*?)\n```", section, re.S)
                expected = block.group(1) + "\n" if block else re.search(r"^# (?:Output: )?([0-9 -]+)$", section, re.M).group(1) + "\n"
            for standard in ("python", "c++17", "c++20"):
                if standard == "python":
                    args = [sys.executable, str(folder / "python/solution.py")]
                else:
                    binary = Path(temporary) / (a["id"] + standard)
                    compiler = shlex.split(os.environ.get("CXX", "g++"))
                    compiled = subprocess.run([*compiler, "-std=" + standard, "-Wall", "-Wextra", "-pedantic",
                                               str(folder / "cpp/solution.cpp"), "-o", str(binary)],
                                              capture_output=True, text=True, timeout=60)
                    assert compiled.returncode == 0, compiled.stderr
                    args = [str(binary)]
                result = subprocess.run(args, input=payload, text=True, capture_output=True, timeout=10)
                assert result.returncode == 0 and not result.stderr and result.stdout == expected, (a["id"], standard, result)
                records.append(dict(algorithm=a["id"], language=standard, input=payload,
                                    expected=expected, actual=result.stdout, status="passed"))
    save("early-examples.json", records)
    print(f"{len(records)} primary Sorting/Searching example configurations passed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("inventory", "configuration", "independent", "examples", "early-examples", "sanitizers", "final"), required=True)
    args = parser.parse_args()
    if args.stage == "inventory":
        inventory()
        return
    if args.stage == "examples":
        examples()
        return
    if args.stage == "early-examples":
        early_examples()
        return
    if args.stage == "configuration":
        jobs = [("catalog", ["scripts/validate_catalog.py"]),
                ("generated", ["scripts/generate_catalog_docs.py", "--check"])]
    elif args.stage == "independent":
        jobs = [("independent", ["docs/reviews/dsa-final-audit/verify_independent.py"])]
    elif args.stage == "sanitizers":
        jobs = [("sanitizers", ["-m", "pytest", "dsa/tree-algorithms", "dsa/string-algorithms",
                               "dsa/graph-algorithms", "dsa/number-theory", "dsa/two-pointers-and-sliding-window",
                               "-m", "cpp", "--cpp-standard=c++20", "--require-cpp", "-q",
                               "--junitxml=" + str(EVIDENCE / "sanitizers.xml")])]
    else:
        jobs = [("final-full-suite", ["-m", "pytest", "--require-cpp", "-q",
                                      "--junitxml=" + str(EVIDENCE / "final-full-suite.xml")])]
    environment = os.environ.copy()
    environment["PYTHONHASHSEED"] = "0"
    if args.stage == "sanitizers":
        environment["CXX"] = "clang++ -fsanitize=address,undefined -fno-omit-frame-pointer -fno-sanitize-recover=all"
        # Apple ASan rejects detect_leaks=1 before main. LeakSanitizer is
        # separate coverage; do not describe ASan/UBSan as a leak audit.
        environment["ASAN_OPTIONS"] = ("detect_leaks=0:" if sys.platform == "darwin" else "") + "halt_on_error=1"
        environment["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
    results = {}
    for label, command in jobs:
        record = run(label, command, environment=environment)
        results[label] = record
        save(args.stage + "-results.json", results)
        if record["returncode"] != 0:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
