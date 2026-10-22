"""union-find. See the adjacent lesson for contracts and correctness."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_graph_support", Path(__file__).resolve().parents[2] / "support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

class UnionFind:
    """Path compression and union by size; smaller root wins equal-size ties."""
    def __init__(self, n):
        _support.integer(n, 0, 1000, "vertex count")
        self._parent = list(range(n))
        self._size = [1]*n
        self.count = n

    def find(self, vertex):
        _support.integer(vertex, 0, len(self._parent)-1, "vertex")
        root = vertex
        while root != self._parent[root]:
            root = self._parent[root]
        while vertex != root:
            nxt = self._parent[vertex]
            self._parent[vertex] = root
            vertex = nxt
        return root

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        if self._size[a] < self._size[b] or (self._size[a] == self._size[b] and a > b):
            a, b = b, a
        self._parent[b] = a
        self._size[a] += self._size[b]
        self.count -= 1
        return True

    def connected(self, a, b):
        return self.find(a) == self.find(b)

    def component_size(self, vertex):
        return self._size[self.find(vertex)]

    def groups(self):
        groups = {}
        for v in range(len(self._parent)):
            groups.setdefault(self.find(v), []).append(v)
        return sorted(groups.values())


def solve(n, edges, directed=False):
    _support.graph(n, edges, directed)
    if directed:
        raise ValueError("Union-Find uses undirected connectivity")
    sets = UnionFind(n)
    for u, v in edges:
        sets.union(u, v)
    return dict(groups=sets.groups(), count=sets.count)

if __name__ == "__main__":
    _support.main(solve)
