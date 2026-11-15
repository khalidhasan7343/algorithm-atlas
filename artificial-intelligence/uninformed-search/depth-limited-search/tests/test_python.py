"""Depth-Limited Search: contract, cutoff/failure semantics and independent oracles."""
import json
import random
import subprocess
import sys

import pytest

pytestmark = pytest.mark.oracle


def graph_problem(edges, n=None):
    n = n if n is not None else 1 + max((max(e[0], e[1]) for e in edges), default=0)
    table = [[] for _ in range(n)]
    for index, (u, v) in enumerate(edges):
        table[u].append((index, v))
    return table.__getitem__


def run(algorithm, edges, start, goals, limit, n=None):
    return algorithm.depth_limited_search(start, set(goals).__contains__, graph_problem(edges, n), limit)


CHAIN = [(0, 1), (1, 2), (2, 3)]


def test_goal_at_initial_state_is_depth_zero(algorithm):
    result = run(algorithm, CHAIN, 0, {0}, 0)
    assert result.status == "FOUND" and result.states == (0,) and result.actions == () and result.depth == 0
    assert result.stats["expanded"] == 0 and result.stats["goal_tests"] == 1


def test_limit_is_inclusive_and_child_beyond_limit_is_not_goal_tested(algorithm):
    exact = run(algorithm, CHAIN, 0, {3}, 3)
    assert exact.status == "FOUND" and exact.states == (0, 1, 2, 3) and exact.actions == (0, 1, 2)
    beyond = run(algorithm, CHAIN, 0, {3}, 2)
    assert beyond.status == "CUTOFF" and beyond.states == () and beyond.cost is None
    tested = []

    def goal(state):
        tested.append(state)
        return state == 3
    algorithm.depth_limited_search(0, goal, graph_problem(CHAIN), 2)
    assert tested == [0, 1, 2]  # State 3 sits at depth 3 = limit + 1 and is never tested.


def test_zero_depth_distinguishes_cutoff_from_failure(algorithm):
    assert run(algorithm, CHAIN, 0, {1}, 0).status == "CUTOFF"
    assert run(algorithm, [], 0, {1}, 0, n=2).status == "FAILURE"  # Empty successor list.
    assert run(algorithm, [(0, 0)], 0, {1}, 0, n=2).status == "FAILURE"  # Only a self-loop.


def test_failure_means_the_finite_space_was_exhausted(algorithm):
    result = run(algorithm, [(0, 1), (1, 2), (2, 0)], 0, {3}, 10, n=4)
    assert result.status == "FAILURE" and result.stats["cycle_skips"] == 1


def test_cycles_are_handled_path_locally_not_with_a_global_visited_set(algorithm):
    # State 3 is first reached at depth 3 (the limit) and later at depth 1. A global
    # visited set would skip the shallow occurrence and report a false CUTOFF.
    edges = [(0, 1), (1, 2), (2, 3), (0, 3), (3, 4)]
    result = run(algorithm, edges, 0, {4}, 3)
    assert result.status == "FOUND" and result.states == (0, 3, 4) and result.actions == (3, 4)


def test_duplicate_successors_and_multiple_paths_keep_a_simple_valid_path(algorithm, oracles):
    edges = [(0, 1), (0, 1), (1, 0), (1, 2), (0, 2), (2, 2)]
    result = run(algorithm, edges, 0, {2}, 4)
    assert result.states == (0, 1, 2) and result.actions == (0, 3)
    oracles.assert_valid_path(edges, result.states, result.actions, start=0, goals={2})
    assert len(set(result.states)) == len(result.states)


def test_deterministic_first_path_in_successor_order(algorithm):
    edges = [(0, 1), (0, 2), (1, 3), (2, 3)]
    first = run(algorithm, edges, 0, {3}, 3)
    assert first.states == (0, 1, 3) and first == run(algorithm, edges, 0, {3}, 3)
    reordered = run(algorithm, [(0, 2), (0, 1), (2, 3), (1, 3)], 0, {3}, 3)
    assert reordered.states == (0, 2, 3)  # Ties follow successor order; depth stays 2.


