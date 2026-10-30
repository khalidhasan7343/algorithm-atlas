"""Bounded transaction contracts and deterministic presentation, not mining logic."""
from fractions import Fraction
from functools import lru_cache
import importlib.util
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
MAX_TRANSACTIONS = 4096
MAX_ITEMS = 32
MAX_RAW_ENTRIES = 65536


class MiningLimitError(RuntimeError):
    """A declared search/output budget was exceeded; no partial fit is installed."""


def integer(value, name, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} must be a native integer in {low}..{high}")
    return value


def threshold(value, name, *, allow_zero=False):
    if type(value) is not float or not math.isfinite(value):
        raise ValueError(f"{name} must be a native finite float fraction, never an absolute count")
    if not (0 <= value <= 1) or (value == 0 and not allow_zero):
        raise ValueError(f"{name} outside {'[0,1]' if allow_zero else '(0,1]'}")
    return Fraction(str(value))


def item_family(item):
    if type(item) is int and -(2**63) <= item < 2**63:
        return int
    if type(item) is str and 1 <= len(item) <= 128:
        return str
    raise ValueError('items must be native int64 integers or nonempty strings <=128 characters')


def transactions(data):
    if type(data) not in (list, tuple) or len(data) > MAX_TRANSACTIONS:
        raise ValueError('transactions must be a bounded list/tuple of rows')
    result, universe, family, entries = [], set(), None, 0
    for row in data:
        if type(row) not in (list, tuple, set, frozenset) or len(row) > 128:
            raise ValueError('each transaction must be list/tuple/set/frozenset with <=128 entries')
        entries += len(row)
        if entries > MAX_RAW_ENTRIES:
            raise ValueError('raw transaction-entry limit exceeded')
        copied = set()
        for item in row:
            current = item_family(item)
            if family is not None and current is not family:
                raise ValueError('all item IDs must have one homogeneous family')
            family = current
            copied.add(item)
        universe.update(copied)
        if len(universe) > MAX_ITEMS:
            raise ValueError('at most32 unique items supported')
        result.append(frozenset(copied))
    return tuple(result), tuple(sorted(universe))


def minimum_count(fraction, n):
    return max(1, (fraction.numerator*n+fraction.denominator-1)//fraction.denominator)


def itemset_key(items):
    return len(items), tuple(sorted(items))


def ordered_counts(counts):
    return {items: counts[items] for items in sorted(counts, key=itemset_key)}


class Budget:
    def __init__(self, max_patterns=10000, max_work=1000000):
        self.max_patterns = integer(max_patterns, 'max_patterns', 1, 50000)
        self.max_work = integer(max_work, 'max_work', 1, 5000000)
        self.used = 0

    def charge(self, amount=1):
        self.used += amount
        if self.used > self.max_work:
            raise MiningLimitError('max_work exceeded; increase budget or reduce the input/search space')

    def collection(self, size):
        if size > self.max_patterns:
            raise MiningLimitError('max_patterns exceeded by output/intermediate collection')

    def add(self, result, items, count):
        if items in result:
            raise ValueError('duplicate mined pattern: internal enumeration invariant violated')
        self.collection(len(result)+1)
        result[items] = count


class Miner:
    def __init__(self, min_support=0.5, max_patterns=10000, max_work=1000000):
        self.min_support = min_support
        self.max_patterns = max_patterns
        self.max_work = max_work
        self._parameters()

    def _parameters(self):
        fraction = threshold(self.min_support, 'min_support')
        budget = Budget(self.max_patterns, self.max_work)
        return fraction, budget

    def fit(self, data):
        fraction, budget = self._parameters()
        rows, items = transactions(data)
        limit = minimum_count(fraction, len(rows))
        result, diagnostics = self._mine(rows, items, limit, budget)
        state = dict(frequent_itemsets_=ordered_counts(result), n_transactions_=len(rows),
                     items_=items, min_count_=limit, work_units_=budget.used)
        state.update(diagnostics)
        self.__dict__.update(state)
        return self


@lru_cache(None)
def module_at(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = sys.modules.get(name)
    if module is None:
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return module


@lru_cache(None)
def load(name):
    if name not in ('apriori', 'eclat', 'fp-growth', 'rules'):
        raise ValueError('unknown B6 canonical/utility')
    path = ROOT/'rules.py' if name == 'rules' else ROOT/name/'python/solution.py'
    return module_at('atlas_b6_'+name.replace('-', '_'), path)


def main(estimator):
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict) or 'transactions' not in data or set(data)-{'transactions','parameters','min_confidence'}:
            raise ValueError('JSON requires transactions and optional parameters/min_confidence')
        params = data.get('parameters', {})
        if not isinstance(params, dict):
            raise ValueError('parameters must be an object')
        model = estimator(**params).fit(data['transactions'])
        output = dict(n_transactions=model.n_transactions_, min_count=model.min_count_,
                      itemsets=[dict(items=sorted(key), support_count=value) for key,value in model.frequent_itemsets_.items()])
        if 'min_confidence' in data:
            rules = load('rules').generate_rules(model.frequent_itemsets_, model.n_transactions_, data['min_confidence'])
            output['rules'] = [dict(antecedent=sorted(rule.antecedent),consequent=sorted(rule.consequent),
                support_count=rule.support_count,support=rule.support,confidence=rule.confidence,lift=rule.lift) for rule in rules]
        print(json.dumps(output, allow_nan=False))
    except (ValueError, TypeError, MiningLimitError) as error:
        print('error: '+str(error), file=sys.stderr)
        raise SystemExit(2)
