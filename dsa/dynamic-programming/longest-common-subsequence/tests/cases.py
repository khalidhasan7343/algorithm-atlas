from itertools import combinations,product
import json,random

def vectors():
    inputs=[('', ''), ('a',''), ('','bbb'), ('aaaa','aa'), ('a😀ব','😀ব'),
            ('é','é'), ('ab','ba'), ('abc','ac'), ('a a','aa')]
    words=[''.join(chars) for n in range(4) for chars in product('ab',repeat=n)]
    inputs += list(product(words,repeat=2))
    rng=random.Random(827)
    inputs += [(''.join(rng.choices('ab😀ব',k=rng.randrange(6))),
                ''.join(rng.choices('ab😀ব',k=rng.randrange(6)))) for _ in range(120)]
    return [(args,oracle(*args)) for args in inputs]

def encode(args):
    return ' '.join(json.dumps(s,ensure_ascii=False) for s in args)

def oracle(a,b):
    left={''.join(a[i] for i in indices) for n in range(len(a)+1) for indices in combinations(range(len(a)),n)}
    right={''.join(b[i] for i in indices) for n in range(len(b)+1) for indices in combinations(range(len(b)),n)}
    return max(map(len,left & right))
