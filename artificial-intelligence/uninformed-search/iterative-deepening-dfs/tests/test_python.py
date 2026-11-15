"""IDDFS: shallowest solutions, iteration semantics and an independent BFS oracle."""
import json
import random
import subprocess
import sys

import pytest

pytestmark = pytest.mark.oracle


def successors_of(edges, n):
    table = [[] for _ in range(n)]
    for index, (u, v) in enumerate(edges):
        table[u].append((index, v))
    return table.__getitem__


def run(algorithm, edges, n, start, goals, max_depth=None):
    return algorithm.iterative_deepening_search(start, set(goals).__contains__, successors_of(edges, n),
                                                max_depth=max_depth)


def test_goal_at_depth_zero_and_one(algorithm):
    zero = run(algorithm, [(0, 1)], 2, 0, {0})
    assert zero.status == "FOUND" and zero.states == (0,) and zero.stats["iterations"] == 1
    one = run(algorithm, [(0, 1)], 2, 0, {1})
    assert one.states == (0, 1) and one.actions == (0,) and one.stats["iterations"] == 2


def test_shallowest_of_several_solutions_is_returned(algorithm):
    # DFS order reaches goal 4 at depth 4 first; IDDFS must return goal 5 at depth 2.
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 6), (6, 5)]
    result = run(algorithm, edges, 7, 0, {4, 5})
    assert result.states == (0, 6, 5) and result.depth == 2
    assert result.stats["iterations"] == 3 and result.stats["final_limit"] == 2


def test_iteration_count_and_totals_match_individual_dls_runs(algorithm):
    import importlib.util
    from pathlib import Path
    path = Path(__file__).parents[2] / "depth-limited-search/python/solution.py"
    spec = importlib.util.spec_from_file_location("c1_iddfs_dls", path)
    dls = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dls)
    edges = [(0, 1), (1, 2), (2, 3), (1, 0), (0, 4), (4, 3)]
    result = run(algorithm, edges, 5, 0, {3})
    runs = [dls.depth_limited_search(0, {3}.__contains__, successors_of(edges, 5), limit) for limit in range(3)]
    assert [r.status for r in runs] == ["CUTOFF", "CUTOFF", "FOUND"]
    assert result.stats["iterations"] == 3
    for name in ("expanded", "generated", "goal_tests", "boundary_checks", "cycle_skips"):
        assert result.stats[name] == sum(r.stats[name] for r in runs), name
    assert (result.states, result.actions) == (runs[-1].states, runs[-1].actions)


def test_definitive_failure_stops_without_max_depth(algorithm):
    result = run(algorithm, [(0, 1), (1, 2), (2, 0)], 4, 0, {3})
    assert result.status == "FAILURE" and result.stats["iterations"] == 3  # Limits 0, 1, 2.


def test_max_depth_cutoff_propagates_from_dls(algorithm):
    chain = [(i, i + 1) for i in range(6)]
    capped = run(algorithm, chain, 7, 0, {6}, max_depth=3)
    assert capped.status == "CUTOFF" and capped.stats["iterations"] == 4 and capped.stats["final_limit"] == 3
    exact = run(algorithm, chain, 7, 0, {6}, max_depth=6)
    assert exact.status == "FOUND" and exact.depth == 6
    assert run(algorithm, chain, 7, 0, {0}, max_depth=0).found
    assert run(algorithm, chain, 7, 0, {6}, max_depth=0).status == "CUTOFF"


def test_cycles_repeated_states_and_determinism(algorithm):
    edges = [(0, 1), (1, 0), (0, 2), (2, 1), (1, 3), (2, 3), (3, 3)]
    first = run(algorithm, edges, 4, 0, {3})
    assert first.states == (0, 1, 3) and first == run(algorithm, edges, 4, 0, {3})


