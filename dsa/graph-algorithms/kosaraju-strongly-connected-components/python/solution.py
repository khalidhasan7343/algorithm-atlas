"""kosaraju-strongly-connected-components. See the adjacent lesson for contracts and correctness."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_graph_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def kosaraju_scc(n, edges, directed=True):
    adj, _ = _support.graph(n, edges, directed)
    if not directed:
        raise ValueError("SCC API requires directed mode")
    seen, finish = [False]*n, []
    for root in range(n):
        if seen[root]:
            continue
        seen[root] = True
        frames = [(root, 0)]
        while frames:
            u, pos = frames[-1]
            if pos == len(adj[u]):
                finish.append(u); frames.pop()
            else:
                frames[-1] = (u, pos+1)
                v = adj[u][pos][0]
                if not seen[v]:
                    seen[v] = True; frames.append((v, 0))
    transpose = [[] for _ in range(n)]
    for u, v in edges:
        transpose[v].append(u)
    seen, components = [False]*n, []
    for root in reversed(finish):
        if seen[root]:
            continue
        stack, group = [root], []
        seen[root] = True
        while stack:
            u = stack.pop(); group.append(u)
            for v in transpose[u]:
                if not seen[v]:
                    seen[v] = True; stack.append(v)
        components.append(sorted(group))
    return sorted(components)


solve = kosaraju_scc

if __name__ == "__main__":
    _support.main(solve)
