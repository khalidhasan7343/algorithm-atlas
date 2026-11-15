"""Bidirectional BFS: termination proof cases, reverse reconstruction and oracles."""
import json
import random
import subprocess
import sys

import pytest

pytestmark = pytest.mark.oracle


def tables(edges, n):
    forward = [[] for _ in range(n)]
    backward = [[] for _ in range(n)]
    for index, (u, v) in enumerate(edges):
        forward[u].append((index, v))
        backward[v].append((index, u))
    return forward.__getitem__, backward.__getitem__


def directed(algorithm, edges, n, start, goal):
    succ, pred = tables(edges, n)
    return algorithm.bidirectional_search(start, goal, succ, pred)


def undirected(algorithm, edges, n, start, goal):
    table = [[] for _ in range(n)]
    for index, (u, v) in enumerate(edges):
        table[u].append((index, v))
        table[v].append((index, u))
    return algorithm.bidirectional_search(start, goal, table.__getitem__, undirected=True)


def test_source_equals_goal(algorithm):
    result = directed(algorithm, [(0, 1)], 2, 1, 1)
    assert result.states == (1,) and result.actions == () and result.stats["meeting_index"] == 0


def test_direct_edge_and_longer_shortest_path(algorithm):
    assert directed(algorithm, [(0, 1)], 2, 0, 1).states == (0, 1)
    chain = [(i, i + 1) for i in range(6)]
    result = directed(algorithm, chain, 7, 0, 6)
    assert result.states == tuple(range(7)) and result.actions == tuple(range(6)) and result.cost == 6
    assert result.stats["forward_expanded"] >= 1 and result.stats["backward_expanded"] >= 1


def node_alternating_first_meeting(n, edges, start, goal):
    """A known-incorrect variant: alternate single expansions and stop as soon as a
    popped state was already expanded by the other side. Kept only as a contrast."""
    from collections import deque
    arcs = [[[] for _ in range(n)], [[] for _ in range(n)]]
    for u, v in edges:
        arcs[0][u].append(v)
        arcs[1][v].append(u)
    dist, queues, closed, side = [{start: 0}, {goal: 0}], [deque([start]), deque([goal])], [set(), set()], 0
    while queues[0] and queues[1]:
        u = queues[side].popleft()
        closed[side].add(u)
        if u in closed[1 - side]:
            return dist[0][u] + dist[1][u]
        for v in arcs[side][u]:
            if v not in dist[side]:
                dist[side][v] = dist[side][u] + 1
                queues[side].append(v)
        side = 1 - side
    return None


def test_first_meeting_pitfall_of_node_alternating_variants_is_avoided(algorithm):
    # Found by exhaustive search: the naive variant meets at state 1 (length 2)
    # although the direct edge 0 -> 3 has length 1.
    edges = [(1, 3), (0, 1), (0, 3)]
    assert node_alternating_first_meeting(4, edges, 0, 3) == 2
    result = directed(algorithm, edges, 4, 0, 3)
    assert result.states == (0, 3) and result.actions == (2,) and result.depth == 1


def test_accepted_length_meets_the_layer_termination_bound(algorithm, oracles):
    # The proof shows every path shorter than depth_f + depth_b + 1 is detected before
    # those layers are expanded, so an accepted meeting has length exactly
    # (unexpanded forward depth) + (unexpanded backward depth) at termination.
    rng = random.Random(27303)
    for _ in range(400):
        n = rng.randint(2, 9)
        edges = oracles.random_graph(rng, n, rng.randint(1, 16))
        result = directed(algorithm, edges, n, 0, n - 1)
        if result.found and result.depth:
            assert result.depth == result.stats["forward_depth"] + result.stats["backward_depth"]
            assert 0 <= result.stats["meeting_index"] < result.depth


def test_chain_meets_in_the_middle(algorithm):
    edges = [(i, i + 1) for i in range(8)]
    result = directed(algorithm, edges, 9, 0, 8)
    assert result.depth == 8
    assert result.stats["forward_depth"] == result.stats["backward_depth"] == 4
    assert result.states[result.stats["meeting_index"]] == 4  # Meeting edge 4 -> 5.


def test_multiple_meeting_candidates_and_shortest_paths_are_deterministic(algorithm):
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)]
    first = directed(algorithm, edges, 5, 0, 4)
    assert first.depth == 3 and first.states == (0, 1, 3, 4) and first == directed(algorithm, edges, 5, 0, 4)


def test_disconnected_components_and_no_solution(algorithm):
    result = directed(algorithm, [(0, 1), (2, 3)], 4, 0, 3)
    assert result.status == "FAILURE" and result.states == () and result.cost is None
    assert undirected(algorithm, [(0, 1), (1, 0), (2, 3)], 4, 0, 3).status == "FAILURE"


def test_cycles_self_loops_and_duplicate_edges(algorithm, oracles):
    edges = [(0, 0), (0, 1), (1, 0), (1, 2), (1, 2), (2, 1), (2, 3), (3, 3)]
    result = directed(algorithm, edges, 4, 0, 3)
    assert result.depth == 3
    oracles.assert_valid_path(edges, result.states, result.actions, start=0, goals={3})


def test_directed_orientation_uses_predecessors(algorithm):
    # 0 -> 1 <- 2: the goal 2 is unreachable although 1 is adjacent to both.
    assert directed(algorithm, [(0, 1), (2, 1)], 3, 0, 2).status == "FAILURE"
    # Treating successors as reverse edges would wrongly find 0 - 1 - 2 here.
    assert undirected(algorithm, [(0, 1), (2, 1)], 3, 0, 2).depth == 2


