"""Execute all B10 examples and compare exact printed lesson output and contracts."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from validate_catalog import SECTIONS

ROOT=Path(__file__).resolve().parents[1]
TOPICS=('batch-gradient-descent', 'stochastic-gradient-descent', 'mini-batch-gradient-descent', 'momentum', 'rmsprop', 'adam', 'adamw', 'l-bfgs', 'genetic-algorithms', 'simulated-annealing')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only',action='store_true');args=parser.parse_args()
    records=[]
    for topic in TOPICS:
        base='machine-learning/optimization/'+topic
        command=[sys.executable,base+'/python/example.py']
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=15)
        assert result.returncode==0,(topic,result.stderr)
        article=(ROOT/base/'README.md').read_text()
        assert re.findall(r'^## (.+)$',article,re.M)==[f'{i}. {v}' for i,v in enumerate(SECTIONS,1)]
        assert result.stdout.strip() in article,topic+' printed output drift'
        output=json.loads(result.stdout)
        assert isinstance(output['objective'],(int,float)) and isinstance(output['converged'],bool)
        if topic=='adamw':assert not output['converged'] and output['status']=='iteration-budget'
        elif topic in ('genetic-algorithms','simulated-annealing'):assert output['objective']==0 and output['status']=='target-reached'
        else:assert output['converged'] and output['status']=='gradient-tolerance'
        records.append(dict(topic=topic,command=['python',base+'/python/example.py'],returncode=result.returncode,output=result.stdout,sections=25))
    if not args.check_only:(ROOT/'docs/optimization-evidence/examples-results.json').write_text(json.dumps(records,indent=2)+'\n')
    print('10 executed examples and exact25-section lessons passed')


if __name__=='__main__':main()
