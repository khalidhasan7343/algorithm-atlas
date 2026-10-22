from functools import lru_cache
import random

@lru_cache(None)
def merge_oracle(weights):
    # Exhaustively try every pair at every merge; no minimum-pair rule.
    if len(weights)<2:return 0
    return min(weights[i]+weights[j]+merge_oracle(tuple(sorted(
        [w for k,w in enumerate(weights) if k not in (i,j)]+[weights[i]+weights[j]])))
        for i in range(len(weights)) for j in range(i+1,len(weights)))

def oracle(frequencies):
    if len(frequencies)==1:return next(iter(frequencies.values()))
    return merge_oracle(tuple(sorted(frequencies.values())))

def vectors():
    inputs=[({},b''),({65:5},b'AAA'),({65:5,66:2,67:1},b'ABCA'),
            ({65:1,66:1,67:1,68:1},b'DCBA'),({0:2,255:3},bytes([0,255,0]))]
    rng=random.Random(6003)
    for _ in range(140):
        symbols=rng.sample(range(256),rng.randrange(7))
        frequencies={s:rng.randrange(1,31) for s in symbols}
        message=bytes(rng.choices(symbols,k=rng.randrange(50))) if symbols else b''
        inputs.append((frequencies,message))
    result=[(args,oracle(args[0])) for args in inputs]
    result += [(({i:10**9 for i in range(256)},bytes(range(256))*39),256*10**9*8)]
    result += [(({i:1<<i for i in range(30)},bytes([0])*10000),2**31-33)]
    return result

def encode(args):
    frequencies,message=args
    return ' '.join(map(str,[len(frequencies),*[x for pair in frequencies.items() for x in pair],len(message),*message]))

def validate(result,args,expected):
    frequencies,message=args
    codes=dict(result['codes'])
    assert set(codes)==set(frequencies)
    assert all(code and set(code)<=set('01') for code in codes.values())
    assert all(not a.startswith(b) for x,a in codes.items() for y,b in codes.items() if x!=y)
    assert result['cost']==expected==sum(f*len(codes[s]) for s,f in frequencies.items())
    assert result['bits']==''.join(codes[s] for s in message)
    assert result['decoded']==list(message)
