"""Uniform Cost Search: goal-pop optimality, cost validation and independent oracles."""
from fractions import Fraction
import json
import math
import random
import subprocess
import sys

import pytest

pytestmark = pytest.mark.oracle


def successors_of(edges, n):
    table = [[] for _ in range(n)]
    for index, (u, v, cost) in enumerate(edges):
        table[u].append((index, v, cost))
    return table.__getitem__


def run(algorithm, edges, n, start, goals):
    return algorithm.uniform_cost_search(start, set(goals).__contains__, successors_of(edges, n))


def test_single_edge_and_goal_is_initial_state(algorithm):
    one = run(algorithm, [(0, 1, 7)], 2, 0, {1})
    assert one.states == (0, 1) and one.actions == (0,) and one.cost == 7
    zero = run(algorithm, [(0, 1, 7)], 2, 0, {0})
    assert zero.states == (0,) and zero.cost == 0 and zero.stats["expanded"] == 0


def test_cheapest_route_found_after_a_more_expensive_route_is_generated(algorithm):
    # The goal is generated first through the direct cost-10 edge; UCS must not stop then.
    edges = [(0, 3, 10), (0, 1, 1), (1, 2, 1), (2, 3, 1)]
    result = run(algorithm, edges, 4, 0, {3})
    assert result.states == (0, 1, 2, 3) and result.actions == (1, 2, 3) and result.cost == 3
    assert result.stats["improvements"] == 1 and result.stats["stale_skipped"] == 0


def test_stale_heap_entries_are_skipped_and_parents_follow_the_best_path(algorithm):
    edges = [(0, 1, 5), (0, 2, 1), (2, 1, 1), (1, 3, 1), (0, 4, 9)]
    result = run(algorithm, edges, 5, 0, {4})
    assert result.cost == 9 and result.states == (0, 4)
    assert result.stats["stale_skipped"] == 1  # The cost-5 entry for state 1 is popped after improvement.
    via = run(algorithm, edges, 5, 0, {3})
    assert via.states == (0, 2, 1, 3) and via.cost == 3  # Not the stale parent 0 -> 1.


def test_zero_cost_edges_cycles_and_self_loops(algorithm):
    edges = [(0, 1, 0), (1, 0, 0), (1, 1, 0), (1, 2, 0), (2, 3, 2), (0, 3, 3)]
    result = run(algorithm, edges, 4, 0, {3})
    assert result.cost == 2 and result.states == (0, 1, 2, 3)


def test_equal_cost_routes_break_ties_by_insertion_order(algorithm):
    edges = [(0, 1, 1), (0, 2, 1), (1, 3, 1), (2, 3, 1)]
    first = run(algorithm, edges, 4, 0, {3})
    assert first.states == (0, 1, 3) and first == run(algorithm, edges, 4, 0, {3})
    swapped = run(algorithm, [(0, 2, 1), (0, 1, 1), (2, 3, 1), (1, 3, 1)], 4, 0, {3})
    assert swapped.states == (0, 2, 3) and swapped.cost == first.cost


def test_multiple_goals_return_the_cheapest_goal(algorithm):
    edges = [(0, 1, 1), (1, 2, 1), (0, 3, 5), (2, 4, 1)]
    result = run(algorithm, edges, 5, 0, {3, 4})
    assert result.states[-1] == 4 and result.cost == 3


def test_fewest_edges_is_not_cheapest(algorithm):
    edges = [(0, 3, 9), (0, 1, 2), (1, 2, 2), (2, 3, 2)]
    result = run(algorithm, edges, 4, 0, {3})
    assert result.depth == 3 and result.cost == 6


def test_disconnected_goal_and_duplicate_successors(algorithm):
    assert run(algorithm, [(0, 1, 1), (2, 3, 1)], 4, 0, {3}).status == "FAILURE"
    duplicate = run(algorithm, [(0, 1, 4), (0, 1, 2), (0, 1, 2)], 2, 0, {1})
    assert duplicate.cost == 2 and duplicate.actions == (1,)


def test_exact_fraction_costs_and_float_costs(algorithm, oracles):
    exact = run(algorithm, oracles.fraction_graph(), 4, 0, {3})
    assert exact.cost == Fraction(3, 10) and exact.states == (0, 1, 3)  # Tie broken by insertion order.
    floats = run(algorithm, [(0, 1, 0.1), (1, 2, 0.2), (0, 2, 0.3)], 3, 0, {2})
    # 0.1 + 0.2 == 0.30000000000000004 > 0.3 in IEEE-754; no tolerance is applied.
    assert floats.states == (0, 2) and floats.cost == 0.3


@pytest.mark.parametrize("cost, error", [(-1, ValueError), (-0.5, ValueError), (math.nan, ValueError),
                                         (math.inf, ValueError), (-math.inf, ValueError), ("1", TypeError),
                                         (None, TypeError), (True, TypeError), (1 + 0j, TypeError)])
def test_invalid_costs_are_rejected(algorithm, cost, error):
    with pytest.raises(error):
        algorithm.uniform_cost_search(0, lambda s: False, lambda s: [("a", 1, cost)] if s == 0 else [])


@pytest.mark.parametrize("produced", [None, "ab", 3, [(1, 2)], [(1, 2, 3, 4)], [1]])
def test_malformed_records(algorithm, produced):
    with pytest.raises((TypeError, ValueError)):
        algorithm.uniform_cost_search(0, lambda s: False, lambda s: produced)


