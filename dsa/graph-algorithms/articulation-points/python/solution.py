"""articulation-points. See the adjacent lesson for contracts and correctness."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_graph_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def articulation_points(n, edges, directed=False):
    adj, _ = _support.graph(n, edges, directed)
    if directed:
        raise ValueError("undirected mode required")
    discovery, low, parent, parent_edge = [-1]*n, [0]*n, [-1]*n, [-1]*n
    children, cut, result, clock = [0]*n, [False]*n, [], 0
    for root in range(n):
        if discovery[root] != -1:
            continue
        discovery[root] = low[root] = clock; clock += 1
        frames = [(root, 0)]
        while frames:
            u, pos = frames[-1]
            if pos < len(adj[u]):
                frames[-1] = (u, pos+1)
                v, _, edge_id = adj[u][pos]
                if edge_id == parent_edge[u]:
                    continue  # Skip the reverse of this exact tree edge, not parallel edges.
                if discovery[v] == -1:
                    parent[v], parent_edge[v] = u, edge_id
                    children[u] += 1
                    discovery[v] = low[v] = clock; clock += 1
                    frames.append((v, 0))
                else:
                    low[u] = min(low[u], discovery[v])
            else:
                frames.pop()
                p = parent[u]
                if p != -1:
                    low[p] = min(low[p], low[u])
                    if parent[p] != -1 and low[u] >= discovery[p]:
                        cut[p] = True
                elif children[u] > 1:
                    cut[u] = True
    return [v for v in range(n) if cut[v]]


solve = articulation_points

if __name__ == "__main__":
    _support.main(solve)
