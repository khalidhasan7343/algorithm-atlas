"""Execute the four documented CLI examples in Python and C++20 exactly."""
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
    "activity-selection": ("5 1 3 2 5 3 4 4 7 5 6\n", "[0,2,4]"),
    "fractional-knapsack": ("50 3 10 60 20 100 30 120\n", '{"value":[240,1],"fractions":[[1,1],[1,1],[2,3]]}'),
    "huffman-coding": ("3 65 5 66 2 67 1 4 65 66 67 65\n", '{"codes":[[65,"1"],[66,"01"],[67,"00"]],"bits":"101001","decoded":[65,66,67,65],"cost":11}'),
    "job-sequencing-with-deadlines": ("5 2 100 1 19 2 27 1 25 3 15\n", '{"profit":142,"slots":[2,0,4]}'),
}


def main():
    compiler = shlex.split(os.environ.get("CXX", "")) or [shutil.which("g++") or shutil.which("clang++")]
    assert compiler[0], "a C++ compiler is required"
    records = []
    with tempfile.TemporaryDirectory(prefix="atlas-greedy-examples-") as temporary:
        for name, (text, expected) in EXAMPLES.items():
            folder = ROOT / "dsa/greedy" / name
            assert "\n"+expected+"\n" in (folder / "README.md").read_text()
            executable = Path(temporary) / name
            compiled = subprocess.run([*compiler,"-std=c++20","-Wall","-Wextra","-pedantic",str(folder/"cpp/solution.cpp"),"-o",str(executable)], capture_output=True,text=True,timeout=60)
            assert compiled.returncode == 0, compiled.stderr
            for language, command in (("python",[sys.executable,str(folder/"python/solution.py")]),("cpp20",[str(executable)])):
                result = subprocess.run(command,input=text,capture_output=True,text=True,timeout=10)
                assert result.returncode == 0 and result.stdout == expected+"\n" and not result.stderr, (name,language,result)
                records.append({"topic":name,"language":language,"input":text,"expected":expected,"returncode":result.returncode,"stdout":result.stdout})
    (ROOT/"docs/greedy-evidence/examples-results.json").write_text(json.dumps(records,indent=2)+"\n")
    print(f"{len(records)}/8 documented examples matched exact output")


if __name__ == "__main__":
    main()
