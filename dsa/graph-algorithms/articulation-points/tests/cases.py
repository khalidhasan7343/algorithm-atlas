import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('graph_oracles',Path(__file__).resolve().parents[2]/'oracles.py')
_o=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_o)
NAME='articulation-points'
SEED=7404

def vectors():return _o.structural_vectors(NAME)
def encode(case):return _o.encode(case)
def check(actual,expected,case):assert actual==expected,(case,actual,expected)
def invalid():
    base=dict(n=2,edges=[],directed='strongly-connected' in NAME)
    changes=[dict(n=-1),dict(n=1001),dict(n=True),dict(edges=[(0,2)]),dict(edges=[(0,True)]),dict(edges=[(0,)]),dict(edges=[(0,1,1)]),dict(edges=[(0,0)]*10001),dict(directed=not base['directed']),dict(directed=1)]
    return [dict(base,**change) for change in changes]
def invalid_cli():
    mode='1' if 'strongly-connected' in NAME else '0'
    return ['', '-1 0 '+mode,'1001 0 '+mode,'1 10001 '+mode,'1 0 2','1 0 '+mode+' extra','1 1 '+mode+' 0 2','1 0 '+('0' if mode=='1' else '1')]
def boundaries(module):
    edges=[(i,i+1) for i in range(999)]
    r=module.solve(1000,edges)
    assert r==list(range(1,999))
    assert module.solve(2,[(0,1)]*9999+[(0,0)])==[]

DRIVER="int count=static_cast<int>(token());while(count--){auto in=read_input(false,false,false,false);emit(articulation_points(make_graph(in.n,in.edges,in.directed)));std::cout<<'\\n';}"
BOUNDARY_DRIVER='std::vector<Edge> e;for(int i=0;i<999;++i)e.push_back({i,i+1,1});auto r=articulation_points(make_graph(1000,e,false));auto q=articulation_points(make_graph(2,std::vector<Edge>(10000,{0,1,1}),false));emit(r.size()==998 && q.empty());'
