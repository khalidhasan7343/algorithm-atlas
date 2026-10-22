from itertools import product
import random

def oracle(values):
    candidates=[(sum(values[a:b]),a,b) for a in range(len(values)) for b in range(a+1,len(values)+1)]
    return min(candidates,key=lambda x:(-x[0],x[1],x[2])) if candidates else None

def vectors():
    inputs=[[],[-3,-1,-2],[0,0,0],[1,-1,1],[0,1],[-2,1,-3,4,-1,2,1,-5,4]]
    inputs += [list(xs) for n in range(8) for xs in product((-1,0,1),repeat=n)]
    rng=random.Random(713)
    inputs += [[rng.randrange(-10**9,10**9+1) for _ in range(rng.randrange(35))] for _ in range(120)]
    return [((v,),oracle(v)) for v in inputs]+[(([10**9]*10000,),(10**13,0,10000))]

def encode(args):return ' '.join(map(str,[len(args[0]),*args[0]]))
