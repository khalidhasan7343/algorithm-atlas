import itertools

def oracle(n):
    return [list(p) for p in itertools.permutations(range(n))
            if len({r+c for r,c in enumerate(p)})==n
            and len({r-c for r,c in enumerate(p)})==n]

def valid_cases():
    return [(n, oracle(n)) for n in range(9)]

def invalid_cases():
    return [(-1, ValueError), (-100, ValueError), (True, TypeError),
            (2.0, TypeError), (None, TypeError)]

def call(module, value):
    return module.n_queens(value)

def serialize(value):
    return str(value)

CLI_VALID=[("0",[[]]),("1",[[0]]),("2",[]),("4",[[1,3,0,2],[2,0,3,1]])]
CLI_INVALID=["", "-1", "1 2", "true", "+", "1.0", "١"]
CPP_BODY=r"""
    long long n;
    while (std::cin >> n) { reply([&] { return algorithm_atlas::n_queens(n); }); }
"""
