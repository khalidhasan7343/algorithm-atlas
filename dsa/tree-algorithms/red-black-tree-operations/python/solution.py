"""red-black-tree-operations: canonical Tree implementation; contracts are in the lesson."""
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('atlas_tree_support',Path(__file__).resolve().parents[2]/'support.py')
_support=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

class Node:
    def __init__(self,key):
        self.key=key;self.red=True;self.left=None;self.right=None


class RedBlackTree:
    """Left-leaning red-black set; None leaves are black."""
    def __init__(self):
        self.root=None;self.size=0;self.stats=[0,0,0,0,0]

    @staticmethod
    def _red(node):return node is not None and node.red

    def _rotate_left(self,node):
        pivot=node.right;node.right=pivot.left;pivot.left=node
        pivot.red=node.red;node.red=True;self.stats[0]+=1;return pivot

    def _rotate_right(self,node):
        pivot=node.left;node.left=pivot.right;pivot.right=node
        pivot.red=node.red;node.red=True;self.stats[1]+=1;return pivot

    def _flip(self,node):
        node.red=not node.red
        if node.left:node.left.red=not node.left.red
        if node.right:node.right.red=not node.right.red
        self.stats[2]+=1

    def _fix(self,node):
        if self._red(node.right):node=self._rotate_left(node)
        if self._red(node.left) and self._red(node.left.left):node=self._rotate_right(node)
        if self._red(node.left) and self._red(node.right):self._flip(node)
        return node

    def _move_red_left(self,node):
        self.stats[3]+=1;self._flip(node)
        if node.right and self._red(node.right.left):
            node.right=self._rotate_right(node.right);node=self._rotate_left(node);self._flip(node)
        return node

    def _move_red_right(self,node):
        self.stats[4]+=1;self._flip(node)
        if node.left and self._red(node.left.left):node=self._rotate_right(node);self._flip(node)
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
        if self._red(node.right) and not self._red(node.left):node=self._rotate_left(node)
        if self._red(node.left) and self._red(node.left.left):node=self._rotate_right(node)
        if self._red(node.left) and self._red(node.right):self._flip(node)
        return node

    def insert(self,key):
        _support.key_checked(key)
        if self.contains(key):return False
        if self.size==1000:raise ValueError("set capacity")
        self.root=self._insert(self.root,key);self.root.red=False;self.size+=1;return True

    def _delete_min(self,node):
        if node.left is None:return None
        if not self._red(node.left) and not self._red(node.left.left):node=self._move_red_left(node)
        node.left=self._delete_min(node.left);return self._fix(node)

    def _erase(self,node,key):
        if key<node.key:
            if not self._red(node.left) and not self._red(node.left.left if node.left else None):node=self._move_red_left(node)
            node.left=self._erase(node.left,key)
        else:
            if self._red(node.left):node=self._rotate_right(node)
            if key==node.key and node.right is None:return None
            if not self._red(node.right) and not self._red(node.right.left if node.right else None):node=self._move_red_right(node)
            if key==node.key:
                successor=node.right
                while successor.left:successor=successor.left
                node.key=successor.key;node.right=self._delete_min(node.right)
            else:node.right=self._erase(node.right,key)
        return self._fix(node)

    def erase(self,key):
        _support.key_checked(key)
        if not self.contains(key):return False
        if not self._red(self.root.left) and not self._red(self.root.right):self.root.red=True
        self.root=self._erase(self.root,key)
        if self.root:self.root.red=False
        self.size-=1;return True

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


def solve(operations=()):return _support.ordered_solve(RedBlackTree(),operations)

if __name__=="__main__":
    _support.main(solve)
