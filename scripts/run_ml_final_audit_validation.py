"""Retain actual bounded Phase26 command output, timing, status and pytest JUnit."""
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/ml-final-audit-evidence'


def run(label, command):
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    count = len(list(EVIDENCE.glob(label + '-[0-9][0-9].json'))) + 1
    prefix = EVIDENCE / f'{label}-{count:02d}'
    while any(prefix.with_suffix(ext).exists() for ext in ('.json', '.txt', '.xml')):
        count += 1
        prefix = EVIDENCE / f'{label}-{count:02d}'
    actual = [sys.executable if i == 0 and v == 'python' else v for i, v in enumerate(command)]
    if '-m' in actual and 'pytest' in actual:
        actual.append('--junitxml=' + str(prefix.with_suffix('.xml')))
    started = datetime.now(ZoneInfo('Asia/Dhaka')).isoformat()
    before = time.monotonic()
    env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1', PYTHONHASHSEED='0')
    try:
        result = subprocess.run(actual, cwd=ROOT, env=env, capture_output=True, text=True, timeout=1200)
        code, output, timed_out = result.returncode, result.stdout + result.stderr, False
    except subprocess.TimeoutExpired as error:
        code, output, timed_out = None, str(error.stdout or '') + str(error.stderr or ''), True
    prefix.with_suffix('.txt').write_text(output)
    record = dict(label=label, command=command, actual_command=actual, cwd=str(ROOT),
                  started_at=started, elapsed_seconds=round(time.monotonic() - before, 3),
                  timeout_seconds=1200, timed_out=timed_out, returncode=code,
                  output=prefix.with_suffix('.txt').relative_to(ROOT).as_posix())
    prefix.with_suffix('.json').write_text(json.dumps(record, indent=2) + '\n')
    print(output[-6000:])
    print(json.dumps(record))
    return code if code is not None else 124


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 3 or args[1] != '--':
        raise SystemExit('Usage: run_ml_final_audit_validation.py LABEL -- COMMAND...')
    raise SystemExit(run(args[0], args[2:]))
