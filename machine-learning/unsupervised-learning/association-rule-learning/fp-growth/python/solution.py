"""FP-tree prefix compression and weighted conditional pattern growth, from scratch."""
from dataclasses import dataclass,field
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

@dataclass(eq=False,repr=False,slots=True)
class Node:
    item: object
    count: int
    parent: object = None
    children: dict = field(default_factory=dict)
    next: object = None


@dataclass(slots=True)
class Header:
    count: int
    head: object = None
    tail: object = None


@dataclass(slots=True)
class Tree:
    root: Node
    header: dict
    rank: dict
    node_count: int


def build_tree(weighted_paths, minimum, budget):
    """Internal binary weighted paths; threshold stays in original count units."""
    frequencies = {}
    for path,weight in weighted_paths:
        budget.charge(1+len(path))
        for item in path:
            frequencies[item] = frequencies.get(item,0)+weight
    frequent = sorted((item for item,count in frequencies.items() if count>=minimum),
                      key=lambda item:(-frequencies[item],item))
    rank = {item:index for index,item in enumerate(frequent)}
    header = {item:Header(frequencies[item]) for item in frequent}
    root = Node(None,0)
    nodes = 0
    for path,weight in weighted_paths:
        root.count += weight
        ordered = sorted((item for item in path if item in rank),key=rank.__getitem__)
        current = root
        budget.charge(1+len(path))
        for item in ordered:
            child = current.children.get(item)
            if child is None:
                budget.collection(nodes+1)
                child = Node(item,0,current)
                current.children[item] = child
                entry = header[item]
                if entry.tail is None:
                    entry.head = child
                else:
                    entry.tail.next = child
                entry.tail = child
                nodes += 1
            child.count += weight
            current = child
    return Tree(root,header,rank,nodes)


def conditional_base(tree,item,budget):
    result = []
    node = tree.header[item].head
    while node is not None:
        budget.charge()
        ancestor = node.parent
        prefix = []
        while ancestor.item is not None:
            budget.charge()
            prefix.append(ancestor.item)
            ancestor = ancestor.parent
        if prefix:
            budget.collection(len(result)+1)
            result.append((tuple(reversed(prefix)),node.count))
        node = node.next
    return result


def mining_order(tree):
    return sorted(tree.header,key=lambda item:(tree.header[item].count,item))


class FPGrowth(support.Miner):
    def _mine(self,rows,items,limit,budget):
        weighted = [(tuple(sorted(row)),1) for row in rows]
        tree = build_tree(weighted,limit,budget)
        result,conditional_trees,max_depth = {},0,0
        frames = [(frozenset(),tree,iter(mining_order(tree)))]
        while frames:
            prefix,current,remaining = frames[-1]
            try:
                item = next(remaining)
            except StopIteration:
                frames.pop()
                continue
            budget.charge()
            pattern = prefix|{item}
            budget.add(result,pattern,current.header[item].count)
            max_depth = max(max_depth,len(pattern))
            base = conditional_base(current,item,budget)
            if base:
                child = build_tree(base,limit,budget)
                conditional_trees += 1
                if child.header:
                    frames.append((pattern,child,iter(mining_order(child))))
        return result,dict(tree_=tree,conditional_tree_count_=conditional_trees,max_depth_=max_depth)


def fp_growth(transactions,min_support=0.5,**limits):
    return FPGrowth(min_support,**limits).fit(transactions).frequent_itemsets_.copy()


if __name__ == '__main__':
    support.main(FPGrowth)
