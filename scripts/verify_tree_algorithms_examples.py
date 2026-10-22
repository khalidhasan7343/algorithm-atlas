"""Execute all fourteen documented CLI examples in Python and C++20 exactly."""
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = json.loads((ROOT/'docs/tree-algorithms-evidence/lesson-examples.json').read_text())


def main():
    compiler = shlex.split(os.environ.get("CXX", "")) or [shutil.which("g++") or shutil.which("clang++")]
    assert compiler[0], "a C++ compiler is required"
    records = []
    with tempfile.TemporaryDirectory(prefix="atlas-tree-examples-") as temporary:
        for name, example in EXAMPLES.items():
            text=example["cpp_input"]
            expected=json.dumps(example["output"],separators=(",",":"))
            folder = ROOT / "dsa/tree-algorithms" / name
            assert "\n"+expected+"\n" in (folder / "README.md").read_text()
            executable = Path(temporary) / name
            compiled = subprocess.run([*compiler,"-std=c++20","-Wall","-Wextra","-pedantic",str(folder/"cpp/solution.cpp"),"-o",str(executable)], capture_output=True,text=True,timeout=60)
            assert compiled.returncode == 0, compiled.stderr
            for language, command in (("python",[sys.executable,str(folder/"python/solution.py")]),("cpp20",[str(executable)])):
                result = subprocess.run(command,input=(json.dumps(example["input"]) if language=="python" else text),capture_output=True,text=True,timeout=10)
                assert result.returncode == 0 and result.stdout == expected+"\n" and not result.stderr, (name,language,result)
                records.append({"topic":name,"language":language,"input":text,"expected":expected,"returncode":result.returncode,"stdout":result.stdout})
    (ROOT/"docs/tree-algorithms-evidence/examples-results.json").write_text(json.dumps(records,indent=2)+"\n")
    print(f"{len(records)}/28 documented examples matched exact output")


if __name__ == "__main__":
    main()
