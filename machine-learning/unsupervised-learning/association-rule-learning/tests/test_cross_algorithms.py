"""Every miner is checked against direct counts, never another miner alone."""
from fractions import Fraction
from itertools import combinations,combinations_with_replacement
import random
import pytest

pytestmark=pytest.mark.ml


def miners(b6):
    return [b6.load('apriori').Apriori,b6.load('eclat').Eclat,b6.load('fp-growth').FPGrowth]


@pytest.mark.oracle
@pytest.mark.parametrize('minimum',[.25,.5,1.0])
def test_exhaustive_three_item_multiset_databases(b6,b6_oracles,minimum):
    transactions=[tuple(x for x in range(3) if mask & (1<<x)) for mask in range(8)]
    checked=0
    for n in range(5):
        for indices in combinations_with_replacement(range(8),n):
            rows=[transactions[j] for j in indices]
            truth=b6_oracles.brute_itemsets(rows,minimum)
            for cls in miners(b6):
                actual=cls(minimum).fit(rows).frequent_itemsets_
                assert actual==truth,(cls.__name__,rows,minimum)
                assert list(actual)==sorted(actual,key=lambda s:(len(s),tuple(sorted(s))))
            checked+=1
    assert checked==495


@pytest.mark.oracle
@pytest.mark.parametrize('seed,density',[(18041,.15),(18042,.5),(18043,.85),(18044,.35),(18045,.7)])
def test_randomized_dense_sparse_duplicates_rules_and_scale_counts(b6,b6_oracles,seed,density):
    rng=random.Random(seed);rows=[[x for x in range(7) if rng.random()<density] for _ in range(20)]
    rows+=rows[:3]+[[],[]]
    truth=b6_oracles.brute_itemsets(rows,.16);expected_rules=b6_oracles.brute_rules(rows,.16,.65)
    for cls in miners(b6):
        model=cls(.16).fit(rows);assert model.frequent_itemsets_==truth
        assert model.n_transactions_==25
        doubled=cls(.16).fit(rows+rows).frequent_itemsets_
        assert doubled=={key:2*count for key,count in truth.items()}
        rules=b6.load('rules').generate_rules(model.frequent_itemsets_,25,.65)
        actual={(r.antecedent,r.consequent):(r.support_count,r.support,r.confidence,r.lift) for r in rules}
        assert actual=={key:tuple(float(v) if isinstance(v,Fraction) else v for v in values) for key,values in expected_rules.items()}
        for larger,count in truth.items():
            assert 0<Fraction(count,len(rows))<=1
            for item in larger:
                smaller=larger-{item}
                if smaller:assert truth[smaller]>=count


@pytest.mark.reference
@pytest.mark.parametrize('density',[.1,.5,.9])
def test_all_miners_independent_sparse_reference(b6,b6_oracles,density):
    rng=random.Random(18046);rows=[[str(x) for x in range(6) if rng.random()<density] for _ in range(18)]
    truth=b6_oracles.sparse_reference(rows,.2)
    for cls in miners(b6):assert cls(.2).fit(rows).frequent_itemsets_==truth


@pytest.mark.oracle
def test_instruction_textbook_basket_counts_and_positive_rule(b6,b6_oracles):
    rows=[['bread','milk'],['bread','diaper','beer','eggs'],['milk','diaper','beer','cola'],['bread','milk','diaper','beer'],['bread','milk','diaper','cola']]
    expected={frozenset([x]):c for x,c in [('beer',3),('bread',4),('diaper',4),('milk',4)]}
    expected.update({frozenset(pair):3 for pair in [('beer','diaper'),('bread','diaper'),('bread','milk'),('diaper','milk')]})
    assert expected==b6_oracles.brute_itemsets(rows,.6)
    for cls in miners(b6):
        m=cls(.6).fit(rows);assert m.frequent_itemsets_==expected
        rules=b6.load('rules').generate_rules(m.frequent_itemsets_,5,.75)
        rule=next(r for r in rules if r.antecedent==frozenset(['beer']) and r.consequent==frozenset(['diaper']))
        assert rule.confidence==1 and rule.lift==1.25


@pytest.mark.parametrize('name',['apriori','eclat','fp-growth'])
def test_large_dense_space_fails_explicitly_with_no_partial_state(b6,name):
    classes={'apriori':'Apriori','eclat':'Eclat','fp-growth':'FPGrowth'}
    model=getattr(b6.load(name),classes[name])(.5,max_patterns=128,max_work=100000)
    model.fit([[0]]);before=model.frequent_itemsets_.copy()
    with pytest.raises(b6.MiningLimitError):model.fit([list(range(32))])
    assert model.frequent_itemsets_==before
