"""inorder-traversal: canonical Tree implementation; contracts are in the lesson."""
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('atlas_tree_support',Path(__file__).resolve().parents[2]/'support.py')
_support=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def inorder(values,children,root=None):
    _,children,root=_support.binary_tree(values,children,root)
    result,stack=[],[]
    current=root
    while stack or current is not None:
        while current is not None:
            stack.append(current);current=children[current][0]
        current=stack.pop();result.append(current);current=children[current][1]
    return result


solve=inorder

if __name__=="__main__":
    _support.main(solve)
