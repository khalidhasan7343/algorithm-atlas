import importlib.util,random
from pathlib import Path
_spec=importlib.util.spec_from_file_location('tree_oracles',Path(__file__).resolve().parents[2]/'oracles.py')
_o=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_o)
CLASS='BPlusTree'
PLUS=True
SEED=8505
def vectors():return [(dict(case,degree=degree),expected) for degree in (2,3,4,8) for case,expected in _o.ordered_vectors(SEED)]
def encode(case):return str(case.get('degree',2))+' '+_o.encode_ordered(case)
def check(actual,expected,case):assert actual==expected,(case,actual,expected)
def structure(tree,state):
    _o.check_multiway_snapshot(_o.multiway_snapshot(tree.root,PLUS),state,tree.degree,PLUS)
    assert tree.size==len(state) and tree.keys()==sorted(state)
def invalid():
    return [dict(operations=[op]) for op in ([0,True],[0,10**9+1],[1,-10**9-1],[2,False],[3,0],[4,2,1],[7],[0])]+[dict(operations=[[0,0]]*1001),dict(operations=None)]+[dict(degree=d) for d in (True,1,9,2.0)]
def invalid_cli():return ['', '1','9','2 -1','2 1001','2 1 0 1000000001','2 1 4 2 1','2 1 9','2 0 extra']
def boundaries(module):
    for degree in range(2,9):
        tree=getattr(module,CLASS)(degree);state=set();rng=random.Random(SEED+degree);order=list(range(600));rng.shuffle(order)
        for key in order:
            assert tree.insert(key);state.add(key);structure(tree,state)
        rng.shuffle(order)
        for key in order:
            assert tree.erase(key);state.remove(key);structure(tree,state)
        assert all(tree.stats), (degree,tree.stats)
    tree=getattr(module,CLASS)();state=set()
    for key in range(1000):
        assert tree.insert(key);state.add(key);structure(tree,state)
    saved=tree.keys()
    try:tree.insert(1000)
    except ValueError:pass
    else:raise AssertionError('capacity')
    assert tree.keys()==saved and not tree.insert(0)
    for key in range(999,-1,-1):
        assert tree.erase(key);state.remove(key);structure(tree,state)
    assert not tree.erase(0)
DRIVER="int count=static_cast<int>(token());while(count--){b_plus_cli(false);std::cout<<'\\n';}"
BOUNDARY_DRIVER='using N=BPlusTree::Node;auto inspect=[&](const BPlusTree& tree){std::vector<Integer> records;std::vector<const N*> leaves;int leaf_depth=-1;\nstd::function<void(const N*,Integer,Integer,int,bool)> walk=[&](const N* p,Integer lo,Integer hi,int depth,bool root){require(p!=nullptr,"node");require(std::is_sorted(p->keys.begin(),p->keys.end()) && std::adjacent_find(p->keys.begin(),p->keys.end())==p->keys.end(),"sorted unique");require(p->keys.size()<=static_cast<std::size_t>(2*tree.degree()-1),"max occupancy");if(!root)require(p->keys.size()>=static_cast<std::size_t>(tree.degree()-1),"min occupancy");for(auto k:p->keys)require(lo<=k && k<hi,"bounds");\nif(p->leaf){require(p->children.empty(),"leaf children");if(leaf_depth<0)leaf_depth=depth;require(leaf_depth==depth,"leaf depth");leaves.push_back(p);records.insert(records.end(),p->keys.begin(),p->keys.end());require(p->minimum==(p->keys.empty()?std::optional<Integer>{}:std::optional<Integer>{p->keys[0]}),"leaf minimum");return;}require(p->children.size()==p->keys.size()+1,"child count");require(p->children.size()>=static_cast<std::size_t>(root?2:tree.degree()) && p->children.size()<=static_cast<std::size_t>(2*tree.degree()),"child occupancy");require(p->minimum==p->children[0]->minimum,"minimum cache");require(p->next==nullptr,"internal link");for(std::size_t i=0;i<p->keys.size();++i)require(p->children[i+1]->minimum==p->keys[i],"separator");for(std::size_t i=0;i<p->children.size();++i){walk(p->children[i].get(),i==0?lo:p->keys[i-1],i==p->keys.size()?hi:p->keys[i],depth+1,false);}};walk(tree.root(),-1000000000,1000000001,0,true);require(records==tree.keys() && records.size()==tree.size(),"all records");for(std::size_t i=0;i<leaves.size();++i)require(leaves[i]->next==(i+1<leaves.size()?leaves[i+1]:nullptr),"leaf chain");};for(int degree=2;degree<=8;++degree){BPlusTree tree(degree);unsigned state=8505+degree;auto shuffle=[&](std::vector<Integer>& values){for(std::size_t i=values.size();i>1;--i){state=1664525u*state+1013904223u;std::swap(values[i-1],values[state%i]);}};\nstd::vector<Integer> order(600);std::iota(order.begin(),order.end(),0);shuffle(order);for(auto k:order){require(tree.insert(k),"insert");inspect(tree);}shuffle(order);for(auto k:order){require(tree.erase(k),"erase");inspect(tree);}for(auto count:tree.stats)require(count>0,"repair coverage");}\nBPlusTree capacity;for(int k=0;k<1000;++k){capacity.insert(k);inspect(capacity);}auto saved=capacity.keys();try{capacity.insert(1000);throw std::logic_error("capacity");}catch(const std::invalid_argument&){}require(capacity.keys()==saved && !capacity.insert(0),"atomic capacity");for(int k=999;k>=0;--k){require(capacity.erase(k),"reverse drain");inspect(capacity);}emit(true);'
INVARIANT_DRIVER='using N=BPlusTree::Node;int count=static_cast<int>(token());while(count--){BPlusTree tree(token());int q=query_count();std::cout<<\'[\';for(int step=0;step<q;++step){if(step)std::cout<<\',\';Integer op=token();if(op==0)tree.insert(token());else if(op==1)tree.erase(token());else if(op==2)tree.contains(token());else if(op==4){auto lo=token(),hi=token();tree.range_query(lo,hi);}else require(op==3,"op");std::vector<const N*> leaves;std::function<void(const N*)> collect=[&](const N* p){if(p->leaf)leaves.push_back(p);for(const auto& child:p->children)collect(child.get());};collect(tree.root());auto identity=[&](const N* p){if(!p){std::cout<<"null";return;}auto found=std::find(leaves.begin(),leaves.end(),p);require(found!=leaves.end(),"dangling leaf link");emit(static_cast<Integer>(found-leaves.begin()));};std::function<void(const N*)> snapshot=[&](const N* p){std::cout<<\'[\';emit(p->keys);std::cout<<",[";for(std::size_t i=0;i<p->children.size();++i){if(i)std::cout<<\',\';snapshot(p->children[i].get());}std::cout<<\']\';std::cout<<\',\';emit(p->minimum);std::cout<<\',\';if(p->leaf)identity(p);else std::cout<<"null";std::cout<<\',\';identity(p->next);std::cout<<\']\';};snapshot(tree.root());}std::cout<<"]\\n";}'
