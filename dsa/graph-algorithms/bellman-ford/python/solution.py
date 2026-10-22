"""bellman-ford. See the adjacent lesson for contracts and correctness."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_graph_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

from collections import deque


def bellman_ford(n, edges, source=None, directed=True):
    adj, arcs = _support.graph(n, edges, directed, True)
    arcs = [(u, v, w, i) for u in range(n) for v, w, i in adj[u]]
    source = _support.source_vertex(n, source)
    distance, parent, parent_edge = [None]*n, [None]*n, [None]*n
    if source is not None:
        distance[source] = 0
    return _relax(n, adj, arcs, distance, parent, parent_edge)


def _relax(n, adj, arcs, distance, parent, parent_edge):
    for _ in range(max(0, n-1)):
        changed = False
        for u, v, weight, edge_id in arcs:
            if distance[u] is not None and (distance[v] is None or distance[u]+weight < distance[v]):
                distance[v], parent[v], parent_edge[v] = distance[u]+weight, u, edge_id
                changed = True
        if not changed:
            break
    affected = set()
    for u, v, weight, _ in arcs:
        if distance[u] is not None and (distance[v] is None or distance[u]+weight < distance[v]):
            affected.add(v)
    queue = deque(sorted(affected))
    while queue:
        u = queue.popleft()
        for v, _, _ in adj[u]:
            if v not in affected:
                affected.add(v)
                queue.append(v)
    for v in affected:
        distance[v], parent[v], parent_edge[v] = "-inf", None, None
    return dict(distance=distance, parent=parent, parent_edge=parent_edge)


def potentials(n, edges):
    """Bellman-Ford after a virtual super-source's zero arcs reach every vertex."""
    adj, _ = _support.graph(n, edges, True, True)
    arcs = [(u, v, w, i) for u in range(n) for v, w, i in adj[u]]
    return _relax(n, adj, arcs, [0]*n, [None]*n, [None]*n)


path_to = _support.path_to
solve = bellman_ford

if __name__ == "__main__":
    _support.main(solve)
