"""Build one independently verified Phase 11 or Phase 12 source review package."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import tempfile
import zipfile
import yaml
from package_bit_manipulation_review import excluded
from package_tree_algorithms_review import PATTERNS
from review_paths import report_paths

ROOT=Path(__file__).resolve().parents[1]
PREFIX='algorithm-atlas/'
CATEGORIES={
    'number-theory':(11,'A9','Mathematical and Number Theory','number-theory',7),
    'two-pointers-sliding-window':(12,'A10','Two Pointers and Sliding Window','two-pointers-and-sliding-window',3),
}


def run(arguments,cwd):
    started=datetime.now(timezone.utc)
    result=subprocess.run([sys.executable,*arguments],cwd=cwd,capture_output=True,text=True,timeout=300)
    assert result.returncode==0,result.stdout+result.stderr
    return dict(command=['python',*arguments],returncode=result.returncode,timed_out=False,
                timeout_seconds=300,elapsed_seconds=round((datetime.now(timezone.utc)-started).total_seconds(),2),
                output=result.stdout+result.stderr)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--category',choices=CATEGORIES,required=True)
    args=parser.parse_args()
    slug=args.category
    phase,category_id,title,folder,count=CATEGORIES[slug]
    output=ROOT/f'artifacts/review-packages/{slug}/algorithm-atlas-{slug}-review.zip'
    assert not any(p.exists() for p in (output,output.with_suffix('.json'),output.with_suffix('.zip.sha256'))),'Refusing to overwrite a review artifact'
    evidence=ROOT/f'docs/{slug}-evidence'
    final=json.loads((evidence/'final-results.json').read_text())
    configuration=json.loads((evidence/'configuration-results.json').read_text())
    assert set(final)=={'python','cpp17','cpp20','full-suite'}
    for record in [*final.values(),*configuration.values()]:
        assert record['returncode']==0 and not record['timed_out']
        record['output']=(ROOT/record['log']).read_text()
        record['summary']=record['output'].strip().splitlines()[-1]
    for stage in ('A','B') if phase==11 else ('C','D'):
        record=json.loads((evidence/f'{stage}-results.json').read_text())
        assert record['algorithms']['returncode']==0 and not record['algorithms']['timed_out']
        assert all(r['returncode']==0 for r in json.loads((evidence/f'{stage}-configuration-results.json').read_text()).values())
    listed=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    paths=sorted({PurePosixPath(p) for p in listed if p and (ROOT/p).exists() and not excluded(PurePosixPath(p))})
    payload={}
    for relative in paths:
        source=ROOT/relative
        assert source.is_file() and not source.is_symlink(),relative
        assert not relative.is_absolute() and '..' not in relative.parts,relative
        data=source.read_bytes();data.decode('utf-8')
        for label,pattern in PATTERNS.items():assert not re.search(pattern,data),f'Potential credential: {relative} ({label})'
        payload[relative.as_posix()]=data
    catalog=yaml.safe_load(payload['catalog.yaml'])
    development=catalog['development']
    assert development['status']=='awaiting-review' and development['completed_batches']==[1,2,3,4]
    assert set(development['completion_reports'])=={'11','12'}
    required={'README.md','LICENSE','AGENTS.md','CONTRIBUTING.md','catalog.yaml','.github/workflows/ci.yml',
              'docs/number-theory-window-scope.md','scripts/package_number_window_reviews.py',
              'scripts/run_number_window_validation.py','scripts/verify_number_window_scope.py',
              'scripts/verify_number_window_examples.py','scripts/verify_number_window_oracles.py',
              'scripts/verify_number_window_tracking.py','tests/test_number_window_oracles.py'}
    required.update(report_paths(ROOT));required.update(development['completion_reports'].values())
    for key,(number,identifier,_,directory,expected_count) in CATEGORIES.items():
        record=development['phase_records'][str(number)]
        assert record['owner_approval']=='pending' and record['status']=='awaiting-review'
        required.add(record['checkpoint'])
        required.add(f'docs/{key}-conventions.md')
        required.update(f'dsa/{directory}/{name}' for name in ('support.py','common.hpp','oracles.py','conftest.py'))
        records=[r for r in catalog['algorithms'] if r['category']==identifier]
        assert len(records)==expected_count
        for r in records:
            assert r['documentation_status']=='implemented' and all(r[k]=='tested' for k in ('python_status','cpp_status','test_status'))
        for name in ('final-results.json','configuration-results.json','approved-baseline.json','catalog-baseline.yaml',
                     'preservation-results.json','tracking-results.json','approval-verification.json','oracle-matrix.json',
                     'oracle-inventory.json','environment.json','examples-results.json','regression-inventory.json',
                     'changed-files.txt','sanitizer-results.json'):
            required.add(f'docs/{key}-evidence/{name}')
    for r in catalog['algorithms']:
        location=r['canonical_location'];required.add(location+'/README.md')
        if r['test_status'] in ('tested','reviewed'):
            required.update(location+'/'+name for name in ('python/solution.py','cpp/solution.cpp','tests/test_python.py','tests/test_cpp.py'))
    assert required<=payload.keys(),sorted(required-payload.keys())
    checks=[['scripts/validate_catalog.py'],['scripts/generate_catalog_docs.py','--check'],
            ['scripts/verify_number_window_scope.py','--check-only','--source-only']]
    with tempfile.TemporaryDirectory(prefix=f'atlas-{slug}-export-') as temporary:
        exported=Path(temporary)/'algorithm-atlas'
        for name,data in payload.items():
            destination=exported/name;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
        source_checks=[run(command,exported) for command in checks]
        source_checks.append(run(['-m','pytest','tests',f'dsa/{folder}','--require-cpp','-q'],exported))
    directories={PREFIX}
    for name in payload:directories.update(PREFIX+p.as_posix()+'/' for p in PurePosixPath(name).parents if p.as_posix()!='.')
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        archive.comment=f'Algorithm Atlas Phase {phase}: {title}; owner approval pending independently.'.encode('utf-8')
        for name in sorted(directories):
            info=zipfile.ZipInfo(name,(2026,10,24,0,0,0));info.create_system=3
            info.external_attr=(stat.S_IFDIR|0o755)<<16|0x10;archive.writestr(info,b'')
        for name,data in payload.items():
            info=zipfile.ZipInfo(PREFIX+name,(2026,10,24,0,0,0));info.create_system=3
            info.external_attr=(stat.S_IFREG|(0o755 if os.access(ROOT/name,os.X_OK) else 0o644))<<16
            info.compress_type=zipfile.ZIP_DEFLATED;archive.writestr(info,data,compresslevel=9)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        entries=archive.infolist();assert len({e.filename for e in entries})==len(entries)
        assert {e.filename for e in entries if not e.is_dir()}=={PREFIX+p for p in payload}
        assert {e.filename for e in entries if e.is_dir()}==directories
        for e in entries:
            path=PurePosixPath(e.filename)
            assert not path.is_absolute() and '..' not in path.parts and e.filename.startswith(PREFIX)
            assert not stat.S_ISLNK(e.external_attr>>16)
            if not e.is_dir():
                name=e.filename[len(PREFIX):]
                assert not excluded(PurePosixPath(name)) and archive.read(e)==payload[name]
        with tempfile.TemporaryDirectory(prefix=f'atlas-{slug}-extracted-') as temporary:
            archive.extractall(temporary);extracted=Path(temporary)/'algorithm-atlas'
            extracted_checks=[run(command,extracted) for command in checks]
            extracted_checks.append(run(['scripts/verify_number_window_oracles.py','--category',slug,'--check-only'],extracted))
    digest=hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix('.zip.sha256').write_text(f'{digest}  {output.name}\n')
    limitations=(['Inputs have explicit bounds shared by Python and C++; exact powers reject signed-64 overflow.',
                  'Sieve limit 10^6; factorization 1..10^12 uses deterministic trial division, not large cryptographic integers.',
                  'No negative exponents, modular inverses, or arbitrary modulus multiplication.'] if phase==11 else
                 ['Array and byte lengths <=10000; array values ±10^9 and target ±2*10^9.',
                  'Two Sum requires sorted input and returns lexicographically earliest zero-based indices.',
                  'Longest distinct substring uses byte offsets, not Unicode character or grapheme offsets; maxima are eager.'])
    metadata=dict(phase_number=phase,roadmap_phase_number=phase,category=title,timestamp=datetime.now(timezone.utc).isoformat(),
                  roadmap_sequence='normal',prior_phase10_owner_approval='explicit official approval on 2026-10-24 Asia/Dhaka',
                  algorithm_count=count,canonical_algorithm_count=count,completed_algorithm_count=count,
                  approval_status='pending',owner_approval_status='pending',other_phase_approval='independently pending',
                  archive=output.name,sha256=digest,bytes=output.stat().st_size,regular_files=len(payload),directory_entries=len(directories),
                  crc_test='passed',safe_unique_paths=True,symlinks=0,required_paths_present=True,excluded_artifacts_present=False,
                  source_byte_comparison='all regular files identical',high_confidence_credential_scan='no matches',
                  checksum_verified=hashlib.sha256(output.read_bytes()).hexdigest()==digest,
                  python_test_results=final['python'],cpp17_test_results=final['cpp17'],cpp20_test_results=final['cpp20'],
                  full_suite_test_results=final['full-suite'],catalog_validation_status=configuration['catalog'],
                  documentation_validation_status=configuration['generated-docs'],
                  sanitizer_test_results=json.loads((evidence/'sanitizer-results.json').read_text()),
                  source_export_checks=source_checks,extracted_checks=extracted_checks,hosted_github_actions='not triggered or verified',
                  known_limitations=limitations+['Local macOS/Apple clang results do not establish the hosted Linux/Python matrix.',
                                               'Unignored new source and reports are ready to track; no staging, commit or push was performed.'],
                  files={name:hashlib.sha256(data).hexdigest() for name,data in payload.items()})
    output.with_suffix('.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps({k:metadata[k] for k in ('phase_number','archive','sha256','bytes','regular_files','crc_test','checksum_verified','approval_status')},indent=2))


if __name__=='__main__':main()
