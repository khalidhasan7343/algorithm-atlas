"""Run bounded Phase 18 gates, preserving numbered attempts including failures."""
from datetime import datetime
import argparse
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT/'docs/association-rule-learning-evidence'
CATEGORY = 'machine-learning/unsupervised-learning/association-rule-learning'
TARGETS = [CATEGORY]
BATCHES = [('apriori',),('eclat',),('fp-growth',),('rules',)]



def run(label, args, timeout=1200):
    attempt = 1
    while (EVIDENCE/f'{label}-attempt{attempt}.json').exists():
        attempt += 1
    name = f'{label}-attempt{attempt}'
    env = os.environ.copy()
    env.update(PYTHONHASHSEED='0', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', LOKY_MAX_CPU_COUNT='2')
    started = time.monotonic()
    try:
        result = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True,
                                text=True, timeout=timeout, env=env)
        code, output, timed_out = result.returncode, result.stdout+result.stderr, False
    except subprocess.TimeoutExpired as error:
        code, timed_out = None, True
        output = ''.join(x.decode(errors='replace') if isinstance(x, bytes) else x or '' for x in (error.stdout,error.stderr))
    record = dict(command=['python', *args], interpreter=sys.executable,
                  timestamp=datetime.now(ZoneInfo('Asia/Dhaka')).isoformat(), elapsed_seconds=round(time.monotonic()-started,3),
                  returncode=code, timed_out=timed_out, timeout_seconds=timeout,
                  environment={k:env.get(k) for k in ('CXX','PYTHONHASHSEED','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS')},
                  log=f'docs/association-rule-learning-evidence/{name}.txt',
                  summary=output.strip().splitlines()[-1] if output.strip() else 'no output')
    (EVIDENCE/(name+'.txt')).write_text(output)
    (EVIDENCE/(name+'.json')).write_text(json.dumps(record,indent=2)+'\n')
    print(label+': '+record['summary'],flush=True)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',choices=('baseline','batch1','batch2','batch3','batch4','targeted','configuration','final'),required=True)
    stage=parser.parse_args().stage
    if stage=='baseline':
        jobs=[('baseline-B1',['-m','pytest','machine-learning/supervised-learning/regression','-q']),
              ('baseline-B2',['-m','pytest','machine-learning/supervised-learning/classification','-q']),
              ('baseline-B3',['-m','pytest','machine-learning/ensemble-methods','-q']),
              ('baseline-B4',['-m','pytest','machine-learning/unsupervised-learning/clustering','-q']),
              ('baseline-B5',['-m','pytest','machine-learning/unsupervised-learning/dimensionality-reduction','machine-learning/deep-learning/vanilla-autoencoders','-q']),
              ('baseline-catalog',['scripts/validate_catalog.py']),
              ('baseline-generated',['scripts/generate_catalog_docs.py','--check'])]
    elif stage.startswith('batch'):
        jobs=[(stage,['-m','pytest',*(CATEGORY+'/tests/test_rules.py' if name=='rules' else CATEGORY+'/'+name for name in BATCHES[int(stage[-1])-1]),'-q'])]
    elif stage=='configuration':
        jobs=[('catalog',['scripts/validate_catalog.py']),('generated',['scripts/generate_catalog_docs.py','--check']),
              ('infrastructure',['-m','pytest','tests','--require-cpp','-q'])]
    else:
        jobs=[('B6',['-m','pytest',*TARGETS,'-q','--junitxml='+str(EVIDENCE/'B6.xml')]),
              *[(m,['-m','pytest',*TARGETS,'-m',m,'-q']) for m in ('numerical','oracle','reference')],
              ('randomized',['-m','pytest',*TARGETS,'-k','randomized','-q'])]
        if stage=='final':
            jobs += [('B1',['-m','pytest','machine-learning/supervised-learning/regression','-q']),
                     ('B2',['-m','pytest','machine-learning/supervised-learning/classification','-q']),
                     ('B3',['-m','pytest','machine-learning/ensemble-methods','-q']),
                     ('B4',['-m','pytest','machine-learning/unsupervised-learning/clustering','-q']),
                     ('B5',['-m','pytest','machine-learning/unsupervised-learning/dimensionality-reduction','machine-learning/deep-learning/vanilla-autoencoders','-q']),
                     ('full-suite',['-m','pytest','--require-cpp','-q','--junitxml='+str(EVIDENCE/'full-suite.xml')])]
    records={}
    for label,args in jobs:
        records[label]=run(label,args)
        (EVIDENCE/(stage+'-results.json')).write_text(json.dumps(records,indent=2)+'\n')
        if records[label]['returncode']!=0:
            raise SystemExit(1)
    versions={k:importlib.metadata.version(k) for k in ('numpy','pytest','scikit-learn','scipy','PyYAML')}
    (EVIDENCE/'environment.json').write_text(json.dumps(dict(python=sys.version,platform=platform.platform(),dependencies=versions,
        dependency_setup='Existing ML development interpreter reused; no installation/upgrade'),indent=2)+'\n')


if __name__=='__main__':
    main()
