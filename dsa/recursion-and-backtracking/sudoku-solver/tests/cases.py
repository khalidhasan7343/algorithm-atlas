import copy
import random

PUZZLE=[[int(c) for c in line] for line in (
"530070000","600195000","098000060","800060003","400803001",
"700020006","060000280","000419005","000080079")]
SOLUTION=[[int(c) for c in line] for line in (
"534678912","672195348","198342567","859761423","426853791",
"713924856","961537284","287419635","345286179")]

def solved(board, givens):
    digits=set(range(1,10))
    assert board is not None and len(board)==9 and all(len(r)==9 for r in board)
    assert all(set(row)==digits for row in board)
    assert all({board[r][c] for r in range(9)}==digits for c in range(9))
    assert all({board[r][c] for r in range(br,br+3) for c in range(bc,bc+3)}==digits
               for br in (0,3,6) for bc in (0,3,6))
    assert all(not givens[r][c] or givens[r][c]==board[r][c]
               for r in range(9) for c in range(9))

def oracle(board):
    # Independent minimum-remaining-values search with set recomputation.
    work=copy.deepcopy(board)
    def fill():
        choices=[]
        for r in range(9):
            for c in range(9):
                if work[r][c]==0:
                    peers=set(work[r]) | {work[i][c] for i in range(9)} | {
                        work[i][j] for i in range(r//3*3,r//3*3+3)
                        for j in range(c//3*3,c//3*3+3)}
                    choices.append((set(range(1,10))-peers,r,c))
        if not choices:
            return copy.deepcopy(work)
        candidates,r,c=min(choices,key=lambda item:len(item[0]))
        for value in sorted(candidates):
            work[r][c]=value
            answer=fill()
            work[r][c]=0
            if answer is not None:
                return answer
        return None
    return fill()

def valid_cases():
    wrong=copy.deepcopy(PUZZLE); wrong[0][2]=1
    assert oracle(PUZZLE)==SOLUTION and oracle(wrong) is None
    cases=[(PUZZLE,SOLUTION),(SOLUTION,SOLUTION),(wrong,None)]
    rng=random.Random(20261023)
    for _ in range(8):
        board=copy.deepcopy(SOLUTION)
        for i in rng.sample(range(81),12):
            board[i//9][i%9]=0
        cases.append((board,oracle(board)))
    return cases

def invalid_cases():
    cases=[([],ValueError),([[0]*9]*8,ValueError),([[0]*8]*9,ValueError)]
    for r,c in ((0,1),(1,0),(1,1)):
        board=[[0]*9 for _ in range(9)]
        board[0][0]=board[r][c]=5
        cases.append((board,ValueError))
    for value,error in ((-1,ValueError),(10,ValueError),(2**63-1,ValueError),
                        (True,TypeError),(1.0,TypeError),(None,TypeError)):
        board=[[0]*9 for _ in range(9)]; board[0][0]=value
        cases.append((board,error))
    return cases

def call(module, value):
    return module.solve_sudoku(value)

def serialize(board):
    return " ".join(map(str,[len(board),*(x for row in board for x in [len(row),*row])]))

CLI_VALID=[(" ".join(map(str,sum(PUZZLE,[]))),SOLUTION)]
CLI_INVALID=["", "0", "0 "*80, "0 "*82, "x "*81,
             " ".join(map(str,[10]+[0]*80)),
             " ".join(map(str,[1,1]+[0]*79))]
CPP_BODY=r"""
    std::size_t n;
    while (std::cin >> n) {
        algorithm_atlas::Board board(n);
        for (auto& row : board) {
            std::size_t width; std::cin >> width; row.resize(width);
            for (auto& cell : row) { std::cin >> cell; }
        }
        const auto before=board;
        reply([&] { return algorithm_atlas::solve_sudoku(board); });
        assert(board==before);
    }
"""
