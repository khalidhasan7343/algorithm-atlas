import random

def oracle(d):
    if len(d)<3:return 0
    # Enumerate all full binary parenthesizations, retaining every cost.
    def costs(left,right):
        if left==right:return [0]
        return [a+b+d[left]*d[k+1]*d[right+1] for k in range(left,right)
                for a in costs(left,k) for b in costs(k+1,right)]
    return min(costs(0,len(d)-2))

def vectors():
    inputs=[[],[10,20],[10,30,5,60],[30,35,15,5,10,20,25],[1,1,1,1]]
    rng=random.Random(230)
    inputs += [[rng.randrange(1,21) for _ in range(rng.randrange(2,9))] for _ in range(150)]
    return [((d,),oracle(d)) for d in inputs]+[(([100000]*101,),99*10**15)]

def encode(args):return ' '.join(map(str,[len(args[0]),*args[0]]))
