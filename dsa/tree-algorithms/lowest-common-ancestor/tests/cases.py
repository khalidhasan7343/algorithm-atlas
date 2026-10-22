import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('tree_oracles',Path(__file__).resolve().parents[2]/'oracles.py')
_o=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_o)
NAME='lowest-common-ancestor'
SEED=8202

def vectors():return _o.rooted_vectors(NAME)
def encode(case):return _o.encode_rooted(case)
def check(actual,expected,case):
    assert actual==expected,(case,actual,expected)
    if NAME=='euler-tour':_o.check_subtree_intervals(actual,case)
def invalid():
    base=dict(parents=[None,0],root=0)
    changes=[dict(root=None),dict(root=2),dict(root=True),dict(parents=[0,0]),dict(parents=[None,None]),dict(parents=[None,1]),dict(parents=[None,2]),dict(parents=[None,True]),dict(parents=[None]*10001)]
    cases=[dict(base,**change) for change in changes]+[dict(parents=[],root=0),dict(parents=[None,2,1],root=0)]
    if NAME=='lowest-common-ancestor':cases += [dict(base,queries=q) for q in ([[0,2]],[[True,1]],[[0]],[[0,0]]*1001)]
    if NAME=='binary-lifting':cases += [dict(base,operations=q) for q in ([[0,0,-1]],[[0,0,10**18+1]],[[0,2,0]],[[1,0,2]],[[True,0,0]],[[2,0,0]],[[0,0]],[[0,0,0]]*1001)]
    return cases
def invalid_cli():
    valid=dict(parents=[None],root=0)
    if NAME=='lowest-common-ancestor':valid['queries']=[]
    if NAME=='binary-lifting':valid['operations']=[]
    bad=dict(valid,parents=[0])
    return ['', '-1 -1','10001 0',encode(valid)+'extra',encode(bad),'1.0 0',encode(dict(valid,root=-1))]
def boundaries(module):
    n=10000;parents=[None]+list(range(n-1))
    index=module.LCA(parents,0)
    assert index.query(9999,4321)==4321 and index.query(0,9999)==0
    assert index.query(9999,9999)==9999

DRIVER="int count=static_cast<int>(token());while(count--){lca_cli(false);std::cout<<'\\n';}"
BOUNDARY_DRIVER='std::vector<Integer> p{-1};for(int i=0;i<9999;++i)p.push_back(i);LCA index(rooted_tree(p,0));emit(index.query(9999,4321)==4321 && index.query(0,9999)==0);'
