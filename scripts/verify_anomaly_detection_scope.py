"""Phase24 identity, approval, dependency and byte-preservation audit."""
import argparse
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

import yaml

from package_bit_manipulation_review import excluded
from track_policy import is_complete
from validate_catalog import SECTIONS

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'docs/anomaly-detection-evidence'
REPORT='docs/reviews/anomaly-detection/ANOMALY-DETECTION-REVIEW-REPORT.md'
TOPICS=('isolation-forest','one-class-svm','local-outlier-factor')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify(source_only=False,require_tracked=False):
    baseline=json.loads((EVIDENCE/'baseline.json').read_text())
    old=yaml.safe_load((EVIDENCE/'catalog-baseline.yaml').read_text())
    current=yaml.safe_load((ROOT/'catalog.yaml').read_text())
    assert current.keys()==old.keys() and current['schema_version']==old['schema_version'] and current['project']==old['project']
    assert current['categories']==old['categories']
    assert [a['id'] for a in current['algorithms']]==[a['id'] for a in old['algorithms']]
    assert len(current['categories'])==35 and len(current['algorithms'])==235
    assert sum(len(c['items']) for c in current['categories'])==256
    b12=[a for a in current['algorithms'] if a['category']=='B12']
    assert tuple(a['id'] for a in b12)==TOPICS
    for before,now in zip(old['algorithms'],current['algorithms']):
        if before['category']!='B12':
            assert before==now,'Unapproved canonical record mutation: '+before['id']
        else:
            assert is_complete(now) and now['cpp_status']=='planned'
            for key in before.keys()-{'notes','documentation_status','python_status','test_status'}:
                assert before[key]==now[key],(before['id'],key)
    state=current['development'];previous=old['development']
    assert state['phase_number']==24 and state['category']=='B12' and state['track']=='machine-learning'
    assert state['status']=='awaiting-review' and state['active_batch'] is None
    assert state['batch_plan']==[['isolation-forest'],['one-class-svm'],['local-outlier-factor']] and state['completed_batches']==[1,2,3]
    assert state['completion_report']==REPORT
    assert state['phase_records']['20']['owner_approval']=='approved'
    assert state['phase_records']['20']['full_catalog_completion'] is False
    assert state['phase_records']['24']['owner_approval']==state['current_review']['owner_approval']=='pending'
    assert state['phase_records']['23']['owner_approval']=='approved'
    for key,record in previous['phase_records'].items():
        if key!='23':assert state['phase_records'][key]==record,key
    assert state['dpo_specification_decision']==previous['dpo_specification_decision']
    assert state['blocker_reviews']==previous['blocker_reviews']
    dpo=next(a for a in current['algorithms'] if a['id']=='dynamic-policy-optimization')
    assert not is_complete(dpo) and all(dpo[k]=='blocked' for k in ('documentation_status','python_status','cpp_status','test_status'))
    assert not (ROOT/dpo['canonical_location']/'python').exists()
    assert not (ROOT/dpo['canonical_location']/'tests').exists()
    approval=json.loads((EVIDENCE/'approval-evidence.json').read_text())
    assert approval['phase23_owner_approval']=='approved' and approval['phase24_owner_approval']=='pending'
    assert state['phase_records']['23']['approved_package_sha256']==approval['approved_package_sha256']
    allowed={'AGENTS.md','CONTRIBUTING.md','README.md','catalog.yaml','docs/development.md',
             'docs/ml-development.md','docs/learning-roadmap.md','docs/algorithm-index.md',
             'docs/progress.md','docs/reviews/README.md','artifacts/review-packages/README.md',
             'scripts/generate_catalog_docs.py'}
    allowed.update(c['path']+'/README.md' for c in current['categories'])
    allowed.update(a['canonical_location']+'/README.md' for a in b12)
    protected,changed,omitted=0,[],[]
    for name,expected in baseline['hashes'].items():
        path=ROOT/name
        if source_only and not path.exists() and excluded(PurePosixPath(name)):
            omitted.append(name);continue
        assert path.is_file(),name
        actual=sha(path.read_bytes())
        if actual!=expected:
            assert name in allowed,'Unapproved prior-file mutation: '+name
            changed.append(name)
        elif name not in allowed:
            protected+=1
    paths=[ROOT/'machine-learning/anomaly-detection/support.py']
    for a in b12:
        folder=ROOT/a['canonical_location']
        assert re.findall(r'^## (.+)$',(folder/'README.md').read_text(),re.M)==[f'{i}. {v}' for i,v in enumerate(SECTIONS,1)]
        for part in ('python/solution.py','python/example.py','tests/test_python.py'):
            assert (folder/part).is_file() and (folder/part).stat().st_size>0
        assert not (folder/'cpp/solution.cpp').exists() and not (folder/'tests/test_cpp.py').exists()
        paths.append(folder/'python/solution.py')
    forbidden={'scipy','statsmodels','prophet','hmmlearn','networkx','torch','torch_geometric','dgl','tensorflow','gensim','sklearn','requests','urllib','pickle','subprocess'}
    for path in paths:
        for node in ast.walk(ast.parse(path.read_text())):
            names=[n.name for n in node.names] if isinstance(node,ast.Import) else [node.module or ''] if isinstance(node,ast.ImportFrom) else []
            assert not any(n.split('.')[0] in forbidden for n in names),path
            if isinstance(node,ast.Call):
                if isinstance(node.func,ast.Name):assert node.func.id not in {'eval','exec','compile'},path
                if isinstance(node.func,ast.Attribute):assert node.func.attr!='seed',path
    tracking='source export; Git index omitted'
    if (ROOT/'.git').exists() and not source_only:
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==baseline['revision']
        staged=subprocess.check_output(['git','diff','--cached','--binary','--','.',':(exclude)'+REPORT],cwd=ROOT)
        assert sha(staged)==baseline['staged_diff_sha256'],'Pre-existing staged bytes changed'
        staged_paths=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT,text=True).splitlines()
        assert set(staged_paths)<=set(baseline['staged_paths'])|{REPORT}
        tracked=subprocess.run(['git','ls-files','--error-unmatch',REPORT],cwd=ROOT,capture_output=True).returncode==0
        unignored=subprocess.run(['git','check-ignore','-q',REPORT],cwd=ROOT).returncode==1
        tracking='tracked and unignored' if tracked and unignored else 'awaiting report tracking'
        if require_tracked:assert tracked and unignored,tracking
    assert (ROOT/REPORT).is_file() and (ROOT/REPORT).stat().st_size>0
    return dict(status='passed',counts=baseline['counts'],implemented=3,completed_batches=[1,2,3],
                phase23_owner_approval='approved:6 completed',phase24_owner_approval='pending',
                dpo='canonical ID/path/four blocked statuses/research/decision unchanged',
                protected_preexisting_files=protected,changed_preexisting_files=sorted(changed),
                historical_artifacts_omitted_from_export=omitted,report_tracking=tracking,
                prior_B1_B11_DSA_sources_tests_lessons_reports_and_archives='byte-identical',
                canonical_reuse='Unchanged B4/B2 validation and distances; unchanged B1 SVR RBF helper; all new detector mechanisms genuine',
                runtime_dependencies='NumPy/stdlib/local approved source only; no downloads or heavyweight frameworks')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-only',action='store_true')
    parser.add_argument('--require-tracked',action='store_true')
    parser.add_argument('--check-only',action='store_true')
    args=parser.parse_args();result=verify(args.source_only,args.require_tracked)
    if not args.check_only:(EVIDENCE/'preservation-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f"Phase24 scope passed:3 canonicals; {result['protected_preexisting_files']} protected prior files; {result['report_tracking']}")


if __name__=='__main__':main()
