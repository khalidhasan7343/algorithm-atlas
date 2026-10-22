from itertools import product
import random

def oracle(coins, amount):
    distinct = sorted(set(coins))
    # Enumerate denomination multiplicities; order never enters the oracle.
    counts = [sum(vector) for vector in product(*(range(amount//c+1) for c in distinct))
              if sum(c*k for c,k in zip(distinct,vector)) == amount]
    return [min(counts) if counts else None, len(counts)]

def vectors():
    inputs = [([],0), ([],3), ([2],3), ([1,2,2,5],5), ([1,3,4],6), ([10**9],10000)]
    rng=random.Random(1947)
    inputs += [([rng.randrange(1,8) for _ in range(rng.randrange(5))],rng.randrange(13)) for _ in range(150)]
    return [(args, oracle(*args)) for args in inputs]

def encode(args):
    coins, amount=args
    return ' '.join(map(str,[amount,len(coins),*coins]))
