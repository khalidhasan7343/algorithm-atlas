from itertools import combinations,product
import random

def oracle(activities):
    # Enumerate every subset; rank all compatible optimum schedules by their
    # finish/start/index sequence, independently of an earliest-finish scan.
    best=[]
    def key(indices):return (-len(indices),tuple((activities[i][1],activities[i][0],i) for i in indices))
    for bits in product((0,1),repeat=len(activities)):
        selected=sorted((i for i,b in enumerate(bits) if b),key=lambda i:(activities[i][1],activities[i][0],i))
        if all(activities[a][1]<=activities[b][0] for a,b in zip(selected,selected[1:])):
            if key(selected)<key(best):best=selected
    return best

def vectors():
    inputs=[[],[(0,1)],[(0,2),(2,3),(1,4)],[(0,2),(0,2),(2,3)],
            [(-4,-2),(-2,-1),(-3,0)],[(1,3),(0,3),(3,4)], [(-10**9,10**9)]]
    pool=[(0,1),(0,2),(1,2),(2,3)]
    inputs += [list(xs) for n in range(4) for xs in product(pool,repeat=n)]
    rng=random.Random(6001)
    for _ in range(180):
        intervals=[]
        for _ in range(rng.randrange(9)):
            start=rng.randrange(-5,8);intervals.append((start,start+rng.randrange(1,6)))
        inputs.append(intervals)
    return [((xs,),oracle(xs)) for xs in inputs]+[(([ (2*i,2*i+1) for i in range(10000)],),list(range(10000)))]

def encode(args):return ' '.join(map(str,[len(args[0]),*[t for interval in args[0] for t in interval]]))
