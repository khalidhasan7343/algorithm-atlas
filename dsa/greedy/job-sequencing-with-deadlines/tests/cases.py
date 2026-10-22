from itertools import product
import random

def oracle(deadlines,profits):
    # Enumerate all subsets. Earliest-deadline feasibility is necessary and
    # sufficient for unit jobs, independent of profit order or slot DSU.
    best=0
    for bits in product((0,1),repeat=len(deadlines)):
        chosen=[i for i,b in enumerate(bits) if b]
        if all(t<=d for t,d in enumerate(sorted(deadlines[i] for i in chosen),1)):
            best=max(best,sum(profits[i] for i in chosen))
    return best

def vectors():
    inputs=[([],[]),([0],[99]),([1,1],[5,5]),([2,1,2,1,3],[100,19,27,25,15]),
            ([10**9,10**9],[4,3]),([2,2],[-1,0]),([1,2,2],[8,7,6])]
    pool=[(0,5),(1,-1),(1,3),(2,3)]
    inputs += [([d for d,p in xs],[p for d,p in xs]) for n in range(4) for xs in product(pool,repeat=n)]
    rng=random.Random(6004)
    for _ in range(180):
        n=rng.randrange(9)
        inputs.append(([rng.choice([0,1,2,3,10**9]) for _ in range(n)], [rng.randrange(-5,30) for _ in range(n)]))
    return [(args,oracle(*args)) for args in inputs]+[(([10**9]*10000,[10**9]*10000),10**13)]

def encode(args):
    deadlines,profits=args
    return ' '.join(map(str,[len(deadlines),*[x for pair in zip(deadlines,profits) for x in pair]]))

def validate(result,args,expected):
    deadlines,profits=args
    assert result['profit']==expected
    assert len(result['slots'])==min(len(deadlines),max(deadlines,default=0))
    selected=[i for i in result['slots'] if i is not None]
    assert len(set(selected))==len(selected)
    assert all(0<=i<len(deadlines) and slot<=deadlines[i] and profits[i]>0 for slot,i in enumerate(result['slots'],1) if i is not None)
    assert sum(profits[i] for i in selected)==expected
