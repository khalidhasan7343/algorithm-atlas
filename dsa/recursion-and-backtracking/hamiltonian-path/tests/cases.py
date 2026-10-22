import itertools
import random

def graphs(n,directed=False):
    edges=[(r,c) for r in range(n) for c in range(n) if r!=c and (directed or r<c)]
    for bits in itertools.product((0,1),repeat=len(edges)):
        graph=[[0]*n for _ in range(n)]
        for (r,c),bit in zip(edges,bits):
            graph[r][c]=bit
            if not directed: graph[c][r]=bit
        yield graph

def serialize(value):
    board,mode=value
    return " ".join(map(str,[len(board),int(mode),
                     *(x for row in board for x in [len(row),*row])]))

def oracle(graph):
    for path in itertools.permutations(range(len(graph))):
        if all(graph[a][b] for a,b in zip(path,path[1:])):
            return list(path)
    return None

def valid_cases():
    cases=[]
    for directed,limit in ((False,5),(True,4)):
        for n in range(limit):
            for graph in graphs(n,directed):
                cases.append(((graph,directed),oracle(graph)))
    rng=random.Random(20261023)
    for directed in (False,True):
        for n in range(4,8):
            for _ in range(5):
                graph=[[0]*n for _ in range(n)]
                for r in range(n):
                    for c in range(n):
                        if r!=c and (directed or r<c):
                            graph[r][c]=rng.randrange(2)
                            if not directed: graph[c][r]=graph[r][c]
                cases.append(((graph,directed),oracle(graph)))
    cases.extend([(([[1]],False),[0]),(([[0,0,0],[1,0,0],[0,1,0]],True),[2,1,0]),
                  (([[1,0],[0,1]],False),None)])
    return cases

def invalid_cases():
    return [(([[0,1],[0,0]],False),ValueError),(([[0],[0]],True),ValueError),
            (([[]],False),ValueError),(([[2]],True),ValueError),
            (([[-1]],False),ValueError),(([[True]],True),TypeError),
            (([[1.0]],False),TypeError),(([],1),TypeError),(([],None),TypeError)]

def call(module,value):
    return module.hamiltonian_path(value[0],directed=value[1])

CLI_VALID=[("0 0",[]),("0 1 0",[0]),("1 3 0 0 0 1 0 0 0 1 0",[2,1,0]),
           ("0 2 0 0 0 0",None)]
CLI_INVALID=["", "0", "2 0", "0 -1", "0 2 0 1 0 0", "1 1 2", "1 0 0",
             "0 9223372036854775807", "1 1 1x", "0 2 0 0"]
CPP_BODY=r"""
    std::size_t n; int mode;
    while (std::cin >> n >> mode) {
        algorithm_atlas::Graph graph(n);
        for (auto& row : graph) {
            std::size_t width; std::cin >> width; row.resize(width);
            for (auto& value : row) { std::cin >> value; }
        }
        const auto before=graph;
        reply([&] { return algorithm_atlas::hamiltonian_path(graph,mode==1); });
        assert(graph==before);
    }
"""
