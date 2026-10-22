import itertools
import random

def oracle(values,target):
    # Rank independently enumerated subsets by their include-first preorder.
    matches=[]
    for size in range(len(values)+1):
        for indices in itertools.combinations(range(len(values)),size):
            if sum(values[i] for i in indices)==target:
                key=tuple(0 if i in indices else 1 for i in range(indices[-1]+1)) if indices else ()
                matches.append((key,list(indices)))
    return min(matches)[1] if matches else None

def valid_cases():
    cases=[]
    for n in range(6):
        for values in itertools.product((-1,0,1),repeat=n):
            for target in range(-3,4):
                cases.append(((list(values),target),oracle(values,target)))
    high=2**63-1; low=-2**63
    extremes=[([high,1,-high],1),([low,-1,high,2],0),
              ([high,high,high,-high,-high,-high,1],1),
              ([low,low,low,high,high,high,4],1),
              ([low,high],-1),([high,high],-2),([],1),([1,0],1),([0,0],0)]
    rng=random.Random(20261023)
    for _ in range(80):
        n=rng.randrange(1,11)
        values=[rng.choice([low,high,-1,0,1,rng.randrange(low,high)]) for _ in range(n)]
        target=rng.choice([low,high,-1,0,1,rng.randrange(-10,11)])
        extremes.append((values,target))
    for values,target in extremes:
        cases.append(((values,target),oracle(values,target)))
    return cases

def invalid_cases():
    return [(([True],1),TypeError),(([1.0],1),TypeError),(([None],1),TypeError),
            (([1],True),TypeError),(([],None),TypeError),(([],1.0),TypeError)]

def call(module,value):
    return module.subset_sum_backtracking(*value)

def serialize(value):
    values,target=value
    return " ".join(map(str,[len(values),target,*values]))

CLI_VALID=[("0",[]),("1",None),("3 1 2 3",[0,1]),
           ("1 9223372036854775807 1 -9223372036854775807",[0,1,2]),
           ("-1 -9223372036854775808 9223372036854775807",[0,1])]
CLI_INVALID=["", "x", "+", "1 1.0", "1 ١", "1_0", "1 2x"]
CPP_BODY=r"""
    std::size_t n; long long target;
    while (std::cin >> n >> target) {
        std::vector<long long> values(n);
        for (auto& value : values) { std::cin >> value; }
        const auto before=values;
        reply([&] { return algorithm_atlas::subset_sum_backtracking(values,target); });
        assert(values==before);
    }
"""
