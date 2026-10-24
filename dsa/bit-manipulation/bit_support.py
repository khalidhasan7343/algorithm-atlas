"""Shared numeric validation and decimal/JSON transport; no bit algorithm."""
import json
import re
import sys

MIN_VALUE = -(1 << 31)
MAX_VALUE = (1 << 31) - 1
MASK = (1 << 32) - 1


def integer(value: int) -> int:
    if type(value) is not int or not MIN_VALUE <= value <= MAX_VALUE:
        raise ValueError("expected a signed 32-bit integer")
    return value


def sequence(values, limit=10000):
    if not isinstance(values, (list, tuple)) or len(values) > limit:
        raise ValueError(f"expected list/tuple with at most {limit} values")
    for value in values:
        integer(value)
    return values


def paired(values, singleton_count):
    sequence(values)
    if len(values) < singleton_count or len(values) % 2 != singleton_count % 2:
        raise ValueError("invalid size for singleton/pair contract")
    frequency = {}
    for value in values:
        frequency[value] = frequency.get(value, 0) + 1
    if sum(count == 1 for count in frequency.values()) != singleton_count or any(
        count not in (1, 2) for count in frequency.values()
    ):
        raise ValueError("expected the documented number of singletons and exact pairs")


def signed(word: int) -> int:
    return word if word < 1 << 31 else word - (1 << 32)


def main(solve, scalar=False, limit=10000):
    try:
        tokens = sys.stdin.read().split()
        if len(tokens) > (1 if scalar else limit):
            raise ValueError("too many values")
        if any(len(t) > 11 or re.fullmatch(r"[+-]?[0-9]+", t) is None for t in tokens):
            raise ValueError("expected signed decimal tokens of at most 11 characters")
        values = [integer(int(token, 10)) for token in tokens]
        if scalar:
            if len(values) != 1:
                raise ValueError("expected exactly one integer")
            result = solve(values[0])
        else:
            result = solve(values)
        print(json.dumps(result, separators=(",", ":")))
    except (ValueError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
