import random

def oracle(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(len(a))) for j in range(len(a))] for i in range(len(a))]

def data():
    cases=[([],[]),([[0]],[[7]]),([[-1000]],[[1000]])]
    rng=random.Random(20261022)
    for n in (2,3,4,5,7,8,9,16,17,32):
        a=[[rng.randrange(-20,21) for _ in range(n)] for _ in range(n)]
        b=[[rng.randrange(-20,21) for _ in range(n)] for _ in range(n)]
        identity=[[int(i==j) for j in range(n)] for i in range(n)]
        zero=[[0]*n for _ in range(n)]
        cases.extend([(a,b),(a,identity),(identity,b),(a,zero)])
    n=128
    a=[[1000 if (r+c)%2 else -1000 for c in range(n)] for r in range(n)]
    b=[[int(r==c) for c in range(n)] for r in range(n)]
    cases.append((a,b))
    return cases

def invalid():
    return [(([],[[1]]),ValueError),(([[1,2]],[[1]]),ValueError),
            (([[1]],[[1,2]]),ValueError),(([[1001]],[[0]]),ValueError),
            (([[0]],[[-1001]]),ValueError),(([[True]],[[1]]),TypeError),
            (([[1.0]],[[1]]),TypeError),(([[1]],[[None]]),TypeError),
            (([[0]*129 for _ in range(129)],[[0]*129 for _ in range(129)]),ValueError)]

CLI_VALID=[("0",[]),("1 -1000 1000",[[-1000000]]),
           ("2 1 2 3 4 5 6 7 8",[[19,22],[43,50]]),
           ("3 1 2 3 4 5 6 7 8 9 1 0 0 0 1 0 0 0 1",[[1,2,3],[4,5,6],[7,8,9]])]
CLI_INVALID=["","-1","129","1","0 1","2 1 2","1 1001 1","1 0 -1001",
             "1 1 2x","9223372036854775807","1 0 9223372036854775808"]
