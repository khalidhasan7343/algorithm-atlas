"""Execute B5 worked examples and equivalent CLIs; independently verify key invariants."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'docs/dimensionality-reduction-evidence'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only',action='store_true')
    parser.add_argument('--topics',nargs='+')
    args=parser.parse_args();records=[]
    env=os.environ.copy();env.update(PYTHONHASHSEED='0',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    for item in json.loads((EVIDENCE/'example-inputs.json').read_text()):
        if args.topics and item['id'] not in args.topics:continue
        folder=ROOT/item['canonical_location'];payload=item['payload'];result=[]
        for source,stdin in [('example.py',None),('solution.py',json.dumps(payload))]:
            run=subprocess.run([sys.executable,str(folder/'python'/source)],input=stdin,text=True,capture_output=True,timeout=60,env=env,cwd=ROOT)
            assert run.returncode==0,(item['id'],run.stderr)
            result.append(json.loads(run.stdout))
        assert result[0]==result[1],item['id']
        Z=np.array(result[0]['embedding']);X=np.array(payload['X'])
        k=payload['parameters'].get('n_components',payload['parameters'].get('latent_dim',2))
        assert Z.shape==(len(X),k) and np.isfinite(Z).all()
        if item['id']=='principal-component-analysis':np.testing.assert_allclose(Z.ravel(),[-2,0,2,0])
        if item['id']=='singular-value-decomposition':np.testing.assert_allclose(Z,[[3,0],[0,0],[0,2]])
        if item['id']=='linear-discriminant-analysis-projection':assert np.ptp(Z[:2])==0 and np.ptp(Z[2:])==0 and Z[2]>Z[0]
        if item['id']=='independent-component-analysis':np.testing.assert_allclose(Z.T@Z/len(Z),np.eye(k),atol=1e-10)
        invalid=subprocess.run([sys.executable,str(folder/'python/solution.py')],input=json.dumps(dict(payload,X=[])),text=True,capture_output=True,timeout=60,cwd=ROOT,env=env)
        assert invalid.returncode==2 and invalid.stderr and not invalid.stdout,item['id']
        records.append(dict(id=item['id'],example='passed',equivalent_cli='passed',invalid_cli='passed',output=result[0]))
    assert records
    if not args.check_only:
        suffix='' if args.topics is None else '-'+('-'.join(args.topics))
        (EVIDENCE/('examples-results'+suffix+'.json')).write_text(json.dumps(records,indent=2)+'\n')
    print(f'{len(records)} examples + {len(records)} equivalent CLIs + {len(records)} invalid CLIs passed')

if __name__=='__main__':main()
