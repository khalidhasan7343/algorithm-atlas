from itertools import combinations
import random
import pytest

pytestmark=pytest.mark.ml


@pytest.mark.oracle
def test_stable_tid_index_pair_triple_and_empty_rows(b6):
    rows=[list('abc'),list('abc'),list('ab'),list('ac'),list('bc'),[]]
    m=b6.load('eclat').Eclat(.3).fit(rows)
    assert m.n_transactions_==6
    assert m.vertical_=={'a':frozenset([0,1,2,3]),'b':frozenset([0,1,2,4]),'c':frozenset([0,1,3,4])}
    assert m.frequent_itemsets_[frozenset('ab')]==3
    assert m.frequent_itemsets_[frozenset('abc')]==2
    assert m.vertical_['a']&m.vertical_['b']&m.vertical_['c']=={0,1}
    assert m.intersection_count_>0


@pytest.mark.oracle
@pytest.mark.parametrize('rows,minimum',[([],0.5),([[],[]],.5),([['a']],1.0),([list('abc')]*3,1.0),([['a'],['b'],[],['c']],.5),([['a','a'],['a'],[]],.5)])
def test_sparse_dense_empty_duplicates(b6,b6_oracles,rows,minimum):
    assert b6.load('eclat').eclat(rows,minimum)==b6_oracles.brute_itemsets(rows,minimum)


@pytest.mark.oracle
@pytest.mark.parametrize('seed',[18011,18012,18013])
def test_randomized_tid_union_identity_and_direct_counts(b6,b6_oracles,seed):
    rng=random.Random(seed);rows=[[x for x in range(6) if rng.random()<.6] for _ in range(18)]
    m=b6.load('eclat').Eclat(.2).fit(rows)
    assert m.frequent_itemsets_==b6_oracles.brute_itemsets(rows,.2)
    for A in combinations(range(6),2):
        for b in range(6):
            expected={i for i,row in enumerate(rows) if set(A)|{b}<=set(row)}
            intersect=set(range(len(rows)))
            for item in set(A)|{b}:intersect&=m.vertical_.get(item,frozenset())
            assert intersect==expected


@pytest.mark.reference
def test_independent_sparse_incidence_reference(b6,b6_oracles):
    rows=[['a','b'],['a','b'],[],['a','c'],['b','c'],['d']]
    assert b6.load('eclat').eclat(rows,.16)==b6_oracles.sparse_reference(rows,.16)


@pytest.mark.numerical
def test_threshold_boundary_and_repeated_observations(b6):
    import math
    cls=b6.load('eclat').Eclat;rows=[[1,1]]*3+[[]]*7
    assert cls(.3).fit(rows).frequent_itemsets_=={frozenset([1]):3}
    assert cls(math.nextafter(.3,1)).fit(rows).frequent_itemsets_=={}
    assert cls(1.0).fit([[1,2]]*4).vertical_[1]==frozenset(range(4))


def test_no_apriori_dependency_and_atomic_limits(b6,monkeypatch):
    module=b6.load('eclat');m=module.Eclat(.5).fit([['a']]);before=m.frequent_itemsets_.copy()
    # Mining cannot delegate to another canonical through the loader.
    def forbidden(*args):raise AssertionError('unexpected canonical delegation')
    monkeypatch.setattr(b6,'load',forbidden)
    assert module.eclat([[1,2],[1,2]])[frozenset([1,2])]==2
    m.max_work=1
    with pytest.raises(b6.MiningLimitError):m.fit([['a','b']])
    assert m.frequent_itemsets_==before
    with pytest.raises(b6.MiningLimitError):module.Eclat(.5,max_patterns=1).fit([[1,2]])
