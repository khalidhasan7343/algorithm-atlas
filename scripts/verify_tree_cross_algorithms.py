"""Seeded Tree cross checks paired with independent references, saved as actual evidence."""
import argparse
import importlib.util
import json
from pathlib import Path
import random

ROOT=Path(__file__).resolve().parents[1]
TREE=ROOT/'dsa/tree-algorithms'
EVIDENCE=ROOT/'docs/tree-algorithms-evidence'


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def verify(through=5,write_evidence=True):
    support=load(TREE/'support.py','tree_support');oracle=load(TREE/'oracles.py','tree_oracles')
    canonical=support.canonical;rng=random.Random(80909);results={}
    def record(name,cases=60):results[name]=dict(seed=80909,cases=cases,failures=0,independent_oracle=True)
    for _ in range(60):
        case=oracle.random_binary(rng,rng.randrange(1,40))
        for name in ('inorder-traversal','preorder-traversal','postorder-traversal','level-order-traversal'):
            assert canonical(name).solve(**case)==oracle.traversal_reference(name,case)
        n=rng.randrange(1,50);parents=[None]+[rng.randrange(v) for v in range(1,n)]
        simple=canonical('lowest-common-ancestor').LCA(parents,0)
        jumps=canonical('binary-lifting').BinaryLifting(parents,0)
        for _ in range(20):
            a,b=rng.randrange(n),rng.randrange(n)
            assert simple.query(a,b)==jumps.lca(a,b)==oracle.lca_reference(parents,a,b)
        tour=canonical('euler-tour').solve(parents,0)
        oracle.check_subtree_intervals(tour,dict(parents=parents,root=0))
    record('iterative traversals vs independent recursive references')
    record('LCA vs Binary Lifting and parent-walking oracle')
    record('Euler intervals vs explicit subtree enumeration')
    if through>=3:
        for _ in range(60):
            n=rng.randrange(1,60);values=[rng.randrange(-100,101) for _ in range(n)]
            bit=canonical('fenwick-tree').FenwickTree(values);segment=canonical('segment-tree').SegmentTree(values)
            for _ in range(50):
                i=rng.randrange(n);value=rng.randrange(-100,101)
                bit.add(i,value-values[i]);segment.set(i,value);values[i]=value
                left=rng.randrange(n+1);right=rng.randrange(left,n+1)
                assert bit.range_sum(left,right)==segment.range_sum(left,right)==sum(values[left:right])
                assert bit.prefix_sum(right)==segment.range_sum(0,right)==sum(values[:right])
        record('Fenwick vs Segment Tree and naive array sums')
    if through>=4:
        constructors=[canonical('avl-tree-rotations').AVLTree,canonical('red-black-tree-operations').RedBlackTree]
        if through>=5:constructors += [canonical('b-tree-operations').BTree,canonical('b-plus-tree-operations').BPlusTree]
        for _ in range(60):
            trees=[make() for make in constructors];state=set()
            for _ in range(100):
                key=rng.randrange(-60,61);insert=rng.choice([True,False])
                expected=key not in state if insert else key in state
                for tree in trees:assert (tree.insert(key) if insert else tree.erase(key))==expected
                if insert:state.add(key)
                else:state.discard(key)
                low,high=sorted([rng.randrange(-70,71),rng.randrange(-70,71)])
                for tree in trees:
                    assert tree.keys()==sorted(state)
                    assert tree.contains(key)==(key in state)
                    assert tree.range_query(low,high)==sorted(x for x in state if low<=x<high)
        record(('AVL/Red-Black/B-Tree/B+ Tree vs independent ordered reference and range scans' if through>=5 else 'AVL/Red-Black vs independent ordered reference'),60)

    result=dict(through_batch=through,comparisons=results,failures=0)
    if write_evidence:(EVIDENCE/f'cross-matrix-batch{through}.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--through',type=int,choices=range(2,6),default=5);parser.add_argument('--check-only',action='store_true');args=parser.parse_args()
    print(json.dumps(verify(args.through,not args.check_only),indent=2))
