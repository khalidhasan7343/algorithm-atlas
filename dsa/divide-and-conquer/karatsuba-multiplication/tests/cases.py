import random

def data():
    cases=[(a,b) for a in range(-15,16) for b in range(-15,16)]
    cases.extend([(0,10**1000),(-2**63,-1),(10**200+1,-10**13+7)])
    rng=random.Random(20261022)
    for bits in (16,17,31,64,65,127,256,1024,4096):
        for _ in range(4):
            cases.append((rng.getrandbits(bits)*rng.choice((-1,1)),rng.getrandbits(max(1,bits//2))*rng.choice((-1,1))))
    cases.extend([(10**n-1,10**n-1) for n in (2,3,7,31,100,501)])
    return cases

CLI_VALID=[("0 -999","0"),("+00012 -0034","-408"),("-0 +000","0"),
           ("123456789 987654321","121932631112635269")]
