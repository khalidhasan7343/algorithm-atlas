import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('graph_oracles',Path(__file__).resolve().parents[2]/'oracles.py')
_o=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_o)
NAME='breadth-first-search'
SEED=7101

def vectors():return _o.foundation_vectors(NAME)
def encode(case):return _o.encode(case,sourced=True)
def invalid():
    base=dict(n=2,edges=[],directed=NAME!='union-find')
    if NAME=='breadth-first-search':base['source']=0
    changes=[dict(n=-1),dict(n=1001),dict(n=True),dict(edges=[(0,2)]),dict(edges=[(True,0)]),dict(edges=[(0,)]),dict(edges=[(0,1,1)]),dict(edges=[(0,0)]*10001),dict(directed=1)]
    if NAME=='breadth-first-search':changes += [dict(source=None),dict(source=2),dict(n=0,source=0)]
    if NAME in ('union-find','topological-sorting'):changes.append(dict(directed=NAME=='union-find'))
    return [dict(base,**change) for change in changes]
def invalid_cli():
    valid=encode(dict(n=1,edges=[],directed=NAME!='union-find',**({'source':0} if NAME=='breadth-first-search' else {})))
    return ['-1 0 1','1001 0 1','1 10001 1','1 0 2','1 1 1 0 9 9',valid+'extra','1.0 0 1','99999999999999999999999 0 1','']

def boundaries(module):
    r=module.bfs(1000,[(i,i+1) for i in range(999)],0)
    assert r['distance'][-1]==999
    assert module.path_to(r,999)==dict(vertices=list(range(1000)),edges=list(range(999)))
    assert module.bfs(2,[(0,0)]*10000,0)['distance']==[0,None]

DRIVER="int count=static_cast<int>(token());while(count--){auto in=read_input(false,true,false,false);emit(bfs(make_graph(in.n,in.edges,in.directed),source_vertex(in.n,in.source)));std::cout<<'\\n';}"
BOUNDARY_DRIVER='std::vector<Edge> edges;for(int i=0;i<999;++i)edges.push_back({i,i+1,1});auto r=bfs(make_graph(1000,edges,true),0);auto p=path_to(r.paths,999);bool ok=r.paths.distance[999]==999 && p.first.size()==1000 && p.second.size()==999;emit(ok);'
