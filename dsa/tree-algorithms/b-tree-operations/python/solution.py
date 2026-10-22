"""b-tree-operations: canonical Tree implementation; contracts are in the lesson."""
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('atlas_tree_support',Path(__file__).resolve().parents[2]/'support.py')
_support=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

from bisect import bisect_left

class Node:
    def __init__(self,leaf=True):
        self.leaf=leaf;self.keys=[];self.children=[]

class BTree:
    def __init__(self,degree=2):
        self.degree=_support.integer(degree,2,8,'degree');self.root=Node();self.size=0
        self.stats=[0]*7 # splits, borrow left/right, merge, contraction, predecessor/successor
    def contains(self,key):
        key=_support.key_checked(key);node=self.root
        while True:
            i=bisect_left(node.keys,key)
            if i<len(node.keys) and node.keys[i]==key:return True
            if node.leaf:return False
            node=node.children[i]
    def _split(self,parent,i):
        t=self.degree;left=parent.children[i];right=Node(left.leaf);middle=left.keys[t-1]
        right.keys=left.keys[t:];left.keys=left.keys[:t-1]
        if not left.leaf:right.children=left.children[t:];left.children=left.children[:t]
        parent.keys.insert(i,middle);parent.children.insert(i+1,right);self.stats[0]+=1
    def _insert(self,node,key):
        i=bisect_left(node.keys,key)
        if node.leaf:node.keys.insert(i,key);return
        if len(node.children[i].keys)==2*self.degree-1:
            self._split(node,i)
            if key>node.keys[i]:i+=1
        self._insert(node.children[i],key)
    def insert(self,key):
        key=_support.key_checked(key)
        if self.contains(key):return False
        if self.size==1000:raise ValueError('set capacity')
        if len(self.root.keys)==2*self.degree-1:
            root=Node(False);root.children=[self.root];self.root=root;self._split(root,0)
        self._insert(self.root,key);self.size+=1;return True
    def _merge(self,parent,i):
        left=parent.children[i];right=parent.children.pop(i+1)
        left.keys.append(parent.keys.pop(i));left.keys.extend(right.keys)
        if not left.leaf:left.children.extend(right.children)
        self.stats[3]+=1
    def _strengthen(self,parent,i):
        t=self.degree;child=parent.children[i]
        if i>0 and len(parent.children[i-1].keys)>=t:
            left=parent.children[i-1];child.keys.insert(0,parent.keys[i-1]);parent.keys[i-1]=left.keys.pop()
            if not child.leaf:child.children.insert(0,left.children.pop())
            self.stats[1]+=1
        elif i<len(parent.keys) and len(parent.children[i+1].keys)>=t:
            right=parent.children[i+1];child.keys.append(parent.keys[i]);parent.keys[i]=right.keys.pop(0)
            if not child.leaf:child.children.append(right.children.pop(0))
            self.stats[2]+=1
        else:
            if i==len(parent.keys):i-=1
            self._merge(parent,i)
        return i
    def _erase(self,node,key):
        i=bisect_left(node.keys,key)
        if i<len(node.keys) and node.keys[i]==key:
            if node.leaf:node.keys.pop(i)
            elif len(node.children[i].keys)>=self.degree:
                pred=node.children[i]
                while not pred.leaf:pred=pred.children[-1]
                replacement=pred.keys[-1];node.keys[i]=replacement;self.stats[5]+=1;self._erase(node.children[i],replacement)
            elif len(node.children[i+1].keys)>=self.degree:
                successor=node.children[i+1]
                while not successor.leaf:successor=successor.children[0]
                replacement=successor.keys[0];node.keys[i]=replacement;self.stats[6]+=1;self._erase(node.children[i+1],replacement)
            else:self._merge(node,i);self._erase(node.children[i],key)
        else:
            if len(node.children[i].keys)==self.degree-1:i=self._strengthen(node,i)
            self._erase(node.children[i],key)
    def erase(self,key):
        key=_support.key_checked(key)
        if not self.contains(key):return False
        self._erase(self.root,key);self.size-=1
        if not self.root.leaf and not self.root.keys:self.root=self.root.children[0];self.stats[4]+=1
        return True
    def keys(self):
        result=[]
        def visit(node):
            for i,key in enumerate(node.keys):
                if not node.leaf:visit(node.children[i])
                result.append(key)
            if not node.leaf:visit(node.children[-1])
        visit(self.root);return result
    def range_query(self,low,high):
        low=_support.key_checked(low);high=_support.key_checked(high)
        if low>high:raise ValueError('invalid range')
        result=[]
        def visit(node):
            i=bisect_left(node.keys,low)
            if not node.leaf:visit(node.children[i])
            while i<len(node.keys) and node.keys[i]<high:
                result.append(node.keys[i]);i+=1
                if not node.leaf:visit(node.children[i])
        if low<high:visit(self.root)
        return result

def solve(operations=(),degree=2):return _support.ordered_solve(BTree(degree),operations)


if __name__=="__main__":
    _support.main(solve)
