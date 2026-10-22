"""euler-tour: canonical Tree implementation; contracts are in the lesson."""
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('atlas_tree_support',Path(__file__).resolve().parents[2]/'support.py')
_support=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def euler_tour(parents,root=None):
    _,children,_=_support.rooted_tree(parents,root);n=len(parents)
    order,tin,tout=[],[0]*n,[0]*n
    stack=[] if root is None else [(root,False)]
    while stack:
        u,exiting=stack.pop()
        if exiting:tout[u]=len(order)
        else:
            tin[u]=len(order);order.append(u);stack.append((u,True))
            for v in reversed(children[u]):stack.append((v,False))
    return dict(order=order,tin=tin,tout=tout)


solve=euler_tour

if __name__=="__main__":
    _support.main(solve)
