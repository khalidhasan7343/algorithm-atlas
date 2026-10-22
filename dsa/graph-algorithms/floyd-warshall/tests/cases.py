import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('graph_oracles',Path(__file__).resolve().parents[2]/'oracles.py')
_o=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_o)
NAME='floyd-warshall'
SEED=7202

def vectors():return _o.weighted_vectors(NAME)
def encode(case):return _o.encode(case,weighted=True,sourced=False)
def check(actual,expected,case):
    if NAME=='floyd-warshall':assert actual==expected
    else:_o.check_paths(actual,expected,case)
def invalid():
    base=dict(n=2,edges=[],directed=True)
    if NAME!='floyd-warshall':base['source']=0
    cap=100 if NAME=='floyd-warshall' else 1000
    high=10**12 if NAME=='dijkstra' else 10**6
    changes=[dict(n=-1),dict(n=cap+1),dict(n=True),dict(edges=[(0,2,0)]),dict(edges=[(0,1,True)]),dict(edges=[(0,1)]),dict(edges=[(0,1,high+1)]),dict(edges=[(0,0,0)]*10001),dict(directed=1)]
    changes.append(dict(edges=[(0,1,-1 if NAME=='dijkstra' else -10**6-1)]))
    if NAME!='floyd-warshall':changes += [dict(source=None),dict(source=2),dict(n=0,source=0)]
    return [dict(base,**change) for change in changes]
def invalid_cli():
    base=dict(n=1,edges=[],directed=True)
    if NAME!='floyd-warshall':base['source']=0
    bad=dict(base,edges=[(0,0,-1 if NAME=='dijkstra' else -10**6-1)])
    return ['',encode(base)+'extra','-1 0 1','1 10001 1','1 0 2','1.5 0 1',encode(bad),'101 0 1' if NAME=='floyd-warshall' else '1001 0 1']

def boundaries(module):
    r=module.floyd_warshall(100,[(i,i+1,-10**6) for i in range(99)])
    assert r[0][-1]==-99*10**6 and r[-1][0] is None
    dense=[(u,v,-10**6) for u in range(30) for v in range(30)]
    assert all(x=='-inf' for row in module.floyd_warshall(30,dense) for x in row)

DRIVER="int count=static_cast<int>(token());while(count--){auto in=read_input(true,false,false,false);emit(floyd_warshall(make_graph(in.n,in.edges,in.directed,100)));std::cout<<'\\n';}"
BOUNDARY_DRIVER='std::vector<Edge> e;for(int i=0;i<99;++i)e.push_back({i,i+1,-1000000});auto r=floyd_warshall(make_graph(100,e,true,100));std::vector<Edge> dense;for(int u=0;u<30;++u)for(int v=0;v<30;++v)dense.push_back({u,v,-1000000});auto q=floyd_warshall(make_graph(30,dense,true));bool ok=r[0][99]==-99000000 && r[99][0]==INF;for(const auto& row:q)for(auto x:row)ok=ok&&x==NEG;emit(ok);'
