"""Run the Phase26 independent B1–B13 oracle scripts and record PASS/FAIL evidence."""
from datetime import datetime
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ORACLES = ROOT / 'scripts/ml_final_audit_oracles'
OUTPUT = ROOT / 'docs/ml-final-audit-evidence/oracle-results.json'


def main():
    records = {}
    for script in sorted(ORACLES.glob('oracle_b*.py'), key=lambda p: int(re.search(r'b(\d+)', p.stem).group(1))):
        started = time.monotonic()
        result = subprocess.run([sys.executable, '-I', str(script)], cwd=ROOT, capture_output=True, text=True, timeout=1200)
        lines = [l for l in result.stdout.splitlines() if l.startswith(('PASS ', 'FAIL '))]
        summary = re.search(r'SUMMARY (\d+) / (\d+) passed', result.stdout)
        records[script.stem] = dict(script=str(script.relative_to(ROOT)), returncode=result.returncode,
                                    elapsed_seconds=round(time.monotonic() - started, 2),
                                    passed=int(summary.group(1)) if summary else None, total=int(summary.group(2)) if summary else None,
                                    checks=[dict(status=l[:4], check=l[5:]) for l in lines],
                                    stderr_tail=result.stderr[-2000:] if result.returncode else '')
        print(f"{script.stem}: {records[script.stem]['passed']}/{records[script.stem]['total']} passed (exit {result.returncode})", flush=True)
    passed = sum(r['passed'] or 0 for r in records.values()); total = sum(r['total'] or 0 for r in records.values())
    OUTPUT.write_text(json.dumps(dict(executed_at=datetime.now(ZoneInfo('Asia/Dhaka')).isoformat(), python=sys.version.split()[0],
                                       total_checks=total, passed_checks=passed, all_passed=passed == total and all(r['returncode'] == 0 for r in records.values()),
                                       scripts=records), indent=2) + '\n')
    print(f'TOTAL {passed}/{total} passed -> {OUTPUT.relative_to(ROOT)}')
    return 0 if passed == total and all(r['returncode'] == 0 for r in records.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
