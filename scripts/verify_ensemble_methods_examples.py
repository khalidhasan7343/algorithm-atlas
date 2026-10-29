"""Execute B3 examples and equivalent JSON CLIs, checking independent fixed outputs."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'docs/ensemble-methods-evidence'
EXPECTED={'bagging':['cold','warm'],'random-forest':['cold','warm'],'adaboost':['cold','warm'],
          'gradient-boosting-machine':[.25,3.75],'xgboost':[1.5,2.5],'catboost':[0.,4.],
          'voting-classifiers':['cold','warm'],'stacking':[146/173,562/173]}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check-only',action='store_true');args=parser.parse_args()
    inputs=json.loads((EVIDENCE/'example-inputs.json').read_text());records=[]
    for name,entry in inputs.items():
        folder='machine-learning/ensemble-methods/'+name+'/python/'
        for script,payload in (('example.py',None),('solution.py',json.dumps(entry['payload']))):
            result=subprocess.run([sys.executable,folder+script],input=payload,cwd=ROOT,capture_output=True,text=True,timeout=60)
            assert result.returncode==0,result.stderr
            actual=json.loads(result.stdout)['predictions'];expected=EXPECTED[name]
            if isinstance(expected[0],str):assert actual==expected,(name,actual,expected)
            else:np.testing.assert_allclose(actual,expected,atol=1e-12,rtol=1e-12,err_msg=name)
            records.append(dict(topic=name,command=['python',folder+script],returncode=0,output=result.stdout.strip()))
        bad=dict(entry['payload']);bad['y']=bad['y'][:-1]
        result=subprocess.run([sys.executable,folder+'solution.py'],input=json.dumps(bad),cwd=ROOT,capture_output=True,text=True,timeout=60)
        assert result.returncode==2 and not result.stdout and 'error:' in result.stderr
    if not args.check_only:(EVIDENCE/'examples-results.json').write_text(json.dumps(dict(status='passed',executions=16,invalid_cli_checks=8,records=records),indent=2)+'\n')
    print('8 lessons; 16 example/CLI executions and 8 invalid-input CLI checks passed')


if __name__=='__main__':main()