def test_directed_space_without_predecessors_is_rejected(algorithm):
    with pytest.raises(ValueError, match="predecessor"):
        algorithm.bidirectional_search(0, 1, lambda s: [("a", 1)])
    with pytest.raises(ValueError, match="either"):
        algorithm.bidirectional_search(0, 1, lambda s: [], lambda s: [], undirected=True)
    with pytest.raises(TypeError):
        algorithm.bidirectional_search(0, 1, lambda s: [], undirected=1)
    with pytest.raises(TypeError):
        algorithm.bidirectional_search(0, 1, lambda s: [], 5)


def test_inconsistent_predecessor_function_is_detected(algorithm):
    succ = {0: [("go", 1)], 1: [], 2: []}
    pred = {0: [], 1: [("go", 0)], 2: [("bogus", 1)]}  # Claims 1 -> 2, which does not exist.
    with pytest.raises(ValueError, match="successors does not contain"):
        algorithm.bidirectional_search(0, 2, succ.__getitem__, pred.__getitem__)
    with pytest.raises(ValueError, match="reverse transition"):
        algorithm.bidirectional_search(0, 2, {0: [("a", 1)], 1: [], 2: [("b", 1)]}.__getitem__, undirected=True)


@pytest.mark.parametrize("produced", [None, "xy", 4, [(1,)], [(1, 2, 3)]])
def test_malformed_successor_and_predecessor_records(algorithm, produced):
    with pytest.raises((TypeError, ValueError)):
        algorithm.bidirectional_search(0, 1, lambda s: produced, lambda s: [])
    with pytest.raises((TypeError, ValueError)):
        # A valid forward step makes the backward side the shallower one to expand next.
        algorithm.bidirectional_search(0, 1, lambda s: [("a", 2)] if s == 0 else [], lambda s: produced)


def test_unequal_frontiers_expand_the_smaller_side(algorithm):
    # The start fans out to six states; the goal has one predecessor chain.
    edges = [(0, i) for i in range(1, 7)] + [(6, 7), (7, 8), (8, 9)]
    result = directed(algorithm, edges, 10, 0, 9)
    assert result.states == (0, 6, 7, 8, 9)
    assert result.stats["forward_expanded"] == 1 and result.stats["backward_expanded"] == 3


def test_general_states_with_state_key_and_reversible_moves(algorithm):
    def moves(state):  # Lists need a state_key; each move has an inverse.
        x, y = state
        return [("east", [x + 1, y]), ("west", [x - 1, y]), ("north", [x, y + 1]), ("south", [x, y - 1])]
    result = algorithm.bidirectional_search([0, 0], [2, 1], moves, undirected=True, state_key=tuple)
    assert result.depth == 3 and result.states[0] == [0, 0] and result.states[-1] == [2, 1]
    assert result.actions.count("east") == 2 and result.actions.count("north") == 1
    with pytest.raises(TypeError, match="hashable"):
        algorithm.bidirectional_search([0, 0], [2, 1], moves, undirected=True)


def test_independent_bfs_and_exhaustive_oracles_on_random_graphs(algorithm, oracles):
    rng = random.Random(27301)
    for trial in range(800):
        n = rng.randint(1, 8)
        edges = oracles.random_graph(rng, n, rng.randint(0, 14))
        start, goal = rng.randrange(n), rng.randrange(n)
        expected = oracles.bfs_distances(n, edges, start)[goal]
        result = directed(algorithm, edges, n, start, goal)
        if expected is None:
            assert result.status == "FAILURE", trial
        else:
            assert result.found and result.depth == expected, (trial, edges, start, goal)
            oracles.assert_valid_path(edges, result.states, result.actions, start=start, goals={goal})
            assert len(set(result.states)) == len(result.states)
        if n <= 6:
            paths = [p for p in oracles.simple_paths(n, edges, start, n) if p[0][-1] == goal]
            shortest = min((len(a) for _, a in paths), default=None)
            assert shortest == result.depth
        both = undirected(algorithm, edges, n, start, goal)
        expected_u = oracles.bfs_distances(n, edges, start, directed=False)[goal]
        assert both.depth == expected_u
        if both.found:
            oracles.assert_valid_path(edges, both.states, both.actions, start=start, goals={goal}, directed=False)


def test_metamorphic_relations(algorithm, oracles):
    rng = random.Random(27302)
    for _ in range(300):
        n = rng.randint(2, 8)
        edges = oracles.random_graph(rng, n, rng.randint(1, 14))
        base = undirected(algorithm, edges, n, 0, n - 1)
        # Reversing an undirected search preserves the shortest length.
        assert undirected(algorithm, edges, n, n - 1, 0).depth == base.depth
        # Agreement with single-direction BFS and invariance to an unreachable component.
        assert base.depth == oracles.bfs_distances(n, edges, 0, directed=False)[n - 1]
        widened = undirected(algorithm, edges + [(n, n + 1)], n + 2, 0, n - 1)
        assert widened.depth == base.depth


def test_cli(algorithm):
    script = algorithm.__file__
    ok = subprocess.run([sys.executable, script], input="6 6 0 5 0  0 1 1 2 2 5 0 3 3 4 4 5",
                        text=True, capture_output=True, timeout=30)
    assert ok.returncode == 0 and not ok.stderr
    out = json.loads(ok.stdout)
    assert out["states"] == [0, 1, 2, 5] and out["actions"] == [0, 1, 2] and out["stats"]["meeting_index"] == 1
    for text in ["", "2 0 0 1 2", "2 0 0 2 1", "2 1 0 1 1 0"]:
        bad = subprocess.run([sys.executable, script], input=text, text=True, capture_output=True, timeout=30)
        assert bad.returncode == 2 and bad.stderr.startswith("error:"), text
