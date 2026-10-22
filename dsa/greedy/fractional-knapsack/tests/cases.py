from fractions import Fraction
from itertools import product
import random

def normal(result):
    value,fractions=result
    pair=lambda f:[f.numerator,f.denominator]
    return {'value':pair(value),'fractions':[pair(f) for f in fractions]}

def oracle(weights,values,capacity):
    # Enumerate all vertices: zero/one for every item except at most one
    # fraction. Optimize value, then the specified density/index allocation.
    order=sorted(range(len(weights)),key=lambda i:(Fraction(values[i],weights[i]),-i),reverse=True)
    best=(Fraction(0),[Fraction(0)]*len(weights))
    def key(result):return (result[0],tuple(result[1][i] for i in order))
    for bits in product((0,1),repeat=len(weights)):
        if any(b and values[i]==0 for i,b in enumerate(bits)):continue
        used=sum(w*b for w,b in zip(weights,bits))
        if used>capacity:continue
        base=[Fraction(b) for b in bits];value=sum(v*b for v,b in zip(values,bits))
        candidate=(Fraction(value),base)
        if key(candidate)>key(best):best=candidate
        for j,b in enumerate(bits):
            if b or not values[j]:continue
            fractions=base.copy();fractions[j]=Fraction(min(capacity-used,weights[j]),weights[j])
            candidate=(value+values[j]*fractions[j],fractions)
            if key(candidate)>key(best):best=candidate
    return normal(best)

def vectors():
    inputs=[([],[],0),([10,20,30],[60,100,120],50),([2,3],[4,6],3),([1,2],[0,5],4),
            ([3],[2],1),([999999,1000000],[1000000,999999],1000000),([1],[1],0)]
    rng=random.Random(6002)
    for _ in range(140):
        n=rng.randrange(7)
        inputs.append(([rng.randrange(1,10) for _ in range(n)], [rng.randrange(13) for _ in range(n)],rng.randrange(25)))
    return [(args,oracle(*args)) for args in inputs]+[(([1]*10000,[10**6]*10000,10**9),{'value':[10**10,1],'fractions':[[1,1]]*10000})]

def encode(args):
    weights,values,capacity=args
    return ' '.join(map(str,[capacity,len(weights),*[x for pair in zip(weights,values) for x in pair]]))
