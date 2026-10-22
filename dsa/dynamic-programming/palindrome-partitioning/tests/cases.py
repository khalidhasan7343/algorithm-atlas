from itertools import product
import json,random

def oracle(text):
    if not text:return 0
    valid=[]
    for mask in range(1 << (len(text)-1)):
        boundaries=[0]+[i+1 for i in range(len(text)-1) if mask & (1 << i)]+[len(text)]
        parts=[text[a:b] for a,b in zip(boundaries,boundaries[1:])]
        if all(part==part[::-1] for part in parts):valid.append(len(parts)-1)
    return min(valid)

def vectors():
    inputs=['','a','aab','abba','abcdef','😀ব😀','éé','ée']
    inputs += [''.join(xs) for n in range(8) for xs in product('ab',repeat=n)]
    rng=random.Random(757)
    inputs += [''.join(rng.choices('ab😀ব',k=rng.randrange(10))) for _ in range(100)]
    return [((s,),oracle(s)) for s in inputs]+[(('a'*1000,),0),((''.join(chr(0x1000+i) for i in range(1000)),),999)]

def encode(args):return json.dumps(args[0],ensure_ascii=False)
