"""Exact byte matching; see the canonical lesson and String contracts."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_string_support", Path(__file__).resolve().parents[2] / "string_support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

class Node:
    def __init__(self, start=0, end=0, suffix=-1):
        self.start,self.end,self.suffix = start,end,suffix
        self.children = {}


class SuffixTree:
    """Compressed-edge suffix insertion: quadratic time, linear structural space."""
    def __init__(self, text):
        _support.checked(text,2048)
        self.text = text
        self.symbols = list(text)+[256]
        self.nodes = [Node()]
        end = len(self.symbols)
        for suffix in range(end):
            parent,pos = 0,suffix
            while pos < end:
                ch = self.symbols[pos]
                child = self.nodes[parent].children.get(ch)
                if child is None:
                    self.nodes[parent].children[ch] = len(self.nodes)
                    self.nodes.append(Node(pos,end,suffix))
                    break
                edge = self.nodes[child]
                matched = 0
                while edge.start+matched < edge.end and self.symbols[edge.start+matched] == self.symbols[pos+matched]:
                    matched += 1
                if edge.start+matched == edge.end:
                    pos += matched
                    parent = child
                    continue
                middle = len(self.nodes)
                self.nodes.append(Node(edge.start,edge.start+matched))
                self.nodes[parent].children[ch] = middle
                edge.start += matched
                self.nodes[middle].children[self.symbols[edge.start]] = child
                leaf = len(self.nodes)
                self.nodes.append(Node(pos+matched,end,suffix))
                self.nodes[middle].children[self.symbols[pos+matched]] = leaf
                break

    def _locus(self, pattern):
        node,pos = 0,0
        while pos < len(pattern):
            child = self.nodes[node].children.get(pattern[pos])
            if child is None:
                return None
            edge = self.nodes[child]
            for i in range(edge.start,edge.end):
                if pos == len(pattern):
                    return child
                if self.symbols[i] != pattern[pos]:
                    return None
                pos += 1
            node = child
        return node

    def contains(self, pattern):
        _support.checked(pattern)
        return self._locus(pattern) is not None

    def find(self, pattern):
        _support.checked(pattern)
        if not pattern:
            return list(range(len(self.text)+1))
        node = self._locus(pattern)
        if node is None:
            return []
        result,stack = [],[node]
        while stack:
            item = self.nodes[stack.pop()]
            if item.suffix >= 0:
                result.append(item.suffix)
            stack.extend(item.children.values())
        return sorted(result)


def solve(text, pattern):
    return SuffixTree(text).find(pattern)


if __name__ == "__main__":
    _support.main(solve, "match")
