"""Mining-independent, validated association rules with decimal-exact filtering."""
from dataclasses import dataclass
from itertools import combinations
import importlib.util
from pathlib import Path
import sys

_spec=importlib.util.spec_from_file_location('atlas_b6_support',Path(__file__).with_name('support.py'))
support=sys.modules.get(_spec.name)
if support is None:
    support=importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name]=support
    _spec.loader.exec_module(support)


@dataclass(frozen=True,slots=True)
class Rule:
    antecedent: frozenset
    consequent: frozenset
    support_count: int
    support: float
    confidence: float
    lift: float


def _validated_counts(counts,n,budget):
    if type(counts) is not dict or len(counts)>50000:
        raise ValueError('counts must be a dict with <=50000 itemsets')
    copied={}
    family=None
    universe=set()
    for key,value in counts.items():
        budget.charge(1+len(key) if type(key) is frozenset else 1)
        if type(key) is not frozenset or not 1<=len(key)<=support.MAX_ITEMS:
            raise ValueError('count keys must be nonempty frozensets of <=32 items')
        for item in key:
            current=support.item_family(item)
            if family is not None and current is not family:
                raise ValueError('support map item IDs must have one family')
            family=current
            universe.add(item)
        if len(universe)>support.MAX_ITEMS:
            raise ValueError('support map universe exceeds32 items')
        if n==0:
            raise ValueError('nonempty support map has zero transaction denominator')
        support.integer(value,'support count',1,n)
        copied[key]=value
    for key,count in copied.items():
        if len(key)>1:
            for item in key:
                budget.charge(len(key))
                subset=key-{item}
                if subset not in copied or copied[subset]<count:
                    raise ValueError('support map must be downward closed and anti-monotonic')
    return copied


def generate_rules(counts,n_transactions,min_confidence=0.5,*,max_rules=10000,max_work=1000000):
    n=support.integer(n_transactions,'n_transactions',0,support.MAX_TRANSACTIONS)
    minimum=support.threshold(min_confidence,'min_confidence',allow_zero=True)
    support.integer(max_rules,'max_rules',1,50000)
    budget=support.Budget(max_rules,max_work)
    copied=_validated_counts(counts,n,budget)
    result=[]
    for union in sorted(copied,key=support.itemset_key):
        values=tuple(sorted(union));count=copied[union]
        for size in range(1,len(values)):
            for chosen in combinations(values,size):
                budget.charge(len(union))
                antecedent=frozenset(chosen);consequent=union-antecedent
                a,b=copied[antecedent],copied[consequent]
                if count*minimum.denominator>=a*minimum.numerator:
                    if len(result)>=max_rules:
                        raise support.MiningLimitError('max_rules exceeded; no partial rule list returned')
                    result.append(Rule(antecedent,consequent,count,count/n,count/a,n*count/(a*b)))
    return sorted(result,key=lambda rule:(*support.itemset_key(rule.antecedent),*support.itemset_key(rule.consequent)))
