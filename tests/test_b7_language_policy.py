"""Phase19 NumPy B7 policy extends ML without relaxing DSA/AI or artifact integrity."""
import json
from pathlib import Path
import pytest,yaml
from scripts.track_policy import cpp_required,is_complete
from scripts.validate_catalog import validate_repository,SECTIONS

@pytest.fixture
def neural_repo(tmp_path):
    folder=tmp_path/'machine-learning/deep-learning/fixture-network';folder.mkdir(parents=True)
    category=dict(id='B7',name='Neural Networks and Deep Learning',path='machine-learning/deep-learning')
    algorithm=dict(id='fixture-network',name='Fixture Network',category='B7',canonical_location=str(folder.relative_to(tmp_path)),difficulty='advanced',documentation_status='implemented',python_status='tested',cpp_status='planned',test_status='tested',related_algorithms=[],notes='Synthetic validation fixture only.')
    catalog=dict(schema_version=1,project='Algorithm Atlas',categories=[dict(category,items=[dict(name=algorithm['name'],algorithm=algorithm['id'])])],algorithms=[algorithm])
    (tmp_path/'catalog.yaml').write_text(yaml.safe_dump(catalog));(folder.parent/'README.md').write_text('# Category\n')
    (folder/'README.md').write_text('\n\n'.join(f'## {i}. {title}\n\nStructural fixture.' for i,title in enumerate(SECTIONS,1)))
    for name in ['python/solution.py','tests/test_python.py']:
        p=folder/name;p.parent.mkdir(exist_ok=True);p.write_text('# Structural fixture\n')
    baseline=tmp_path/'tests/fixtures/required_syllabus.json';baseline.parent.mkdir(parents=True);baseline.write_text(json.dumps(dict(categories=[dict(category,items=[algorithm['name']])])) )
    return tmp_path,folder,catalog


def test_b7_python_only_complete_and_dsa_ai_policy_unchanged(neural_repo):
    root,_,c=neural_repo;assert validate_repository(root).ok;assert is_complete(c['algorithms'][0])
    assert cpp_required(dict(canonical_location='dsa/sorting/topic'))
    assert cpp_required(dict(canonical_location='artificial-intelligence/local-search/topic'))

@pytest.mark.parametrize('missing',['python/solution.py','tests/test_python.py'])
def test_b7_required_python_deliverables_enforced(neural_repo,missing):
    root,folder,_=neural_repo;(folder/missing).unlink();assert not validate_repository(root).ok

@pytest.mark.parametrize('defect',['partial-cpp','duplicate','path','sections'])
def test_b7_optional_pair_identity_and_lessons_remain_strict(neural_repo,defect):
    root,folder,c=neural_repo
    if defect=='partial-cpp':p=folder/'cpp/solution.cpp';p.parent.mkdir();p.write_text('// Incomplete optional pair\n')
    elif defect=='duplicate':c['algorithms'].append(c['algorithms'][0].copy())
    elif defect=='path':c['algorithms'][0]['canonical_location']='../outside'
    else:(folder/'README.md').write_text('# Incomplete lesson\n')
    (root/'catalog.yaml').write_text(yaml.safe_dump(c));assert not validate_repository(root).ok
