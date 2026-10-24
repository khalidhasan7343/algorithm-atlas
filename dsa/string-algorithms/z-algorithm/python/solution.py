"""Exact byte matching; see the canonical lesson and String contracts."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_string_support", Path(__file__).resolve().parents[2] / "string_support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def _z(values):
    n = len(values)
    z = [0] * n
    left = right = 0  # known box [left,right)
    for i in range(1,n):
        if i < right:
            z[i] = min(right-i,z[i-left])
        while i+z[i] < n and values[z[i]] == values[i+z[i]]:
            z[i] += 1
        if i+z[i] > right:
            left,right = i,i+z[i]
    return z


def z_array(text):
    _support.checked(text)
    return _z(text)


def solve(text, pattern):
    _support.checked(text)
    _support.checked(pattern)
    if not pattern:
        return list(range(len(text)+1))
    values = list(pattern)+[256]+list(text)
    z = _z(values)
    offset = len(pattern)+1
    return [i-offset for i in range(offset,len(values)) if z[i] >= len(pattern)]


if __name__ == "__main__":
    _support.main(solve, "match")
