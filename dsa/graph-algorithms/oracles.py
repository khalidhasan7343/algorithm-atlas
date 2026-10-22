"""Independent bounded graph references: enumeration, closure and removal."""
import itertools
import random


def reachability(n, edges, directed=True, removed_vertex=None, removed_edge=None):
    reach = [[False]*n for _ in range(n)]
    for u in range(n):
        if u != removed_vertex:
            reach[u][u] = True
    for i, e in enumerate(edges):
        u, v = e[:2]
        if i != removed_edge and removed_vertex not in (u,v):
            reach[u][v] = True
            if not directed:
                reach[v][u] = True
    for k in range(n):
        for u in range(n):
            for v in range(n):
                reach[u][v] |= reach[u][k] and reach[k][v]
    return reach


def groups(n, edges, removed_vertex=None, removed_edge=None):
    reach = reachability(n, edges, False, removed_vertex, removed_edge)
    remaining = set(range(n)) - {removed_vertex}
    result = []
    while remaining:
        root = min(remaining)
        group = sorted(v for v in remaining if reach[root][v])
        result.append(group)
        remaining.difference_update(group)
    return result


def simple_distances(n, edges, source, directed=True):
    """Enumerate all vertex-simple paths; valid for graphs with no negative cycle."""
    best = [None]*n
    if source is None:
        return best
    def visit(u, used, cost):
        if best[u] is None or cost < best[u]:
            best[u] = cost
        for e in edges:
            a,b = e[:2]; w=e[2] if len(e)==3 else 1
            targets = ([b] if a==u else []) + ([a] if not directed and b==u else [])
            for v in targets:
                if v not in used:
                    visit(v, used|{v}, cost+w)
    visit(source,{source},0)
    return best


def foundation_expected(name, case):
    n, edges, directed = case['n'],case['edges'],case['directed']
    if name == 'union-find':
        partition=groups(n,edges)
        return dict(groups=partition,count=len(partition))
    if name == 'topological-sorting':
        return next((list(p) for p in itertools.permutations(range(n))
                     if all(p.index(u)<p.index(v) for u,v in edges)),None)
    neighbors=[[] for _ in range(n)]
    for i,(u,v) in enumerate(edges):
        neighbors[u].append((v,i))
        if not directed:
            neighbors[v].append((u,i))
    parent,parent_edge=[None]*n,[None]*n
    if name=='breadth-first-search':
        distance=simple_distances(n,edges,case['source'],directed)
        # At each depth, first-discovery order is induced by the previous level's arcs.
        order=[];front=[] if case['source'] is None else [case['source']]
        discovered=set(front)
        while front:
            order.extend(front); following=[]
            for u in front:
                for v,i in neighbors[u]:
                    if v not in discovered:
                        discovered.add(v);parent[v]=u;parent_edge[v]=i;following.append(v)
            front=following
        return dict(order=order,distance=distance,parent=parent,parent_edge=parent_edge)
    order,finish,component=[],[],[None]*n
    def visit(u,root):
        component[u]=root;order.append(u)
        for v,i in neighbors[u]:
            if component[v] is None:
                parent[v],parent_edge[v]=u,i;visit(v,root)
        finish.append(u)
    for root in range(n):
        if component[root] is None:
            visit(root,root)
    return dict(order=order,finish=finish,parent=parent,parent_edge=parent_edge,component=component)


def foundation_vectors(name):
    rng=random.Random(7101)
    cases=[]
    for n in range(5):
        pool=list(itertools.product(range(n),repeat=2))
        for _ in range(24):
            directed=False if name=='union-find' else True if name=='topological-sorting' else bool(rng.randrange(2))
            edges=[list(rng.choice(pool)) for _ in range(rng.randrange(9))] if pool else []
            case=dict(n=n,edges=edges,directed=directed)
            if name=='breadth-first-search':case['source']=rng.randrange(n) if n else None
            cases.append((case,foundation_expected(name,case)))
    # Exhaust every loop-free directed three-vertex graph, including all DAG orders.
    pool=[(u,v) for u in range(3) for v in range(3) if u!=v]
    for mask in range(1<<len(pool)):
        case=dict(n=3,edges=[list(e) for i,e in enumerate(pool) if mask>>i&1],directed=name!='union-find')
        if name=='breadth-first-search':case['source']=0
        cases.append((case,foundation_expected(name,case)))
    return cases


