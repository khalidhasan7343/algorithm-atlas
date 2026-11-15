"""Run every C1 example twice; require determinism and verbatim agreement with the lessons."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CATEGORY = 'artificial-intelligence/uninformed-search/'
EXAMPLES = {
    CATEGORY + 'depth-limited-search/python/example.py': CATEGORY + 'depth-limited-search/README.md',
    CATEGORY + 'iterative-deepening-dfs/python/example.py': CATEGORY + 'iterative-deepening-dfs/README.md',
    CATEGORY + 'uniform-cost-search/python/example.py': CATEGORY + 'uniform-cost-search/README.md',
    CATEGORY + 'bidirectional-search/python/example.py': CATEGORY + 'bidirectional-search/README.md',
    CATEGORY + 'examples/compare_uninformed.py': CATEGORY + 'README.md',
    CATEGORY + 'examples/shared_bfs_dfs.py': None,
}


def run(script):
    env = dict(os.environ, PYTHONHASHSEED='0')
    return subprocess.run([sys.executable, script], cwd=ROOT, env=env, capture_output=True, text=True, timeout=120, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    results = {}
    for script, lesson in EXAMPLES.items():
        first, second = run(script), run(script)
        assert first.stdout == second.stdout and not first.stderr and not second.stderr, script
        if lesson:
            text = (ROOT / lesson).read_text(encoding='utf-8')
            missing = [line for line in first.stdout.splitlines() if line.rstrip() not in text]
            assert not missing, (script, missing)
        results[script] = dict(stdout=first.stdout, deterministic=True, documented_in=lesson)
    if not args.check_only:
        (ROOT / 'docs/uninformed-search-evidence/examples-results.json').write_text(json.dumps(results, indent=2) + '\n')
    print(f'Verified {len(results)} deterministic C1 examples; documented outputs match.')


if __name__ == '__main__':
    main()
