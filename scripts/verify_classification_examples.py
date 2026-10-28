"""Check authored examples and JSON CLIs against independent known labels."""
import argparse
import ast
import json
from pathlib import Path
import subprocess
import sys

import yaml

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"machine-learning/supervised-learning/classification"
CASES={
"logistic-regression":dict(X=[[-2],[-1],[1],[2]],y=["cold","cold","warm","warm"],predict=[[-3],[3]],parameters=dict(alpha=.1),expected=["cold","warm"]),
"k-nearest-neighbors":dict(X=[[-1],[1],[1],[3]],y=["z","a","b","a"],predict=[[1]],parameters=dict(n_neighbors=2),expected=["a"]),
"gaussian-naive-bayes":dict(X=[[0],[1],[5],[6]],y=["a","a","b","b"],predict=[[0],[6]],expected=["a","b"]),
"multinomial-naive-bayes":dict(X=[[3,0],[2,1],[0,3],[1,2]],y=["left","left","right","right"],predict=[[2,0],[0,2]],expected=["left","right"]),
"bernoulli-naive-bayes":dict(X=[[1,0],[1,0],[0,1],[0,1]],y=["a","a","b","b"],predict=[[1,0],[0,1]],expected=["a","b"]),
"support-vector-machines":dict(X=[[-2],[-1],[1],[2]],y=[-1,-1,1,1],predict=[[-3],[3]],expected=[-1,1]),
"cart-decision-trees":dict(X=[[0],[1],[2],[3]],y=["a","a","b","b"],predict=[[.5],[2.5]],parameters=dict(max_depth=1),expected=["a","b"]),
"id3-decision-trees":dict(X=[[0,0],[0,1],[1,0],[1,1]],y=["no","no","yes","yes"],predict=[[0,1],[1,0]],expected=["no","yes"]),
"c4-5-decision-trees":dict(X=[[0,0],[0,1],[1,2],[1,3]],y=["no","no","yes","yes"],predict=[[0,99],[1,-1],[2,2]],parameters=dict(categorical_features=[0]),expected=["no","yes","no"]),
"linear-discriminant-analysis":dict(X=[[-2],[-1],[1],[2]],y=["left","left","right","right"],predict=[[-3],[3]],expected=["left","right"]),
"quadratic-discriminant-analysis":dict(X=[[-2],[-1],[1],[2]],y=["left","left","right","right"],predict=[[-3],[3]],expected=["left","right"]),
}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--check-only",action="store_true");args=parser.parse_args()
    catalog=yaml.safe_load((ROOT/"catalog.yaml").read_text())
    names=[a["id"] for a in catalog["algorithms"] if a["category"]=="B2" and a["test_status"] in ("tested","reviewed")]
    records=[]
    for name in names:
        case=CASES[name].copy();expected=case.pop("expected")
        for kind,filename,data in (("example","example.py",None),("JSON CLI","solution.py",json.dumps(case))):
            result=subprocess.run([sys.executable,str(BASE/name/"python"/filename)],input=data,capture_output=True,text=True,timeout=60,check=True)
            assert not result.stderr,result.stderr
            observed=json.loads(result.stdout)["predictions"] if kind=="JSON CLI" else ast.literal_eval(result.stdout)
            assert observed==expected,(name,observed,expected)
            records.append(dict(algorithm=name,kind=kind,expected=expected,observed=observed,status="passed"))
        bad=subprocess.run([sys.executable,str(BASE/name/"python/solution.py")],input='{"X":[[1]],"y":[0,1],"predict":[[1]]}',capture_output=True,text=True,timeout=60)
        assert bad.returncode==2 and not bad.stdout and bad.stderr.startswith("error:"),name
        records.append(dict(algorithm=name,kind="invalid-shape CLI",returncode=2,status="passed"))
    if not args.check_only:
        folder=ROOT/"docs/classification-evidence";n=len(list(folder.glob("examples-attempt*.json")))+1
        (folder/f"examples-attempt{n}.json").write_text(json.dumps(records,indent=2)+"\n")
    print(f"{len(names)} lessons: {2*len(names)} example/CLI predictions and {len(names)} invalid-input CLIs passed")


if __name__=="__main__":main()
