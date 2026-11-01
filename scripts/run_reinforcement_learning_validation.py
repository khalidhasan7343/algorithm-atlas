"""Execute one bounded check and retain actual output, status, time and JUnit.

Usage: python scripts/run_reinforcement_learning_validation.py LABEL -- COMMAND...
Use the invoking interpreter's absolute path when the command starts with python.
"""
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/reinforcement-learning-evidence'


def run(label, command, timeout=1200, cwd=ROOT):
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    existing = list(EVIDENCE.glob(label + '-*.json'))
    sequence = len(existing) + 1
    prefix = EVIDENCE / f'{label}-{sequence:02d}'
    actual = [sys.executable if item == 'python' and index == 0 else item for index, item in enumerate(command)]
    if '-m' in actual and 'pytest' in actual:
        actual.append('--junitxml=' + str(prefix.with_suffix('.xml')))
    started = datetime.now(ZoneInfo('Asia/Dhaka')).isoformat()
    before = time.monotonic()
    environment = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONHASHSEED='0')
    try:
        result = subprocess.run(actual, cwd=cwd, env=environment, capture_output=True, text=True, timeout=timeout)
        code, output, timed_out = result.returncode, result.stdout + result.stderr, False
    except subprocess.TimeoutExpired as error:
        code, timed_out = None, True
        output = str(error.stdout or '') + str(error.stderr or '')
    prefix.with_suffix('.txt').write_text(output)
    record = dict(label=label, command=command, actual_command=actual, cwd=str(cwd),
                  started_at=started, elapsed_seconds=round(time.monotonic() - before, 3),
                  timeout_seconds=timeout, timed_out=timed_out, returncode=code,
                  output=prefix.with_suffix('.txt').relative_to(ROOT).as_posix())
    prefix.with_suffix('.json').write_text(json.dumps(record, indent=2) + '\n')
    print(output[-6000:])
    print(json.dumps(record))
    return code if code is not None else 124


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 3 or args[1] != '--':
        raise SystemExit(__doc__)
    raise SystemExit(run(args[0], args[2:]))
