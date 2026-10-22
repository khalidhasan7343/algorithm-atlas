"""topological-sorting. See the adjacent lesson for contracts and correctness."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_graph_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

import heapq


def topological_sort(n, edges, directed=True):
    adj, _ = _support.graph(n, edges, directed)
    if not directed:
        raise ValueError("topological sorting requires directed mode")
    indegree = [0]*n
    for _, v in edges:
        indegree[v] += 1
    ready = [v for v in range(n) if indegree[v] == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        u = heapq.heappop(ready)
        order.append(u)
        for v, _, _ in adj[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                heapq.heappush(ready, v)
    return order if len(order) == n else None


solve = topological_sort

if __name__ == "__main__":
    _support.main(solve)
