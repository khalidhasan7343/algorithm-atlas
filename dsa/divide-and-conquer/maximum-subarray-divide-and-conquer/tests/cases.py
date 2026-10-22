import itertools
import random

def oracle(values):
    candidates=[(sum(values[i:j]),i,j) for i in range(len(values)) for j in range(i+1,len(values)+1)]
    return min(candidates,key=lambda r:(-r[0],r[1],r[2])) if candidates else None

def data():
    cases=[list(v) for n in range(7) for v in itertools.product((-1,0,1),repeat=n)]
    high=2**63-1;low=-2**63
    cases.extend([[low],[low,low],[high,high],[high,1,-high],[low,high,high],
                  [-2,-1,-1],[-2,1,-3,4,-1,2,1,-5,4]])
    rng=random.Random(20261022)
    cases.extend([[rng.choice((low,high,-1,0,1,rng.randrange(-100,101))) for _ in range(rng.randrange(1,31))] for _ in range(80)])
    return cases

CLI_VALID=[("",None),("-3 -2 -2",["-2",1,2]),("0 0",["0",0,1]),
           ("9223372036854775807 9223372036854775807",["18446744073709551614",0,2])]
