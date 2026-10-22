import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('graph_oracles',Path(__file__).resolve().parents[2]/'oracles.py')
_o=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_o)
NAME='a-star-search'
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
    edges=[(i,i+1,10**6) for i in range(999)]
    r=module.a_star(1000,edges,0,999,[0]*1000)
    assert r['cost']==999*10**6 and len(r['path'])==1000
    assert module.a_star(3,[(0,1,1),(1,2,1),(0,2,5)],0,2,[0,100,0])['cost']==5
    assert module.a_star(1,[(0,0,0)]*10000,0,0,[0])==dict(cost=0,path=[0],edges=[])

DRIVER="int count=static_cast<int>(token());while(count--){auto in=read_input(true,true,true,false);emit(a_star(make_graph(in.n,in.edges,in.directed,1000,0,1000000),source_vertex(in.n,in.source),source_vertex(in.n,in.goal),in.heuristic));std::cout<<'\\n';}"
BOUNDARY_DRIVER='std::vector<Edge> e;for(int i=0;i<999;++i)e.push_back({i,i+1,1000000});auto r=a_star(make_graph(1000,e,true),0,999,std::vector<Integer>(1000));auto q=a_star(make_graph(3,{{0,1,1},{1,2,1},{0,2,5}},true),0,2,{0,100,0});emit(r.cost==999000000 && r.path.size()==1000 && q.cost==5);'
