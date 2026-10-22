"""Exact-fill rod cutting with optional unavailable cut lengths."""
import json
import sys
import re


def rod_cutting(prices: list[int | None], length: int) -> int | None:
    """prices[i] is the price for length i+1; None means unavailable."""
    if type(length) is not int or not 0 <= length <= 10000:
        raise ValueError("length must be an integer in 0..10000")
    if len(prices) > 1000 or len(prices) * (length + 1) > 2000000:
        raise ValueError("DP work limit exceeded")
    if any(p is not None and (type(p) is not int or not -10**9 <= p <= 10**9) for p in prices):
        raise ValueError("prices must be None or integers in +/-10^9")
    best: list[int | None] = [0] + [None] * length
    for total in range(1, length + 1):
        for cut, price in enumerate(prices, 1):
            if cut <= total and price is not None and best[total - cut] is not None:
                candidate = price + best[total - cut]
                if best[total] is None or candidate > best[total]:
                    best[total] = candidate
    return best[length]


def _parse(token: str) -> int:
    if not re.fullmatch(r"[+-]?[0-9]+", token):
        raise ValueError("expected ASCII decimal integer")
    return int(token)


if __name__ == "__main__":
    try:
        tokens = sys.stdin.read().split()
        if len(tokens) < 2:
            raise ValueError("expected length, price count, prices (x for unavailable)")
        length, count = map(_parse, tokens[:2])
        if not 0 <= count <= 1000 or len(tokens) != count + 2:
            raise ValueError("invalid price count")
        prices = [None if x == "x" else _parse(x) for x in tokens[2:]]
        print(json.dumps(rod_cutting(prices, length)))
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
