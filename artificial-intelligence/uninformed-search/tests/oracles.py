"""Independent C1 test oracles for tiny explicit graphs.

Nothing here imports production C1 code or the A5 implementations. Graphs use
vertices ``0..n-1`` and edge-index actions, matching the canonical CLIs:
``edges[i] = (u, v)`` or ``(u, v, cost)`` is action ``i`` from ``u`` to ``v``.
"""
from __future__ import annotations

from collections import deque
from fractions import Fraction
import random


def out_arcs(n, edges, *, directed=True, reverse=False):
    arcs = [[] for _ in range(n)]
    for index, edge in enumerate(edges):
        u, v = (edge[1], edge[0]) if reverse else (edge[0], edge[1])
        cost = edge[2] if len(edge) == 3 else 1
        arcs[u].append((index, v, cost))
        if not directed:
            arcs[v].append((index, u, cost))
    return arcs


def random_graph(rng: random.Random, n: int, m: int, *, max_cost: int | None = None):
    """Directed multigraph with possible self-loops, duplicates and zero costs."""
    edges = []
    for _ in range(m):
        u, v = rng.randrange(n), rng.randrange(n)
        edges.append((u, v) if max_cost is None else (u, v, rng.randint(0, max_cost)))
    return edges


def simple_paths(n, edges, start, max_length, *, directed=True):
    """All simple paths from start with at most max_length actions, in DFS preorder.

    Recursive enumeration in adjacency order: the first goal-ending path in this
    order is the path a depth-first search with path-local cycle checks returns.
    """
    arcs = out_arcs(n, edges, directed=directed)
    paths = []

    def extend(states, actions):
        paths.append((tuple(states), tuple(actions)))
        if len(actions) == max_length:
            return
        for index, v, _ in arcs[states[-1]]:
            if v not in states:
                extend(states + [v], actions + [index])

    extend([start], [])
    return paths


def dls_expected(n, edges, start, goals, limit):
    """Expected DLS status and first-found path from exhaustive bounded enumeration."""
    arcs = out_arcs(n, edges)
    paths = simple_paths(n, edges, start, limit)
    for states, actions in paths:
        if states[-1] in goals:
            return "FOUND", states, actions
    truncated = any(len(actions) == limit and any(v not in states for _, v, _ in arcs[states[-1]])
                    for states, actions in paths)
    return ("CUTOFF" if truncated else "FAILURE"), (), ()


def bfs_distances(n, edges, start, *, directed=True, reverse=False):
    """Plain queue BFS over the explicit graph (unit costs)."""
    arcs = out_arcs(n, edges, directed=directed, reverse=reverse)
    distance = [None] * n
    distance[start] = 0
    queue = deque([start])
    while queue:
        u = queue.popleft()
        for _, v, _ in arcs[u]:
            if distance[v] is None:
                distance[v] = distance[u] + 1
                queue.append(v)
    return distance


def nearest_goal_depth(n, edges, start, goals):
    distance = bfs_distances(n, edges, start)
    depths = [distance[g] for g in goals if distance[g] is not None]
    return min(depths) if depths else None


def bellman_ford(n, edges, start):
    """Bellman-Ford distances; costs here are nonnegative so no cycle check is needed."""
    distance = [None] * n
    distance[start] = 0
    for _ in range(max(n - 1, 0)):
        changed = False
        for u, v, cost in edges:
            if distance[u] is not None and (distance[v] is None or distance[u] + cost < distance[v]):
                distance[v] = distance[u] + cost
                changed = True
        if not changed:
            break
    return distance


def cheapest_goal_cost(n, edges, start, goals):
    distance = bellman_ford(n, edges, start)
    costs = [distance[g] for g in goals if distance[g] is not None]
    return min(costs) if costs else None


def exhaustive_cheapest(n, edges, start, goals):
    """Minimum cost over every simple path; optimal paths may be taken simple when costs >= 0."""
    best = None
    for states, actions in simple_paths(n, edges, start, n):
        if states[-1] in goals:
            cost = sum(edges[i][2] for i in actions)
            best = cost if best is None or cost < best else best
    return best


def path_cost(edges, actions):
    return sum((edges[i][2] if len(edges[i]) == 3 else 1) for i in actions)


def assert_valid_path(edges, states, actions, *, start, goals, directed=True):
    """Every action must be the transition between consecutive returned states."""
    assert states[0] == start and states[-1] in goals
    assert len(states) == len(actions) + 1
    for i, action in enumerate(actions):
        u, v = edges[action][0], edges[action][1]
        forward_ok = (u, v) == (states[i], states[i + 1])
        assert forward_ok or (not directed and (v, u) == (states[i], states[i + 1])), (i, action)


def fraction_graph():
    """Exact rational costs where float rounding could otherwise hide ties."""
    return [(0, 1, Fraction(1, 10)), (1, 3, Fraction(2, 10)), (0, 2, Fraction(3, 10)), (2, 3, Fraction(0))]
