import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('graph_oracles',Path(__file__).resolve().parents[2]/'oracles.py')
_o=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_o)
NAME='union-find'
SEED=7101

def vectors():return _o.foundation_vectors(NAME)
def encode(case):return _o.encode(case,sourced=False)
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
    sets=module.UnionFind(1000)
    for i in range(999):assert sets.union(i,i+1)
    assert sets.component_size(500)==1000 and sets.count==1
    assert sets.connected(0,999) and not sets.union(0,999)
    assert sets.groups()==[list(range(1000))]
    for v in (-1,1000,True):
        try: sets.find(v)
        except ValueError: pass
        else: raise AssertionError(v)

DRIVER="int count=static_cast<int>(token());while(count--){auto in=read_input(false,false,false,false);union_find_cli(make_graph(in.n,in.edges,in.directed));std::cout<<'\\n';}"
BOUNDARY_DRIVER='UnionFind sets(1000);bool ok=true;for(int i=0;i<999;++i)ok=ok&&sets.unite(i,i+1);ok=ok && sets.component_size(500)==1000 && sets.count()==1 && sets.connected(0,999) && !sets.unite(0,999) && sets.groups().size()==1;try{sets.find(1000);ok=false;}catch(const std::invalid_argument&){}emit(ok);'
