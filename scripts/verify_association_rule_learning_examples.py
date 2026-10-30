"""Run each B6 worked example/CLI and independently verify counts and rule numbers."""
import argparse
from fractions import Fraction
from itertools import combinations
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT/'docs/association-rule-learning-evidence'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--topics', nargs='+')
    parser.add_argument('--rules', action='store_true')
    args = parser.parse_args()
    items = json.loads((EVIDENCE/'example-inputs.json').read_text())
    env = os.environ.copy(); env.update(PYTHONHASHSEED='0',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    expected = [(('a',),4),(('b',),4),(('c',),4),(('a','b'),3),(('a','c'),3),(('b','c'),3),(('a','b','c'),2)]
    records = []
    for name,item in items.items():
        if args.topics and name not in args.topics:
            continue
        folder = ROOT/item['canonical_location'];payload = item['payload'];runs=[]
        for script,stdin in [('example.py',None),('solution.py',json.dumps(payload))]:
            run = subprocess.run([sys.executable,str(folder/'python'/script)],input=stdin,text=True,capture_output=True,timeout=60,cwd=ROOT,env=env)
            assert run.returncode == 0,(name,run.stderr)
            runs.append(json.loads(run.stdout))
        assert runs[0] == runs[1]
        assert runs[0]['n_transactions'] == 5 and runs[0]['min_count'] == 2
        assert [(tuple(x['items']),x['support_count']) for x in runs[0]['itemsets']] == expected
        invalid = subprocess.run([sys.executable,str(folder/'python/solution.py')],input=json.dumps(dict(payload,transactions='abc')),text=True,capture_output=True,timeout=60,cwd=ROOT,env=env)
        assert invalid.returncode == 2 and invalid.stderr and not invalid.stdout
        record = dict(id=name,example='passed',equivalent_cli='passed',invalid_cli='passed',output=runs[0])
        if args.rules:
            run = subprocess.run([sys.executable,str(folder/'python/solution.py')],input=json.dumps(dict(payload,min_confidence=.6)),text=True,capture_output=True,timeout=60,cwd=ROOT,env=env)
            assert run.returncode == 0,run.stderr
            output = json.loads(run.stdout);rules=output['rules'];assert len(rules) == 9
            rows = list(map(set,payload['transactions']))
            observed = {}
            for rule in rules:
                A,B=set(rule['antecedent']),set(rule['consequent'])
                assert A and B and not A&B
                union=sum(A|B<=row for row in rows);a=sum(A<=row for row in rows);b=sum(B<=row for row in rows)
                assert rule['support_count']==union
                for field,value in [('support',Fraction(union,5)),('confidence',Fraction(union,a)),('lift',Fraction(5*union,a*b))]:
                    assert abs(rule[field]-float(value))<1e-14
                observed[tuple(sorted(A)),tuple(sorted(B))]=rule
            assert observed[('a',),('b',)]['lift'] == float(Fraction(15,16))
            assert observed[('a','b'),('c',)]['confidence'] == float(Fraction(2,3))
            record.update(rule_cli='passed',rule_output=rules)
        records.append(record)
    assert records
    if not args.check_only:
        suffix = '' if args.topics is None else '-'+('-'.join(args.topics))
        (EVIDENCE/('examples-results'+suffix+'.json')).write_text(json.dumps(records,indent=2)+'\n')
    print(f'{len(records)} examples + equivalent/invalid CLIs passed; rule CLIs: {len(records) if args.rules else 0}')


if __name__ == '__main__':
    main()
