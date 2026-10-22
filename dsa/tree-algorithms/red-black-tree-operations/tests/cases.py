import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('tree_oracles',Path(__file__).resolve().parents[2]/'oracles.py')
_o=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_o)
CLASS='RedBlackTree'
KIND='rb'
SEED=8404
def vectors():return _o.ordered_vectors(SEED)
def encode(case):return _o.encode_ordered(case)
def check(actual,expected,case):assert actual==expected,(case,actual,expected)
def structure(tree,state):
    _o.check_binary_snapshot(_o.binary_snapshot(tree.root,KIND),state,KIND)
    assert tree.size==len(state) and tree.keys()==sorted(state)
def invalid():
    return [dict(operations=[op]) for op in ([0,True],[0,10**9+1],[1,-10**9-1],[2,False],[3,0],[4,2,1],[4,0,True],[7],[0])]+[dict(operations=[[0,0]]*1001),dict(operations=None)]
def invalid_cli():return ['', '-1','1001','1 0 1000000001','1 4 2 1','1 9','0 extra','1.0']
def boundaries(module):
    tree=getattr(module,CLASS)();state=set()
    for i in range(1000):
        assert tree.insert(i);state.add(i);structure(tree,state)
    saved=tree.keys()
    try:tree.insert(1000)
    except ValueError:pass
    else:raise AssertionError('capacity')
    assert tree.keys()==saved and not tree.insert(0)
    for i in list(range(0,1000,2))+list(range(999,0,-2)):
        assert tree.erase(i);state.remove(i);structure(tree,state)
    assert tree.size==0 and not tree.erase(0)
    if KIND=='rb':assert all(tree.stats)
    else:
        for index,order in enumerate(([3,2,1],[1,2,3],[3,1,2],[1,3,2])):
            rotated=module.AVLTree()
            for key in order:rotated.insert(key)
            structure(rotated,order);assert rotated.root.key==2 and rotated.rotations[index]>0
DRIVER="int count=static_cast<int>(token());while(count--){red_black_cli(false);std::cout<<'\\n';}"
BOUNDARY_DRIVER='using N=RedBlackTree::Node;std::function<int(const N*,Integer,Integer)> verify=[&](const N* p,Integer lo,Integer hi)->int{if(!p)return 1;require(lo<p->key && p->key<hi,"BST");int l=verify(p->left.get(),lo,p->key),r=verify(p->right.get(),p->key,hi);require(l==r,"black height");require(!p->right || !p->right->red,"left leaning");require(!p->red || ((!p->left || !p->left->red) && (!p->right || !p->right->red)),"red adjacency");return l+!p->red;};RedBlackTree tree;auto check=[&](){verify(tree.root(),-1000000001LL,1000000001LL);require(!tree.root() || !tree.root()->red,"root color");require(tree.keys().size()==tree.size(),"size");};\nfor(int i=0;i<1000;++i){require(tree.insert(i),"insert");check();}auto saved=tree.keys();try{tree.insert(1000);throw std::logic_error("capacity");}catch(const std::invalid_argument&){}require(tree.keys()==saved,"atomic capacity");require(!tree.insert(0),"duplicate at capacity");for(int i=0;i<1000;i+=2){require(tree.erase(i),"erase even");check();}for(int i=999;i>=1;i-=2){require(tree.erase(i),"erase odd");check();}require(tree.size()==0 && !tree.erase(0),"empty");for(auto count:tree.stats)require(count>0,"repair branch coverage");emit(true);'
INVARIANT_DRIVER='using N=RedBlackTree::Node;std::function<void(const N*)> snapshot=[&](const N* p){if(!p){std::cout<<"null";return;}std::cout<<\'[\';emit(p->key);std::cout<<\',\';emit(p->red);std::cout<<\',\';snapshot(p->left.get());std::cout<<\',\';snapshot(p->right.get());std::cout<<\']\';};\nint count=static_cast<int>(token());while(count--){RedBlackTree tree;int q=query_count();std::cout<<\'[\';for(int i=0;i<q;++i){if(i)std::cout<<\',\';Integer op=token();if(op==0)tree.insert(token());else if(op==1)tree.erase(token());else if(op==2)tree.contains(token());else if(op==4){auto lo=token(),hi=token();tree.range_query(lo,hi);}else require(op==3,"op");snapshot(tree.root());}std::cout<<"]\\n";}'
