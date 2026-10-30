"""Small explicit benchmark; never imported by pytest, no general speed claims."""
from fractions import Fraction
from itertools import combinations
import importlib.util
import json
from pathlib import Path
import random
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('atlas_b6_support',ROOT/'support.py')
support=sys.modules.get(spec.name)
if support is None:
    support=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=support
    spec.loader.exec_module(support)


def direct_counts(rows,minimum):
    result={}
    for size in range(1,9):
        for chosen in combinations(range(8),size):
            count=sum(all(item in row for item in chosen) for row in rows)
            if Fraction(count,len(rows))>=Fraction(str(minimum)):
                result[frozenset(chosen)]=count
    return result


def main():
    names={'apriori':'Apriori','eclat':'Eclat','fp-growth':'FPGrowth'}
    classes={name:getattr(support.load(name),cls) for name,cls in names.items()}
    results=[]
    for index,regime in enumerate(['sparse','dense','shared-prefix']):
        seed=18060+index;rng=random.Random(seed)
        if regime=='shared-prefix':
            rows=[[item for item in range(8) if rng.random()<(.9 if item<4 else .2)] for _ in range(96)]
        else:
            density=.15 if regime=='sparse' else .8
            rows=[[item for item in range(8) if rng.random()<density] for _ in range(96)]
        truth=direct_counts(rows,.25)
        for name,cls in names.items():
            started=time.perf_counter();model=classes[name](.25).fit(rows);elapsed=time.perf_counter()-started
            assert model.frequent_itemsets_==truth
            results.append(dict(regime=regime,seed=seed,transactions=96,universe=8,min_support=.25,
                algorithm=name,frequent_itemsets=len(truth),work_units=model.work_units_,seconds=elapsed,
                fp_tree_nodes=model.tree_.node_count if hasattr(model,'tree_') else None,
                direct_count_oracle='passed'))
    print(json.dumps(dict(results=results,interpretation='Canonical imports excluded. Single bounded seeded construction/fit experiments, not repeated performance estimates or a universal winner; work units differ by algorithm and are not comparable CPU instructions.'),indent=2))


if __name__=='__main__':main()
