import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('tree_oracles',Path(__file__).resolve().parents[2]/'oracles.py')
_o=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_o)
NAME='postorder-traversal'
SEED=8101

def vectors():return _o.traversal_vectors(NAME)
def encode(case):return _o.encode_binary(case)
def check(actual,expected,case):assert actual==expected,(case,actual,expected)
def invalid():
    base=dict(values=[1,1],children=[[1,None],[None,None]],root=0)
    return [dict(base,**change) for change in [dict(root=None),dict(root=2),dict(root=True),dict(values=[1]),dict(values=[True,1]),dict(values=[10**9+1,1]),dict(children=[[1,1],[None,None]]),dict(children=[[0,None],[None,None]]),dict(children=[[None,None],[None,None]]),dict(children=[[2,None],[None,None]]),dict(children=[[True,None],[None,None]]),dict(children=[[1],[None,None]]),dict(children=[[1,None],[0,None]])]]+[
      dict(values=[],children=[],root=0),dict(values=[0]*10001,children=[[None,None]]*10001,root=0),
      dict(values=[0,0,0],children=[[None,None],[2,None],[1,None]],root=0)]
def invalid_cli():return ['', '-1 -1','10001 0','1 -1 0 -1 -1','1 0 0 0 -1','1 0 0 1 -1','1 0 1000000001 -1 -1','0 -1 trailing','1.0 0','2 0 0 0 1 1 -1 -1']
def boundaries(module):
    n=10000
    for side in (0,1):
        children=[[None,None] for _ in range(n)]
        for u in range(n-1):children[u][side]=u+1
        result=module.solve([7]*n,children,0)
        if NAME=='level-order-traversal':assert result==[[u] for u in range(n)]
        else:
            reverse=NAME=='postorder-traversal' or (NAME=='inorder-traversal' and side==0)
            assert result==list(range(n-1,-1,-1) if reverse else range(n))
    n=1023;children=[[2*u+1 if 2*u+1<n else None,2*u+2 if 2*u+2<n else None] for u in range(n)]
    result=module.solve([0]*n,children,0)
    if NAME=='level-order-traversal':assert list(map(len,result))==[2**d for d in range(10)]
    else:assert sorted(result)==list(range(n))

DRIVER="int count=static_cast<int>(token());while(count--){emit(postorder(read_binary(false)));std::cout<<'\\n';}"
BOUNDARY_DRIVER='std::vector<Integer> values(10000,7);std::vector<std::array<Integer,2>> children(10000,{-1,-1});for(int i=0;i<9999;++i)children[i][0]=i+1;auto tree=binary_tree(values,children,0);auto result=postorder(tree);emit(result.size()==10000 && result.front()==9999 && tree.children[0][0]==1 && tree.values[0]==7);'
