"""Phase 17 extends only the exact shared NumPy canonical; deferred/DSA remain strict."""
from copy import deepcopy
from pathlib import Path
import json
import pytest
import yaml
from scripts.track_policy import track,cpp_required,is_complete
from scripts.validate_catalog import SECTIONS,validate_repository

AUTO=dict(id='vanilla-autoencoders',category='B7',canonical_location='machine-learning/deep-learning/vanilla-autoencoders')


def test_shared_numpy_autoencoder_only_exception():
    assert track(AUTO)=='machine-learning' and not cpp_required(AUTO)
    for field,value in [('id','other-autoencoder'),('category','B5'),('canonical_location','machine-learning/deep-learning/other-topic')]:
        record=dict(AUTO,**{field:value})
        assert track(record)=='deferred' and cpp_required(record)
    for location in ['dsa/sorting/bubble-sort','artificial-intelligence/local-search/hill-climbing','machine-learning/deep-learning/denoising-autoencoders']:
        assert cpp_required(dict(canonical_location=location))


@pytest.fixture
def shared_repo(tmp_path):
    def build():
        pca=dict(id='principal-component-analysis',category='B5',canonical_location='machine-learning/unsupervised-learning/dimensionality-reduction/principal-component-analysis')
        algorithms=[]
        for record in (pca,AUTO):
            record=dict(record,name=record['id'],difficulty='advanced',documentation_status='implemented',python_status='tested',cpp_status='planned',test_status='tested',related_algorithms=[],notes='Synthetic structural fixture only.')
            algorithms.append(record);folder=tmp_path/record['canonical_location'];folder.mkdir(parents=True)
            (folder/'README.md').write_text('\n\n'.join(f'## {i}. {title}\n\nStructural fixture.' for i,title in enumerate(SECTIONS,1)))
            for file in ['python/solution.py','tests/test_python.py']:
                p=folder/file;p.parent.mkdir(exist_ok=True);p.write_text('# Structural fixture\n')
        categories=[dict(id='B5',name='Dimensionality Reduction',path=str(Path(pca['canonical_location']).parent),items=[dict(name=a['name'],algorithm=a['id']) for a in algorithms]),dict(id='B7',name='Neural Networks and Deep Learning',path='machine-learning/deep-learning',items=[dict(name=algorithms[1]['name'],algorithm=AUTO['id'])])]
        for category in categories:(tmp_path/category['path']/'README.md').write_text('# Category\n')
        checkpoint=tmp_path/'docs/checkpoint.md';checkpoint.parent.mkdir();checkpoint.write_text('# Test checkpoint\n')
        data=dict(schema_version=1,project='Algorithm Atlas',categories=categories,algorithms=algorithms,development=dict(phase='Phase 17',scope='B5 only',approval='Synthetic explicit authorization',status='awaiting-review',active_batch=None,completed_batches=[1],checkpoint='docs/checkpoint.md',track='machine-learning',category='B5',batch_plan=[[a['id'] for a in algorithms]]))
        baseline=tmp_path/'tests/fixtures/required_syllabus.json';baseline.parent.mkdir(parents=True);baseline.write_text(json.dumps(dict(categories=[dict(id=c['id'],name=c['name'],path=c['path'],items=[i['name'] for i in c['items']]) for c in categories])))
        (tmp_path/'catalog.yaml').write_text(yaml.safe_dump(data));return data
    return tmp_path,build


def test_shared_member_required_exactly_once_with_real_deliverables(shared_repo):
    root,build=shared_repo;data=build();assert validate_repository(root).ok
    assert all(is_complete(a) for a in data['algorithms'])
    auto=root/AUTO['canonical_location'];(auto/'tests/test_python.py').unlink()
    assert any('test_python.py' in error for error in validate_repository(root).errors)


@pytest.mark.parametrize('defect',['missing-shared','duplicate-shared','unrelated','missing-python','partial-cpp'])
def test_shared_member_cannot_weaken_batch_or_language_checks(shared_repo,defect):
    root,build=shared_repo;data=build();plan=data['development']['batch_plan'][0]
    if defect=='missing-shared':plan.remove(AUTO['id'])
    elif defect=='duplicate-shared':plan.append(AUTO['id'])
    elif defect=='unrelated':plan.append('denoising-autoencoders')
    elif defect=='missing-python':(root/AUTO['canonical_location']/'python/solution.py').unlink()
    else:
        p=root/AUTO['canonical_location']/'cpp/solution.cpp';p.parent.mkdir();p.write_text('// Incomplete optional pair\n')
    (root/'catalog.yaml').write_text(yaml.safe_dump(data))
    assert not validate_repository(root).ok
