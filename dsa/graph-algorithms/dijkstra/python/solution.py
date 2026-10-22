"""dijkstra. See the adjacent lesson for contracts and correctness."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_graph_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

import heapq


def dijkstra(n, edges, source=None, directed=True):
    adj, _ = _support.graph(n, edges, directed, True, low=0, high=10**12)
    source = _support.source_vertex(n, source)
    distance, parent, parent_edge = [None]*n, [None]*n, [None]*n
    heap = []
    if source is not None:
        distance[source] = 0
        heap.append((0, source))
    while heap:
        cost, u = heapq.heappop(heap)
        if cost != distance[u]:
            continue  # A later improvement made this queued label stale.
        for v, weight, edge_id in adj[u]:
            candidate = cost + weight
            if distance[v] is None or candidate < distance[v]:
                distance[v], parent[v], parent_edge[v] = candidate, u, edge_id
                heapq.heappush(heap, (candidate, v))
    return dict(distance=distance, parent=parent, parent_edge=parent_edge)


path_to = _support.path_to
solve = dijkstra

if __name__ == "__main__":
    _support.main(solve)
