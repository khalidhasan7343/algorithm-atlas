"""Exact byte matching; see the canonical lesson and String contracts."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_string_support", Path(__file__).resolve().parents[2] / "string_support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

from collections import deque


class AhoCorasick:
    def __init__(self, patterns):
        if not isinstance(patterns,(list,tuple)) or len(patterns) > 256:
            raise ValueError("expected at most 256 ordered patterns")
        for pattern in patterns:
            _support.checked(pattern)
        if sum(map(len,patterns)) > 4096:
            raise ValueError("total pattern bytes exceed 4096")
        self.patterns = tuple(patterns)
        self.goto = [[-1]*256]
        self.failure = [0]
        self.output_link = [-1]
        self.terminal = [[]]
        self.depth = [0]
        for identity,pattern in enumerate(patterns):
            node = 0
            for ch in pattern:
                child = self.goto[node][ch]
                if child == -1:
                    child = len(self.goto)
                    self.goto[node][ch] = child
                    self.goto.append([-1]*256)
                    self.failure.append(0)
                    self.output_link.append(-1)
                    self.terminal.append([])
                    self.depth.append(self.depth[node]+1)
                node = child
            self.terminal[node].append(identity)
        queue = deque()
        for ch in range(256):
            child = self.goto[0][ch]
            if child == -1:
                self.goto[0][ch] = 0
            else:
                queue.append(child)
        while queue:
            node = queue.popleft()
            failure = self.failure[node]
            self.output_link[node] = (failure if failure and self.terminal[failure]
                                      else self.output_link[failure])
            for ch in range(256):
                child = self.goto[node][ch]
                if child == -1:
                    self.goto[node][ch] = self.goto[failure][ch]
                else:
                    self.failure[child] = self.goto[failure][ch]
                    queue.append(child)

    def find(self, text):
        _support.checked(text)
        result = [[0,identity,0] for identity in self.terminal[0]]
        state = 0
        for end,ch in enumerate(text,1):
            state = self.goto[state][ch]
            output = state
            while output > 0:
                for identity in self.terminal[output]:
                    result.append([end,identity,end-len(self.patterns[identity])])
                output = self.output_link[output]
            for identity in self.terminal[0]:
                result.append([end,identity,end])
        return result


def solve(text, patterns):
    return AhoCorasick(patterns).find(text)


if __name__ == "__main__":
    _support.main(solve, "multi")
