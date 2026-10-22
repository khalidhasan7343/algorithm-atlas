"""johnson. See the adjacent lesson for contracts and correctness."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_graph_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def johnson(n, edges, directed=True):
    _support.graph(n, edges, directed, True, cap=100)
    if not directed:
        raise ValueError("Johnson requires directed mode")
    # Initial zero labels are exactly the virtual super-source's zero arcs.
    potential = _support.canonical("bellman-ford").potentials(n, edges)['distance']
    if "-inf" in potential:
        return None  # Includes negative cycles disconnected from an ordinary source.
    reweighted = [(u, v, w+potential[u]-potential[v]) for u, v, w in edges]
    result = []
    for source in range(n):
        row = _support.canonical("dijkstra").dijkstra(n, reweighted, source)['distance']
        result.append([None if cost is None else cost-potential[source]+potential[v]
                       for v, cost in enumerate(row)])
    return result


solve = johnson

if __name__ == "__main__":
    _support.main(solve)