def test_general_states_actions_and_state_key():
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("c1_dls_general", Path(__file__).parents[1] / "python/solution.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def moves(state):  # Lists are unhashable; state_key gives them an identity.
        a, b = state
        return [("fill-a", [3, b]), ("pour-a-b", [a - min(a, 4 - b), b + min(a, 4 - b)]), ("empty-b", [a, 0])]
    result = module.depth_limited_search([0, 0], lambda s: s[1] == 3, moves, 6, state_key=tuple)
    assert result.found and result.states[0] == [0, 0] and result.states[-1][1] == 3
    with pytest.raises(TypeError, match="hashable"):
        module.depth_limited_search([0, 0], lambda s: False, moves, 1)
    with pytest.raises(TypeError, match="hashable"):
        module.depth_limited_search((0, 0), lambda s: False, moves, 1)  # Unhashable child state.


@pytest.mark.parametrize("limit, error", [(-1, ValueError), (True, TypeError), (1.0, TypeError), (None, TypeError)])
def test_invalid_limits(algorithm, limit, error):
    with pytest.raises(error):
        algorithm.depth_limited_search(0, lambda s: False, lambda s: [], limit)


@pytest.mark.parametrize("produced", [None, 5, "ab", {1: 2}, [(1,)], [(1, 2, 3)], [7]])
def test_malformed_successor_records(algorithm, produced):
    with pytest.raises((TypeError, ValueError)):
        algorithm.depth_limited_search(0, lambda s: False, lambda s: produced, 2)


def test_non_callable_arguments(algorithm):
    with pytest.raises(TypeError):
        algorithm.depth_limited_search(0, 5, lambda s: [], 1)
    with pytest.raises(TypeError):
        algorithm.depth_limited_search(0, lambda s: False, [], 1)
    with pytest.raises(TypeError):
        algorithm.depth_limited_search(0, lambda s: False, lambda s: [], 1, state_key=3)


def test_result_is_immutable(algorithm):
    result = run(algorithm, CHAIN, 0, {2}, 2)
    with pytest.raises(AttributeError):
        result.status = "FAILURE"
    with pytest.raises(TypeError):
        result.stats["expanded"] = 0


def test_exhaustive_bounded_oracle_on_random_graphs(algorithm, oracles):
    rng = random.Random(27001)
    for trial in range(600):
        n = rng.randint(1, 6)
        edges = oracles.random_graph(rng, n, rng.randint(0, 10))
        start, limit = rng.randrange(n), rng.randint(0, 5)
        goals = set(rng.sample(range(n), rng.randint(0, min(2, n))))
        status, states, actions = oracles.dls_expected(n, edges, start, goals, limit)
        result = run(algorithm, edges, start, goals, limit, n=n)
        assert (result.status, result.states, result.actions) == (status, states, actions), (trial, edges)
        if result.found:
            oracles.assert_valid_path(edges, result.states, result.actions, start=start, goals=goals)
            assert result.depth <= limit and result.cost == result.depth


def test_metamorphic_limit_and_unreachable_component(algorithm, oracles):
    rng = random.Random(27002)
    for _ in range(300):
        n = rng.randint(2, 6)
        edges = oracles.random_graph(rng, n, rng.randint(1, 9))
        goals, limit = {n - 1}, rng.randint(0, 4)
        base = run(algorithm, edges, 0, goals, limit, n=n)
        # Increasing the limit never invalidates solvability, and a found path stays valid.
        larger = run(algorithm, edges, 0, goals, limit + 1, n=n)
        if base.found:
            assert larger.found and larger.depth <= limit + 1
        if base.status == "FAILURE":
            assert larger.status == "FAILURE"
        # An unreachable component (new vertices, edges only among themselves) changes nothing.
        extra = edges + [(n, n + 1), (n + 1, n)]
        widened = run(algorithm, extra, 0, goals, limit, n=n + 2)
        assert (widened.status, widened.states, widened.actions) == (base.status, base.states, base.actions)


def test_long_chain_uses_explicit_stack(algorithm):
    edges = [(i, i + 1) for i in range(5000)]
    result = run(algorithm, edges, 0, {5000}, 5000)
    assert result.found and result.depth == 5000 and result.states[-1] == 5000


def test_cli_success_and_errors(algorithm):
    script = algorithm.__file__
    ok = subprocess.run([sys.executable, script], input="5 5 0 2 1 4  0 1 1 2 2 4 0 3 3 4",
                        text=True, capture_output=True, timeout=30)
    assert ok.returncode == 0 and not ok.stderr
    assert json.loads(ok.stdout) == dict(status="FOUND", states=[0, 3, 4], actions=[3, 4], cost=2, depth=2,
                                         stats=dict(expanded=3, generated=5, goal_tests=5, boundary_checks=1,
                                                    cycle_skips=0, max_depth_reached=2))
    for text in ["", "1 0 0", "1 0 0 -1 0", "2 1 0 1 1 1 0 2", "1 0 0 0 0 9", "1 0 0 0 0 1.5", "1 0 00 0 0"]:
        bad = subprocess.run([sys.executable, script], input=text, text=True, capture_output=True, timeout=30)
        assert bad.returncode == 2 and bad.stderr.startswith("error:"), text


def test_dls_is_not_optimal(algorithm):
    result = run(algorithm, [(0, 1), (1, 2), (2, 3), (0, 3)], 0, {3}, 3)
    assert result.states == (0, 1, 2, 3) and result.depth == 3  # The 1-action route exists.
