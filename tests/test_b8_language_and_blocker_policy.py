"""B8 Python-only policy and the exact Phase20 DPO blocker-review exception."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import pytest
import yaml

from scripts import generate_catalog_docs as generator
from scripts.track_policy import is_complete, cpp_required
from scripts.validate_catalog import SECTIONS, validate_repository


@pytest.fixture
def b8_repo(tmp_path):
    category=dict(id='B8',name='Reinforcement Learning',path='machine-learning/reinforcement-learning')
    records=[]
    for topic in ('fixture-agent','dynamic-policy-optimization'):
        blocked=topic=='dynamic-policy-optimization'
        record=dict(id=topic,name=topic,category='B8',canonical_location=category['path']+'/'+topic,
                    difficulty='advanced',documentation_status='blocked' if blocked else 'implemented',
                    python_status='blocked' if blocked else 'tested',cpp_status='blocked' if blocked else 'planned',
                    test_status='blocked' if blocked else 'tested',related_algorithms=[],
                    notes='Missing defining paper, mathematical objective and intended variant.' if blocked else 'Synthetic infrastructure fixture.')
        records.append(record)
        folder=tmp_path/record['canonical_location'];folder.mkdir(parents=True)
        (folder/'README.md').write_text('# Blocked specification\n' if blocked else '\n\n'.join(f'## {i}. {title}\n\nFixture content.' for i,title in enumerate(SECTIONS,1)))
        if not blocked:
            for part in ('python/solution.py','tests/test_python.py'):
                p=folder/part;p.parent.mkdir(exist_ok=True);p.write_text('# Structural fixture only\n')
    (tmp_path/category['path']/'README.md').write_text('# Category\n')
    d=dict(phase='Phase20',phase_number=20,category='B8',track='machine-learning',scope='B8 only',
           approval='Owner authorized nine defined algorithms and a separate blocked review.',
           status='awaiting-review',active_batch=None,completed_batches=[1,2],
           batch_plan=[['fixture-agent'],['dynamic-policy-optimization']],checkpoint='docs/checkpoint.md',
           completion_report='docs/report.md',blocker_reviews={'dynamic-policy-optimization':'verified-blocked'})
    (tmp_path/'docs').mkdir()
    (tmp_path/'docs/checkpoint.md').write_text('# Fixture checkpoint\n')
    (tmp_path/'docs/report.md').write_text('# Fixture report\n')
    c=dict(schema_version=1,project='Algorithm Atlas',development=d,
           categories=[dict(category,items=[dict(name=r['name'],algorithm=r['id']) for r in records])],algorithms=records)
    p=tmp_path/'tests/fixtures/required_syllabus.json';p.parent.mkdir(parents=True)
    p.write_text(json.dumps(dict(categories=[dict(category,items=[r['name'] for r in records])])))
    (tmp_path/'catalog.yaml').write_text(yaml.safe_dump(c))
    return tmp_path,c


def save(root,c):
    (root/'catalog.yaml').write_text(yaml.safe_dump(c))


def test_python_only_and_explicit_dpo_blocker_are_valid_without_becoming_complete(b8_repo):
    root,c=b8_repo
    report=validate_repository(root)
    assert report.ok,report.errors
    assert is_complete(c['algorithms'][0]) and not is_complete(c['algorithms'][1])
    assert not cpp_required(c['algorithms'][0])
    assert cpp_required(dict(canonical_location='dsa/sorting/topic'))


@pytest.mark.parametrize('part',['python/solution.py','tests/test_python.py'])
def test_required_python_artifacts_are_rejected_when_missing(b8_repo,part):
    root,c=b8_repo;(root/c['algorithms'][0]['canonical_location']/part).unlink()
    assert not validate_repository(root).ok


@pytest.mark.parametrize('defect',['partial-cpp','duplicate','unsafe-path','sections'])
def test_optional_cpp_identity_paths_and_sections_stay_strict(b8_repo,defect):
    root,c=b8_repo;folder=root/c['algorithms'][0]['canonical_location']
    if defect=='partial-cpp':p=folder/'cpp/solution.cpp';p.parent.mkdir();p.write_text('// Incomplete pair\n')
    elif defect=='duplicate':c['algorithms'].append(copy.deepcopy(c['algorithms'][0]))
    elif defect=='unsafe-path':c['algorithms'][0]['canonical_location']='../escape'
    else:(folder/'README.md').write_text('# Missing sections\n')
    save(root,c);assert not validate_repository(root).ok


@pytest.mark.parametrize('defect',['unacknowledged','partial-status','wrong-phase','wrong-category','other-blocked','empty-reason','malformed-acknowledgement'])
def test_blocker_review_exception_cannot_bypass_other_completion_rules(b8_repo,defect):
    root,c=b8_repo;d=c['development'];blocked=c['algorithms'][1]
    if defect=='unacknowledged':d.pop('blocker_reviews')
    elif defect=='partial-status':blocked['python_status']='planned'
    elif defect=='wrong-phase':d['phase_number']=21
    elif defect=='wrong-category':d['category']='B7'
    elif defect=='other-blocked':
        c['algorithms'][0].update({f:'blocked' for f in ('documentation_status','python_status','cpp_status','test_status')})
        d['blocker_reviews']['fixture-agent']='verified-blocked'
    elif defect=='empty-reason':blocked['notes']=''
    else:d['blocker_reviews']=[]
    save(root,c);assert not validate_repository(root).ok


def test_dsa_missing_cpp_is_still_rejected(b8_repo):
    root,c=b8_repo
    # Remove development so this isolates track policy rather than ML scope.
    c.pop('development');c['algorithms']=c['algorithms'][:1]
    a=c['algorithms'][0];old=root/a['canonical_location'];new=root/'dsa/sorting/fixture-agent';new.parent.mkdir(parents=True);old.rename(new)
    a.update(category='A1',canonical_location='dsa/sorting/fixture-agent')
    c['categories']=[dict(id='A1',name='Sorting',path='dsa/sorting',items=[dict(name=a['name'],algorithm=a['id'])])]
    (new.parent/'README.md').write_text('# Sorting\n');(root/'tests/fixtures/required_syllabus.json').write_text(json.dumps(dict(categories=[dict(id='A1',name='Sorting',path='dsa/sorting',items=[a['name']])])) )
    save(root,c);assert not validate_repository(root).ok


def test_generated_documentation_drift_is_detected(b8_repo,monkeypatch):
    root,c=b8_repo
    monkeypatch.setattr(generator,'ROOT',root);monkeypatch.setattr(sys,'argv',['generator'])
    assert generator.main()==0
    page=root/'docs/progress.md';page.write_text(page.read_text()+'\nDrift\n')
    monkeypatch.setattr(sys,'argv',['generator','--check'])
    assert generator.main()==1


def test_b8_discovery_matches_ci_roots():
    root=Path(__file__).resolve().parents[1]
    result=subprocess.run([sys.executable,'-m','pytest','machine-learning/reinforcement-learning','--collect-only','-q'],cwd=root,capture_output=True,text=True,timeout=30)
    assert result.returncode==0
    for topic in ('q-learning','sarsa','deep-q-networks','reinforce-policy-gradient','advantage-actor-critic','asynchronous-advantage-actor-critic','proximal-policy-optimization','deep-deterministic-policy-gradient','monte-carlo-tree-search'):
        assert topic+'/tests/test_python.py' in result.stdout
    workflow=(root/'.github/workflows/ci.yml').read_text()
    assert 'python -m pytest --require-cpp' in workflow
