"""Seeded cross-algorithm comparisons, each paired with an independent oracle."""
import argparse
import importlib.util
import json
from pathlib import Path
import random

ROOT=Path(__file__).resolve().parents[1]
GRAPH=ROOT/'dsa/graph-algorithms'
EVIDENCE=ROOT/'docs/graph-algorithms-evidence'

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--through',type=int,choices=range(2,6),default=5)
    through=parser.parse_args().through
    support=load(GRAPH/'support.py','graph_support');oracle=load(GRAPH/'oracles.py','graph_oracle')
    canonical=support.canonical;rng=random.Random(70909);results={}
    def record(name):results[name]={'seed':70909,'cases':60,'failures':0,'independent_reference':True}
    for _ in range(60):
        n=rng.randrange(1,6);directed=bool(rng.randrange(2))
        edges=[(rng.randrange(n),rng.randrange(n)) for _ in range(rng.randrange(9))]
        weighted=[(u,v,1) for u,v in edges];s=rng.randrange(n)
        assert canonical('breadth-first-search').bfs(n,edges,s,directed)['distance']==canonical('dijkstra').dijkstra(n,weighted,s,directed)['distance']==oracle.simple_distances(n,weighted,s,directed)
        nonnegative=[(u,v,rng.randrange(6)) for u,v in edges]
        assert canonical('dijkstra').dijkstra(n,nonnegative,s,directed)['distance']==canonical('bellman-ford').bellman_ford(n,nonnegative,s,directed)['distance']==oracle.simple_distances(n,nonnegative,s,directed)
        potential=[rng.randrange(-5,6) for _ in range(n)]
        signed=[(u,v,rng.randrange(6)+potential[v]-potential[u]) for u,v in edges]
        matrix=canonical('floyd-warshall').floyd_warshall(n,signed)
        expected=[oracle.simple_distances(n,signed,source,True) for source in range(n)]
        assert matrix==expected
        assert all(canonical('bellman-ford').bellman_ford(n,signed,source)['distance']==matrix[source] for source in range(n))
    for name in ('BFS vs Dijkstra (unit weights)','Dijkstra vs Bellman-Ford (nonnegative)','Bellman-Ford vs Floyd-Warshall (no negative cycles)'):record(name)
    if through>=3:
        for _ in range(60):
            n=rng.randrange(6)
            edges=[(rng.randrange(n),rng.randrange(n),rng.randrange(-5,6)) for _ in range(rng.randrange(9))] if n else []
            case=dict(n=n,edges=edges,directed=False);expected=oracle.mst_weight(n,edges)
            a=canonical('prim').prim(**case);b=canonical('kruskal').kruskal(**case)
            oracle.check_mst(a,expected,case);oracle.check_mst(b,expected,case)
            assert a['weight']==b['weight']
        record('Prim vs Kruskal (minimum spanning forest)')
    if through>=4:
        for _ in range(60):
            n=rng.randrange(6)
            edges=[(rng.randrange(n),rng.randrange(n)) for _ in range(rng.randrange(10))] if n else []
            expected=oracle.structural_expected('tarjan-strongly-connected-components',n,edges)
            assert canonical('tarjan-strongly-connected-components').solve(n,edges)==canonical('kosaraju-strongly-connected-components').solve(n,edges)==expected
            assert canonical('bridges-detection').solve(n,edges)==oracle.structural_expected('bridges-detection',n,edges)
            assert canonical('articulation-points').solve(n,edges)==oracle.structural_expected('articulation-points',n,edges)
        for name in ('Tarjan vs Kosaraju (normalized SCCs)','Bridges vs edge-removal oracle','Articulation points vs vertex-removal oracle'):record(name)
    if through>=5:
        for _ in range(60):
            n=rng.randrange(1,6)
            edges=[(rng.randrange(n),rng.randrange(n)) for _ in range(rng.randrange(9))]
            potential=[rng.randrange(-5,6) for _ in range(n)]
            signed=[(u,v,rng.randrange(6)+potential[v]-potential[u]) for u,v in edges]
            expected=[oracle.simple_distances(n,signed,source,True) for source in range(n)]
            assert canonical('floyd-warshall').solve(n,signed)==canonical('johnson').solve(n,signed)==expected
            nonnegative=[(u,v,rng.randrange(6)) for u,v in edges];source=rng.randrange(n);goal=rng.randrange(n)
            optimal=oracle.simple_distances(n,nonnegative,source,True)[goal]
            result=canonical('a-star-search').solve(n,nonnegative,source,goal,[0]*n)
            assert result['cost']==canonical('dijkstra').solve(n,nonnegative,source)['distance'][goal]==optimal
            oracle.check_astar(result,optimal,dict(n=n,edges=nonnegative,source=source,goal=goal,directed=True))
        for name in ('Floyd-Warshall vs Johnson (no negative cycles)','A* h=0 vs Dijkstra'):record(name)
    result={'through_batch':through,'comparisons':results,'failures':0}
    (EVIDENCE/f'cross-matrix-batch{through}.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
