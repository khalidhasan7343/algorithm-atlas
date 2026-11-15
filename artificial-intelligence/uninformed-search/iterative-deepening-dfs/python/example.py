"""IDDFS example: watch the depth limit grow until the shallowest goal appears.

Run from the repository root:
python artificial-intelligence/uninformed-search/iterative-deepening-dfs/python/example.py
"""
import importlib.util
from pathlib import Path


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HERE = Path(__file__).resolve()
iddfs = _load("iddfs_example", HERE.with_name("solution.py"))
dls = _load("iddfs_example_dls", HERE.parents[2] / "depth-limited-search/python/solution.py")

# Integer puzzle: from 1, reach 10 using "+1" or "*2". Depth-first order tries "+1"
# first, so plain DFS would wander along 2, 3, 4, ... before trying doubling.


def successors(n):
    return [("+1", n + 1), ("*2", n * 2)] if n <= 20 else []


def is_goal(n):
    return n == 10


if __name__ == "__main__":
    for limit in range(5):  # The DLS runs IDDFS performs internally.
        run = dls.depth_limited_search(1, is_goal, successors, limit)
        found = " route=" + " ".join(f"{a}" for a in run.actions) if run.found else ""
        print(f"limit={limit} status={run.status:<7} expanded={run.stats['expanded']}{found}")
    result = iddfs.iterative_deepening_search(1, is_goal, successors)
    print("IDDFS:", " -> ".join(map(str, result.states)), "actions", list(result.actions),
          "depth", result.depth, "iterations", result.stats["iterations"],
          "total expanded", result.stats["expanded"])