def encode(case, weighted=False, sourced=False, astar=False):
    parts=[case['n'],len(case['edges']),int(case['directed'])]
    if sourced:parts.append(-1 if case['source'] is None else case['source'])
    if astar:
        parts.append(-1 if case['goal'] is None else case['goal'])
        parts.extend(case['heuristic'])
    for e in case['edges']:parts.extend(e)
    return ' '.join(map(str,parts))+'\n'


def negative_vertices(n,edges,directed):
    negative=set()
    def visit(start,u,used,cost):
        for edge in edges:
            a,b,w=edge
            targets=([b] if a==u else [])+([a] if not directed and b==u else [])
            for v in targets:
                if v==start and cost+w<0:negative.add(start)
                elif v not in used:visit(start,v,used|{v},cost+w)
    for start in range(n):visit(start,start,{start},0)
    return negative


def weighted_expected(n,edges,source,directed):
    distance=simple_distances(n,edges,source,directed)
    reach=reachability(n,edges,directed)
    negative=negative_vertices(n,edges,directed)
    for v in range(n):
        if any(reach[source][k] and reach[k][v] for k in negative):distance[v]='-inf'
    return distance


def weighted_vectors(name):
    rng=random.Random(7202);cases=[]
    for n in range(6):
        for _ in range(24):
            edges=[[rng.randrange(n),rng.randrange(n),rng.randrange(0 if name=='dijkstra' else -4,7)] for _ in range(rng.randrange(9))] if n else []
            case=dict(n=n,edges=edges,directed=bool(rng.randrange(2)))
            source=rng.randrange(n) if n else None
            if name!='floyd-warshall':case['source']=source
            expected=([weighted_expected(n,edges,s,case['directed']) for s in range(n)]
                      if name=='floyd-warshall' else weighted_expected(n,edges,source,case['directed']))
            cases.append((case,expected))
    for edges in ([[0,1,2],[1,2,-3],[2,1,1],[2,3,2]],[[0,1,2],[2,3,-2],[3,2,1]],[[0,0,-1]],[[0,1,0],[1,0,0],[0,1,2]]):
        if name=='dijkstra':edges=[[u,v,abs(w)] for u,v,w in edges]
        n=1+max(max(u,v) for u,v,w in edges)
        case=dict(n=n,edges=edges,directed=True)
        if name!='floyd-warshall':case['source']=0
        expected=[weighted_expected(n,edges,s,True) for s in range(n)] if name=='floyd-warshall' else weighted_expected(n,edges,0,True)
        cases.append((case,expected))
    return cases


def check_paths(actual, expected, case):
    assert actual['distance']==expected, (case,actual,expected)
    n=case['n'];edges=case['edges'];source=case['source']
    assert len(actual['parent'])==len(actual['parent_edge'])==n
    for target,cost in enumerate(expected):
        if cost in (None,'-inf') or target==source:
            assert actual['parent'][target] is None and actual['parent_edge'][target] is None
            continue
        seen=set();v=target;total=0
        while v!=source:
            assert v not in seen;seen.add(v)
            parent,i=actual['parent'][v],actual['parent_edge'][v]
            assert type(parent) is int and 0<=parent<n and type(i) is int and 0<=i<len(edges)
            a,b,w=edges[i]
            assert (a,b)==(parent,v) or (not case['directed'] and (b,a)==(parent,v))
            total+=w;v=parent
        assert total==cost


def mst_weight(n,edges):
    original=groups(n,edges);required=n-len(original);best=None
    for ids in itertools.combinations(range(len(edges)),required):
        chosen=[edges[i] for i in ids]
        if groups(n,chosen)==original:
            cost=sum(e[2] for e in chosen)
            best=cost if best is None else min(best,cost)
    return best


