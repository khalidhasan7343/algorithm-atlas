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

def oracle(graph,m):
    n=len(graph)
    for colors in itertools.product(range(m),repeat=n):
        if all(not graph[r][c] or colors[r]!=colors[c]
               for r in range(n) for c in range(n)):
            return list(colors)
    return None

def valid_cases():
    cases=[((graph,m),oracle(graph,m)) for n in range(5) for graph in graphs(n)
           for m in range(n+1)]
    cases.extend([(([[1]],1),None),(([[0,0],[0,0]],2**63-1),[0,0]),
                  (([[0,1,0],[1,0,0],[0,0,0]],2),[0,1,0]),
                  (([[0,0],[0,1]],2),None)])
    return cases

def invalid_cases():
    return [(([], -1),ValueError),(([[0,1],[0,0]],2),ValueError),
            (([[0],[0]],2),ValueError),(([[]],2),ValueError),
            (([[2]],1),ValueError),(([[-1]],1),ValueError),
            (([[True]],1),TypeError),(([[1.0]],1),TypeError),
            (([],True),TypeError),(([],1.0),TypeError)]

def call(module,value):
    return module.graph_coloring(*value)

CLI_VALID=[("0 0",[]),("0 1 0",None),("2 2 0 1 1 0",[0,1]),("2 1 1",None)]
CLI_INVALID=["", "2", "-1 0", "2 -1", "2 2 0 1 0 0", "2 1 2", "2 0 0",
             "2 9223372036854775807", "2 1 1x", "2 2 0 0"]
CPP_BODY=r"""
    std::size_t n; long long m;
    while (std::cin >> n >> m) {
        algorithm_atlas::Graph graph(n);
        for (auto& row : graph) {
            std::size_t width; std::cin >> width; row.resize(width);
            for (auto& value : row) { std::cin >> value; }
        }
        const auto before=graph;
        reply([&] { return algorithm_atlas::graph_coloring(graph,m); });
        assert(graph==before);
    }
"""
