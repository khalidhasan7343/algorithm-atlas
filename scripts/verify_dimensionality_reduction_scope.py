"""Verify exact Phase 17 B5 scope and preserve all pre-existing approved work."""
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
EVIDENCE=ROOT/'docs/dimensionality-reduction-evidence'
REPORT='docs/reviews/dimensionality-reduction/DIMENSIONALITY-REDUCTION-REVIEW-REPORT.md'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only',action='store_true')
    parser.add_argument('--source-only',action='store_true')
    args=parser.parse_args()
    baseline=json.loads((EVIDENCE/'baseline.json').read_text())
    old=yaml.safe_load((EVIDENCE/'catalog-baseline.yaml').read_text())
    current=yaml.safe_load((ROOT/'catalog.yaml').read_text())
    assert current['categories']==old['categories']
    assert [a['id'] for a in current['algorithms']]==[a['id'] for a in old['algorithms']]
    ids={a['id'] for a in baseline['algorithms']}
    assert len(ids)==7
    for previous,now in zip(old['algorithms'],current['algorithms']):
        if previous['id'] not in ids:
            assert previous==now,previous['id']
        else:
            for key in previous.keys()-{'notes','documentation_status','python_status','test_status'}:
                assert previous[key]==now[key],(previous['id'],key)
            assert is_complete(now) and now['cpp_status']=='planned'
    state=current['development']
    assert state['phase_number']==17 and state['category']=='B5'
    assert state['phase_records']['16']['owner_approval']=='approved'
    assert state['current_review']['owner_approval']==state['phase_records']['17']['owner_approval']=='pending'
    allowed={'AGENTS.md','CONTRIBUTING.md','README.md','catalog.yaml',
             'docs/algorithm-index.md','docs/progress.md','docs/development.md','docs/ml-development.md',
             'docs/learning-roadmap.md','docs/getting-started.md','docs/glossary.md',
             'docs/reviews/README.md','artifacts/review-packages/README.md','scripts/generate_catalog_docs.py',
             'scripts/track_policy.py','scripts/validate_catalog.py'}
    allowed.update(c['path']+'/README.md' for c in current['categories'])
    allowed.update(a['canonical_location']+'/README.md' for a in current['algorithms'] if a['id'] in ids)
    checked=0;omitted=[]
    for name,expected in baseline['hashes'].items():
        if name in allowed:
            continue
        path=ROOT/name
        if args.source_only and name.startswith('artifacts/review-packages/') and not path.exists():
            omitted.append(name)
            continue
        assert path.is_file() and sha(path.read_bytes())==expected,'Unapproved pre-existing change: '+name
        checked+=1
    lessons=[]
    forbidden={'sklearn','scipy','hdbscan','pickle','subprocess','requests','torch','tensorflow'}
    core_paths=[]
    for algorithm in current['algorithms']:
        if algorithm['id'] not in ids:
            continue
        folder=ROOT/algorithm['canonical_location']
        headings=re.findall(r'^##[ \t]+(.+)$',(folder/'README.md').read_text(),re.M)
        assert headings==[f'{i}. {title}' for i,title in enumerate(SECTIONS,1)],algorithm['id']
        for part in ('python/solution.py','python/example.py','tests/test_python.py'):
            source=folder/part
            assert source.is_file() and source.stat().st_size>0
        core_paths.append(folder/'python/solution.py')
        assert not (folder/'cpp/solution.cpp').exists() and not (folder/'tests/test_cpp.py').exists()
        lessons.append(dict(id=algorithm['id'],sections=25,python='from scratch',cpp='optional, absent'))
    core_paths.extend(ROOT/'machine-learning/unsupervised-learning/dimensionality-reduction'/name for name in ('support.py',))
    for source in core_paths:
        for node in ast.walk(ast.parse(source.read_text())):
            names=[]
            if isinstance(node,ast.Import):names=[v.name for v in node.names]
            elif isinstance(node,ast.ImportFrom):names=[node.module or '']
            assert not any(v.split('.')[0] in forbidden for v in names),source
    tracking='not checked in source export'
    if (ROOT/'.git').exists() and not args.source_only:
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==baseline['revision']
        staged=subprocess.check_output(['git','diff','--cached','--binary'],cwd=ROOT)
        names=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT,text=True).splitlines()
        assert sha(staged)==baseline['staged_diff_sha256'] or names==[REPORT],'Unrelated staged changes'
        tracked=subprocess.run(['git','ls-files','--error-unmatch',REPORT],cwd=ROOT,capture_output=True).returncode==0
        unignored=subprocess.run(['git','check-ignore','-q',REPORT],cwd=ROOT).returncode==1
        tracking='tracked and unignored' if tracked and unignored else 'awaiting report staging; no force-add permitted'
    result=dict(status='passed',inventory=baseline['counts'],B5_canonical_members=7,implemented=7,
                protected_preexisting_files=checked,historical_artifacts_omitted_from_export=omitted,lessons=lessons,
                B1_B2_B3_B4_DSA_preservation='all approved implementations/tests/lessons/reports/evidence/packages byte-identical',
                phase16_owner_approval='approved',phase17_owner_approval='pending',report_tracking=tracking,
                core_external_estimator_imports='none',language_policy='DSA Python/C++ mandatory; ML Python mandatory, C++ optional')
    if not args.check_only:
        (EVIDENCE/'preservation-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'Phase 17 scope passed: 7 B5 canonical members; {checked} protected pre-existing files byte-identical; {tracking}')


if __name__=='__main__':
    main()
