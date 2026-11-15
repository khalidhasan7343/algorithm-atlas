"""Run all six C1 syllabus entries on one small weighted state space.

BFS and DFS are the canonical A5 implementations (states numbered S=0 ... G=5);
the four C1 searches use the state-space contract directly.

Run from the repository root:
python artificial-intelligence/uninformed-search/examples/compare_uninformed.py
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
C1 = "artificial-intelligence/uninformed-search/"


def load(relative: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NAMES = "SABCDG"
ROADS = [("S", "A", 1), ("A", "B", 1), ("B", "G", 1), ("S", "C", 4), ("C", "G", 4), ("S", "D", 2), ("D", "C", 1)]
WEIGHTED = {c: [] for c in NAMES}
FORWARD = {c: [] for c in NAMES}
BACKWARD = {c: [] for c in NAMES}
for u, v, w in ROADS:
    WEIGHTED[u].append((u + v, v, w))
    FORWARD[u].append((u + v, v))
    BACKWARD[v].append((u + v, u))


def is_goal(state):
    return state == "G"


def main() -> None:
    dls = load(C1 + "depth-limited-search/python/solution.py", "cmp_dls")
    iddfs = load(C1 + "iterative-deepening-dfs/python/solution.py", "cmp_iddfs")
    ucs = load(C1 + "uniform-cost-search/python/solution.py", "cmp_ucs")
    bidirectional = load(C1 + "bidirectional-search/python/solution.py", "cmp_bidirectional")
    bfs = load("dsa/graph-algorithms/breadth-first-search/python/solution.py", "cmp_bfs")
    dfs = load("dsa/graph-algorithms/depth-first-search/python/solution.py", "cmp_dfs")

    index = {c: i for i, c in enumerate(NAMES)}
    edges = [(index[u], index[v]) for u, v, _ in ROADS]
    layers = bfs.bfs(len(NAMES), edges, 0)
    print("A5 BFS  :", "-".join(NAMES[v] for v in bfs.path_to(layers, index["G"])["vertices"]), "(fewest actions)")
    forest, chain, v = dfs.dfs(len(NAMES), edges), [], index["G"]
    while v is not None:
        chain.append(NAMES[v])
        v = forest["parent"][v]
    print("A5 DFS  :", "-".join(reversed(chain)), "(first DFS-tree path; not shortest in general)")
    for limit in (1, 2, 3):
        r = dls.depth_limited_search("S", is_goal, FORWARD.__getitem__, limit)
        print(f"DLS L={limit}:", r.status, *(["-".join(r.states)] if r.found else []))
    r = iddfs.iterative_deepening_search("S", is_goal, FORWARD.__getitem__)
    print("IDDFS   :", "-".join(r.states), f"after {r.stats['iterations']} iterations")
    r = ucs.uniform_cost_search("S", is_goal, WEIGHTED.__getitem__)
    print("UCS     :", "-".join(r.states), f"cost {r.cost} (cheapest; S-C-G costs 8)")
    r = bidirectional.bidirectional_search("S", "G", FORWARD.__getitem__, BACKWARD.__getitem__)
    print("Bidir   :", "-".join(r.states), f"meeting {r.states[r.stats['meeting_index']]}->"
          f"{r.states[r.stats['meeting_index'] + 1]}")


if __name__ == "__main__":
    main()
