import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('graph_oracles',Path(__file__).resolve().parents[2]/'oracles.py')
_o=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_o)
NAME='johnson'
SEED=7505 if NAME=='a-star-search' else 7202

def vectors():return _o.astar_vectors() if NAME=='a-star-search' else _o.johnson_vectors()
def encode(case):return _o.encode(case,weighted=True,sourced=NAME=='a-star-search',astar=NAME=='a-star-search')
def check(actual,expected,case):
    if NAME=='a-star-search':_o.check_astar(actual,expected,case)
    else:assert actual==expected,(case,actual,expected)
def invalid():
    base=dict(n=2,edges=[],directed=True)
    if NAME=='a-star-search':base.update(source=0,goal=1,heuristic=[0,0])
    changes=[dict(n=-1),dict(n=1001 if NAME=='a-star-search' else 101),dict(n=True),dict(edges=[(0,2,0)]),dict(edges=[(0,1,True)]),dict(edges=[(0,1)]),dict(edges=[(0,1,10**6+1)]),dict(edges=[(0,1,-1 if NAME=='a-star-search' else -10**6-1)]),dict(edges=[(0,0,0)]*10001),dict(directed=1)]
    if NAME=='a-star-search':changes += [dict(source=None),dict(goal=None),dict(source=2),dict(goal=2),dict(heuristic=None),dict(heuristic=[]),dict(heuristic=[True,0]),dict(heuristic=[-1,0]),dict(heuristic=[10**9+1,0]),dict(heuristic=[0,1])]
    else:changes += [dict(directed=False)]
    return [dict(base,**change) for change in changes]
def invalid_cli():
    base=dict(n=1,edges=[],directed=True)
    if NAME=='a-star-search':base.update(source=0,goal=0,heuristic=[0])
    return ['',encode(base)+'extra','-1 0 1','1 10001 1','1 0 2','1.1 0 1',encode(dict(base,edges=[(0,0,1000001)])),('1 0 1 0 0 1' if NAME=='a-star-search' else '101 0 1')]
def boundaries(module):
    edges=[(i,i+1,-10**6) for i in range(99)]
    assert module.johnson(100,edges)[0][-1]==-99*10**6
    assert module.johnson(4,[(2,3,-2),(3,2,1)]) is None
    assert module.johnson(100,[(i%100,i%100,0) for i in range(10000)])[0][-1] is None

DRIVER='int count=static_cast<int>(token());while(count--){auto in=read_input(true,false,false,false);auto result=johnson(make_graph(in.n,in.edges,in.directed,100));if(result)emit(*result);else std::cout<<"null";std::cout<<\'\\n\';}'
BOUNDARY_DRIVER='std::vector<Edge> e;for(int i=0;i<99;++i)e.push_back({i,i+1,-1000000});auto r=johnson(make_graph(100,e,true));auto q=johnson(make_graph(4,{{2,3,-2},{3,2,1}},true));auto z=johnson(make_graph(100,std::vector<Edge>(10000,{0,0,0}),true));emit(r.has_value() && (*r)[0][99]==-99000000 && !q.has_value() && z.has_value() && (*z)[0][99]==INF);'