@pytest.mark.parametrize("max_depth, error", [(-1, ValueError), (True, TypeError), (2.0, TypeError)])
def test_invalid_maximum_depth(algorithm, max_depth, error):
    with pytest.raises(error):
        algorithm.iterative_deepening_search(0, lambda s: False, lambda s: [], max_depth=max_depth)


def test_invalid_callables_and_records(algorithm):
    with pytest.raises(TypeError):
        algorithm.iterative_deepening_search(0, None, lambda s: [])
    with pytest.raises(TypeError):
        algorithm.iterative_deepening_search(0, lambda s: False, lambda s: [], state_key="key")
    with pytest.raises(ValueError):
        algorithm.iterative_deepening_search(0, lambda s: False, lambda s: [(1, 2, 3)])
    with pytest.raises(TypeError, match="hashable"):
        algorithm.iterative_deepening_search({0}, lambda s: False, lambda s: [])


def test_infinite_state_space_with_max_depth(algorithm):
    # Integers with +1/*2 moves form an infinite space; the shallowest route to 10 has 4 actions.
    result = algorithm.iterative_deepening_search(
        1, lambda s: s == 10, lambda s: [("+1", s + 1), ("*2", s * 2)], max_depth=8)
    assert result.depth == 4 and result.states[-1] == 10
    assert algorithm.iterative_deepening_search(1, lambda s: s < 0, lambda s: [("+1", s + 1)],
                                                max_depth=5).status == "CUTOFF"


def test_independent_bfs_oracle_on_random_unweighted_graphs(algorithm, oracles):
    rng = random.Random(27101)
    for trial in range(700):
        n = rng.randint(1, 8)
        edges = oracles.random_graph(rng, n, rng.randint(0, 14))
        start = rng.randrange(n)
        goals = set(rng.sample(range(n), rng.randint(0, min(3, n))))
        expected = oracles.nearest_goal_depth(n, edges, start, goals)
        cap = rng.choice([None, rng.randint(0, 4)])
        result = run(algorithm, edges, n, start, goals, cap)
        if expected is None:
            assert result.status == ("FAILURE" if cap is None else result.status), trial
            assert result.status in ("FAILURE", "CUTOFF") and not result.found
        elif cap is not None and expected > cap:
            assert result.status == "CUTOFF", trial
        else:
            assert result.found and result.depth == expected, (trial, edges, goals)
            oracles.assert_valid_path(edges, result.states, result.actions, start=start, goals=goals)


def test_metamorphic_successor_permutation_preserves_depth(algorithm, oracles):
    rng = random.Random(27102)
    for _ in range(300):
        n = rng.randint(2, 8)
        edges = oracles.random_graph(rng, n, rng.randint(1, 14))
        shuffled = edges[:]
        rng.shuffle(shuffled)
        a, b = run(algorithm, edges, n, 0, {n - 1}), run(algorithm, shuffled, n, 0, {n - 1})
        assert a.status == b.status and a.depth == b.depth


def test_cli(algorithm):
    script = algorithm.__file__
    ok = subprocess.run([sys.executable, script], input="5 5 0 -1 1 4  0 1 1 2 2 4 0 3 3 4",
                        text=True, capture_output=True, timeout=30)
    assert ok.returncode == 0 and not ok.stderr
    out = json.loads(ok.stdout)
    assert out["status"] == "FOUND" and out["states"] == [0, 3, 4] and out["stats"]["iterations"] == 3
    capped = subprocess.run([sys.executable, script], input="3 2 0 1 1 2 0 1 1 2", text=True,
                            capture_output=True, timeout=30)
    assert json.loads(capped.stdout)["status"] == "CUTOFF"
    for text in ["", "2 0 0 -2 0", "2 0 0 0 3 0 1 1", "2 1 0 0 1 1 0"]:
        bad = subprocess.run([sys.executable, script], input=text, text=True, capture_output=True, timeout=30)
        assert bad.returncode == 2 and bad.stderr.startswith("error:"), text
