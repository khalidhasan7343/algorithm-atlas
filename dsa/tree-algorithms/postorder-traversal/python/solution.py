"""postorder-traversal: canonical Tree implementation; contracts are in the lesson."""
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('atlas_tree_support',Path(__file__).resolve().parents[2]/'support.py')
_support=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def postorder(values,children,root=None):
    _,children,root=_support.binary_tree(values,children,root)
    result=[];stack=[] if root is None else [(root,False)]
    while stack:
        u,returning=stack.pop()
        if returning:result.append(u)
        else:
            stack.append((u,True));left,right=children[u]
            if right is not None:stack.append((right,False))
            if left is not None:stack.append((left,False))
    return result


solve=postorder

if __name__=="__main__":
    _support.main(solve)
