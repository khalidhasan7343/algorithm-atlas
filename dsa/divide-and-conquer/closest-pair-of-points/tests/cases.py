import itertools
import random

def oracle(points):
    candidates=[((a[0]-b[0])**2+(a[1]-b[1])**2,i,j)
                for i,a in enumerate(points) for j,b in enumerate(points) if i<j]
    return min(candidates) if candidates else None

def data():
    cases=[[],[(0,0)],[(0,0),(0,0)],[(1,1),(0,0),(1,1),(0,0)],
           [(-10**9,-10**9),(10**9,10**9)],[(0,i) for i in range(20)],
           [(i,0) for i in range(20)],[(i,3*i-1) for i in range(-10,11)],
           [(x,y) for x in range(-3,4) for y in range(-3,4)]]
    lattice=[(-1,0),(0,0),(0,1),(1,0)]
    cases.extend([list(points) for n in range(5) for points in itertools.product(lattice,repeat=n)])
    rng=random.Random(20261022)
    for n in (2,3,4,5,7,8,15,32,65):
        for _ in range(12):cases.append([(rng.randrange(-100,101),rng.randrange(-100,101)) for _ in range(n)])
    # Many zero-distance pairs must choose by original indices, not coordinates.
    cases.append([(8,8),(9,9),(8,8),(0,0),(0,0)])
    return cases

def invalid():
    return [([(1,)],ValueError),([(1,2,3)],ValueError),([(True,0)],TypeError),
            ([(0,1.0)],TypeError),([(None,0)],TypeError),([(10**9+1,0)],ValueError),
            ([(0,-10**9-1)],ValueError)]

CLI_VALID=[("0",None),("1 0 0",None),("3 0 0 3 4 0 1",[1,0,2]),
           ("2 -1000000000 -1000000000 1000000000 1000000000",[8000000000000000000,0,1])]
CLI_INVALID=["","-1","2 0 0","0 0","1 1 1 1","1 1000000001 0","1 x 0",
             "9223372036854775807","1 0 9223372036854775808"]
