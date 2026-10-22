from itertools import product
import random

def oracle(values,target):
    return any(sum(v for v,b in zip(values,bits) if b)==target for bits in product((0,1),repeat=len(values)))

def vectors():
    inputs=[([],0),([],1),([0,0],0),([2],4),([2,2],4),([1,3,7],6),([10**9],10000)]
    inputs += [(list(xs),target) for n in range(5) for xs in product((0,1,2),repeat=n) for target in range(6)]
    rng=random.Random(187)
    inputs += [([rng.randrange(9) for _ in range(rng.randrange(10))],rng.randrange(24)) for _ in range(120)]
    return [(args,oracle(*args)) for args in inputs]+[(( [0]*1000,0),True), (([10000],10000),True)]

def encode(args):
    values,target=args
    return ' '.join(map(str,[target,len(values),*values]))
