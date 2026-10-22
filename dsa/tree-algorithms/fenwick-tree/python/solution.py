"""fenwick-tree: canonical Tree implementation; contracts are in the lesson."""
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('atlas_tree_support',Path(__file__).resolve().parents[2]/'support.py')
_support=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

class FenwickTree:
    def __init__(self,values):
        self._values=_support.values_checked(values);n=len(self._values)
        self._bit=[0]*(n+1)
        for i,value in enumerate(self._values,1):
            self._bit[i]+=value
            parent=i+(i&-i)
            if parent<=n:self._bit[parent]+=self._bit[i]

    def add(self,index,delta):
        n=len(self._values);_support.integer(index,0,n-1,"index")
        _support.integer(delta,-2*10**9,2*10**9,"delta")
        value=_support.integer(self._values[index]+delta,-10**9,10**9,"updated value")
        self._values[index]=value;i=index+1
        while i<=n:self._bit[i]+=delta;i+=i&-i

    def prefix_sum(self,end):
        _support.integer(end,0,len(self._values),"prefix end")
        total=0
        while end:total+=self._bit[end];end-=end&-end
        return total

    def range_sum(self,left,right):
        _support.integer(left,0,len(self._values),"left")
        _support.integer(right,left,len(self._values),"right")
        return self.prefix_sum(right)-self.prefix_sum(left)


def solve(values,operations=()):
    tree=FenwickTree(values);result=[]
    for op in _support.operations_checked(operations):
        if not isinstance(op,(list,tuple)) or not op:raise ValueError("operation required")
        _support.integer(op[0],0,2,"operation")
        _support.operation(op,2 if op[0]==1 else 3)
        if op[0]==0:tree.add(op[1],op[2]);result.append(None)
        elif op[0]==1:result.append(tree.prefix_sum(op[1]))
        else:result.append(tree.range_sum(op[1],op[2]))
    return result

if __name__=="__main__":
    _support.main(solve)
