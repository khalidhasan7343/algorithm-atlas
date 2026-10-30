"""Vertical transaction-ID intersection mining with bounded explicit DFS frames."""
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

def vertical_index(rows, items, budget):
    index = {item:set() for item in items}
    for tid,row in enumerate(rows):
        budget.charge(1+len(row))
        for item in row:
            index[item].add(tid)
    return {item:frozenset(tids) for item,tids in index.items()}


class Eclat(support.Miner):
    def _mine(self, rows, items, limit, budget):
        vertical = vertical_index(rows, items, budget)
        extensions = [(item,vertical[item]) for item in items if len(vertical[item]) >= limit]
        result, intersections = {}, 0
        frames = [(frozenset(),extensions,0)]
        while frames:
            prefix,group,index = frames.pop()
            if index == len(group):
                continue
            frames.append((prefix,group,index+1))
            item,tids = group[index]
            pattern = prefix|{item}
            budget.charge()
            budget.add(result,pattern,len(tids))
            following = []
            for other,other_tids in group[index+1:]:
                budget.charge(1+min(len(tids),len(other_tids)))
                common = tids & other_tids
                intersections += 1
                if len(common) >= limit:
                    budget.collection(len(following)+1)
                    following.append((other,common))
            if following:
                frames.append((pattern,following,0))
        return result,dict(vertical_=vertical,intersection_count_=intersections)


def eclat(transactions,min_support=0.5,**limits):
    return Eclat(min_support,**limits).fit(transactions).frequent_itemsets_.copy()


if __name__ == '__main__':
    support.main(Eclat)
