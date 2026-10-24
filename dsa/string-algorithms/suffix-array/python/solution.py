"""Exact byte matching; see the canonical lesson and String contracts."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_string_support", Path(__file__).resolve().parents[2] / "string_support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

class SuffixArray:
    def __init__(self, text):
        self.text = _support.checked(text)
        n = len(text)
        self.sa = list(range(n))
        rank = list(text)
        width = 1
        while width < n:
            def key(i):
                return rank[i], rank[i+width] if i+width < n else -1
            self.sa.sort(key=key)
            next_rank = [0]*n
            for j in range(1,n):
                next_rank[self.sa[j]] = (next_rank[self.sa[j-1]]
                                        + (key(self.sa[j]) != key(self.sa[j-1])))
            rank = next_rank
            if rank[self.sa[-1]] == n-1:
                break
            width *= 2
        inverse = [0]*n
        for j,i in enumerate(self.sa):
            inverse[i] = j
        self.lcp = [0]*n
        common = 0
        for i in range(n):
            j = inverse[i]
            if j == 0:
                common = 0
                continue
            previous = self.sa[j-1]
            while i+common < n and previous+common < n and text[i+common] == text[previous+common]:
                common += 1
            self.lcp[j] = common
            if common:
                common -= 1

    def _compare(self, start, pattern):
        j = 0
        while j < len(pattern) and start+j < len(self.text):
            if self.text[start+j] != pattern[j]:
                return -1 if self.text[start+j] < pattern[j] else 1
            j += 1
        return 0 if j == len(pattern) else -1

    def find(self, pattern):
        _support.checked(pattern)
        if not pattern:
            return list(range(len(self.text)+1))
        def bound(upper):
            low,high = 0,len(self.sa)
            while low < high:
                mid = (low+high)//2
                cmp = self._compare(self.sa[mid],pattern)
                if cmp < 0 or (upper and cmp == 0):
                    low = mid+1
                else:
                    high = mid
            return low
        left,right = bound(False),bound(True)
        return sorted(self.sa[left:right])


def solve(text, pattern):
    index = SuffixArray(text)
    return [index.sa,index.lcp,index.find(pattern)]


if __name__ == "__main__":
    _support.main(solve, "match")
