"""Exact byte matching; see the canonical lesson and String contracts."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_string_support", Path(__file__).resolve().parents[2] / "string_support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

BASE = 257
MODULUS = 1000000007


def _parameters(base, modulus):
    _support.integer(base, 1, 1000000007)
    _support.integer(modulus, 2, 1000000007)


def fingerprint(data, base=BASE, modulus=MODULUS):
    _support.checked(data)
    _parameters(base, modulus)
    value = 0
    for ch in data:
        value = (value * base + ch + 1) % modulus
    return value


def solve(text, pattern, base=BASE, modulus=MODULUS):
    _support.checked(text)
    _support.checked(pattern)
    _parameters(base, modulus)
    n, m = len(text), len(pattern)
    if not m:
        return list(range(n + 1))
    if m > n:
        return []
    high = pow(base, m - 1, modulus)
    target = fingerprint(pattern, base, modulus)
    window = fingerprint(text[:m], base, modulus)
    result = []
    for start in range(n - m + 1):
        if window == target:
            j = 0
            while j < m and text[start + j] == pattern[j]:
                j += 1
            if j == m:
                result.append(start)
        if start + m < n:
            window = ((window - (text[start] + 1) * high) * base
                      + text[start + m] + 1) % modulus
    return result


if __name__ == "__main__":
    _support.main(solve)