def test_invalid_callables_and_unhashable_states(algorithm):
    with pytest.raises(TypeError):
        algorithm.uniform_cost_search(0, "goal", lambda s: [])
    with pytest.raises(TypeError):
        algorithm.uniform_cost_search(0, lambda s: False, None)
    with pytest.raises(TypeError, match="hashable"):
        algorithm.uniform_cost_search([0], lambda s: False, lambda s: [])
    result = algorithm.uniform_cost_search([0], lambda s: s == [2], lambda s: [("inc", [s[0] + 1], 1)],
                                           state_key=tuple)
    assert result.states == ([0], [1], [2]) and result.cost == 2


def test_states_are_never_compared(algorithm):
    class Opaque:
        def __init__(self, label):
            self.label = label

        def __lt__(self, other):
            raise AssertionError("UCS must not order states")

        __gt__ = __le__ = __ge__ = __lt__
    nodes = [Opaque(i) for i in range(4)]
    edges = {0: [("a", nodes[1], 1), ("b", nodes[2], 1)], 1: [("c", nodes[3], 1)], 2: [("d", nodes[3], 1)], 3: []}
    result = algorithm.uniform_cost_search(nodes[0], lambda s: s.label == 3, lambda s: edges[s.label])
    assert result.cost == 2 and result.actions == ("a", "c")


def test_bellman_ford_and_exhaustive_oracles_on_random_graphs(algorithm, oracles):
    rng = random.Random(27201)
    for trial in range(700):
        n = rng.randint(1, 7)
        edges = oracles.random_graph(rng, n, rng.randint(0, 14), max_cost=rng.choice([0, 1, 3, 9]))
        start = rng.randrange(n)
        goals = set(rng.sample(range(n), rng.randint(0, min(3, n))))
        expected = oracles.cheapest_goal_cost(n, edges, start, goals)
        assert expected == oracles.exhaustive_cheapest(n, edges, start, goals)  # Oracles agree.
        result = run(algorithm, edges, n, start, goals)
        if expected is None:
            assert result.status == "FAILURE", trial
        else:
            assert result.found and result.cost == expected, (trial, edges, goals)
            oracles.assert_valid_path(edges, result.states, result.actions, start=start, goals=goals)
            assert oracles.path_cost(edges, result.actions) == result.cost


def test_metamorphic_relations(algorithm, oracles):
    rng = random.Random(27202)
    for _ in range(300):
        n = rng.randint(2, 7)
        edges = oracles.random_graph(rng, n, rng.randint(1, 12), max_cost=6)
        base = run(algorithm, edges, n, 0, {n - 1})
        # Permuting successor order may change the tied path but never the optimal cost.
        shuffled = edges[:]
        rng.shuffle(shuffled)
        assert run(algorithm, shuffled, n, 0, {n - 1}).cost == base.cost
        # Adding an expensive parallel copy of an existing edge cannot improve the cost.
        u, v, c = rng.choice(edges)
        assert run(algorithm, edges + [(u, v, c + 5)], n, 0, {n - 1}).cost == base.cost
        # Adding any nonnegative edge can only keep or lower the optimal cost.
        extra = run(algorithm, edges + [(rng.randrange(n), rng.randrange(n), rng.randint(0, 6))], n, 0, {n - 1})
        if base.found:
            assert extra.found and extra.cost <= base.cost
        # An unreachable component never changes the result.
        widened = run(algorithm, edges + [(n, n + 1, 0)], n + 2, 0, {n - 1})
        assert (widened.status, widened.states, widened.cost) == (base.status, base.states, base.cost)


def test_agrees_with_a5_dijkstra_on_graph_shaped_spaces(algorithm, oracles):
    import importlib.util
    from pathlib import Path
    path = Path(__file__).resolve().parents[4] / "dsa/graph-algorithms/dijkstra/python/solution.py"
    spec = importlib.util.spec_from_file_location("c1_a5_dijkstra", path)
    dijkstra = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dijkstra)
    rng = random.Random(27203)
    for _ in range(200):
        n = rng.randint(1, 8)
        edges = oracles.random_graph(rng, n, rng.randint(0, 16), max_cost=9)
        distances = dijkstra.dijkstra(n, [list(e) for e in edges], 0)["distance"]
        for goal in range(n):
            result = run(algorithm, edges, n, 0, {goal})
            assert result.cost == distances[goal]  # Both None when unreachable.


def test_cli(algorithm):
    script = algorithm.__file__
    ok = subprocess.run([sys.executable, script], input="4 4 0 1 3  0 1 1 1 3 5 0 2 2 2 3 2",
                        text=True, capture_output=True, timeout=30)
    assert ok.returncode == 0 and not ok.stderr
    out = json.loads(ok.stdout)
    assert out["states"] == [0, 2, 3] and out["cost"] == 4 and out["stats"]["improvements"] == 1
    for text in ["", "2 1 0 1 1 0 1 -1", "2 1 0 1 1 0 1 1000000000001", "2 1 0 1 1 0 1"]:
        bad = subprocess.run([sys.executable, script], input=text, text=True, capture_output=True, timeout=30)
        assert bad.returncode == 2 and bad.stderr.startswith("error:"), text
