"""Exact byte matching; see the canonical lesson and String contracts."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_string_support", Path(__file__).resolve().parents[2] / "string_support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def bad_character(pattern):
    _support.checked(pattern)
    last = [-1] * 256
    for i,ch in enumerate(pattern):
        last[ch] = i
    return last


def good_suffix(pattern):
    _support.checked(pattern)
    m = len(pattern)
    shift = [0] * (m+1)
    border = [0] * (m+1)
    i,j = m,m+1
    border[i] = j
    while i > 0:
        while j <= m and pattern[i-1] != pattern[j-1]:
            if shift[j] == 0:
                shift[j] = j-i
            j = border[j]
        i,j = i-1,j-1
        border[i] = j
    j = border[0]
    for i in range(m+1):
        if shift[i] == 0:
            shift[i] = j
        if i == j:
            j = border[j]
    return shift


def solve(text, pattern):
    _support.checked(text)
    _support.checked(pattern)
    n,m = len(text),len(pattern)
    if not m:
        return list(range(n+1))
    last,good = bad_character(pattern),good_suffix(pattern)
    result = []
    start = 0
    while start <= n-m:
        j = m-1
        while j >= 0 and pattern[j] == text[start+j]:
            j -= 1
        if j < 0:
            result.append(start)
            start += good[0]
        else:
            start += max(1,j-last[text[start+j]],good[j+1])
    return result


if __name__ == "__main__":
    _support.main(solve, "match")
