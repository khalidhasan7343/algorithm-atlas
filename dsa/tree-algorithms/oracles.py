"""Independent references and fixed seeds for bounded Tree tests."""
import itertools
import random
from functools import lru_cache


@lru_cache(None)
def shapes(n):
    if not n:return (None,)
    return tuple((left,right) for size in range(n) for left in shapes(size) for right in shapes(n-1-size))


def from_shape(shape):
    children=[]
    def build(node):
        if node is None:return None
        u=len(children);children.append(None)
        children[u]=[build(node[0]),build(node[1])];return u
    root=build(shape)
    return dict(values=[i%2 for i in range(len(children))],children=children,root=root)


def traversal_reference(name,case):
    order=[];levels=[];children=case['children']
    def visit(u,depth):
        if u is None:return
        left,right=children[u]
        if name=='preorder-traversal':order.append(u)
        if name=='level-order-traversal':
            if len(levels)==depth:levels.append([])
            levels[depth].append(u)
        visit(left,depth+1)
        if name=='inorder-traversal':order.append(u)
        visit(right,depth+1)
        if name=='postorder-traversal':order.append(u)
    visit(case['root'],0)
    return levels if name=='level-order-traversal' else order


def random_binary(rng,n):
    children=[[None,None] for _ in range(n)]
    slots=[(0,0),(0,1)] if n else []
    for v in range(1,n):
        pos=rng.randrange(len(slots));u,side=slots.pop(pos);children[u][side]=v;slots.extend([(v,0),(v,1)])
    permutation=list(range(n));rng.shuffle(permutation);mapped=[None]*n
    for u,pair in enumerate(children):mapped[permutation[u]]=[None if v is None else permutation[v] for v in pair]
    return dict(values=[rng.randrange(-2,3) for _ in range(n)],children=mapped,root=permutation[0] if n else None)


def traversal_vectors(name):
    result=[];rng=random.Random(8101)
    for n in range(6):
        for shape in shapes(n):
            case=from_shape(shape);result.append((case,traversal_reference(name,case)))
    for _ in range(160):
        case=random_binary(rng,rng.randrange(41));result.append((case,traversal_reference(name,case)))
    return result


def encode_binary(case):
    parts=[len(case['values']),-1 if case['root'] is None else case['root'],*case['values']]
    for pair in case['children']:parts.extend(-1 if v is None else v for v in pair)
    return ' '.join(map(str,parts))+'\n'


def ancestor_chain(parents,u):
    chain=[]
    while u is not None:chain.append(u);u=parents[u]
    return chain


def lca_reference(parents,a,b):
    other=set(ancestor_chain(parents,b))
    return next(u for u in ancestor_chain(parents,a) if u in other)


def euler_reference(parents,root):
    order=[];tin=[0]*len(parents);tout=[0]*len(parents)
    def visit(u):
        tin[u]=len(order);order.append(u)
        for v,p in enumerate(parents):
            if p==u:visit(v)
        tout[u]=len(order)
    if root is not None:visit(root)
    return dict(order=order,tin=tin,tout=tout)


def rooted_vectors(name):
    rng=random.Random(8202);trees=[dict(parents=[],root=None)]
    for n in range(1,6):
        for choices in itertools.product(*(range(v) for v in range(1,n))):trees.append(dict(parents=[None,*choices],root=0))
    for _ in range(140):
        n=rng.randrange(1,51);parents=[None]+[rng.randrange(v) for v in range(1,n)]
        labels=list(range(n));rng.shuffle(labels);mapped=[None]*n
        for v,p in enumerate(parents):mapped[labels[v]]=None if p is None else labels[p]
        trees.append(dict(parents=mapped,root=labels[0]))
    result=[]
    for tree in trees:
        n=len(tree['parents']);pairs=[(rng.randrange(n),rng.randrange(n)) for _ in range(30)] if n else []
        if n:pairs += [(tree['root'],tree['root']),(n-1,n-1)]
        if name=='lowest-common-ancestor':
            case=dict(tree,queries=[list(p) for p in pairs]);expected=[lca_reference(tree['parents'],a,b) for a,b in pairs]
        elif name=='binary-lifting':
            ops=[];expected=[]
            for a,b in pairs:
                ops.append([1,a,b]);expected.append(lca_reference(tree['parents'],a,b))
                k=rng.choice([0,1,2,n,10**18]);chain=ancestor_chain(tree['parents'],a)
                ops.append([0,a,k]);expected.append(chain[k] if k<len(chain) else None)
            case=dict(tree,operations=ops)
        else:case=tree;expected=euler_reference(tree['parents'],tree['root'])
        result.append((case,expected))
    return result


