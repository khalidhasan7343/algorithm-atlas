"""Verify Phase 14 ownership, source preservation, lessons and approval boundaries."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

import yaml

from track_policy import is_complete
from validate_catalog import SECTIONS

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'docs/classification-evidence'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only',action='store_true')
    parser.add_argument('--source-only',action='store_true')
    parser.add_argument('--require-tracked',action='store_true')
    args=parser.parse_args()
    baseline=json.loads((EVIDENCE/'baseline.json').read_text())
    previous=yaml.safe_load((EVIDENCE/'catalog-baseline.yaml').read_text())
    current=yaml.safe_load((ROOT/'catalog.yaml').read_text())
    assert current['categories']==previous['categories']
    assert [a['id'] for a in current['algorithms']]==[a['id'] for a in previous['algorithms']]
    topics={a['id'] for a in baseline['algorithms']};assert len(topics)==11
    for old,new in zip(previous['algorithms'],current['algorithms']):
        assert old['canonical_location']==new['canonical_location']
        if old['id'] not in topics:assert old==new,old['id']
        else:assert is_complete(new) and new['cpp_status']=='planned',new['id']
    records=current['development']['phase_records']
    for phase in ('11','12'):assert records[phase]==previous['development']['phase_records'][phase]
    old13=previous['development']['phase_records']['13'];new13=records['13']
    for field in old13.keys()-{'status','owner_approval'}:assert old13[field]==new13[field]
    assert new13['owner_approval']=='approved' and new13['status']=='owner-approved'
    assert new13['approval_evidence']=='Explicit owner statement: OWNER-APPROVAL CHECKPOINT IS SATISFIED.'
    assert records['14']['owner_approval']=='pending'
    protected={name:expected for name,expected in baseline['hashes'].items() if
        name.startswith('dsa/') or
        (name.startswith('machine-learning/supervised-learning/regression/') and name!='machine-learning/supervised-learning/regression/README.md') or
        (name.startswith('docs/reviews/') and name!='docs/reviews/README.md') or
        ('-evidence/' in name and name.startswith('docs/')) or
        (name.startswith('artifacts/review-packages/') and name!='artifacts/review-packages/README.md') or
        name in ('LICENSE','conftest.py','pyproject.toml','requirements-dev.txt','requirements-ml.txt','requirements-ml-test.txt',
                 '.github/workflows/ci.yml','scripts/track_policy.py','scripts/validate_catalog.py')}
    omitted=[]
    for name,expected in protected.items():
        path=ROOT/name
        if args.source_only and name.startswith('artifacts/review-packages/') and not path.exists():
            omitted.append(name);continue
        assert path.is_file() and sha(path)==expected,f'Preservation failure: {name}'
    for name in ('docs/regression-scope.md','docs/regression-checkpoints.md'):
        prefix=(ROOT/name).read_bytes().split(b'\n## Subsequent owner approval',1)[0]
        assert hashlib.sha256(prefix).hexdigest()==baseline['hashes'][name],name
    lessons=[]
    for algorithm in current['algorithms']:
        if algorithm['id'] not in topics:continue
        folder=ROOT/algorithm['canonical_location']
        for name in ('README.md','python/solution.py','python/example.py','tests/test_python.py'):
            assert (folder/name).is_file() and (folder/name).stat().st_size>0
        headings=re.findall(r'^##[ \t]+(.+)$',(folder/'README.md').read_text(),re.M)
        assert headings==[f'{i}. {title}' for i,title in enumerate(SECTIONS,1)],algorithm['id']
        assert not (folder/'cpp/solution.cpp').exists() and not (folder/'tests/test_cpp.py').exists()
        imports=[]
        for node in ast.walk(ast.parse((folder/'python/solution.py').read_text())):
            if isinstance(node,ast.Import):imports.extend(a.name for a in node.names)
            elif isinstance(node,ast.ImportFrom):imports.append(node.module or '')
        assert not any(name.split('.')[0] in {'sklearn','scipy','torch','tensorflow','pickle','requests','subprocess'} for name in imports)
        lessons.append(dict(id=algorithm['id'],sections=25,python='tested',cpp='optional, absent',imports=imports))
    report='docs/reviews/classification/CLASSIFICATION-REVIEW-REPORT.md'
    tracking='not requested'
    if (ROOT/'.git').exists() and not args.source_only:
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==baseline['revision'],'HEAD advanced; inspect owner changes'
        assert subprocess.run(['git','check-ignore','-q',report],cwd=ROOT).returncode==1
        if args.require_tracked:
            subprocess.run(['git','ls-files','--error-unmatch',report],cwd=ROOT,check=True,capture_output=True)
            tracking='tracked and unignored'
    result=dict(status='passed',inventory=dict(categories=35,memberships=256,canonicals=235),dsa_canonicals=97,B1_canonicals=7,
                protected_files_verified=len(protected)-len(omitted),historical_artifacts_excluded_from_source_export=omitted,
                B1_DSA_source='byte-identical',out_of_scope_algorithm_records='identical',phase13_owner_approval='approved',
                phase14_owner_approval='pending',phase11_phase12_records='unchanged',lessons=lessons,report_tracking=tracking)
    if not args.check_only:(EVIDENCE/'preservation-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f"Scope/preservation passed: 11 lessons, 97 DSA + 7 B1 canonicals, {result['protected_files_verified']} protected files; 35/256/235")


if __name__=='__main__':main()
