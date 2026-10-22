import random

def oracle(prices, length):
    # Exhaustively enumerate ordered compositions, with no memoization.
    def all_revenues(remaining):
        if remaining==0:
            yield 0
        for cut, price in enumerate(prices,1):
            if cut<=remaining and price is not None:
                for rest in all_revenues(remaining-cut):
                    yield price+rest
    return max(all_revenues(length), default=None)

def vectors():
    inputs=[([],0),([],2),([None,5],3),([None,5],4),([-2],3),([2,5,7,8],4),
            ([1,1,1,10],4),([10**9],10000)]
    rng=random.Random(455)
    inputs += [([rng.choice([None,-3,-1,0,2,5,9]) for _ in range(rng.randrange(6))],rng.randrange(9)) for _ in range(150)]
    return [(args,10**13 if args[1]==10000 else oracle(*args)) for args in inputs]

def encode(args):
    prices,length=args
    return ' '.join(map(str,[length,len(prices),*['x' if p is None else p for p in prices]]))
