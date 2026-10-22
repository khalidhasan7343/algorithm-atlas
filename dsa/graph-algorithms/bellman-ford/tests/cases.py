import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('graph_oracles',Path(__file__).resolve().parents[2]/'oracles.py')
_o=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_o)
NAME='bellman-ford'
SEED=7202

def vectors():return _o.weighted_vectors(NAME)
def encode(case):return _o.encode(case,weighted=True,sourced=True)
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
    r=module.bellman_ford(1000,[(i,i+1,-10**6) for i in range(999)],0)
    assert r['distance'][-1]==-999*10**6
    assert len(module.path_to(r,999)['vertices'])==1000
    assert module.bellman_ford(2,[(1,1,-1)],0)['distance']==[0,None]
    assert module.bellman_ford(2,[(0,1,-1)],0,False)['distance']==['-inf','-inf']

DRIVER="int count=static_cast<int>(token());while(count--){auto in=read_input(true,true,false,false);emit(bellman_ford(make_graph(in.n,in.edges,in.directed),source_vertex(in.n,in.source)));std::cout<<'\\n';}"
BOUNDARY_DRIVER='std::vector<Edge> e;for(int i=0;i<999;++i)e.push_back({i,i+1,-1000000});auto r=bellman_ford(make_graph(1000,e,true),0);auto q=bellman_ford(make_graph(2,{{0,1,-1}},false),0);emit(r.distance.back()==-999000000LL && path_to(r,999).first.size()==1000 && q.distance[0]==NEG && q.distance[1]==NEG);'
