"""Independent semantic relationships for the two separately reviewed categories."""
import argparse
import importlib.util
import json
from pathlib import Path
import random

ROOT=Path(__file__).resolve().parents[1]


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify(category):
    number=category=='number-theory'
    folder=ROOT/'dsa'/('number-theory' if number else 'two-pointers-and-sliding-window')
    names=(('sieve-of-eratosthenes','euclidean-algorithm','least-common-multiple','modular-exponentiation','fast-exponentiation','extended-euclidean-algorithm','prime-factorization')
           if number else ('two-sum-sorted-array','sliding-window-maximum','longest-substring-without-repeating-characters'))
    modules={name:load(folder/name/'python/solution.py','cross_'+name) for name in names}
    oracle=load(folder/'oracles.py','cross_reference_'+category)
    rng=random.Random(11109 if number else 12109)
    checks={}
    if number:
        primes=modules['sieve-of-eratosthenes'].solve(500)
        assert primes==[n for n in range(2,501) if oracle.prime(n)]
        for n in range(1,201):
            result=modules['prime-factorization'].solve(n)
            oracle.check('prime-factorization',(n,),result)
            assert all(p in primes for p,e in result)
        checks['sieve/factorization vs primality and reconstruction']=200
        for _ in range(120):
            a,b=rng.randrange(-10**9,10**9+1),rng.randrange(-10**9,10**9+1)
            g=modules['euclidean-algorithm'].solve(a,b)
            lcm=modules['least-common-multiple'].solve(a,b)
            extended=modules['extended-euclidean-algorithm'].solve(a,b)
            oracle.check('extended-euclidean-algorithm',(a,b),extended)
            assert extended[0]==g and g*lcm==abs(a*b)
            base,exponent,modulus=rng.randrange(-6,7),rng.randrange(17),rng.randrange(1,1001)
            exact=modules['fast-exponentiation'].solve(base,exponent)
            residue=modules['modular-exponentiation'].solve(base,exponent,modulus)
            assert residue==exact%modulus==pow(base,exponent,modulus)
        checks.update({'gcd/extended/LCM identities':120,'exact/modular powers vs builtin':120})
    else:
        for _ in range(120):
            values=[rng.randrange(-10,11) for _ in range(rng.randrange(30))]
            ordered=sorted(values);target=rng.randrange(-20,21)
            pair=modules['two-sum-sorted-array'].solve(ordered,target)
            assert pair==oracle.expected('two-sum-sorted-array',(ordered,target))
            k=rng.randrange(1,len(values)+1) if values else 0
            assert modules['sliding-window-maximum'].solve(values,k)==oracle.expected('sliding-window-maximum',(values,k))
            text=bytes(rng.choice(b'abcd\0\xff') for _ in range(rng.randrange(50)))
            result=modules['longest-substring-without-repeating-characters'].solve(text)
            assert result==oracle.expected('longest-substring-without-repeating-characters',(text,))
            assert len(set(text[result[0]:result[1]]))==result[1]-result[0]
        checks={'pair vs exhaustive index order':120,'maximum vs all complete windows':120,
                'distinct interval vs independent expansion':120}
    return dict(phase_number=11 if number else 12,category=category,seed=11109 if number else 12109,
                relationships=checks,status='passed',owner_approval='pending')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--category',choices=('number-theory','two-pointers-sliding-window'),required=True)
    parser.add_argument('--check-only',action='store_true');args=parser.parse_args()
    result=verify(args.category)
    if not args.check_only:(ROOT/f'docs/{args.category}-evidence/oracle-matrix.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
