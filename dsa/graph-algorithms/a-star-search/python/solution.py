"""a-star-search. See the adjacent lesson for contracts and correctness."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_graph_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

import heapq


def a_star(n, edges, source=None, goal=None, heuristic=None, directed=True):
    adj, _ = _support.graph(n, edges, directed, True, low=0)
    source = _support.source_vertex(n, source)
    goal = _support.source_vertex(n, goal)
    if not isinstance(heuristic, (list, tuple)) or len(heuristic) != n:
        raise ValueError("one heuristic per vertex required")
    for value in heuristic:
        _support.integer(value, 0, 10**9, "heuristic")
    if goal is not None and heuristic[goal] != 0:
        raise ValueError("goal heuristic must be zero")
    distance, parent, parent_edge = [None]*n, [None]*n, [None]*n
    heap = []
    if source is not None:
        distance[source] = 0
        heap.append((heuristic[source], 0, source))
    while heap:
        _, cost, u = heapq.heappop(heap)
        if cost != distance[u]:
            continue
        if u == goal:
            path = _support.path_to(dict(distance=distance, parent=parent, parent_edge=parent_edge), goal)
            return dict(cost=cost, path=path['vertices'], edges=path['edges'])
        for v, weight, edge_id in adj[u]:
            candidate = cost + weight
            if distance[v] is None or candidate < distance[v]:
                distance[v], parent[v], parent_edge[v] = candidate, u, edge_id
                # No permanent closed set: a later improvement reopens v.
                heapq.heappush(heap, (candidate+heuristic[v], candidate, v))
    return dict(cost=None, path=[], edges=[])


solve = a_star

if __name__ == "__main__":
    _support.main(solve)
