"""Run the actual lesson hex input/JSON output in Python, C++17 and C++20."""
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from validate_catalog import STRING_BATCHES

ROOT=Path(__file__).resolve().parents[1]


def execute(command,data):
    result=subprocess.run(command,input=data,text=True,capture_output=True,timeout=30,cwd=ROOT)
    assert result.returncode==0 and not result.stderr,result.stderr
    return json.loads(result.stdout)


def main():
    compiler=shlex.split(os.environ.get("CXX",shutil.which("g++") or shutil.which("clang++") or ""))
    assert compiler,"C++ compiler required"
    records={}
    with tempfile.TemporaryDirectory(prefix="atlas-string-examples-") as directory:
        for batch in STRING_BATCHES:
            for name in batch:
                folder=ROOT/"dsa/string-algorithms"/name
                lesson=(folder/"README.md").read_text()
                data=re.search(r"printf '([^']+)\\n'",lesson).group(1)+"\n"
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
                records[name]=dict(hex_input=data.strip(),expected=expected,observed=observed,status="passed")
    (ROOT/"docs/string-algorithms-evidence/examples-results.json").write_text(json.dumps(records,indent=2)+"\n")
    print("9 lessons, 27 executable example configurations passed")


if __name__=="__main__":main()
