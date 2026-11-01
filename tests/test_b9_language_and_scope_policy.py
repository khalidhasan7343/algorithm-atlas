"""B9 Python-only policy, exact category ownership and retained B8 blocker policy."""
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
def b9_repo(b8_repo):
    root,c=b8_repo
    a=c['algorithms'][0]
    old=root/a['canonical_location'];new=root/'machine-learning/graph-learning/fixture-agent'
    new.parent.mkdir(parents=True);old.rename(new)
    a.update(category='B9',canonical_location='machine-learning/graph-learning/fixture-agent')
    c['categories'][0]['items']=c['categories'][0]['items'][1:]
    c['categories'].append(dict(id='B9',name='Graph-Based Learning',path='machine-learning/graph-learning',items=[dict(name=a['name'],algorithm=a['id'])]))
    (new.parent/'README.md').write_text('# B9 synthetic policy fixture\n')
    c['development'].update(phase='Phase21',phase_number=21,category='B9',scope='B9 only',completed_batches=[1],batch_plan=[['fixture-agent']])
    (root/'tests/fixtures/required_syllabus.json').write_text(json.dumps(dict(categories=[dict(id=x['id'],name=x['name'],path=x['path'],items=[i['name'] for i in x['items']]) for x in c['categories']])))
    save(root,c)
    return root,c


def save(root,c):
    (root/'catalog.yaml').write_text(yaml.safe_dump(c))


def test_b9_python_only_valid_and_dpo_remains_blocked(b9_repo):
    root,c=b9_repo;report=validate_repository(root)
    assert report.ok,report.errors
    assert is_complete(c['algorithms'][0]) and not cpp_required(c['algorithms'][0])
    assert not is_complete(c['algorithms'][1])
    assert all(c['algorithms'][1][key]=='blocked' for key in ('documentation_status','python_status','cpp_status','test_status'))


@pytest.mark.parametrize('part',['python/solution.py','tests/test_python.py'])
def test_missing_required_python_artifact_rejected(b9_repo,part):
    root,c=b9_repo;(root/c['algorithms'][0]['canonical_location']/part).unlink()
    assert not validate_repository(root).ok


@pytest.mark.parametrize('defect',['partial-cpp','duplicate','unsafe-path','sections'])
def test_b9_artifact_identity_and_documentation_failures(b9_repo,defect):
    root,c=b9_repo;folder=root/c['algorithms'][0]['canonical_location']
    if defect=='partial-cpp':p=folder/'cpp/solution.cpp';p.parent.mkdir();p.write_text('// Structural incomplete pair\n')
    elif defect=='duplicate':c['algorithms'].append(copy.deepcopy(c['algorithms'][0]))
    elif defect=='unsafe-path':c['algorithms'][0]['canonical_location']='../escape'
    else:(folder/'README.md').write_text('# Missing required sections\n')
    save(root,c);assert not validate_repository(root).ok


@pytest.mark.parametrize('defect',['dpo-in-b9-plan','blocked-b9-bypass'])
def test_phase20_blocker_acknowledgement_cannot_complete_b9(b9_repo,defect):
    root,c=b9_repo
    if defect=='dpo-in-b9-plan':c['development']['batch_plan']=[['fixture-agent','dynamic-policy-optimization']]
    else:
        c['algorithms'][0].update({key:'blocked' for key in ('documentation_status','python_status','cpp_status','test_status')})
        c['development']['blocker_reviews']['fixture-agent']='verified-blocked'
    save(root,c);assert not validate_repository(root).ok


def test_dsa_cpp_requirement_is_preserved(b9_repo):
    root,c=b9_repo;c.pop('development');c['algorithms']=c['algorithms'][:1];a=c['algorithms'][0]
    old=root/a['canonical_location'];new=root/'dsa/sorting/fixture-agent';new.parent.mkdir(parents=True);old.rename(new)
    a.update(category='A1',canonical_location='dsa/sorting/fixture-agent')
    category=dict(id='A1',name='Sorting',path='dsa/sorting',items=[dict(name=a['name'],algorithm=a['id'])]);c['categories']=[category]
    (new.parent/'README.md').write_text('# Sorting\n')
    (root/'tests/fixtures/required_syllabus.json').write_text(json.dumps(dict(categories=[dict(category,items=[a['name']])])) )
    save(root,c);assert not validate_repository(root).ok and cpp_required(a)


def test_b9_generated_documentation_drift(b9_repo,monkeypatch):
    root,c=b9_repo;monkeypatch.setattr(generator,'ROOT',root);monkeypatch.setattr(sys,'argv',['generator'])
    assert generator.main()==0
    p=root/'docs/progress.md';p.write_text(p.read_text()+'\nUnregenerated drift\n')
    monkeypatch.setattr(sys,'argv',['generator','--check']);assert generator.main()==1


def test_b9_tests_are_in_ci_discovery():
    root=Path(__file__).resolve().parents[1]
    result=subprocess.run([sys.executable,'-m','pytest','machine-learning/graph-learning','--collect-only','-q'],cwd=root,capture_output=True,text=True,timeout=30)
    assert result.returncode==0
    for topic in ('pagerank','node2vec','graph-convolutional-networks'):
        assert topic+'/tests/test_python.py' in result.stdout
    assert 'python -m pytest --require-cpp' in (root/'.github/workflows/ci.yml').read_text()
