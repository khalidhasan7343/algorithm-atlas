import itertools

MOVES={"D":(1,0),"L":(0,-1),"R":(0,1),"U":(-1,0)}

def oracle(grid):
    if not grid or not grid[0][0] or not grid[-1][-1]:
        return []
    h,w=len(grid),len(grid[0]); result=[]
    # Enumerate move strings by length, then validate; no recursive path solver.
    for length in range(h*w):
        for moves in itertools.product("DLRU",repeat=length):
            r=c=0; seen={(0,0)}
            for move in moves:
                dr,dc=MOVES[move]; r+=dr; c+=dc
                if not(0<=r<h and 0<=c<w) or not grid[r][c] or (r,c) in seen:
                    break
                seen.add((r,c))
            else:
                if (r,c)==(h-1,w-1):
                    result.append("".join(moves))
    return sorted(result)

def valid_cases():
    cases=[([],[]),([[0]],[]),([[1]],[""])]
    for h,w in ((1,3),(2,2),(2,3),(3,2)):
        for cells in itertools.product((0,1),repeat=h*w):
            grid=[list(cells[r*w:(r+1)*w]) for r in range(h)]
            cases.append((grid,oracle(grid)))
    grid=[[1]*3 for _ in range(3)]
    cases.append((grid,oracle(grid)))
    return cases

def invalid_cases():
    return [([[]],ValueError),([[1],[1,0]],ValueError),([[2]],ValueError),
            ([[-1]],ValueError),([[2**63-1]],ValueError),([[True]],TypeError),
            ([[1.0]],TypeError),([[None]],TypeError)]

def call(module, value):
    return module.rat_in_a_maze(value)

def serialize(board):
    return " ".join(map(str,[len(board),*(x for row in board for x in [len(row),*row])]))

CLI_VALID=[("0 0",[]),("1 1 1",[""]),("2 2 1 1 1 1",["DR","RD"])]
CLI_INVALID=["", "1", "0 1", "1 0", "-1 2", "2 2 1", "1 1 2", "0 0 1",
             "9223372036854775807 9223372036854775807", "1 1 1x"]
CPP_BODY=r"""
    std::size_t n;
    while (std::cin >> n) {
        std::vector<std::vector<long long>> board(n);
        for (auto& row : board) {
            std::size_t width; std::cin >> width; row.resize(width);
            for (auto& cell : row) { std::cin >> cell; }
        }
        const auto before=board;
        reply([&] { return algorithm_atlas::rat_in_a_maze(board); });
        assert(board==before);
    }
"""
