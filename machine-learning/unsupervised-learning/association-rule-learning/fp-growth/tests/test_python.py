import random
import pytest
pytestmark=pytest.mark.ml


def linked_nodes(entry):
    result=[];node=entry.head
    while node is not None:
        assert all(node is not old for old in result),'header cycle'
        result.append(node);node=node.next
    assert (result[-1] if result else None) is entry.tail
    return result


@pytest.mark.oracle
def test_shared_prefix_counts_parent_child_and_header_links(b6):
    module=b6.load('fp-growth');rows=[list('abc'),list('abc'),list('ab'),list('ac'),list('bc')]
    m=module.FPGrowth(.4).fit(rows);tree=m.tree_;root=tree.root
    assert root.item is None and root.parent is None and root.count==5
    assert tree.node_count==6
    assert tree.rank=={'a':0,'b':1,'c':2}
    assert root.children['a'].count==4 and root.children['b'].count==1
    assert root.children['a'].children['b'].count==3
    assert root.children['a'].children['b'].children['c'].count==2
    assert root.children['a'].children['b'].parent is root.children['a']
    for item,entry in tree.header.items():
        nodes=linked_nodes(entry)
        assert all(node.item==item for node in nodes)
        assert sum(node.count for node in nodes)==entry.count==4
        for node in nodes:assert node.parent.children[item] is node
    assert len(linked_nodes(tree.header['b']))==2
    assert len(linked_nodes(tree.header['c']))==3


@pytest.mark.oracle
def test_weighted_conditional_base_and_tree_support(b6):
    module=b6.load('fp-growth');rows=[list('abc'),list('abc'),list('ab'),list('ac'),list('bc')]
    m=module.FPGrowth(.4).fit(rows);base=module.conditional_base(m.tree_,'c',b6.Budget())
    assert base==[(('a','b'),2),(('a',),1),(('b',),1)]
    child=module.build_tree(base,2,b6.Budget())
    assert child.header['a'].count==child.header['b'].count==3
    assert module.conditional_base(child,'b',b6.Budget())==[(('a',),2)]
    assert m.frequent_itemsets_[frozenset('abc')]==2
    assert m.conditional_tree_count_>=2 and m.max_depth_==3


@pytest.mark.oracle
def test_compressed_repeated_paths_keep_full_weight(b6,b6_oracles):
    rows=[list('abc')]*7+[list('ab')]*2+[[]]
    m=b6.load('fp-growth').FPGrowth(.1).fit(rows)
    assert m.tree_.node_count==3 and m.tree_.root.count==10
    assert m.frequent_itemsets_==b6_oracles.brute_itemsets(rows,.1)
    assert m.frequent_itemsets_[frozenset('abc')]==7
    base=b6.load('fp-growth').conditional_base(m.tree_,'c',b6.Budget())
    assert base==[(('a','b'),7)]


@pytest.mark.oracle
@pytest.mark.parametrize('rows,minimum',[([],0.5),([[],[]],.5),([['a']],1.0),([['a','a'],['a'],[]],.5),([['a'],['b'],['c']],.2),([['a'],['b'],['c']],1.0),([list('abcd')]*4,.5)])
def test_empty_single_disjoint_dense_and_duplicates(b6,b6_oracles,rows,minimum):
    assert b6.load('fp-growth').fp_growth(rows,minimum)==b6_oracles.brute_itemsets(rows,minimum)


@pytest.mark.oracle
@pytest.mark.parametrize('seed',[18021,18022,18023])
def test_randomized_conditional_patterns_against_raw_counts(b6,b6_oracles,seed):
    rng=random.Random(seed);rows=[[x for x in range(6) if rng.random()<.55] for _ in range(20)]
    m=b6.load('fp-growth').FPGrowth(.2).fit(rows)
    assert m.frequent_itemsets_==b6_oracles.brute_itemsets(rows,.2)
    for item,entry in m.tree_.header.items():assert sum(n.count for n in linked_nodes(entry))==sum(item in row for row in rows)


@pytest.mark.reference
def test_independent_sparse_reference(b6,b6_oracles):
    rows=[list('abc'),list('abc'),list('ab'),list('ac'),list('bc'),[]]
    assert b6.load('fp-growth').fp_growth(rows,.3)==b6_oracles.sparse_reference(rows,.3)


@pytest.mark.numerical
def test_frequency_ties_filtering_and_threshold_boundary(b6):
    import math
    cls=b6.load('fp-growth').FPGrowth
    m=cls(.5).fit([['z','a','rare'],['a','z'],[]])
    assert list(m.tree_.header)==['a','z'] and 'rare' not in m.tree_.root.children
    assert cls(.2).fit([['x']]*2+[[]]*8).frequent_itemsets_=={frozenset(['x']):2}
    assert cls(math.nextafter(.2,1)).fit([['x']]*2+[[]]*8).frequent_itemsets_=={}


def test_no_other_miner_delegation_and_atomic_limits(b6,monkeypatch):
    module=b6.load('fp-growth');m=module.FPGrowth().fit([['a']]);before=m.frequent_itemsets_.copy()
    def forbidden(*args):raise AssertionError('unexpected mining delegation')
    monkeypatch.setattr(b6,'load',forbidden)
    assert module.fp_growth([[1,2],[1,2]])[frozenset([1,2])]==2
    m.max_work=1
    with pytest.raises(b6.MiningLimitError):m.fit([['a','b']])
    assert m.frequent_itemsets_==before
    with pytest.raises(b6.MiningLimitError):module.FPGrowth(max_patterns=1).fit([[1,2]])