def mst_vectors():
    rng=random.Random(7303);result=[]
    for n in range(6):
        for _ in range(24):
            edges=[[rng.randrange(n),rng.randrange(n),rng.randrange(-6,7)] for _ in range(rng.randrange(9))] if n else []
            case=dict(n=n,edges=edges,directed=False)
            result.append((case,mst_weight(n,edges)))
    return result


def check_mst(actual,expected,case):
    ids=actual['edges'];edges=case['edges'];n=case['n']
    assert len(ids)==len(set(ids)) and all(type(i) is int and 0<=i<len(edges) for i in ids)
    chosen=[edges[i] for i in ids]
    assert sum(e[2] for e in chosen)==actual['weight']==expected
    assert groups(n,chosen)==groups(n,edges)
    assert len(ids)==n-len(groups(n,edges))  # connectivity plus this size implies acyclicity.


def structural_expected(name,n,edges):
    if 'strongly-connected' in name:
        reach=reachability(n,edges);remaining=set(range(n));result=[]
        while remaining:
            root=min(remaining);group=sorted(v for v in remaining if reach[root][v] and reach[v][root])
            result.append(group);remaining.difference_update(group)
        return result
    count=len(groups(n,edges))
    if name=='bridges-detection':
        return [i for i in range(len(edges)) if len(groups(n,edges,removed_edge=i))>count]
    return [v for v in range(n) if len(groups(n,edges,removed_vertex=v))>count]


def structural_vectors(name):
    rng=random.Random(7404);cases=[]
    for n in range(6):
        for _ in range(24):
            edges=[[rng.randrange(n),rng.randrange(n)] for _ in range(rng.randrange(10))] if n else []
            cases.append((dict(n=n,edges=edges,directed='strongly-connected' in name),structural_expected(name,n,edges)))
    pool=[(u,v) for u in range(3) for v in range(3) if u!=v]
    for mask in range(64):
        edges=[list(e) for i,e in enumerate(pool) if mask>>i&1]
        cases.append((dict(n=3,edges=edges,directed='strongly-connected' in name),structural_expected(name,3,edges)))
    return cases


def astar_vectors():
    rng=random.Random(7505);result=[]
    for n in range(6):
        for _ in range(24):
            directed=bool(rng.randrange(2))
            edges=[[rng.randrange(n),rng.randrange(n),rng.randrange(7)] for _ in range(rng.randrange(9))] if n else []
            source=rng.randrange(n) if n else None;goal=rng.randrange(n) if n else None
            true=[simple_distances(n,edges,v,directed)[goal] for v in range(n)]
            heuristic=[rng.randrange((cost if cost is not None else 8)+1) for cost in true]
            case=dict(n=n,edges=edges,directed=directed,source=source,goal=goal,heuristic=heuristic)
            result.append((case,simple_distances(n,edges,source,directed)[goal] if n else None))
    case=dict(n=4,edges=[[0,1,3],[0,2,1],[2,1,1],[1,3,2],[2,3,100]],source=0,goal=3,heuristic=[0,0,3,0],directed=True)
    result.append((case,4))  # Admissible inconsistent h forces vertex 1 to reopen.
    return result


def check_astar(actual,expected,case):
    assert actual['cost']==expected
    if expected is None:
        assert actual['path']==actual['edges']==[];return
    path,ids=actual['path'],actual['edges']
    assert path[0]==case['source'] and path[-1]==case['goal'] and len(path)==len(ids)+1
    assert len(path)==len(set(path))
    total=0
    for u,v,i in zip(path,path[1:],ids):
        assert type(i) is int and 0<=i<len(case['edges'])
        a,b,w=case['edges'][i]
        assert (a,b)==(u,v) or (not case['directed'] and (b,a)==(u,v))
        total+=w
    assert total==expected


def johnson_vectors():
    result=[]
    for case,matrix in weighted_vectors('floyd-warshall'):
        case=dict(case,directed=True)
        n,edges=case['n'],case['edges']
        matrix=[weighted_expected(n,edges,s,True) for s in range(n)]
        result.append((case,None if any('-inf' in row for row in matrix) else matrix))
    return result
