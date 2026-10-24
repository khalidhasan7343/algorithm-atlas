"""Exact byte matching; see the canonical lesson and String contracts."""
import importlib.util
from pathlib import Path
_spec = importlib.util.spec_from_file_location("atlas_string_support", Path(__file__).resolve().parents[2] / "string_support.py")
_support = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_support)

def solve(text, pattern):
    _support.checked(text)
    _support.checked(pattern)
    result = []
    for start in range(len(text) - len(pattern) + 1):
        j = 0
        while j < len(pattern) and text[start + j] == pattern[j]:
            j += 1
        if j == len(pattern):
            result.append(start)
    return result


if __name__ == "__main__":
    _support.main(solve)
