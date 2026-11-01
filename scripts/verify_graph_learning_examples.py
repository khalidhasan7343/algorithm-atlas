"""Execute all B9 examples and compare exact printed lesson output and contracts."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from validate_catalog import SECTIONS

ROOT=Path(__file__).resolve().parents[1]
TOPICS=('pagerank','node2vec','graph-convolutional-networks')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only',action='store_true');args=parser.parse_args()
    records=[]
    for topic in TOPICS:
        base='machine-learning/graph-learning/'+topic
        command=[sys.executable,base+'/python/example.py']
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=15)
        assert result.returncode==0,(topic,result.stderr)
        article=(ROOT/base/'README.md').read_text()
        assert re.findall(r'^## (.+)$',article,re.M)==[f'{i}. {v}' for i,v in enumerate(SECTIONS,1)]
        assert result.stdout.strip() in article,topic+' printed output drift'
        output=json.loads(result.stdout)
        if topic=='pagerank':assert output['converged'] and output['sum']==1.
        elif topic=='node2vec':assert output['shape']==[6,4] and output['loss_final']<output['loss_initial'] and output['updates']==100
        else:assert output['predictions']==[0,0,0,1,1,1] and output['loss_final']<output['loss_initial'] and output['updates']==200
        records.append(dict(topic=topic,command=['python',base+'/python/example.py'],returncode=result.returncode,output=result.stdout,sections=25))
    if not args.check_only:(ROOT/'docs/graph-learning-evidence/examples-results.json').write_text(json.dumps(records,indent=2)+'\n')
    print('3 executed examples and exact25-section lessons passed')


if __name__=='__main__':main()
