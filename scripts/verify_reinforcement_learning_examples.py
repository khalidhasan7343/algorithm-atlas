"""Execute B8 worked examples, compare independent hand results and exact lessons."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import time

import numpy as np
from validate_catalog import SECTIONS

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/reinforcement-learning-evidence'
EXPECTED = {
    'q-learning': dict(update=5.), 'sarsa': dict(update=1.85),
    'deep-q-networks': dict(loss=.5, bias_gradient=[0., -1.]),
    'reinforce-policy-gradient': dict(loss=float(np.log(2)), bias_gradient=[.5, -.5]),
    'advantage-actor-critic': dict(actor_loss=float(.75 * np.log(2)), critic_loss=.28125),
    'asynchronous-advantage-actor-critic': dict(updates=2, workers_alive=0),
    'proximal-policy-optimization': dict(loss=.1),
    'deep-deterministic-policy-gradient': dict(action=1., target_bias=.5),
    'monte-carlo-tree-search': dict(action=1, root_visits=200),
}


def verify(topics):
    results = []
    for topic in topics:
        folder = ROOT / 'machine-learning/reinforcement-learning' / topic
        text = (folder / 'README.md').read_text()
        assert re.findall(r'^##[ \t]+(.+)$', text, re.M) == [f'{i}. {title}' for i, title in enumerate(SECTIONS, 1)], topic
        command = [sys.executable, str(folder / 'python/example.py')]
        before = time.monotonic()
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=15)
        assert result.returncode == 0, (topic, result.stdout, result.stderr)
        actual = json.loads(result.stdout)
        assert actual.keys() == EXPECTED[topic].keys()
        for key in actual:
            np.testing.assert_allclose(actual[key], EXPECTED[topic][key], rtol=1e-13, atol=1e-13)
        assert result.stdout.strip() in text, f'{topic}: documented output differs from execution'
        results.append(dict(topic=topic, command=command, returncode=0, sections=25,
                            output=result.stdout.strip(), elapsed_seconds=round(time.monotonic() - before, 4)))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('topics', nargs='*', choices=list(EXPECTED))
    args = parser.parse_args()
    results = verify(args.topics or list(EXPECTED))
    if not args.check_only:
        (EVIDENCE / 'examples-results.json').write_text(json.dumps(results, indent=2) + '\n')
    print(f'{len(results)} executed examples and exact25-section lessons passed')


if __name__ == '__main__':
    main()
