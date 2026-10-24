"""Independent frequency/representation/recursive oracles and seeded cases."""
from collections import Counter
import itertools
import random

MIN_VALUE, MAX_VALUE = -(2**31), 2**31-1
SEED = 10101


def frequencies(values, count):
    table = Counter(values)
    assert all(n in (1, 2) for n in table.values())
    singletons = sorted(value for value, n in table.items() if n == 1)
    assert len(singletons) == count
    return singletons[0] if count == 1 else singletons


def xor_vectors(count):
    rng = random.Random(SEED+count)
    cases = ([[0],[MIN_VALUE],[MAX_VALUE],[-1],[5,2,5,-7,2],
              [0,-1,-1,MIN_VALUE,MIN_VALUE]] if count == 1 else
             [[0,MIN_VALUE],[MIN_VALUE,MAX_VALUE],[-1,0],[1,2],
              [4,1,2,1,2,-7],[0,1,-1,0]])
    alphabet = [-2,-1,0,1,2]
    for singles in itertools.combinations(alphabet,count):
        remaining = [v for v in alphabet if v not in singles]
        for flags in itertools.product((0,1),repeat=len(remaining)):
            values = list(singles)+[v for v,flag in zip(remaining,flags) if flag for _ in range(2)]
            rng.shuffle(values)
            cases.append(values)
    for _ in range(300):
        pair_count = rng.randrange(51)
        distinct = rng.sample(range(MIN_VALUE,MAX_VALUE+1),pair_count+count)
        values = distinct[:count]+[v for v in distinct[count:] for _ in range(2)]
        rng.shuffle(values)
        cases.append(values)
    maximum = [MIN_VALUE]+([MAX_VALUE] if count==2 else [])+[v for v in range(4999) for _ in range(2)]
    rng.shuffle(maximum)
    cases.append(maximum)
    return cases


def invalid_xor(count):
    return ([[],[1,1],[1,1,1],[1,2,3],[0,0,0,0,1],
             [MIN_VALUE]*3,[0]*10001] if count == 1 else
            [[],[1],[1,1],[0,1,2,3],[1,1,1,2],
             [0,0,0,0,1,2],[0,0,1,1],[MIN_VALUE]*2,[0]*10002])


def encode(values):
    return str(len(values))+" "+" ".join(map(str,values))+"\n"


def bit_count(value):
    return bin(value % (2**32)).count("1")


def count_vectors():
    cases = [0,-1,MIN_VALUE,MAX_VALUE,1,2,-2,-3,
             0x55555555,-1431655766,0x33333333,-858993460]
    for bit in range(32):
        word = 2**bit
        cases.append(word if word<=MAX_VALUE else MIN_VALUE)
        complement = (2**32-1)-word
        cases.append(complement if complement<=MAX_VALUE else complement-2**32)
    cases += list(range(4096))+[-value-1 for value in range(4096)]
    rng = random.Random(SEED+3)
    cases += [rng.randrange(MIN_VALUE,MAX_VALUE+1) for _ in range(1000)]
    return cases


def recursive_subsets(values):
    """Independent positional recursion; sort terminal selections by their IDs."""
    leaves = []
    def visit(position, chosen):
        if position == len(values):
            # Ordering the recursively generated position sets implements only
            # the output contract, not the production mask enumeration.
            identity = sum(2**i for i in chosen)
            leaves.append((identity,[values[i] for i in chosen]))
            return
        visit(position+1,chosen)
        visit(position+1,chosen+[position])
    visit(0,[])
    return [row for _,row in sorted(leaves)]


def subset_vectors():
    cases = [[],[0],[-1],[MIN_VALUE,MAX_VALUE],[1,1],[2,-1,2]]
    cases += [list(v) for n in range(7) for v in itertools.product((0,1),repeat=n)]
    rng = random.Random(SEED+4)
    for _ in range(160):
        cases.append([rng.choice((MIN_VALUE,MAX_VALUE,-2,-1,0,1,2))
                      for _ in range(rng.randrange(11))])
    cases += [list(range(16)),[0]*16]
    return cases
