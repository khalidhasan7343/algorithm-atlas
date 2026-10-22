import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('graph_oracles',Path(__file__).resolve().parents[2]/'oracles.py')
_o=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_o)
NAME='kruskal'
SEED=7303

def vectors():return _o.mst_vectors()
def encode(case):return _o.encode(case,weighted=True)
def check(actual,expected,case):_o.check_mst(actual,expected,case)
def invalid():
    base=dict(n=2,edges=[],directed=False)
    changes=[dict(n=-1),dict(n=1001),dict(n=True),dict(edges=[(0,2,0)]),dict(edges=[(0,1,True)]),dict(edges=[(0,1)]),dict(edges=[(0,1,10**6+1)]),dict(edges=[(0,1,-10**6-1)]),dict(edges=[(0,0,0)]*10001),dict(directed=True),dict(directed=0)]
    return [dict(base,**change) for change in changes]
def invalid_cli():return ['','-1 0 0','1001 0 0','1 10001 0','1 0 2','1 0 1','1 0 0 extra','1 1 0 0 0 1000001','1 1 0 0 2 0']
def boundaries(module):
    edges=[(i,i+1,-10**6) for i in range(999)]
    result=module.solve(1000,edges)
    assert result['weight']==-999*10**6 and len(result['edges'])==999
    assert module.solve(1,[(0,0,-10**6)]*10000)==dict(weight=0,edges=[])

DRIVER="int count=static_cast<int>(token());while(count--){auto in=read_input(true,false,false,false);emit(kruskal(make_graph(in.n,in.edges,in.directed)));std::cout<<'\\n';}"
BOUNDARY_DRIVER='std::vector<Edge> e;for(int i=0;i<999;++i)e.push_back({i,i+1,-1000000});auto r=kruskal(make_graph(1000,e,false));auto q=kruskal(make_graph(1,std::vector<Edge>(10000,{0,0,-1000000}),false));emit(r.weight==-999000000 && r.edges.size()==999 && q.weight==0 && q.edges.empty());'
