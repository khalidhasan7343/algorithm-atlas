"""breadth-first-search. See the adjacent lesson for contracts and correctness."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_graph_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

from collections import deque


def bfs(n, edges, source=None, directed=True):
    adj, _ = _support.graph(n, edges, directed)
    source = _support.source_vertex(n, source)
    distance, parent, parent_edge, order = [None]*n, [None]*n, [None]*n, []
    queue = deque()
    if source is not None:
        distance[source] = 0
        queue.append(source)
    while queue:
        u = queue.popleft()
        order.append(u)
        for v, _, edge_id in adj[u]:
            if distance[v] is None:
                distance[v], parent[v], parent_edge[v] = distance[u]+1, u, edge_id
                queue.append(v)
    return dict(order=order, distance=distance, parent=parent, parent_edge=parent_edge)


path_to = _support.path_to
solve = bfs

if __name__ == "__main__":
    _support.main(solve)
