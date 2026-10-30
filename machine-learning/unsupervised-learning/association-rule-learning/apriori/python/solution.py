"""Level-wise prefix joins, downward-closure pruning and horizontal support scans."""
from itertools import combinations
import importlib.util
from pathlib import Path
import sys

_path = Path(__file__).resolve().parents[2]/'support.py'
_spec = importlib.util.spec_from_file_location('atlas_b6_support', _path)
support = sys.modules.get(_spec.name)
if support is None:
    support = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = support
    _spec.loader.exec_module(support)

def join_candidates(previous, budget):
    """Join same-prefix size-k sets and prune missing immediate subsets."""
    ordered = sorted(tuple(sorted(items)) for items in previous)
    known = set(previous)
    candidates = []
    if not ordered:
        return candidates
    size = len(ordered[0])+1
    for index, left in enumerate(ordered):
        for right in ordered[index+1:]:
            budget.charge()
            if left[:-1] != right[:-1]:
                break
            merged = left+(right[-1],)
            budget.charge(size)
            if all(frozenset(subset) in known for subset in combinations(merged, size-1)):
                budget.collection(len(candidates)+1)
                candidates.append(frozenset(merged))
    return candidates


class Apriori(support.Miner):
    def _mine(self, rows, items, limit, budget):
        singleton_counts = dict.fromkeys(items, 0)
        for row in rows:
            budget.charge(1+len(row))
            for item in row:
                singleton_counts[item] += 1
        level = [frozenset((item,)) for item in items if singleton_counts[item] >= limit]
        result, levels, candidate_sizes = {}, [], []
        for itemset in level:
            budget.add(result, itemset, singleton_counts[next(iter(itemset))])
        while level:
            levels.append(tuple(sorted(level, key=support.itemset_key)))
            candidates = join_candidates(level, budget)
            candidate_sizes.append(len(candidates))
            following = []
            for candidate in candidates:
                count = 0
                for row in rows:
                    budget.charge(len(candidate))
                    count += candidate <= row
                if count >= limit:
                    budget.add(result, candidate, count)
                    following.append(candidate)
            level = following
        return result, dict(levels_=tuple(levels), candidate_counts_=tuple(candidate_sizes))


def apriori(transactions, min_support=0.5, **limits):
    return Apriori(min_support, **limits).fit(transactions).frequent_itemsets_.copy()


if __name__ == '__main__':
    support.main(Apriori)
