"""Create and independently validate a source-only Phase 9 review artifact."""
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

from package_tree_algorithms_review import EXCLUDED_DIRS, EXCLUDED_SUFFIXES, EXCLUDED_NAMES, PATTERNS
from review_paths import report_paths
from validate_catalog import STRING_BATCHES

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'artifacts/review-packages/string-algorithms/algorithm-atlas-string-algorithms-review.zip'
PREFIX='algorithm-atlas/'


def excluded(path):
    return (bool(set(path.parts)&EXCLUDED_DIRS)
            or any(p.startswith('cmake-build-') or p.endswith(('.egg-info','.dSYM')) for p in path.parts)
            or path.suffix.lower() in EXCLUDED_SUFFIXES
            or path.name in EXCLUDED_NAMES or '.zip.' in path.name
            or (path.name.startswith('.env') and path.name!='.env.example')
            or (path.as_posix().startswith('artifacts/review-packages/')
                and path.suffix in ('.json','.sha256')))


def run(arguments,cwd,timeout=180):
    command=[sys.executable,*arguments]
    result=subprocess.run(command,cwd=cwd,capture_output=True,text=True,timeout=timeout)
    assert result.returncode==0,result.stdout+result.stderr
    return dict(command=['python',*arguments],returncode=result.returncode,
                timed_out=False,timeout_seconds=timeout,output=result.stdout+result.stderr)


