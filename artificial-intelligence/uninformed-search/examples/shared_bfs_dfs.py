"""Run the canonical A5 BFS and DFS on a C1 state space (no duplicate implementation).

The A5 APIs search explicit integer graphs: ``bfs(n, edges, source)`` and
``dfs(n, edges)``. A finite state space can use them after its states are
numbered and every successor record becomes an edge. This example numbers the
20 water-jug states (jug A holds 3 litres, jug B holds 4), so state 0 is the
empty start (0, 0) and edge ``i`` remembers the action that produced it.

Run from the repository root: ``python artificial-intelligence/uninformed-search/examples/shared_bfs_dfs.py``
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def load(relative: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CAP_A, CAP_B = 3, 4


def jug_successors(state):
    a, b = state
    pour_ab, pour_ba = min(a, CAP_B - b), min(b, CAP_A - a)
    return [("fill A", (CAP_A, b)), ("fill B", (a, CAP_B)), ("empty A", (0, b)), ("empty B", (a, 0)),
            ("pour A->B", (a - pour_ab, b + pour_ab)), ("pour B->A", (a + pour_ba, b - pour_ba))]


def is_goal(state):
    return state[1] == 2


def numbered_graph():
    """Number every (a, b) state without searching, then list one edge per action."""
    states = [(a, b) for a in range(CAP_A + 1) for b in range(CAP_B + 1)]
    index = {state: i for i, state in enumerate(states)}
    edges, labels = [], []
    for state in states:
        for action, child in jug_successors(state):
            edges.append((index[state], index[child]))
            labels.append(action)
    return states, edges, labels


def main() -> None:
    bfs = load("dsa/graph-algorithms/breadth-first-search/python/solution.py", "a5_bfs")
    dfs = load("dsa/graph-algorithms/depth-first-search/python/solution.py", "a5_dfs")
    iddfs = load("artificial-intelligence/uninformed-search/iterative-deepening-dfs/python/solution.py", "c1_iddfs")
    states, edges, labels = numbered_graph()
    print(f"states={len(states)} edges={len(edges)} start={states[0]}")

    layers = bfs.bfs(len(states), edges, 0)
    goals = [v for v, s in enumerate(states) if is_goal(s) and layers["distance"][v] is not None]
    target = min(goals, key=lambda v: (layers["distance"][v], v))
    path = bfs.path_to(layers, target)
    print("A5 BFS shortest:", [states[v] for v in path["vertices"]])
    print("  actions:", [labels[e] for e in path["edges"]], "depth", layers["distance"][target])

    forest = dfs.dfs(len(states), edges)
    reachable = sorted(states[v] for v in range(len(states)) if forest["component"][v] == 0)
    chain, v = [], target
    while v is not None:
        chain.append(v)
        v = forest["parent"][v]
    print("A5 DFS reachable from start:", len(reachable), "states")
    print("A5 DFS tree path to the same goal has", len(chain) - 1, "actions (DFS is not shortest-path)")

    result = iddfs.iterative_deepening_search((0, 0), is_goal, jug_successors)
    print("C1 IDDFS depth", result.depth, "after", result.stats["iterations"], "iterations")


if __name__ == "__main__":
    main()