def encode_rooted(case):
    parts=[len(case['parents']),-1 if case['root'] is None else case['root'],*[-1 if p is None else p for p in case['parents']]]
    if 'queries' in case:
        parts.append(len(case['queries']))
        for query in case['queries']:parts.extend(query)
    if 'operations' in case:
        parts.append(len(case['operations']))
        for operation in case['operations']:parts.extend(operation)
    return ' '.join(map(str,parts))+'\n'


def check_subtree_intervals(actual,case):
    parents=case['parents'];n=len(parents)
    assert sorted(actual['order'])==list(range(n))
    for u in range(n):
        expected={v for v in range(n) if u in ancestor_chain(parents,v)}
        start,end=actual['tin'][u],actual['tout'][u]
        assert 0<=start<end<=n and actual['order'][start]==u
        assert set(actual['order'][start:end])==expected


def range_vectors(name):
    rng=random.Random(8303);result=[]
    for n in [0,1,2,3,7,16,31]*12:
        values=[rng.randrange(-20,21) for _ in range(n)];current=values.copy();ops=[];expected=[]
        for _ in range(35):
            if n:
                i=rng.randrange(n);value=rng.randrange(-20,21)
                ops.append([0,i,value-current[i] if name=='fenwick-tree' else value]);expected.append(None);current[i]=value
            left=rng.randrange(n+1);right=rng.randrange(left,n+1)
            ops.append([2 if name=='fenwick-tree' else 1,left,right]);expected.append(sum(current[left:right]))
            end=rng.randrange(n+1)
            ops.append([1,end] if name=='fenwick-tree' else [1,0,end]);expected.append(sum(current[:end]))
            ops.append([2 if name=='fenwick-tree' else 1,0,n]);expected.append(sum(current))
        result.append((dict(values=values,operations=ops),expected))
    return result


def encode_range(case):
    parts=[len(case['values']),*case['values'],len(case['operations'])]
    for op in case['operations']:parts.extend(op)
    return ' '.join(map(str,parts))+'\n'


def trie_vectors():
    rng=random.Random(8303);words=['','a','ab','abc','abd','b','ba','cat','car','cater']
    result=[]
    for _ in range(100):
        pool=words+[''.join(rng.choice('abcd') for _ in range(rng.randrange(1,9))) for _ in range(20)]
        reference=set();ops=[];expected=[]
        for _ in range(180):
            op=rng.randrange(4);word=rng.choice(pool);ops.append([op,word])
            if op==0:expected.append(word not in reference);reference.add(word)
            elif op==1:expected.append(word in reference)
            elif op==2:expected.append(not word or any(w.startswith(word) for w in reference))
            else:expected.append(word in reference);reference.discard(word)
        result.append((dict(operations=ops),expected))
    ops=[[0,''],[0,'abc'],[0,'ab'],[3,'ab'],[1,'abc'],[2,'ab'],[3,'abc'],[2,'ab'],[1,''],[3,''],[2,'']]
    result.append((dict(operations=ops),[True,True,True,True,True,True,True,False,True,True,True]))
    return result


def encode_trie(case):
    parts=[str(len(case['operations']))]
    for op,word in case['operations']:parts.extend([str(op),word or '-'])
    return ' '.join(parts)+'\n'


