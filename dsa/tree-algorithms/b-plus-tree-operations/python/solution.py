"""b-plus-tree-operations: canonical Tree implementation; contracts are in the lesson."""
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('atlas_tree_support',Path(__file__).resolve().parents[2]/'support.py')
_support=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

from bisect import bisect_left,bisect_right

class Node:
    def __init__(self,leaf=True):
        self.leaf=leaf;self.keys=[];self.children=[];self.next=None;self.minimum=None

class BPlusTree:
    def __init__(self,degree=2):
        self.degree=_support.integer(degree,2,8,'degree');self.root=Node();self.size=0
        self.stats=[0]*6 # leaf/internal splits, borrow left/right, merge, root contraction
    @staticmethod
    def _refresh(node):
        if node.leaf:node.minimum=node.keys[0] if node.keys else None
        else:node.minimum=node.children[0].minimum;node.keys=[child.minimum for child in node.children[1:]]
    def _leaf(self,key):
        node=self.root
        while not node.leaf:node=node.children[bisect_right(node.keys,key)]
        return node
    def contains(self,key):
        key=_support.key_checked(key);node=self._leaf(key);i=bisect_left(node.keys,key)
        return i<len(node.keys) and node.keys[i]==key
    def _insert(self,node,key):
        if node.leaf:
            node.keys.insert(bisect_left(node.keys,key),key);self._refresh(node)
            if len(node.keys)<2*self.degree:return None
            right=Node();right.keys=node.keys[self.degree:];node.keys=node.keys[:self.degree]
            right.next=node.next;node.next=right;self._refresh(node);self._refresh(right);self.stats[0]+=1;return right
        i=bisect_right(node.keys,key);right=self._insert(node.children[i],key)
        if right is not None:node.children.insert(i+1,right)
        self._refresh(node)
        if len(node.children)<=2*self.degree:return None
        right=Node(False);right.children=node.children[self.degree:];node.children=node.children[:self.degree]
        self._refresh(node);self._refresh(right);self.stats[1]+=1;return right
    def insert(self,key):
        key=_support.key_checked(key)
        if self.contains(key):return False
        if self.size==1000:raise ValueError('set capacity')
        right=self._insert(self.root,key)
        if right is not None:
            root=Node(False);root.children=[self.root,right];self._refresh(root);self.root=root
        self.size+=1;return True
    def _underfull(self,node):return len(node.keys)<self.degree-1 if node.leaf else len(node.children)<self.degree
    def _spare(self,node):return len(node.keys)>self.degree-1 if node.leaf else len(node.children)>self.degree
    def _repair(self,parent,i):
        child=parent.children[i]
        if i>0 and self._spare(parent.children[i-1]):
            left=parent.children[i-1]
            if child.leaf:child.keys.insert(0,left.keys.pop())
            else:child.children.insert(0,left.children.pop())
            self._refresh(left);self._refresh(child);self.stats[2]+=1
        elif i+1<len(parent.children) and self._spare(parent.children[i+1]):
            right=parent.children[i+1]
            if child.leaf:child.keys.append(right.keys.pop(0))
            else:child.children.append(right.children.pop(0))
            self._refresh(right);self._refresh(child);self.stats[3]+=1
        else:
            if i==len(parent.children)-1:i-=1
            left=parent.children[i];right=parent.children.pop(i+1)
            if left.leaf:left.keys.extend(right.keys);left.next=right.next
            else:left.children.extend(right.children)
            self._refresh(left);self.stats[4]+=1
        self._refresh(parent)
    def _erase(self,node,key):
        if node.leaf:node.keys.pop(bisect_left(node.keys,key));self._refresh(node);return
        i=bisect_right(node.keys,key);self._erase(node.children[i],key)
        if self._underfull(node.children[i]):self._repair(node,i)
        self._refresh(node)
    def erase(self,key):
        key=_support.key_checked(key)
        if not self.contains(key):return False
        self._erase(self.root,key);self.size-=1
        if not self.root.leaf and len(self.root.children)==1:self.root=self.root.children[0];self.stats[5]+=1
        return True
    def keys(self):
        node=self.root
        while not node.leaf:node=node.children[0]
        result=[]
        while node is not None:result.extend(node.keys);node=node.next
        return result
    def range_query(self,low,high):
        low=_support.key_checked(low);high=_support.key_checked(high)
        if low>high:raise ValueError('invalid range')
        result=[];node=self._leaf(low);i=bisect_left(node.keys,low)
        while node is not None:
            while i<len(node.keys):
                if node.keys[i]>=high:return result
                result.append(node.keys[i]);i+=1
            node=node.next;i=0
        return result

def solve(operations=(),degree=2):return _support.ordered_solve(BPlusTree(degree),operations)


if __name__=="__main__":
    _support.main(solve)
