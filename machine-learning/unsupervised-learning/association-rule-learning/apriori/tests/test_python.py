from fractions import Fraction
import random
import pytest

pytestmark = pytest.mark.ml


@pytest.mark.oracle
def test_known_pairs_triple_and_levels(b6):
    rows = [['a','b','c'],['a','b','c'],['a','b'],['a','c'],['b','c']]
    model = b6.load('apriori').Apriori(.4).fit(rows)
    expected = {frozenset(k):v for k,v in [(('a',),4),(('b',),4),(('c',),4),(('a','b'),3),(('a','c'),3),(('b','c'),3),(('a','b','c'),2)]}
    assert model.frequent_itemsets_ == expected
    assert list(model.frequent_itemsets_) == list(expected)
    assert tuple(map(len,model.levels_)) == (3,3,1)
    assert model.candidate_counts_ == (3,1,0)
    assert model.n_transactions_ == 5 and model.min_count_ == 2


@pytest.mark.oracle
def test_prefix_candidate_join_and_subset_pruning(b6):
    module = b6.load('apriori');budget = b6.Budget()
    previous = [frozenset('ab'),frozenset('ac')]
    assert module.join_candidates(previous,budget) == [] # bc is absent
    previous.append(frozenset('bc'))
    assert module.join_candidates(previous,budget) == [frozenset('abc')]
    assert module.join_candidates([],budget) == []


@pytest.mark.parametrize('rows,minimum',[( [['x']],1.0),([],0.5),([[],[]],.5),([['x','x'],['x'],[]],.5),([['a'],['b'],[]],1.0),([['a','b','c']],1.0)])
@pytest.mark.oracle
def test_boundary_databases(b6,b6_oracles,rows,minimum):
    assert b6.load('apriori').apriori(rows,minimum) == b6_oracles.brute_itemsets(rows,minimum)


@pytest.mark.numerical
def test_decimal_threshold_and_empty_denominator(b6):
    cls = b6.load('apriori').Apriori
    rows = [['a']]*14+[[]]*86
    model = cls(.14).fit(rows)
    assert model.min_count_ == 14 and model.frequent_itemsets_ == {frozenset(['a']):14}
    import math
    assert cls(math.nextafter(.14,1)).fit(rows).frequent_itemsets_ == {}
    assert cls(.5).fit([['a'],[]]).frequent_itemsets_ == {frozenset(['a']):1}
    assert cls(.5).fit([]).min_count_ == 1


@pytest.mark.oracle
@pytest.mark.parametrize('seed',[18001,18002,18003])
def test_randomized_oracle_downward_closure(b6,b6_oracles,seed):
    rng = random.Random(seed)
    rows = [[item for item in range(6) if rng.random()<.45] for _ in range(16)]
    result = b6.load('apriori').apriori(rows,.25)
    assert result == b6_oracles.brute_itemsets(rows,.25)
    for larger,count in result.items():
        for item in larger:
            smaller = larger-{item}
            if smaller:assert result[smaller]>=count


@pytest.mark.reference
def test_independent_sparse_incidence_reference(b6,b6_oracles):
    rows = [['bread','milk','bread'],['milk'],[],['bread','milk'],['eggs']]
    assert b6.load('apriori').apriori(rows,.2) == b6_oracles.sparse_reference(rows,.2)


def test_limits_and_failed_refit_are_atomic(b6):
    cls = b6.load('apriori').Apriori
    model = cls(.5).fit([['a'],['a']]);before = model.frequent_itemsets_.copy()
    model.max_patterns = 1
    with pytest.raises(b6.MiningLimitError):model.fit([['a','b','c']])
    assert model.frequent_itemsets_ == before
    with pytest.raises(b6.MiningLimitError):cls(.5,max_work=1).fit([['a','b']])
    model.min_support = True
    with pytest.raises(ValueError):model.fit([['a']])
    assert model.frequent_itemsets_ == before
