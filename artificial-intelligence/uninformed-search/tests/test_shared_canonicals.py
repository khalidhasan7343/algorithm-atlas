"""C1 shared ownership: BFS/DFS stay canonical in A5 and are reused, never duplicated."""
import importlib.util
from pathlib import Path
import random
import subprocess
import sys

import pytest
import yaml

pytestmark = pytest.mark.oracle

ROOT = Path(__file__).resolve().parents[3]
CATEGORY = ROOT / "artificial-intelligence/uninformed-search"
NEW = ("depth-limited-search", "iterative-deepening-dfs", "uniform-cost-search", "bidirectional-search")


def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def a5():
    return dict(bfs=load("dsa/graph-algorithms/breadth-first-search/python/solution.py", "c1_shared_bfs"),
                dfs=load("dsa/graph-algorithms/depth-first-search/python/solution.py", "c1_shared_dfs"))


@pytest.fixture(scope="module")
def oracle():
    return load("artificial-intelligence/uninformed-search/tests/oracles.py", "c1_shared_oracles")


def test_catalog_shares_a5_canonicals_and_owns_exactly_four_new_topics():
    catalog = yaml.safe_load((ROOT / "catalog.yaml").read_text(encoding="utf-8"))
    c1 = next(c for c in catalog["categories"] if c["id"] == "C1")
    assert c1["path"] == "artificial-intelligence/uninformed-search"
    assert [i["algorithm"] for i in c1["items"]] == ["breadth-first-search", "depth-first-search", *NEW]
    records = {a["id"]: a for a in catalog["algorithms"]}
    for shared in ("breadth-first-search", "depth-first-search"):
        assert records[shared]["category"] == "A5"
        assert records[shared]["canonical_location"] == f"dsa/graph-algorithms/{shared}"
    assert [a["id"] for a in catalog["algorithms"] if a["category"] == "C1"] == list(NEW)
    for topic in NEW:
        assert records[topic]["canonical_location"] == f"artificial-intelligence/uninformed-search/{topic}"


def test_no_duplicate_bfs_or_dfs_implementation_under_c1():
    for shared in ("breadth-first-search", "depth-first-search", "bfs", "dfs"):
        assert not (CATEGORY / shared).exists()
    folders = sorted(p.name for p in CATEGORY.iterdir() if p.is_dir() and (p / "README.md").exists())
    assert folders == sorted(NEW)
    # Only the shared example reuses A5 sources; it loads them instead of redefining them.
    example = (CATEGORY / "examples/shared_bfs_dfs.py").read_text(encoding="utf-8")
    assert "def bfs" not in example and "def dfs" not in example
    assert "dsa/graph-algorithms/breadth-first-search/python/solution.py" in example


def test_c1_readme_links_resolve_to_a5_lessons():
    text = (CATEGORY / "README.md").read_text(encoding="utf-8")
    for shared in ("breadth-first-search", "depth-first-search"):
        assert f"(../../dsa/graph-algorithms/{shared}/README.md)" in text
        assert (ROOT / f"dsa/graph-algorithms/{shared}/README.md").is_file()


def random_state_space(rng, oracle):
    n = rng.randint(1, 9)
    return n, oracle.random_graph(rng, n, rng.randint(0, 16))


def test_a5_bfs_returns_minimum_edge_paths_on_state_graphs(a5, oracle):
    rng = random.Random(27401)
    for _ in range(400):
        n, edges = random_state_space(rng, oracle)
        layers = a5["bfs"].bfs(n, edges, 0)
        assert layers["distance"] == oracle.bfs_distances(n, edges, 0)
        for goal in range(n):
            if layers["distance"][goal] is not None:
                path = a5["bfs"].path_to(layers, goal)
                oracle.assert_valid_path(edges, path["vertices"], path["edges"], start=0, goals={goal})
                assert len(path["edges"]) == layers["distance"][goal]


def test_a5_dfs_reachability_matches_and_does_not_claim_optimality(a5, oracle):
    rng = random.Random(27402)
    for _ in range(400):
        n, edges = random_state_space(rng, oracle)
        forest = a5["dfs"].dfs(n, edges)
        reached = {v for v in range(n) if forest["component"][v] == 0}
        assert reached == {v for v, d in enumerate(oracle.bfs_distances(n, edges, 0)) if d is not None}
    # A concrete counterexample: the DFS tree reaches state 2 through 1 although 0 -> 2 exists.
    forest = a5["dfs"].dfs(3, [(0, 1), (1, 2), (0, 2)])
    assert forest["parent"][2] == 1 and oracle.bfs_distances(3, [(0, 1), (1, 2), (0, 2)], 0)[2] == 1


def test_new_c1_searches_agree_with_a5_bfs_depths(a5, oracle):
    iddfs = load("artificial-intelligence/uninformed-search/iterative-deepening-dfs/python/solution.py", "c1_sh_iddfs")
    bidir = load("artificial-intelligence/uninformed-search/bidirectional-search/python/solution.py", "c1_sh_bidir")
    rng = random.Random(27403)
    for _ in range(300):
        n, edges = random_state_space(rng, oracle)
        distance = a5["bfs"].bfs(n, edges, 0)["distance"]
        succ = [[] for _ in range(n)]
        pred = [[] for _ in range(n)]
        for i, (u, v) in enumerate(edges):
            succ[u].append((i, v))
            pred[v].append((i, u))
        goal = rng.randrange(n)
        assert iddfs.iterative_deepening_search(0, {goal}.__contains__, succ.__getitem__).depth == distance[goal]
        assert bidir.bidirectional_search(0, goal, succ.__getitem__, pred.__getitem__).depth == distance[goal]


def test_shared_example_runs_deterministically():
    script = CATEGORY / "examples/shared_bfs_dfs.py"
    runs = [subprocess.run([sys.executable, str(script)], text=True, capture_output=True, timeout=60, check=True)
            for _ in range(2)]
    assert runs[0].stdout == runs[1].stdout and not runs[0].stderr
    assert "A5 BFS shortest" in runs[0].stdout and "depth 6" in runs[0].stdout
    assert "C1 IDDFS depth 6" in runs[0].stdout
