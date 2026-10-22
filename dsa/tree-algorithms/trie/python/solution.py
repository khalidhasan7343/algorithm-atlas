"""trie: canonical Tree implementation; contracts are in the lesson."""
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('atlas_tree_support',Path(__file__).resolve().parents[2]/'support.py')
_support=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

class _Node:
    def __init__(self):
        self.children={};self.terminal=False


class Trie:
    def __init__(self):
        self._root=_Node();self.size=0;self._nodes=1

    @staticmethod
    def _word(word):
        if not isinstance(word,str) or len(word)>256 or any(not 'a'<=ch<='z' for ch in word):
            raise ValueError("word must be at most 256 lowercase ASCII letters")

    def _find(self,word):
        node=self._root
        for ch in word:
            node=node.children.get(ch)
            if node is None:return None
        return node

    def contains(self,word):
        self._word(word);node=self._find(word);return node is not None and node.terminal

    def starts_with(self,prefix):
        self._word(prefix);return self._find(prefix) is not None

    def insert(self,word):
        self._word(word);node=self._root;matched=0
        for ch in word:
            if ch not in node.children:break
            node=node.children[ch];matched+=1
        if matched==len(word) and node.terminal:return False
        if self.size==10000 or self._nodes+len(word)-matched>100000:
            raise ValueError("trie resource limit")
        for ch in word[matched:]:
            child=_Node();node.children[ch]=child;node=child;self._nodes+=1
        node.terminal=True;self.size+=1;return True

    def erase(self,word):
        self._word(word);node=self._root;path=[]
        for ch in word:
            if ch not in node.children:return False
            path.append((node,ch));node=node.children[ch]
        if not node.terminal:return False
        node.terminal=False;self.size-=1
        for parent,ch in reversed(path):
            child=parent.children[ch]
            if child.terminal or child.children:break
            del parent.children[ch];self._nodes-=1
        return True


def solve(operations=()):
    tree=Trie();result=[]
    for op in _support.operations_checked(operations):
        _support.operation(op,2);_support.integer(op[0],0,3,"operation")
        result.append((tree.insert,tree.contains,tree.starts_with,tree.erase)[op[0]](op[1]))
    return result

if __name__=="__main__":
    _support.main(solve)
