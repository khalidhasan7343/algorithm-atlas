"""prim. See the adjacent lesson for contracts and correctness."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_graph_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

import heapq


def prim(n, edges, directed=False):
    adj, _ = _support.graph(n, edges, directed, True)
    if directed:
        raise ValueError("Prim requires undirected mode")
    seen, selected, total = [False]*n, [], 0
    for root in range(n):
        if seen[root]:
            continue
        seen[root] = True
        heap = [(w, i, root, v) for v, w, i in adj[root]]
        heapq.heapify(heap)
        while heap:
            weight, edge_id, _, v = heapq.heappop(heap)
            if seen[v]:
                continue
            seen[v] = True
            selected.append(edge_id)
            total += weight
            for target, w, i in adj[v]:
                if not seen[target]:
                    heapq.heappush(heap, (w, i, v, target))
    return dict(weight=total, edges=selected)


solve = prim

if __name__ == "__main__":
    _support.main(solve)
