"""depth-first-search. See the adjacent lesson for contracts and correctness."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_graph_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def dfs(n, edges, directed=True):
    adj, _ = _support.graph(n, edges, directed)
    seen, parent, parent_edge = [False]*n, [None]*n, [None]*n
    order, finish, component = [], [], [None]*n
    for root in range(n):
        if seen[root]:
            continue
        seen[root], component[root] = True, root
        order.append(root)
        stack = [(root, iter(adj[root]))]
        while stack:
            u, iterator = stack[-1]
            arc = next(iterator, None)
            if arc is None:
                finish.append(u)
                stack.pop()
            else:
                v, _, edge_id = arc
                if not seen[v]:
                    seen[v], parent[v], parent_edge[v], component[v] = True, u, edge_id, root
                    order.append(v)
                    stack.append((v, iter(adj[v])))
    return dict(order=order, finish=finish, parent=parent, parent_edge=parent_edge, component=component)


solve = dfs

if __name__ == "__main__":
    _support.main(solve)
