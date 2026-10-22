"""floyd-warshall. See the adjacent lesson for contracts and correctness."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_graph_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def floyd_warshall(n, edges, directed=True):
    _, arcs = _support.graph(n, edges, directed, True, cap=100)
    distance = [[None]*n for _ in range(n)]
    for v in range(n):
        distance[v][v] = 0
    for u, v, weight, _ in arcs:
        if distance[u][v] is None or weight < distance[u][v]:
            distance[u][v] = weight
    for k in range(n):
        for u in range(n):
            if distance[u][k] is None:
                continue
            for v in range(n):
                if distance[k][v] is not None:
                    candidate = max(-10**12, distance[u][k] + distance[k][v])
                    if distance[u][v] is None or candidate < distance[u][v]:
                        distance[u][v] = candidate
    negative = [k for k in range(n) if distance[k][k] < 0]
    # Classify using an unchanged reachability snapshot, before writing tagged values.
    affected = [[any(distance[u][k] is not None and distance[k][v] is not None
                     for k in negative) for v in range(n)] for u in range(n)]
    return [["-inf" if affected[u][v] else distance[u][v] for v in range(n)] for u in range(n)]


solve = floyd_warshall

if __name__ == "__main__":
    _support.main(solve)