def main():
    assert not OUTPUT.exists(),'Refusing to overwrite an existing review artifact'
    evidence=ROOT/'docs/string-algorithms-evidence'
    final=json.loads((evidence/'final-results.json').read_text())
    configuration=json.loads((evidence/'configuration-results.json').read_text())
    for record in [*final.values(),*configuration.values()]:
        record['output']=(ROOT/record['log']).read_text()
        record['summary']=record['output'].strip().splitlines()[-1]
    assert set(final)=={'python','cpp17','cpp20','full-suite'}
    assert all(v['returncode']==0 and not v['timed_out'] for v in final.values())
    assert all(v['returncode']==0 and not v['timed_out'] for v in configuration.values())
    for batch in range(1,4):
        records=json.loads((evidence/f'batch{batch}-results.json').read_text())
        assert records['algorithms']['returncode']==0
    listed=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode().split('\0')
    paths=sorted({PurePosixPath(p) for p in listed if p and (ROOT/p).exists() and not excluded(PurePosixPath(p))})
    payload={}
    for relative in paths:
        source=ROOT/relative
        assert source.is_file() and not source.is_symlink(),relative
        assert not relative.is_absolute() and '..' not in relative.parts,relative
        data=source.read_bytes()
        data.decode('utf-8')
        for label,pattern in PATTERNS.items():
            assert not re.search(pattern,data),f'Potential credential: {relative} ({label})'
        payload[relative.as_posix()]=data
    import yaml
    catalog=yaml.safe_load(payload['catalog.yaml'])
    assert catalog['development']['status']=='awaiting-review'
    assert catalog['development']['completed_batches']==[1,2,3]
    required={'README.md','LICENSE','AGENTS.md','CONTRIBUTING.md','catalog.yaml',
              'docs/string-algorithms-checkpoints.md','docs/string-conventions.md',
              'docs/reviews/string-algorithms/STRING-ALGORITHMS-REVIEW-REPORT.md',
              'dsa/string-algorithms/string_support.py','dsa/string-algorithms/common.hpp',
              'dsa/string-algorithms/string_oracles.py','dsa/string-algorithms/structure_oracles.py',
              'dsa/string-algorithms/conftest.py','.github/workflows/ci.yml',
              'scripts/run_string_algorithms_validation.py','scripts/verify_string_algorithms_scope.py',
              'scripts/verify_string_cross_algorithms.py','scripts/verify_string_examples.py',
              'scripts/verify_string_tracking.py','scripts/audit_string_complexity.py',
              'scripts/package_string_algorithms_review.py','tests/test_string_cross_algorithms.py'}
    required.update(report_paths(ROOT))
    for name in ('final-results.json','configuration-results.json','batch1-results.json','batch2-results.json','batch3-results.json',
                 'batch1-configuration-results.json','batch2-configuration-results.json','batch3-configuration-results.json',
                 'catalog-baseline.yaml','approved-baseline.json','preservation-results.json','tracking-results.json',
                 'cross-matrix-batch3.json','oracle-inventory.json','environment.json','examples-results.json',
                 'complexity-results.json','regression-inventory.json','changed-files.txt','sanitizer-results.json'):
        required.add('docs/string-algorithms-evidence/'+name)
    for record in catalog['algorithms']:
        folder=record['canonical_location']
        required.add(folder+'/README.md')
        if record['test_status'] in ('tested','reviewed'):
            required.update(folder+'/'+part for part in ('python/solution.py','cpp/solution.cpp','tests/test_python.py','tests/test_cpp.py'))
    assert required<=payload.keys(),sorted(required-payload.keys())
    for batch in STRING_BATCHES:
        for name in batch:
            record=next(r for r in catalog['algorithms'] if r['id']==name)
            assert record['documentation_status']=='implemented'
            assert all(record[k]=='tested' for k in ('python_status','cpp_status','test_status'))
    directories={PREFIX}
    for name in payload:
        directories.update(PREFIX+p.as_posix()+'/' for p in PurePosixPath(name).parents if p.as_posix()!='.')
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    # Validate the exported payload before creating the final immutable ZIP.
    with tempfile.TemporaryDirectory(prefix='atlas-string-export-') as temporary:
        exported=Path(temporary)/'algorithm-atlas'
        for name,data in payload.items():
            destination=exported/name
            destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes(data)
        source_checks=[run(['scripts/validate_catalog.py'],exported),
                       run(['scripts/generate_catalog_docs.py','--check'],exported),
                       run(['scripts/verify_string_algorithms_scope.py','--check-only','--source-only'],exported),
                       run(['-m','pytest','tests','dsa/string-algorithms','--require-cpp','-q'],exported)]
    with zipfile.ZipFile(OUTPUT,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name in sorted(directories):
            info=zipfile.ZipInfo(name,(2026,10,23,0,0,0));info.create_system=3
            info.external_attr=(stat.S_IFDIR|0o755)<<16|0x10
            archive.writestr(info,b'')
        for name,data in payload.items():
            info=zipfile.ZipInfo(PREFIX+name,(2026,10,23,0,0,0));info.create_system=3
            info.external_attr=(stat.S_IFREG|(0o755 if os.access(ROOT/name,os.X_OK) else 0o644))<<16
            info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,data,compresslevel=9)
    with zipfile.ZipFile(OUTPUT) as archive:
        assert archive.testzip() is None
        entries=archive.infolist()
        assert len({e.filename for e in entries})==len(entries)
        assert {e.filename for e in entries if not e.is_dir()}=={PREFIX+p for p in payload}
        assert {e.filename for e in entries if e.is_dir()}==directories
        for entry in entries:
            path=PurePosixPath(entry.filename)
            assert not path.is_absolute() and '..' not in path.parts and entry.filename.startswith(PREFIX)
            assert not stat.S_ISLNK(entry.external_attr>>16)
            if not entry.is_dir():
                name=entry.filename[len(PREFIX):]
                assert not excluded(PurePosixPath(name))
                assert archive.read(entry)==payload[name]
        with tempfile.TemporaryDirectory(prefix='atlas-string-extracted-') as temporary:
            archive.extractall(temporary)
            extracted=Path(temporary)/'algorithm-atlas'
            extracted_checks=[run(['scripts/validate_catalog.py'],extracted),
                              run(['scripts/generate_catalog_docs.py','--check'],extracted),
                              run(['scripts/verify_string_algorithms_scope.py','--check-only','--source-only'],extracted),
                              run(['scripts/verify_string_cross_algorithms.py','--check-only'],extracted)]
    digest=hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    OUTPUT.with_suffix('.zip.sha256').write_text(f'{digest}  {OUTPUT.name}\n')
    metadata=dict(phase_number=9,category='String Algorithms',timestamp=datetime.now(timezone.utc).isoformat(),
                  canonical_algorithm_count=9,completed_algorithm_count=9,approval_status='pending',owner_approval_status='pending',
                  archive=OUTPUT.name,sha256=digest,bytes=OUTPUT.stat().st_size,regular_files=len(payload),
                  directory_entries=len(directories),crc_test='passed',safe_unique_paths=True,symlinks=0,
                  required_paths_present=True,excluded_artifacts_present=False,source_byte_comparison='all regular files identical',
                  high_confidence_credential_scan='no matches',
                  checksum_verified=hashlib.sha256(OUTPUT.read_bytes()).hexdigest()==digest,
                  python_test_results=final['python'],cpp17_test_results=final['cpp17'],cpp20_test_results=final['cpp20'],
                  full_suite_test_results=final['full-suite'],catalog_validation_status=configuration['catalog'],
                  documentation_validation_status=configuration['generated-docs'],
                  sanitizer_test_results=json.loads((evidence/'sanitizer-results.json').read_text()),
                  source_export_checks=source_checks,extracted_checks=extracted_checks,
                  hosted_github_actions='not triggered or verified',
                  known_limitations=['Exact unsigned-byte semantics; UTF-8 offsets are bytes, not code points/graphemes.',
                                     'Boyer-Moore has no Galil rule; Rabin-Karp verifies collisions; both can be quadratic.',
                                     'Suffix Array uses comparison-sort prefix doubling: O(n log² n) construction.',
                                     'Suffix Tree uses genuine compressed-edge O(n²) insertion, bounded to 2048 text bytes.',
                                     'Dense Aho-Corasick tables and eager outputs can consume substantial memory.',
                                     'Local Python 3.14/macOS/Apple clang results do not establish hosted Linux matrix results.',
                                     'New source/review files are unignored and ready to track; no commit or push was made.'],
                  files={name:hashlib.sha256(data).hexdigest() for name,data in payload.items()})
    OUTPUT.with_suffix('.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps({k:metadata[k] for k in ('archive','sha256','bytes','regular_files','crc_test','checksum_verified','approval_status')},indent=2))


if __name__=='__main__':main()
