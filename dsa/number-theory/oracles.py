"""Independent bounded mathematical references; no solution imports."""
import math
import random

FUNCTIONS = {"sieve-of-eratosthenes":("sieve",1),"euclidean-algorithm":("gcd",2),
             "least-common-multiple":("lcm",2)}
SEED = 11101


def prime(value):
    return value >= 2 and all(value % divisor for divisor in range(2,math.isqrt(value)+1))


def vectors(name):
    rng = random.Random(SEED)
    if name == "sieve-of-eratosthenes":
        return [(n,) for n in range(101)]+[(rng.randrange(2001),) for _ in range(100)]
    cases = [(0,0),(0,1),(1,0),(-1,0),(0,-1),(1,1),(-12,18),(12,-18),(-12,-18),
             (10**9,10**9-1),(-10**9,10**9),(-10**9,0),(832040,514229)]
    cases += [(a,b) for a in range(-12,13) for b in range(-12,13)]
    cases += [(rng.randrange(-10**9,10**9+1),rng.randrange(-10**9,10**9+1)) for _ in range(160)]
    return cases


def expected(name,args):
    if name == "sieve-of-eratosthenes":
        return [n for n in range(2,args[0]+1) if prime(n)]
    a,b = args
    if name == "euclidean-algorithm": return math.gcd(a,b)
    return abs(a*b)//math.gcd(a,b) if a and b else 0


def check(name,args,result):
    assert result == expected(name,args), (name,args,result)
    if name == "euclidean-algorithm" and result:
        assert args[0]%result == args[1]%result == 0


def invalid_numeric(name):
    if name == "sieve-of-eratosthenes": return [(-1,),(1000001,),(-(2**63),)]
    return [(10**9+1,0),(0,-10**9-1),(-(2**63),1),(1,2**63-1)]


def boundaries(module,name):
    if name == "sieve-of-eratosthenes":
        primes = module.solve(1000000)
        assert len(primes)==78498 and primes[:4]==[2,3,5,7] and primes[-1]==999983
    else:
        check(name,(10**9,10**9-1),module.solve(10**9,10**9-1))


_FOUNDATION_VECTORS = vectors
_FOUNDATION_EXPECTED = expected
_FOUNDATION_CHECK = check
_FOUNDATION_INVALID = invalid_numeric
_FOUNDATION_BOUNDARIES = boundaries
FUNCTIONS.update({'modular-exponentiation':('mod_power',3),'fast-exponentiation':('power',2),
                  'extended-euclidean-algorithm':('extended_gcd',2),'prime-factorization':('factorize',1)})


def vectors(name):
    rng=random.Random(SEED+1)
    if name in ('sieve-of-eratosthenes','euclidean-algorithm','least-common-multiple'):
        return _FOUNDATION_VECTORS(name)
    if name=='extended-euclidean-algorithm':return _FOUNDATION_VECTORS('euclidean-algorithm')
    if name=='modular-exponentiation':
        cases=[(0,0,1),(0,0,7),(0,1,7),(-2,5,13),(2,0,4),(-10**9,10**9,1000000007),
               (10**9,10**9,1),(-1,999999999,1000000007),(2,62,1000000007)]
        cases += [(a,e,m) for a in range(-3,4) for e in range(7) for m in range(1,8)]
        cases += [(rng.randrange(-10**9,10**9+1),rng.randrange(10**9+1),rng.randrange(1,1000000008)) for _ in range(200)]
        return cases
    if name=='fast-exponentiation':
        cases=[(0,0),(0,10**9),(1,10**9),(-1,999999999),(-2,63),(2,62),(-2,62),(10**9,2),(-10**9,2)]
        cases += [(a,e) for a in range(-8,9) for e in range(18) if -(2**63)<=pow(a,e)<2**63]
        for _ in range(180):
            a,e=rng.randrange(-100,101),rng.randrange(18)
            if -(2**63)<=pow(a,e)<2**63:cases.append((a,e))
        return cases
    cases=[(1,),(2,),(3,),(4,),(64,),(360,),(999983,),(999983**2,),(10**12,),
           (9999999967,),(2**39,)]
    cases += [(n,) for n in range(1,301)]
    cases += [(rng.randrange(1,10**7),) for _ in range(120)]
    return cases


def expected(name,args):
    if name in ('sieve-of-eratosthenes','euclidean-algorithm','least-common-multiple'):
        return _FOUNDATION_EXPECTED(name,args)
    if name=='modular-exponentiation':return pow(*args)
    if name=='fast-exponentiation':return pow(*args)
    if name=='extended-euclidean-algorithm':return math.gcd(*args)
    value=args[0];result=[]
    # All candidate divisors, including even composites, differ from the
    # production odd-only scan; primality/product checks add independent evidence.
    divisor=2
    while divisor*divisor<=value:
        if value%divisor==0:
            count=0
            while value%divisor==0:value//=divisor;count+=1
            result.append([divisor,count])
        divisor+=1
    if value>1:result.append([value,1])
    return result


def check(name,args,result):
    if name=='extended-euclidean-algorithm':
        assert len(result)==3
        g,x,y=result
        assert g==math.gcd(*args) and args[0]*x+args[1]*y==g
        if args==(0,0):assert result==[0,0,0]
        if g:assert args[0]%g==args[1]%g==0
    else:
        assert result==expected(name,args),(name,args,result)
        if name=='prime-factorization':
            product=1;previous=1
            for p,e in result:
                assert p>previous and prime(p) and e>=1
                product*=p**e;previous=p
            assert product==args[0]
        if name=='euclidean-algorithm' and result:
            assert args[0]%result==args[1]%result==0


def invalid_numeric(name):
    if name in ('sieve-of-eratosthenes','euclidean-algorithm','least-common-multiple'):
        return _FOUNDATION_INVALID(name)
    if name=='extended-euclidean-algorithm':return _FOUNDATION_INVALID('euclidean-algorithm')
    if name=='prime-factorization':return [(0,),(-1,),(10**12+1,),(-(2**63),)]
    if name=='modular-exponentiation':return [(1,1,0),(1,1,-1),(1,-1,7),(1,10**9+1,7),(1,1,1000000008),(10**9+1,1,7)]
    return [(2,63),(-2,64),(10**9,3),(2,-1),(2,10**9+1),(10**9+1,1)]


def boundaries(module,name):
    if name in ('sieve-of-eratosthenes','euclidean-algorithm','least-common-multiple'):
        return _FOUNDATION_BOUNDARIES(module,name)
    if name=='fast-exponentiation':
        assert module.solve(-2,63)==-(2**63)
        assert module.solve(2,62)==2**62
        assert module.solve(-1,10**9)==1
    elif name=='modular-exponentiation':
        for args in [(-10**9,10**9,1000000007),(0,0,1),(10**9,10**9,1000000007)]:check(name,args,module.solve(*args))
    elif name=='extended-euclidean-algorithm':
        for args in [(-10**9,10**9-1),(10**9,0),(0,0)]:check(name,args,module.solve(*args))
    else:check(name,(10**12,),module.solve(10**12))
