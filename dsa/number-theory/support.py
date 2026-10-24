"""Shared bounded integer contracts and executable transport; no algorithm."""
import importlib.util
import json
from pathlib import Path
import re
import sys

MIN64, MAX64 = -(2**63), 2**63-1


def bounded(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"expected integer in {low}..{high}")
    return value


def operand(value):
    return bounded(value, -10**9, 10**9)


def load(name):
    path = Path(__file__).parent / name / "python/solution.py"
    spec = importlib.util.spec_from_file_location("number_"+name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(solve, arity):
    try:
        tokens = sys.stdin.read().split()
        if len(tokens) != arity or any(
            len(token) > 20 or re.fullmatch(r"[+-]?[0-9]+", token) is None
            for token in tokens
        ):
            raise ValueError("incorrect decimal input arity or token")
        values = [bounded(int(token), MIN64, MAX64) for token in tokens]
        print(json.dumps(solve(*values), separators=(",", ":")))
    except (ValueError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
