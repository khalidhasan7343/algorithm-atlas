from dataclasses import FrozenInstanceError
from fractions import Fraction
import math
import random
import pytest
pytestmark=pytest.mark.ml

ROWS=[list('abc'),list('abc'),list('ab'),list('ac'),list('bc')]


def mapping(rules):
    return {(r.antecedent,r.consequent):(r.support_count,r.support,r.confidence,r.lift) for r in rules}


@pytest.mark.oracle
@pytest.mark.numerical
def test_known_rule_formulas_nine_directions_and_threshold(b6,b6_oracles):
    counts=b6_oracles.brute_itemsets(ROWS,.4);before=counts.copy()
    rules=b6.load('rules').generate_rules(counts,5,.6)
    assert len(rules)==9 and counts==before
    got=mapping(rules);expected=b6_oracles.brute_rules(ROWS,.4,.6)
    assert set(got)==set(expected)
    for key,values in expected.items():assert got[key]==tuple(float(v) if isinstance(v,Fraction) else v for v in values)
    assert got[frozenset('a'),frozenset('b')]==(3,.6,.75,float(Fraction(15,16)))
    assert got[frozenset('ab'),frozenset('c')]==(2,.4,float(Fraction(2,3)),float(Fraction(5,6)))
    assert (frozenset('b'),frozenset('a')) in got
    for rule in rules:
        assert rule.antecedent and rule.consequent and not rule.antecedent&rule.consequent
        assert rule.antecedent|rule.consequent in counts
        assert 0<rule.support<=1 and 0<rule.confidence<=1 and rule.lift>0
    with pytest.raises(FrozenInstanceError):rules[0].support=0


@pytest.mark.numerical
def test_confidence_decimal_boundaries_no_tolerance(b6,b6_oracles):
    counts=b6_oracles.brute_itemsets(ROWS,.4);generate=b6.load('rules').generate_rules
    assert len(generate(counts,5,.75))==6
    assert generate(counts,5,math.nextafter(.75,1))==[]
    assert len(generate(counts,5,2/3))==9 # shortest decimal is below exact2/3
    assert len(generate(counts,5,math.nextafter(2/3,1)))==6
    assert len(generate(counts,5,0.0))==12
    assert generate(counts,5,1.0)==[]


@pytest.mark.oracle
@pytest.mark.parametrize('rows,lift',[([list('ab'),list('ab'),[],[]],2.0),([list('ab'),['a'],['b'],[]],1.0),([list('ab'),['a'],['b'],['b']],float(Fraction(2,3)))])
def test_positive_independent_negative_association(b6,b6_oracles,rows,lift):
    rules=b6.load('rules').generate_rules(b6_oracles.brute_itemsets(rows,.25),4,0.0)
    pair=next(r for r in rules if r.antecedent==frozenset('a') and r.consequent==frozenset('b'))
    assert pair.lift==lift


@pytest.mark.reference
def test_scipy_independent_contingency_lift_reference(b6,b6_oracles):
    from scipy.stats.contingency import expected_freq
    counts=b6_oracles.brute_itemsets(ROWS,.4)
    for rule in b6.load('rules').generate_rules(counts,5,0.0):
        both=sum(rule.antecedent|rule.consequent<=set(row) for row in ROWS)
        a=sum(rule.antecedent<=set(row) for row in ROWS);b=sum(rule.consequent<=set(row) for row in ROWS)
        table=[[both,a-both],[b-both,5-a-b+both]]
        assert rule.lift==pytest.approx(both/expected_freq(table)[0,0],rel=1e-14)


@pytest.mark.oracle
@pytest.mark.parametrize('seed',[18031,18032,18033,18034])
def test_randomized_rules_direct_raw_transaction_oracle(b6,b6_oracles,seed):
    rng=random.Random(seed);rows=[[x for x in range(5) if rng.random()<.6] for _ in range(14)]
    counts=b6_oracles.brute_itemsets(rows,.2)
    actual=mapping(b6.load('rules').generate_rules(counts,len(rows),.6));expected=b6_oracles.brute_rules(rows,.2,.6)
    assert actual=={key:tuple(float(v) if isinstance(v,Fraction) else v for v in values) for key,values in expected.items()}


@pytest.mark.parametrize('counts,n',[( {frozenset('a'):1},0),({frozenset('a'):0},3),({frozenset('a'):True},3),({frozenset('a'):4},3),({frozenset():1},3),({('a',):1},3),({frozenset('ab'):1,frozenset('a'):2},3),({frozenset('ab'):2,frozenset('a'):1,frozenset('b'):2},3),({frozenset('a'):1,frozenset([1]):1},3)])
def test_incomplete_invalid_or_inconsistent_count_maps(b6,counts,n):
    with pytest.raises(ValueError):b6.load('rules').generate_rules(counts,n)


@pytest.mark.parametrize('minimum',[True,1,0,-.1,1.1,float('nan'),float('inf'),'0.5'])
def test_invalid_confidence(b6,minimum):
    with pytest.raises(ValueError):b6.load('rules').generate_rules({},0,minimum)


def test_empty_singleton_no_rules_and_resource_limits(b6,b6_oracles):
    generate=b6.load('rules').generate_rules
    assert generate({},0)==[] and generate({},3)==[]
    assert generate({frozenset('a'):2},2)==[]
    counts=b6_oracles.brute_itemsets(ROWS,.4)
    with pytest.raises(b6.MiningLimitError):generate(counts,5,0.0,max_rules=1)
    with pytest.raises(b6.MiningLimitError):generate(counts,5,max_work=1)
    for limits in [{'max_rules':True},{'max_rules':0},{'max_rules':50001},{'max_work':0},{'max_work':True}]:
        with pytest.raises(ValueError):generate(counts,5,**limits)
    for n in [-1,True,1.5,4097]:
        with pytest.raises(ValueError):generate({},n)


def test_deterministic_rule_order_independent_of_mapping_order(b6,b6_oracles):
    counts=b6_oracles.brute_itemsets(ROWS,.4);generate=b6.load('rules').generate_rules
    left=generate(counts,5,0.0);right=generate(dict(reversed(list(counts.items()))),5,0.0)
    assert left==right
    keys=[(len(r.antecedent),tuple(sorted(r.antecedent)),len(r.consequent),tuple(sorted(r.consequent))) for r in left]
    assert keys==sorted(keys)
