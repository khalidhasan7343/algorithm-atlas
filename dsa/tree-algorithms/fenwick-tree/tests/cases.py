import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('tree_oracles',Path(__file__).resolve().parents[2]/'oracles.py')
_o=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_o)
NAME='fenwick-tree'
SEED=8303

def vectors():return _o.range_vectors(NAME)
def encode(case):return _o.encode_range(case)
def check(actual,expected,case):assert actual==expected,(case,actual,expected)
def invalid():
    base=dict(values=[1,2],operations=[])
    bad=[[0,2,0],[0,-1,0],[0,True,0],[0,0,True],[0,0],[3,0,0]]
    if NAME=='fenwick-tree':bad += [[0,0,2*10**9+1],[0,0,10**9],[1,3],[1,True],[2,1,0],[2,-1,1],[2,0,3]]
    else:bad += [[0,0,10**9+1],[1,1,0],[1,-1,1],[1,0,3]]
    return [dict(values=values) for values in ([True],[10**9+1],[0]*10001,None)]+[dict(base,operations=[op]) for op in bad]+[dict(base,operations=[[0,0,0]]*1001)]
def invalid_cli():
    return ['', '-1','10001','1 1000000001 0','0 0 extra','1 0 1 0 1 0','1 0 1 4 0 0','1.0','1 0 1001']
def boundaries(module):
    values=[10**9]*10000;tree=getattr(module,'FenwickTree')(values)
    assert tree.range_sum(0,10000)==10**13
    tree.add(0,-2*10**9);assert tree.prefix_sum(10000)==9998*10**9
    before=tree.prefix_sum(10000)
    try:tree.add(0,-1)
    except ValueError:pass
    else:raise AssertionError('updated bound must reject')
    assert tree.prefix_sum(10000)==before and values[0]==10**9
    assert module.FenwickTree([]).prefix_sum(0)==0
    for i in range(1,len(tree._bit)):
        assert tree._bit[i]==sum(tree._values[i-(i&-i):i])

DRIVER="int count=static_cast<int>(token());while(count--){fenwick_cli(false);std::cout<<'\\n';}"
BOUNDARY_DRIVER='FenwickTree tree(std::vector<Integer>(10000,1000000000));bool ok=tree.prefix_sum(10000)==10000000000000LL;tree.add(0,-2000000000LL);auto before=tree.prefix_sum(10000);try{tree.add(0,-1);ok=false;}catch(const std::invalid_argument&){}emit(ok && before==9998000000000LL && tree.prefix_sum(10000)==before && FenwickTree(std::vector<Integer>{}).range_sum(0,0)==0);'
