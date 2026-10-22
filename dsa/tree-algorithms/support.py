"""Tree validation and executable support; core algorithms remain canonical."""
import importlib.util
import json
from pathlib import Path
import sys
from functools import lru_cache


def integer(value,low,high,name):
    if type(value) is not int or not low<=value<=high:
        raise ValueError(f"{name} must be an integer in [{low}, {high}]")
    return value


def values_checked(values):
    if not isinstance(values,(list,tuple)) or len(values)>10000:
        raise ValueError("expected at most 10000 values")
    return [integer(value,-10**9,10**9,"value") for value in values]


def binary_tree(values,children,root):
    values=values_checked(values);n=len(values)
    if not isinstance(children,(list,tuple)) or len(children)!=n:
        raise ValueError("one pair of children per node required")
    pairs=[];degree=[0]*n
    for pair in children:
        if not isinstance(pair,(list,tuple)) or len(pair)!=2:
            raise ValueError("two child slots per node required")
        copied=[]
        for child in pair:
            if child is not None:
                integer(child,0,n-1,"child")
                degree[child]+=1
                if degree[child]>1:raise ValueError("shared child")
            copied.append(child)
        pairs.append(tuple(copied))
    if not n:
        if root is not None:raise ValueError("empty tree requires absent root")
        return values,pairs,None
    integer(root,0,n-1,"root")
    if degree[root]!=0:raise ValueError("root has a parent")
    seen=set();stack=[root]
    while stack:
        u=stack.pop()
        if u in seen:raise ValueError("cycle")
        seen.add(u)
        stack.extend(v for v in pairs[u] if v is not None)
    if len(seen)!=n:raise ValueError("tree must be connected")
    return values,pairs,root


def rooted_tree(parents,root):
    if not isinstance(parents,(list,tuple)) or len(parents)>10000:
        raise ValueError("at most 10000 parents required")
    n=len(parents)
    if not n:
        if root is not None:raise ValueError("empty tree requires absent root")
        return [],[],[]
    integer(root,0,n-1,"root")
    children=[[] for _ in range(n)]
    for v,p in enumerate(parents):
        if v==root:
            if p is not None:raise ValueError("root parent must be absent")
        else:
            integer(p,0,n-1,"parent");children[p].append(v)
    depth=[-1]*n;depth[root]=0;stack=[root]
    while stack:
        u=stack.pop()
        for v in children[u]:
            if depth[v]!=-1:raise ValueError("cycle")
            depth[v]=depth[u]+1;stack.append(v)
    if -1 in depth:raise ValueError("disconnected or cyclic parent relation")
    return list(parents),children,depth


def operations_checked(operations):
    if not isinstance(operations,(list,tuple)) or len(operations)>1000:
        raise ValueError("at most 1000 operations required")
    return operations


def operation(op,width):
    if not isinstance(op,(list,tuple)) or len(op)!=width:
        raise ValueError("incorrect operation width")


def key_checked(key):
    return integer(key,-10**9,10**9,"key")


def ordered_solve(tree,operations):
    result=[]
    for op in operations_checked(operations):
        if not isinstance(op,(list,tuple)) or not op:raise ValueError("operation required")
        integer(op[0],0,4,"operation")
        operation(op,1 if op[0]==3 else 3 if op[0]==4 else 2)
        if op[0]==0:result.append(tree.insert(op[1]))
        elif op[0]==1:result.append(tree.erase(op[1]))
        elif op[0]==2:result.append(tree.contains(op[1]))
        elif op[0]==3:result.append(tree.keys())
        else:result.append(tree.range_query(op[1],op[2]))
    return result


@lru_cache(None)
def canonical(name):
    spec=importlib.util.spec_from_file_location('atlas_tree_'+name,Path(__file__).parent/name/'python/solution.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def main(solve):
    try:
        payload=json.load(sys.stdin)
        if not isinstance(payload,dict):raise ValueError("JSON object required")
        print(json.dumps(solve(**payload),separators=(',',':')))
    except (ValueError,TypeError,KeyError) as error:
        print('error: '+str(error),file=sys.stderr);raise SystemExit(2)
