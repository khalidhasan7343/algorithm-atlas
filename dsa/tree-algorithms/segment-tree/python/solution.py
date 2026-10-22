"""segment-tree: canonical Tree implementation; contracts are in the lesson."""
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('atlas_tree_support',Path(__file__).resolve().parents[2]/'support.py')
_support=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

class SegmentTree:
    def __init__(self,values):
        values=_support.values_checked(values);self._n=len(values);self._base=1
        while self._base<self._n:self._base*=2
        self._tree=[0]*(2*self._base)
        self._tree[self._base:self._base+self._n]=values
        for node in range(self._base-1,0,-1):self._tree[node]=self._tree[2*node]+self._tree[2*node+1]

    def set(self,index,value):
        _support.integer(index,0,self._n-1,"index");_support.integer(value,-10**9,10**9,"value")
        node=self._base+index;self._tree[node]=value;node//=2
        while node:self._tree[node]=self._tree[2*node]+self._tree[2*node+1];node//=2

    def range_sum(self,left,right):
        _support.integer(left,0,self._n,"left");_support.integer(right,left,self._n,"right")
        left+=self._base;right+=self._base;total=0
        while left<right:
            if left&1:total+=self._tree[left];left+=1
            if right&1:right-=1;total+=self._tree[right]
            left//=2;right//=2
        return total


def solve(values,operations=()):
    tree=SegmentTree(values);result=[]
    for op in _support.operations_checked(operations):
        _support.operation(op,3);_support.integer(op[0],0,1,"operation")
        if op[0]==0:tree.set(op[1],op[2]);result.append(None)
        else:result.append(tree.range_sum(op[1],op[2]))
    return result

if __name__=="__main__":
    _support.main(solve)
