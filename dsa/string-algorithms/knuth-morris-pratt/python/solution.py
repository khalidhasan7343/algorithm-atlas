"""Exact byte matching; see the canonical lesson and String contracts."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_string_support", Path(__file__).resolve().parents[2] / "string_support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def prefix_function(pattern):
    _support.checked(pattern)
    lps = [0] * len(pattern)
    for i in range(1, len(pattern)):
        j = lps[i - 1]
        while j and pattern[i] != pattern[j]:
            j = lps[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
        lps[i] = j
    return lps


def solve(text, pattern):
    _support.checked(text)
    lps = prefix_function(pattern)
    if not pattern:
        return list(range(len(text) + 1))
    result = []
    j = 0
    for i, ch in enumerate(text):
        while j and ch != pattern[j]:
            j = lps[j - 1]
        if ch == pattern[j]:
            j += 1
        if j == len(pattern):
            result.append(i - j + 1)
            j = lps[j - 1]
    return result


if __name__ == "__main__":
    _support.main(solve)
