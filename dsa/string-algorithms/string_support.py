"""Byte contracts and executable transport; no algorithm logic."""
import json
import re
import sys

MAX_LENGTH = 10000


def checked(value, limit=MAX_LENGTH):
    if not isinstance(value, bytes) or len(value) > limit:
        raise ValueError(f"expected bytes of length at most {limit}")
    return value


def integer(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"expected integer in {low}..{high}")
    return value


def decode(token):
    if token == "-":
        return b""
    if not re.fullmatch(r"(?:[0-9a-fA-F]{2})+", token):
        raise ValueError("expected even-length hex token or -")
    if len(token) > 2 * MAX_LENGTH:
        raise ValueError("hex string too long")
    return bytes.fromhex(token)


def main(solve, kind="match"):
    try:
        tokens = sys.stdin.read().split()
        if kind == "palindrome":
            if len(tokens) != 1:
                raise ValueError("expected text")
            result = solve(decode(tokens[0]))
        elif kind == "multi":
            if len(tokens) < 2 or not re.fullmatch(r"[0-9]+", tokens[1]):
                raise ValueError("expected text and pattern count")
            count = integer(int(tokens[1]), 0, 256)
            if len(tokens) != count + 2:
                raise ValueError("incorrect pattern count")
            result = solve(decode(tokens[0]), [decode(t) for t in tokens[2:]])
        else:
            if len(tokens) != 2:
                raise ValueError("expected text and pattern")
            result = solve(decode(tokens[0]), decode(tokens[1]))
        print(json.dumps(result, separators=(",", ":")))
    except (ValueError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