def ordered_vectors(seed=8404):
    import itertools,random
    result=[]
    def add(ops):
        state=set();expected=[]
        for op in ops:
            code=op[0]
            if code==0:
                expected.append(op[1] not in state);state.add(op[1])
            elif code==1:
                expected.append(op[1] in state);state.discard(op[1])
            elif code==2:expected.append(op[1] in state)
            elif code==3:expected.append(sorted(state))
            else:expected.append(sorted(x for x in state if op[1]<=x<op[2]))
        result.append((dict(operations=ops),expected))
    add([])
    for n in range(1,6):
        for order in itertools.permutations(range(n)):
            add([op for x in order for op in ([0,x],[3])]+[op for x in reversed(order) for op in ([1,x],[3])])
    for order in itertools.permutations(range(4)):
        add([[0,x] for x in range(4)]+[op for x in order for op in ([1,x],[3])])
    rng=random.Random(seed)
    for _ in range(40):
        ops=[]
        for _ in range(80):
            code=rng.randrange(3);key=rng.randrange(-40,41);ops.append([code,key])
            if code<2:ops.append([3])
            low,high=sorted([rng.randrange(-45,46),rng.randrange(-45,46)])
            ops.append([4,low,high])
        add(ops)
    add([[0,-10**9],[0,10**9],[0,0],[0,0],[4,-10**9,10**9],[1,0],[1,0],[3],[1,-10**9],[1,10**9],[3]])
    return result

def encode_ordered(case):
    return str(len(case['operations']))+'\n'+'\n'.join(' '.join(map(str,op)) for op in case['operations'])+'\n'

def binary_snapshot(node,kind):
    return None if node is None else [node.key,node.height if kind=='avl' else node.red,binary_snapshot(node.left,kind),binary_snapshot(node.right,kind)]

def check_binary_snapshot(snapshot,expected,kind):
    keys=[];seen=set()
    def walk(node,lo,hi):
        if node is None:return 0 if kind=='avl' else 1
        assert id(node) not in seen;seen.add(id(node))
        key,meta,left,right=node;assert lo<key<hi
        a=walk(left,lo,key);keys.append(key);b=walk(right,key,hi)
        if kind=='avl':assert meta==1+max(a,b) and abs(a-b)<=1;return meta
        assert a==b
        if meta:assert (left is None or not left[1]) and (right is None or not right[1])
        assert right is None or not right[1]
        return a+(not meta)
    assert kind=='avl' or snapshot is None or not snapshot[1]
    walk(snapshot,float('-inf'),float('inf'));assert keys==sorted(expected)


def multiway_snapshot(root,plus):
    leaves=[];seen=set()
    def collect(node):
        assert id(node) not in seen;seen.add(id(node))
        if node.leaf:leaves.append(node)
        for child in node.children:collect(child)
    collect(root);ids={id(node):i for i,node in enumerate(leaves)}
    def snap(node):
        base=[list(node.keys),[snap(child) for child in node.children]]
        if plus:base += [node.minimum,ids[id(node)] if node.leaf else None,ids[id(node.next)] if node.next is not None else None]
        return base
    return snap(root)

def check_multiway_snapshot(root,expected,degree,plus):
    records=[];leaves=[];depths=set()
    def walk(node,low,high,depth,isroot):
        keys,children=node[:2];assert keys==sorted(set(keys)) and all(low<=x<high for x in keys)
        assert len(keys)<=2*degree-1
        if not isroot:assert len(keys)>=degree-1
        if not children:
            depths.add(depth);records.extend(keys)
            if plus:
                minimum,ident,nextid=node[2:];assert minimum==(keys[0] if keys else None);leaves.append((ident,nextid))
            return keys[0] if keys else None
        assert len(children)==len(keys)+1 and (2 if isroot else degree)<=len(children)<=2*degree
        mins=[]
        for i,child in enumerate(children):
            lo=low if i==0 else keys[i-1]
            hi=high if i==len(keys) else keys[i]
            if not plus and i>0:lo+=1
            mins.append(walk(child,lo,hi,depth+1,False))
            if not plus and i<len(keys):records.append(keys[i])
        if plus:assert keys==mins[1:] and node[2]==mins[0] and node[3:] == [None,None]
        return mins[0]
    walk(root,-10**9,10**9+1,0,True)
    assert len(depths)==1 and records==sorted(expected)
    if plus:
        assert [ident for ident,_ in leaves]==list(range(len(leaves)))
        assert [nxt for _,nxt in leaves]==list(range(1,len(leaves)))+[None]
