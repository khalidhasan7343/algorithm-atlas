"""lowest-common-ancestor: canonical Tree implementation; contracts are in the lesson."""
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('atlas_tree_support',Path(__file__).resolve().parents[2]/'support.py')
_support=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

class LCA:
    def __init__(self,parents,root=None):
        self._parent,self._children,self._depth=_support.rooted_tree(parents,root)

    def query(self,a,b):
        n=len(self._parent)
        _support.integer(a,0,n-1,"first vertex");_support.integer(b,0,n-1,"second vertex")
        while self._depth[a]>self._depth[b]:a=self._parent[a]
        while self._depth[b]>self._depth[a]:b=self._parent[b]
        while a!=b:a,b=self._parent[a],self._parent[b]
        return a


def solve(parents,root=None,queries=()):
    tree=LCA(parents,root);result=[]
    for pair in _support.operations_checked(queries):
        _support.operation(pair,2);result.append(tree.query(*pair))
    return result

if __name__=="__main__":
    _support.main(solve)
