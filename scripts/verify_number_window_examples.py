"""Run actual Number Theory/window lesson input and JSON output in all three configurations."""
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import argparse
import yaml

ROOT=Path(__file__).resolve().parents[1]


def execute(command,data):
    result=subprocess.run(command,input=data,text=True,capture_output=True,timeout=30,cwd=ROOT)
    assert result.returncode==0 and not result.stderr,result.stderr
    return json.loads(result.stdout)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--category",choices=("number-theory","two-pointers-sliding-window"),required=True)
    args=parser.parse_args()
    category_id="A9" if args.category=="number-theory" else "A10"
    catalog=yaml.safe_load((ROOT/"catalog.yaml").read_text())
    names=[r["id"] for r in catalog["algorithms"] if r["category"]==category_id]
    category_folder="number-theory" if category_id=="A9" else "two-pointers-and-sliding-window"
    compiler=shlex.split(os.environ.get("CXX",shutil.which("g++") or shutil.which("clang++") or ""))
    assert compiler,"C++ compiler required"
    records={}
    with tempfile.TemporaryDirectory(prefix="atlas-number-window-examples-") as directory:
        for batch in [names]:
            for name in batch:
                folder=ROOT/"dsa"/category_folder/name
                lesson=(folder/"README.md").read_text()
                data=re.search(r"printf '%s\\n' '([^']*)'",lesson).group(1)+"\n"
                expected=json.loads(re.search(r"```json\n(.*?)\n```",lesson,re.S).group(1))
                observed={"python":execute([sys.executable,str(folder/"python/solution.py")],data)}
                for standard in ("c++17","c++20"):
                    binary=Path(directory)/name
                    result=subprocess.run([*compiler,"-std="+standard,"-Wall","-Wextra","-pedantic",
                                           str(folder/"cpp/solution.cpp"),"-o",str(binary)],
                                          capture_output=True,text=True,timeout=60)
                    assert result.returncode==0,result.stderr
                    observed[standard]=execute([str(binary)],data)
                assert all(value==expected for value in observed.values()),name
                records[name]=dict(input=data.strip(),expected=expected,observed=observed,status="passed")
    (ROOT/f"docs/{args.category}-evidence/examples-results.json").write_text(json.dumps(records,indent=2)+"\n")
    print(f"{len(names)} lessons, {len(names)*3} executable example configurations passed")


if __name__=="__main__":main()
