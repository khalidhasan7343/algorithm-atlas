from itertools import product
import random

def oracle(weights, values, capacity):
    return max((sum(v for v, b in zip(values, bits) if b)
                for bits in product((0, 1), repeat=len(weights))
                if sum(w for w, b in zip(weights, bits) if b) <= capacity), default=0)

def vectors():
    inputs = [([], [], 0), ([0, 0, 1], [5, 7, 100], 0), ([1], [5], 2),
              ([2, 2], [3, 4], 4), ([0, 1], [-5, -2], 1),
              ([0]*1000, [10**9]*1000, 0), ([1], [10**9], 10000)]
    rng = random.Random(7343)
    for _ in range(180):
        n = rng.randrange(9)
        inputs.append(([rng.randrange(6) for _ in range(n)],
                       [rng.randrange(-5, 12) for _ in range(n)], rng.randrange(12)))
    return [(args, (10**12 if len(args[0]) == 1000 else oracle(*args))) for args in inputs]

def encode(args):
    weights, values, capacity = args
    return ' '.join(map(str, [capacity, len(weights), *[x for pair in zip(weights, values) for x in pair]]))
