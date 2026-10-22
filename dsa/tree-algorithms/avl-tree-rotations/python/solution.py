"""avl-tree-rotations: canonical Tree implementation; contracts are in the lesson."""
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('atlas_tree_support',Path(__file__).resolve().parents[2]/'support.py')
_support=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

class Node:
    def __init__(self,key):
        self.key=key;self.height=1;self.left=None;self.right=None


class AVLTree:
    def __init__(self):
        self.root=None;self.size=0;self.rotations=[0,0,0,0]  # LL, RR, LR, RL

    @staticmethod
    def _height(node):return node.height if node else 0

    def _refresh(self,node):
        node.height=1+max(self._height(node.left),self._height(node.right))

    def _rotate_left(self,node):
        pivot=node.right;node.right=pivot.left;pivot.left=node
        self._refresh(node);self._refresh(pivot);return pivot

    def _rotate_right(self,node):
        pivot=node.left;node.left=pivot.right;pivot.right=node
        self._refresh(node);self._refresh(pivot);return pivot

    def _balance(self,node):
        self._refresh(node)
        difference=self._height(node.left)-self._height(node.right)
        if difference>1:
            if self._height(node.left.left)<self._height(node.left.right):
                node.left=self._rotate_left(node.left);self.rotations[2]+=1
            else:self.rotations[0]+=1
            return self._rotate_right(node)
        if difference<-1:
            if self._height(node.right.right)<self._height(node.right.left):
                node.right=self._rotate_right(node.right);self.rotations[3]+=1
            else:self.rotations[1]+=1
            return self._rotate_left(node)
        return node

    def contains(self,key):
        _support.key_checked(key);node=self.root
        while node:
            if key==node.key:return True
            node=node.left if key<node.key else node.right
        return False

    def _insert(self,node,key):
        if node is None:return Node(key)
        if key<node.key:node.left=self._insert(node.left,key)
        else:node.right=self._insert(node.right,key)
        return self._balance(node)

    def insert(self,key):
        _support.key_checked(key)
        if self.contains(key):return False
        if self.size==1000:raise ValueError("set capacity")
        self.root=self._insert(self.root,key);self.size+=1;return True

    def _erase(self,node,key):
        if key<node.key:node.left=self._erase(node.left,key)
        elif key>node.key:node.right=self._erase(node.right,key)
        else:
            if node.left is None:return node.right
            if node.right is None:return node.left
            successor=node.right
            while successor.left:successor=successor.left
            node.key=successor.key;node.right=self._erase(node.right,successor.key)
        return self._balance(node)

    def erase(self,key):
        _support.key_checked(key)
        if not self.contains(key):return False
        self.root=self._erase(self.root,key);self.size-=1;return True

    def keys(self):
        result=[];stack=[];node=self.root
        while stack or node:
            while node:stack.append(node);node=node.left
            node=stack.pop();result.append(node.key);node=node.right
        return result

    def range_query(self,low,high):
        _support.key_checked(low);_support.key_checked(high)
        if low>high:raise ValueError("invalid range")
        result=[]
        def visit(node):
            if node is None:return
            if node.key>=low:visit(node.left)
            if low<=node.key<high:result.append(node.key)
            if node.key<high:visit(node.right)
        visit(self.root);return result


def solve(operations=()):return _support.ordered_solve(AVLTree(),operations)

if __name__=="__main__":
    _support.main(solve)
