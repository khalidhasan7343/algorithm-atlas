from itertools import combinations,product
import random

def oracle(values):
    return max((len(indices) for n in range(len(values)+1) for indices in combinations(range(len(values)),n)
                if all(values[a]<values[b] for a,b in zip(indices,indices[1:]))),default=0)

def vectors():
    inputs=[[],[2,2,2],[-3,-2,-1],[3,2,1],[-10**9,0,10**9]]
    inputs += [list(xs) for n in range(6) for xs in product((-1,0,1),repeat=n)]
    rng=random.Random(929)
    inputs += [[rng.randrange(-5,6) for _ in range(rng.randrange(10))] for _ in range(120)]
    return [((xs,),oracle(xs)) for xs in inputs]

def encode(args):
    return ' '.join(map(str,[len(args[0]),*args[0]]))
