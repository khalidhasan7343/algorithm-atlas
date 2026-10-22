"""binary-lifting: canonical Tree implementation; contracts are in the lesson."""
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('atlas_tree_support',Path(__file__).resolve().parents[2]/'support.py')
_support=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

class BinaryLifting:
    def __init__(self,parents,root=None):
        parent,_,self._depth=_support.rooted_tree(parents,root)
        self._up=[parent]
        for _ in range(1,max(1,len(parent).bit_length())):
            previous=self._up[-1]
            self._up.append([None if p is None else previous[p] for p in previous])

    def kth_ancestor(self,vertex,k):
        _support.integer(vertex,0,len(self._depth)-1,"vertex")
        _support.integer(k,0,10**18,"k")
        if k>self._depth[vertex]:return None
        bit=0
        while k:
            if k&1:vertex=self._up[bit][vertex]
            k>>=1;bit+=1
        return vertex

    def lca(self,a,b):
        n=len(self._depth)
        _support.integer(a,0,n-1,"first vertex");_support.integer(b,0,n-1,"second vertex")
        if self._depth[a]<self._depth[b]:a,b=b,a
        a=self.kth_ancestor(a,self._depth[a]-self._depth[b])
        if a==b:return a
        for row in reversed(self._up):
            if row[a]!=row[b]:a,b=row[a],row[b]
        return self._up[0][a]


def solve(parents,root=None,operations=()):
    tree=BinaryLifting(parents,root);result=[]
    for op in _support.operations_checked(operations):
        _support.operation(op,3);_support.integer(op[0],0,1,"operation")
        result.append(tree.kth_ancestor(op[1],op[2]) if op[0]==0 else tree.lca(op[1],op[2]))
    return result

if __name__=="__main__":
    _support.main(solve)
