"""preorder-traversal: canonical Tree implementation; contracts are in the lesson."""
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('atlas_tree_support',Path(__file__).resolve().parents[2]/'support.py')
_support=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def preorder(values,children,root=None):
    _,children,root=_support.binary_tree(values,children,root)
    result=[];stack=[] if root is None else [root]
    while stack:
        u=stack.pop();result.append(u)
        left,right=children[u]
        if right is not None:stack.append(right)
        if left is not None:stack.append(left)
    return result


solve=preorder

if __name__=="__main__":
    _support.main(solve)
