"""Direct divide-and-conquer implementation with exact integer contracts."""
from collections.abc import Sequence
import json
import re
import sys


MAX_SIZE = 128
ENTRY_LIMIT = 1000
BASE_THRESHOLD = 2


def strassen_multiply(a: Sequence[Sequence[int]],
                      b: Sequence[Sequence[int]]) -> list[list[int]]:
    """Exact square matrix product; pad odd/non-power-of-two sizes, crop output.

    Same-size square matrices only; n<=128, entries in [-1000,1000].
    Empty times empty gives []; cubic fallback only for blocks <=2.
    """
    n = len(a)
    if len(b) != n or n > MAX_SIZE:
        raise ValueError("same-size square matrices with n<=128 required")
    for matrix in (a, b):
        if any(len(row) != n for row in matrix):
            raise ValueError("matrices must be square")
        for row in matrix:
            for value in row:
                if type(value) is not int:
                    raise TypeError("entries must be native ints")
                if abs(value) > ENTRY_LIMIT:
                    raise ValueError("entries must lie in [-1000,1000]")
    if n == 0:
        return []
    size = 1
    while size < n:
        size *= 2
    pa = [[a[r][c] if r < n and c < n else 0 for c in range(size)] for r in range(size)]
    pb = [[b[r][c] if r < n and c < n else 0 for c in range(size)] for r in range(size)]

    def combine(x, y, sign=1):
        return [[u + sign*v for u, v in zip(rx, ry)] for rx, ry in zip(x, y)]

    def split(x):
        half = len(x) // 2
        return ([row[:half] for row in x[:half]], [row[half:] for row in x[:half]],
                [row[:half] for row in x[half:]], [row[half:] for row in x[half:]])

    def multiply(x, y):
        width = len(x)
        if width <= BASE_THRESHOLD:
            return [[sum(x[r][k]*y[k][c] for k in range(width))
                     for c in range(width)] for r in range(width)]
        aa, ab, ac, ad = split(x)
        ba, bb, bc, bd = split(y)
        m1 = multiply(combine(aa, ad), combine(ba, bd))
        m2 = multiply(combine(ac, ad), ba)
        m3 = multiply(aa, combine(bb, bd, -1))
        m4 = multiply(ad, combine(bc, ba, -1))
        m5 = multiply(combine(aa, ab), bd)
        m6 = multiply(combine(ac, aa, -1), combine(ba, bb))
        m7 = multiply(combine(ab, ad, -1), combine(bc, bd))
        ca = combine(combine(combine(m1, m4), m5, -1), m7)
        cb = combine(m3, m5)
        cc = combine(m2, m4)
        cd = combine(combine(combine(m1, m2, -1), m3), m6)
        half = width // 2
        return [ca[r] + cb[r] for r in range(half)] + [cc[r] + cd[r] for r in range(half)]

    product = multiply(pa, pb)
    return [row[:n] for row in product[:n]]


def main() -> int:
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    tokens = sys.stdin.read().split()
    try:
        if any(re.fullmatch(r"[+-]?[0-9]+", token) is None for token in tokens):
            raise ValueError("expected ASCII signed decimal integers")
        numbers = [int(token) for token in tokens]
        if not numbers or not 0 <= numbers[0] <= MAX_SIZE:
            raise ValueError("n in 0..128 required")
        n = numbers[0]
        if len(numbers) != 1 + 2*n*n:
            raise ValueError("exactly two square matrices required")
        a = [numbers[1 + r*n:1 + (r + 1)*n] for r in range(n)]
        b = [numbers[1 + n*n + r*n:1 + n*n + (r + 1)*n] for r in range(n)]
        result = strassen_multiply(a, b)
        print(json.dumps(result, separators=(",", ":")))
    except (ValueError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
