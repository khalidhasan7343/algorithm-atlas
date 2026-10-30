"""Executed deterministic transaction example; run from any directory."""
import json
from solution import FPGrowth

if __name__ == '__main__':
    payload = {'transactions': [['a', 'b', 'c'], ['a', 'b', 'c'], ['a', 'b'], ['a', 'c'], ['b', 'c']], 'parameters': {'min_support': 0.4}}
    model = FPGrowth(**payload['parameters']).fit(payload['transactions'])
    print(json.dumps(dict(n_transactions=model.n_transactions_,min_count=model.min_count_,
        itemsets=[dict(items=sorted(key),support_count=value) for key,value in model.frequent_itemsets_.items()]),allow_nan=False))
