"""Execute six real examples and verify exact lesson headings/captured output."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from validate_catalog import SECTIONS
from verify_time_series_scope import TOPICS

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'docs/time-series-evidence'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only',action='store_true')
    args=parser.parse_args();records=[]
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONHASHSEED='0')
    for topic in TOPICS:
        folder=ROOT/'machine-learning/time-series'/topic
        lesson=(folder/'README.md').read_text()
        assert re.findall(r'^## (.+)$',lesson,re.M)==[f'{i}. {name}' for i,name in enumerate(SECTIONS,1)],topic
        command=[sys.executable,str(folder/'python/example.py')]
        result=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,timeout=30)
        assert result.returncode==0,(topic,result.stderr)
        assert result.stdout.strip() in lesson,topic
        parsed=json.loads(result.stdout)
        original=json.loads((EVIDENCE/(topic+'-example.json')).read_text())
        assert parsed==original['parsed'],topic
        records.append(dict(topic=topic,command=['python',(folder/'python/example.py').relative_to(ROOT).as_posix()],returncode=result.returncode,sections=25,output=result.stdout,parsed=parsed))
    if not args.check_only:(EVIDENCE/'examples-results.json').write_text(json.dumps(records,indent=2)+'\n')
    print('6 executed examples and exact25-section lessons passed')


if __name__=='__main__':main()
