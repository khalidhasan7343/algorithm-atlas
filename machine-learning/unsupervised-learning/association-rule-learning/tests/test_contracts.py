"""Strict item families, denominator, limits, determinism and failure contracts."""
from copy import deepcopy
from fractions import Fraction
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import pytest

pytestmark=pytest.mark.ml
NAMES={'apriori':'Apriori','eclat':'Eclat','fp-growth':'FPGrowth'}


@pytest.mark.parametrize('name',NAMES)
@pytest.mark.parametrize('data',['abc',None,{'a':1},['abc'],[[True]],[[1.0]],[[None]],[[[]]],[['']],[[2**63]],[['x',1]],[[('tuple',)]]])
def test_invalid_transaction_forms_and_identifiers(b6,name,data):
    with pytest.raises(ValueError):getattr(b6.load(name),NAMES[name])().fit(data)


@pytest.mark.parametrize('name',NAMES)
@pytest.mark.parametrize('minimum',[True,1,0,0.0,-.1,1.1,float('nan'),float('inf'),'0.5',Fraction(1,2)])
def test_invalid_support_no_count_reinterpretation(b6,name,minimum):
    with pytest.raises(ValueError):getattr(b6.load(name),NAMES[name])(minimum)


@pytest.mark.parametrize('name',NAMES)
def test_all_supported_containers_no_mutation_and_stable_order(b6,name):
    cls=getattr(b6.load(name),NAMES[name]);data=[['b','a','a'],('a','b'),frozenset('a'),set(),[]]
    original=deepcopy(data);state=random.getstate();model=cls(.4).fit(data)
    assert data==original and random.getstate()==state
    assert model.n_transactions_==5
    assert model.frequent_itemsets_=={frozenset('a'):3,frozenset('b'):2,frozenset('ab'):2}
    assert cls(.4).fit(tuple(reversed(data))).frequent_itemsets_==model.frequent_itemsets_
    assert list(model.frequent_itemsets_)==[frozenset('a'),frozenset('b'),frozenset('ab')]
    # Caller-owned input is not used as fitted mutable state.
    data[0].clear();assert model.frequent_itemsets_[frozenset('b')]==2
    integer=cls(.4).fit([[10,-2],[-2,10],[]]);assert integer.items_==(-2,10)
    assert list(integer.frequent_itemsets_)==[frozenset([-2]),frozenset([10]),frozenset([-2,10])]


@pytest.mark.parametrize('name',NAMES)
def test_resource_inputs_invalid_mutations_and_atomic_fit(b6,name):
    cls=getattr(b6.load(name),NAMES[name]);model=cls().fit([['x']]);before=model.frequent_itemsets_.copy()
    for invalid in [[[]]*4097,[list(range(33))],[['x']*129],[['x']*128]*513]:
        with pytest.raises(ValueError):model.fit(invalid)
        assert model.frequent_itemsets_==before
    with pytest.raises(ValueError):model.fit((row for row in [['x']]))
    with pytest.raises(ValueError):cls(max_patterns=True)
    with pytest.raises(ValueError):cls(max_work=0)
    model.min_support=1
    with pytest.raises(ValueError):model.fit([['x']])
    assert model.frequent_itemsets_==before


@pytest.mark.parametrize('name',NAMES)
def test_hashseed_independent_cli_itemsets_and_rules(b6,name):
    payload={'transactions':[list('abc'),list('abc'),list('ab'),list('ac'),list('bc')],'parameters':{'min_support':.4},'min_confidence':.6}
    outputs=[]
    for seed in ['0','7','123']:
        env=os.environ.copy();env['PYTHONHASHSEED']=seed
        result=subprocess.run([sys.executable,str(b6.ROOT/name/'python/solution.py')],input=json.dumps(payload),text=True,capture_output=True,env=env,timeout=30)
        assert result.returncode==0,result.stderr
        outputs.append(result.stdout)
    assert outputs[0]==outputs[1]==outputs[2]
