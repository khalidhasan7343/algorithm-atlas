"""tarjan-strongly-connected-components. See the adjacent lesson for contracts and correctness."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_graph_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def tarjan_scc(n, edges, directed=True):
    adj, _ = _support.graph(n, edges, directed)
    if not directed:
        raise ValueError("SCC API requires directed mode")
    index, low, parent = [-1]*n, [0]*n, [-1]*n
    active, on_stack, components, clock = [], [False]*n, [], 0
    for root in range(n):
        if index[root] != -1:
            continue
        index[root] = low[root] = clock; clock += 1
        active.append(root); on_stack[root] = True
        frames = [(root, 0)]
        while frames:
            u, pos = frames[-1]
            if pos < len(adj[u]):
                frames[-1] = (u, pos+1)
                v = adj[u][pos][0]
                if index[v] == -1:
                    parent[v] = u
                    index[v] = low[v] = clock; clock += 1
                    active.append(v); on_stack[v] = True
                    frames.append((v, 0))
                elif on_stack[v]:
                    low[u] = min(low[u], index[v])
            else:
                frames.pop()
                if parent[u] != -1:
                    low[parent[u]] = min(low[parent[u]], low[u])
                if low[u] == index[u]:
                    group = []
                    while True:
                        v = active.pop(); on_stack[v] = False; group.append(v)
                        if v == u:
                            break
                    components.append(sorted(group))
    return sorted(components)


solve = tarjan_scc

if __name__ == "__main__":
    _support.main(solve)
