"""B12 Python-only policy, exact category ownership and retained B8 blocker policy."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from scripts import generate_catalog_docs as generator
from scripts.track_policy import is_complete, cpp_required
from scripts.validate_catalog import validate_repository
from tests.test_b8_language_and_blocker_policy import b8_repo


@pytest.fixture
def b12_repo(b8_repo):
    root,c=b8_repo
    a=c['algorithms'][0]
    old=root/a['canonical_location'];new=root/'machine-learning/anomaly-detection/fixture-agent'
    new.parent.mkdir(parents=True);old.rename(new)
    a.update(category='B12',canonical_location='machine-learning/anomaly-detection/fixture-agent')
    c['categories'][0]['items']=c['categories'][0]['items'][1:]
    c['categories'].append(dict(id='B12',name='Optimization',path='machine-learning/anomaly-detection',items=[dict(name=a['name'],algorithm=a['id'])]))
    (new.parent/'README.md').write_text('# B12 synthetic policy fixture\n')
    c['development'].update(phase='Phase24',phase_number=22,category='B12',scope='B12 only',completed_batches=[1],batch_plan=[['fixture-agent']])
    (root/'tests/fixtures/required_syllabus.json').write_text(json.dumps(dict(categories=[dict(id=x['id'],name=x['name'],path=x['path'],items=[i['name'] for i in x['items']]) for x in c['categories']])))
    save(root,c)
    return root,c


def save(root,c):
    (root/'catalog.yaml').write_text(yaml.safe_dump(c))


def test_b12_python_only_valid_and_dpo_remains_blocked(b12_repo):
    root,c=b12_repo;report=validate_repository(root)
    assert report.ok,report.errors
    assert is_complete(c['algorithms'][0]) and not cpp_required(c['algorithms'][0])
    assert not is_complete(c['algorithms'][1])
    assert all(c['algorithms'][1][key]=='blocked' for key in ('documentation_status','python_status','cpp_status','test_status'))


@pytest.mark.parametrize('part',['python/solution.py','tests/test_python.py'])
def test_missing_required_python_artifact_rejected(b12_repo,part):
    root,c=b12_repo;(root/c['algorithms'][0]['canonical_location']/part).unlink()
    assert not validate_repository(root).ok


@pytest.mark.parametrize('defect',['partial-cpp','duplicate','unsafe-path','sections'])
def test_b12_artifact_identity_and_documentation_failures(b12_repo,defect):
    root,c=b12_repo;folder=root/c['algorithms'][0]['canonical_location']
    if defect=='partial-cpp':p=folder/'cpp/solution.cpp';p.parent.mkdir();p.write_text('// Structural incomplete pair\n')
    elif defect=='duplicate':c['algorithms'].append(copy.deepcopy(c['algorithms'][0]))
    elif defect=='unsafe-path':c['algorithms'][0]['canonical_location']='../escape'
    else:(folder/'README.md').write_text('# Missing required sections\n')
    save(root,c);assert not validate_repository(root).ok


@pytest.mark.parametrize('defect',['dpo-in-b12-plan','blocked-b12-bypass'])
def test_phase20_blocker_acknowledgement_cannot_complete_b12(b12_repo,defect):
    root,c=b12_repo
    if defect=='dpo-in-b12-plan':c['development']['batch_plan']=[['fixture-agent','dynamic-policy-anomaly-detection']]
    else:
        c['algorithms'][0].update({key:'blocked' for key in ('documentation_status','python_status','cpp_status','test_status')})
        c['development']['blocker_reviews']['fixture-agent']='verified-blocked'
    save(root,c);assert not validate_repository(root).ok


@pytest.mark.parametrize('kind',['dsa','ai'])
def test_dsa_and_unrelated_ai_cpp_requirements_are_preserved(b12_repo,kind):
    root,c=b12_repo;c.pop('development');c['algorithms']=c['algorithms'][:1];a=c['algorithms'][0]
    old=root/a['canonical_location'];prefix='dsa/sorting' if kind=='dsa' else 'artificial-intelligence/local-search'
    owner='A1' if kind=='dsa' else 'C3';title='Sorting' if kind=='dsa' else 'Local Search'
    new=root/prefix/'fixture-agent';new.parent.mkdir(parents=True);old.rename(new)
    a.update(category=owner,canonical_location=prefix+'/fixture-agent')
    category=dict(id=owner,name=title,path=prefix,items=[dict(name=a['name'],algorithm=a['id'])]);c['categories']=[category]
    (new.parent/'README.md').write_text('# Sorting\n')
    (root/'tests/fixtures/required_syllabus.json').write_text(json.dumps(dict(categories=[dict(category,items=[a['name']])])) )
    save(root,c);assert not validate_repository(root).ok and cpp_required(a)


def test_b12_generated_documentation_drift(b12_repo,monkeypatch):
    root,c=b12_repo;monkeypatch.setattr(generator,'ROOT',root);monkeypatch.setattr(sys,'argv',['generator'])
    assert generator.main()==0
    p=root/'docs/progress.md';p.write_text(p.read_text()+'\nUnregenerated drift\n')
    monkeypatch.setattr(sys,'argv',['generator','--check']);assert generator.main()==1


def test_b12_tests_are_in_ci_discovery():
    root=Path(__file__).resolve().parents[1]
    result=subprocess.run([sys.executable,'-m','pytest','machine-learning/anomaly-detection','--collect-only','-q'],cwd=root,capture_output=True,text=True,timeout=30)
    assert result.returncode==0
    for topic in ('isolation-forest','one-class-svm','local-outlier-factor'):
        assert topic+'/tests/test_python.py' in result.stdout
    assert 'python -m pytest --require-cpp' in (root/'.github/workflows/ci.yml').read_text()


def test_shared_ml_canonical_membership_does_not_require_duplicate_ai_code(b12_repo):
    root,c=b12_repo;a=c['algorithms'][0]
    shared=dict(id='C3',name='Local Search',path='artificial-intelligence/local-search',items=[dict(name=a['name'],algorithm=a['id'])])
    c['categories'].append(shared);folder=root/shared['path'];folder.mkdir(parents=True);(folder/'README.md').write_text('# Shared canonical navigation fixture\n')
    (root/'tests/fixtures/required_syllabus.json').write_text(json.dumps(dict(categories=[dict(id=x['id'],name=x['name'],path=x['path'],items=[i['name'] for i in x['items']]) for x in c['categories']])))
    save(root,c);result=validate_repository(root)
    assert result.ok,result.errors
    assert not cpp_required(a) and a['canonical_location']=='machine-learning/anomaly-detection/fixture-agent'


@pytest.mark.parametrize('defect',['invalid-id','duplicate-path'])
def test_b12_canonical_identity_and_path_uniqueness(b12_repo,defect):
    root,c=b12_repo
    if defect=='invalid-id':
        c['algorithms'][0]['id']='Bad_ID'
    else:
        duplicate=copy.deepcopy(c['algorithms'][0]);duplicate['id']='other-valid';c['algorithms'].append(duplicate)
        c['categories'][-1]['items'].append(dict(name=duplicate['name'],algorithm=duplicate['id']))
    save(root,c);assert not validate_repository(root).ok
