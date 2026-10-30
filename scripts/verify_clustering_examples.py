"""Execute independent fixed B4 example labels and equivalent JSON CLIs."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'docs/clustering-evidence'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only',action='store_true')
    parser.add_argument('--topics',nargs='*')
    args=parser.parse_args()
    entries=json.loads((EVIDENCE/'example-inputs.json').read_text())
    names=args.topics if args.topics else list(entries)
    records=[]
    for name in names:
        item=entries[name];folder='machine-learning/unsupervised-learning/clustering/'+name+'/python/'
        for script,payload in (('example.py',None),('solution.py',json.dumps(item['payload']))):
            result=subprocess.run([sys.executable,folder+script],input=payload,cwd=ROOT,capture_output=True,text=True,timeout=60)
            assert result.returncode==0,result.stderr
            assert json.loads(result.stdout)['labels']==item['expected_labels'],(name,result.stdout,item['expected_labels'])
            records.append(dict(topic=name,command=['python',folder+script],returncode=0,output=result.stdout.strip()))
        bad=dict(item['payload']);bad['X']=[]
        result=subprocess.run([sys.executable,folder+'solution.py'],input=json.dumps(bad),cwd=ROOT,capture_output=True,text=True,timeout=60)
        assert result.returncode==2 and not result.stdout and 'error:' in result.stderr
    if not args.check_only:
        suffix='examples-results.json' if not args.topics else 'examples-'+'--'.join(names)+'-results.json'
        (EVIDENCE/suffix).write_text(json.dumps(dict(status='passed',topics=names,executions=2*len(names),invalid_cli_checks=len(names),records=records),indent=2)+'\n')
    print(f'{len(names)} lessons; {2*len(names)} example/CLI executions and {len(names)} invalid-input CLI checks passed')


if __name__=='__main__':main()
