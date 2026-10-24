"""Independent exhaustive-pair/window/substring references; test-only."""
import itertools
import random

SEED=12101


def vectors(name):
    rng=random.Random(SEED)
    cases=[([],0),([1],2),([1,1],2),([0,0,0],0),([-10**9,10**9],0),
           ([1,1,2,2],3),([-3,-2,-1,0,1,2],-3),([1,2,3,4,5],6)]
    for n in range(6):
        for values in itertools.combinations_with_replacement(range(-2,3),n):
            cases.extend((list(values),target) for target in range(-4,5))
    for _ in range(160):
        values=sorted(rng.randrange(-20,21) for _ in range(rng.randrange(25)))
        cases.append((values,rng.randrange(-40,41)))
    return cases


def expected(name,args):
    values,target=args
    for i in range(len(values)):
        for j in range(i+1,len(values)):
            if values[i]+values[j]==target:return [i,j]
    return []


def invalid_numeric(name):
    return [([2,1],3),([10**9+1],0),([-10**9-1],0),([],2*10**9+1),([],-2*10**9-1),([0]*10001,0)]


def invalid(name):
    return invalid_numeric(name)+[(None,0),(1,0),("1",0),([True],0),([1.0],0),([],True),([],"0")]


def encode(case):
    values,scalar=case
    return str(len(values))+" "+" ".join(map(str,values))+" "+str(scalar)+"\n"


def cli(case):
    values,scalar=case
    return str(scalar)+" "+" ".join(map(str,values))


def invalid_cli(name):
    return ["","x","+","0 2 1","2000000001","0 1000000001","0 1.0","0"*21]


def driver(name):
    return 'std::size_t n;std::cin>>n;std::vector<Integer> values(n);for(auto& x:values)std::cin>>x;Integer scalar;std::cin>>scalar;', 'two_sum(values,scalar)'


def boundaries(module,name):
    assert module.solve(list(range(10000)),9999)==[0,9999]
    assert module.solve([0]*10000,0)==[0,1]
    assert module.solve([-10**9,10**9],0)==[0,1]


def cpp_boundary(name):
    return '''std::vector<Integer> values(10000);for(int i=0;i<10000;++i)values[i]=i;
    if(two_sum(values,9999)!=std::vector<Integer>({0,9999}))return 3;
    if(two_sum(std::vector<Integer>(10000,0),0)!=std::vector<Integer>({0,1}))return 4;'''


_TWO_VECTORS=vectors
_TWO_EXPECTED=expected
_TWO_INVALID=invalid_numeric
_TWO_INVALID_PY=invalid
_TWO_CLI=cli
_TWO_DRIVER=driver
_TWO_BOUNDARIES=boundaries
_TWO_CPP_BOUNDARY=cpp_boundary
_TWO_INVALID_CLI=invalid_cli


def vectors(name):
    if name=='two-sum-sorted-array':return _TWO_VECTORS(name)
    rng=random.Random(SEED+1)
    if name=='sliding-window-maximum':
        cases=[([],0),([1],1),([-2,-1,-3],2),([0,0,0],2),([1,3,-1,-3,5,3,6,7],3),
               ([-10**9,10**9],1),([-10**9,10**9],2)]
        for n in range(6):
            for v in itertools.product((-1,0,1),repeat=n):
                cases.extend((list(v),k) for k in (range(1,n+1) if n else [0]))
        for _ in range(160):
            n=rng.randrange(1,40);cases.append(([rng.randrange(-100,101) for _ in range(n)],rng.randrange(1,n+1)))
        return cases
    cases=[(b'',),(b'a',),(b'aaaa',),(b'abba',),(b'tmmzuxt',),(b'abcabcbb',),
           (bytes(range(256))*2,),(b'\0\xff\0#$\xff',),(b'AbA',),("ééবাংলা🙂abc".encode(),)]
    cases += [(bytes(v),) for n in range(7) for v in itertools.product(b'abc',repeat=n)]
    for _ in range(160):
        alphabet=rng.choice([b'ab',b'abc\0\xff#$',bytes(range(256))])
        cases.append((bytes(rng.choice(alphabet) for _ in range(rng.randrange(61))),))
    return cases


