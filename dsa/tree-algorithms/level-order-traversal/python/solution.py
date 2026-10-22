"""level-order-traversal: canonical Tree implementation; contracts are in the lesson."""
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('atlas_tree_support',Path(__file__).resolve().parents[2]/'support.py')
_support=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

from collections import deque


def level_order(values,children,root=None):
    _,children,root=_support.binary_tree(values,children,root)
    levels=[];queue=deque([] if root is None else [root])
    while queue:
        level=[]
        for _ in range(len(queue)):
            u=queue.popleft();level.append(u)
            for child in children[u]:
                if child is not None:queue.append(child)
        levels.append(level)
    return levels


solve=level_order

if __name__=="__main__":
    _support.main(solve)
