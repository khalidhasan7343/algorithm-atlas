"""Freeze the Phase22 repository and independently validate the actual ZIP export."""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
import time
import zipfile
from zoneinfo import ZoneInfo

import yaml

from package_bit_manipulation_review import excluded
from package_tree_algorithms_review import PATTERNS
from track_policy import cpp_required, is_complete
from verify_optimization_scope import verify, REPORT, TOPICS

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'docs/optimization-evidence'
OUTPUT=ROOT/'artifacts/review-packages/optimization/algorithm-atlas-optimization-review.zip'
PREFIX='algorithm-atlas/'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    sidecar=OUTPUT.with_suffix('.json');checksum=OUTPUT.with_suffix('.zip.sha256')
    assert not any(p.exists() for p in (OUTPUT,sidecar,checksum)),'Refusing to overwrite review artifacts'
    preservation=verify(require_tracked=True)
    final=json.loads((EVIDENCE/'final-results.json').read_text())
    config=json.loads((EVIDENCE/'configuration-results.json').read_text())
    matrix=json.loads((EVIDENCE/'test-matrix.json').read_text())
    assert set(config)=={'catalog','generated','examples','scope'},'Missing configuration evidence'
    assert {'audit-B10','infrastructure-B10','full-suite','exact-updates','oracle','gradient',
            'curvature','numerical','reproducibility','stopping','edge-cases','compatibility',
            'educational-training',*(f'B{i}' for i in range(1,10))}<=final.keys()
    assert all(r['returncode']==0 and not r['timed_out'] for r in [*final.values(),*config.values()])
    assert matrix['failures']==matrix['errors']==matrix['skipped']==0
    for batch in range(1,5):assert json.loads((EVIDENCE/f'batch{batch}-gate.json').read_text())['returncode']==0
    names=subprocess.check_output(['git','ls-files','-c','-o','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    paths=sorted({PurePosixPath(n) for n in names if n and (ROOT/n).is_file() and not excluded(PurePosixPath(n))})
    payload={}
    for name in paths:
        path=ROOT/name
        assert not path.is_symlink() and not name.is_absolute() and '..' not in name.parts
        data=path.read_bytes();data.decode('utf-8')
        for label,pattern in PATTERNS.items():assert not re.search(pattern,data),f'Potential credential: {name} ({label})'
        payload[name.as_posix()]=data
    catalog=yaml.safe_load(payload['catalog.yaml']);state=catalog['development']
    assert state['phase_number']==22 and state['status']=='awaiting-review'
    assert state['current_review']['owner_approval']==state['phase_records']['22']['owner_approval']=='pending'
    assert state['phase_records']['21']['owner_approval']=='approved'
    b10=[a for a in catalog['algorithms'] if a['category']=='B10']
    assert tuple(a['id'] for a in b10)==TOPICS and all(is_complete(a) for a in b10)
    dpo=next(a for a in catalog['algorithms'] if a['id']=='dynamic-policy-optimization')
    assert all(dpo[k]=='blocked' for k in ('documentation_status','python_status','cpp_status','test_status'))
    required={REPORT,'README.md','AGENTS.md','CONTRIBUTING.md','LICENSE','catalog.yaml',
              'requirements-dev.txt','requirements-ml.txt','requirements-ml-test.txt','pyproject.toml','conftest.py',
              '.github/workflows/ci.yml','scripts/validate_catalog.py','scripts/generate_catalog_docs.py',
              'scripts/track_policy.py','scripts/package_bit_manipulation_review.py','scripts/package_tree_algorithms_review.py',
              'scripts/verify_optimization_scope.py','scripts/verify_optimization_examples.py',
              'scripts/evaluate_optimization.py','scripts/run_optimization_validation.py','scripts/package_optimization_review.py',
              'docs/optimization-scope.md','docs/optimization-conventions.md','docs/optimization-checkpoints.md',
              'machine-learning/optimization/README.md','machine-learning/optimization/support.py',
              'machine-learning/optimization/conftest.py','machine-learning/optimization/tests/test_objective_oracles.py',
              'machine-learning/optimization/tests/test_first_order_contracts.py','machine-learning/optimization/tests/test_search_contracts.py',
              'machine-learning/optimization/tests/objectives.py',
              'machine-learning/deep-learning/support.py','machine-learning/deep-learning/conftest.py',
              'machine-learning/deep-learning/graph-neural-networks/python/solution.py',
              'machine-learning/deep-learning/graph-neural-networks/tests/test_python.py',
              'tests/test_b10_language_and_scope_policy.py',state['dpo_specification_decision']['report'],
              state['dpo_specification_decision']['evidence'],dpo['canonical_location']+'/README.md'}
    for a in catalog['algorithms']:
        required.add(a['canonical_location']+'/README.md')
        if is_complete(a):
            required.update(a['canonical_location']+'/'+part for part in ('python/solution.py','tests/test_python.py'))
            if cpp_required(a):required.update(a['canonical_location']+'/'+part for part in ('cpp/solution.cpp','tests/test_cpp.py'))
    required.update(a['canonical_location']+'/python/example.py' for a in b10)
    required.update(n for n in payload if n.startswith('docs/reviews/') and n.endswith('.md'))
    for name in ('baseline.json','catalog-baseline.yaml','phase22-request.md','approval-evidence.json',
                 'final-results.json','configuration-results.json','test-matrix.json','preservation-results.json',
                 'examples-results.json','educational-training-results.json','reference-sources.json',
                 'development-findings.json','changed-files.json','negative-validation-matrix.json'):
        required.add('docs/optimization-evidence/'+name)
    assert required<=payload.keys(),sorted(required-payload.keys())
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(OUTPUT,'x',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in payload.items():
            info=zipfile.ZipInfo(PREFIX+name,date_time=(2026,10,31,0,0,0));info.create_system=3
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(stat.S_IFREG|0o644)<<16
            z.writestr(info,data)
    digest=sha(OUTPUT.read_bytes());checksum.write_text(f'{digest}  {OUTPUT.name}\n')
    baseline=json.loads((EVIDENCE/'baseline.json').read_text())
    approval=json.loads((EVIDENCE/'approval-evidence.json').read_text())
    metadata=dict(phase_number=22,phase_name=state['phase'],category_id='B10',category_name='Optimization',
        catalog_entries=10,implementation_count=10,completed_batches=[1,2,3,4],algorithm_ids=list(TOPICS),incomplete_algorithms=[],blocked_B10_algorithms=[],
        shared_memberships={a['id']:[c['id'] for c in catalog['categories'] if any(i['algorithm']==a['id'] for i in c['items'])] for a in b10 if a['id'] in ('genetic-algorithms','simulated-annealing')},
        owner_approval='pending',phase21_owner_approval='approved',phase21_approved_package_sha256=approval['approved_package_sha256'],
        B8_catalog_completion=dict(entries=10,implemented=9,intentionally_blocked=1,complete=False),
        dpo=dict(id=dpo['id'],canonical_path=dpo['canonical_location'],statuses={k:dpo[k] for k in ('documentation_status','python_status','cpp_status','test_status')},
                 specification_decision='owner-approved: remain blocked',substitution_authorized=False),
        client_date='2026-10-31 Asia/Dhaka',execution_timestamp=datetime.now(ZoneInfo('Asia/Dhaka')).isoformat(),
        starting_revision=baseline['revision'],branch=baseline['branch'],environment=baseline['environment'],dependencies_changed=False,
        report=REPORT,report_tracking_status='tracked and unignored',archive=OUTPUT.name,bytes=OUTPUT.stat().st_size,files=len(payload),sha256=digest,
        file_sha256={n:sha(data) for n,data in payload.items()},required_files=sorted(required),
        local_test_matrix=matrix,local_validation=final,configuration_validation=config,prior_source_preservation=preservation,
        source_only=True,nested_archives=False,hosted_github_actions='not executed or verified',
        extraction_checks=[],extraction_validation_status='running')
    def save():sidecar.write_text(json.dumps(metadata,indent=2)+'\n')
    save()
    with tempfile.TemporaryDirectory(prefix='atlas-b10-export-') as temp:
        folder=Path(temp)
        with zipfile.ZipFile(OUTPUT) as z:
            assert z.testzip() is None
            assert len(z.infolist())==len(set(z.namelist()))==len(payload)
            for info in z.infolist():
                path=PurePosixPath(info.filename)
                assert path.parts[0]=='algorithm-atlas' and len(path.parts)>1 and not path.is_absolute()
                assert '..' not in path.parts and '\\' not in info.filename and stat.S_ISREG(info.external_attr>>16)
                name=PurePosixPath(*path.parts[1:]).as_posix()
                assert name in payload and not excluded(PurePosixPath(name)) and sha(z.read(info))==metadata['file_sha256'][name]
            z.extractall(folder)
        exported=folder/'algorithm-atlas'
        for name,data in payload.items():assert (exported/name).read_bytes()==data
        env=dict(os.environ,PYTHONPATH='',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONHASHSEED='0')
        commands=[['scripts/validate_catalog.py'],['scripts/generate_catalog_docs.py','--check'],
                  ['scripts/verify_optimization_scope.py','--source-only','--check-only'],
                  ['scripts/verify_optimization_examples.py','--check-only'],
                  ['-m','pytest','machine-learning/optimization','-q'],
                  ['-m','pytest','machine-learning/graph-learning','-q'],
                  ['-m','pytest','machine-learning/deep-learning/graph-neural-networks','-q'],
                  ['-m','pytest','--require-cpp','-q']]
        for args in commands:
            print('Export check: python '+' '.join(args),flush=True);before=time.monotonic()
            try:
                r=subprocess.run([sys.executable,*args],cwd=exported,env=env,capture_output=True,text=True,timeout=1200)
                record=dict(command=['python',*args],returncode=r.returncode,timed_out=False,output=r.stdout+r.stderr,elapsed_seconds=round(time.monotonic()-before,3))
            except subprocess.TimeoutExpired as error:
                record=dict(command=['python',*args],returncode=None,timed_out=True,output=str(error.stdout or '')+str(error.stderr or ''),elapsed_seconds=round(time.monotonic()-before,3))
            metadata['extraction_checks'].append(record);save()
            if record['returncode']!=0:
                metadata['extraction_validation_status']='failed';save();raise AssertionError(record)
            print(record['output'][-500:],flush=True)
        for name,data in payload.items():assert (exported/name).read_bytes()==data,'Export source changed: '+name
    for name,data in payload.items():assert (ROOT/name).read_bytes()==data,'Working source changed after freeze: '+name
    assert sha(OUTPUT.read_bytes())==digest==checksum.read_text().split()[0]
    metadata.update(extraction_validation_status='passed',zip_crc='passed',safe_unique_regular_paths=True,
                    required_files_present=True,checksum_consistency='passed',source_bytes='identical',
                    credential_scan='no high-confidence matches',json_metadata_consistency='passed')
    save();check=json.loads(sidecar.read_text());assert check['sha256']==digest and check['files']==len(check['file_sha256'])
    print(f'Package verified: {OUTPUT.relative_to(ROOT)}; SHA256 {digest}',flush=True)


if __name__=='__main__':main()
