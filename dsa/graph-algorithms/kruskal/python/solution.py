"""kruskal. See the adjacent lesson for contracts and correctness."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_graph_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def kruskal(n, edges, directed=False):
    _support.graph(n, edges, directed, True)
    if directed:
        raise ValueError("Kruskal requires undirected mode")
    sets = _support.canonical("union-find").UnionFind(n)
    selected, total = [], 0
    for edge_id in sorted(range(len(edges)), key=lambda i: (edges[i][2], i)):
        u, v, weight = edges[edge_id]
        if sets.union(u, v):
            selected.append(edge_id)
            total += weight
    return dict(weight=total, edges=selected)


solve = kruskal

if __name__ == "__main__":
    _support.main(solve)