def expected(name,args):
    if name=='two-sum-sorted-array':return _TWO_EXPECTED(name,args)
    if name=='sliding-window-maximum':
        values,k=args
        return [max(values[i:i+k]) for i in range(len(values)-k+1)] if values else []
    text=args[0];best=[0,0]
    for start in range(len(text)):
        used=set()
        for end in range(start,len(text)):
            if text[end] in used:break
            used.add(text[end])
            if end+1-start>best[1]-best[0]:best=[start,end+1]
    return best


def invalid_numeric(name):
    if name=='two-sum-sorted-array':return _TWO_INVALID(name)
    if name=='sliding-window-maximum':return [([],1),([1],0),([1],2),([1],-1),([10**9+1],1),([0]*10001,1)]
    return [(b'a'*10001,)]


def invalid(name):
    if name=='two-sum-sorted-array':return _TWO_INVALID_PY(name)
    if name=='sliding-window-maximum':return invalid_numeric(name)+[(None,0),(1,0),("1",0),([True],1),([1.0],1),([1],True),([1],"1")]
    return invalid_numeric(name)+[("abc",),(None,),(True,),(bytearray(b'a'),)]


def encode(case):
    if len(case)==1:
        return str(len(case[0]))+' '+ ' '.join(map(str,case[0]))+'\n'
    values,scalar=case
    return str(len(values))+' '+' '.join(map(str,values))+' '+str(scalar)+'\n'


def cli(case):
    if len(case)==1:return case[0].hex() or '-'
    return _TWO_CLI(case)


def invalid_cli(name):
    if name=='two-sum-sorted-array':return _TWO_INVALID_CLI(name)
    if name=='sliding-window-maximum':return ['', 'x','+','0 1','1','2 1','1 1000000001','1 1.0','0'*21]
    return ['', 'zz','0','- -','00 extra','0' * 20002]


def driver(name):
    if name=='two-sum-sorted-array':return _TWO_DRIVER(name)
    if name=='sliding-window-maximum':
        read,expr=_TWO_DRIVER(name)
        return read,'sliding_max(values,scalar)'
    return 'std::size_t n;std::cin>>n;std::string text;for(std::size_t i=0;i<n;++i){int byte;std::cin>>byte;text.push_back(static_cast<char>(byte));}', 'longest_distinct(text)'


def boundaries(module,name):
    if name=='two-sum-sorted-array':return _TWO_BOUNDARIES(module,name)
    if name=='sliding-window-maximum':
        assert module.solve(list(range(10000)),9999)==[9998,9999]
        assert module.solve([-10**9]*10000,10000)==[-10**9]
        assert module.solve(list(range(10000)),1)==list(range(10000))
    else:
        assert module.solve(bytes(range(256))*39+bytes(range(16)))==[0,256]
        assert module.solve(b'a'*10000)==[0,1]
        assert module.solve(b'abba')==[0,2]


def cpp_boundary(name):
    if name=='two-sum-sorted-array':return _TWO_CPP_BOUNDARY(name)
    if name=='sliding-window-maximum':return '''std::vector<Integer> v(10000);for(int i=0;i<10000;++i)v[i]=i;
    if(sliding_max(v,9999)!=std::vector<Integer>({9998,9999}))return 3;
    if(sliding_max(std::vector<Integer>(10000,-1000000000LL),10000)!=std::vector<Integer>({-1000000000LL}))return 4;'''
    return '''std::string text;for(int i=0;i<10000;++i)text.push_back(static_cast<char>(i%256));
    if(longest_distinct(text)!=std::vector<Integer>({0,256}))return 3;
    if(longest_distinct(std::string(10000,'a'))!=std::vector<Integer>({0,1}))return 4;'''
