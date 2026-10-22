"""Direct divide-and-conquer implementation with exact integer contracts."""
from collections.abc import Sequence
import json
import re
import sys


def maximum_subarray(values: Sequence[int]) -> tuple[int, int, int] | None:
    """Return (sum, start, end-exclusive), or None for empty input.

    Maximize sum, then minimize start, then end. No empty subarray competes
    with nonempty answers. Values are read only; Python sums are exact.
    """
    if any(type(value) is not int for value in values):
        raise TypeError("values must contain native ints")
    if not values:
        return None

    def better(a, b):
        return a if (-a[0], a[1], a[2]) < (-b[0], b[1], b[2]) else b

    def solve(lo: int, hi: int) -> tuple[int, int, int]:
        if hi - lo == 1:
            return values[lo], lo, hi
        mid = lo + (hi - lo) // 2
        left, right = solve(lo, mid), solve(mid, hi)
        total = 0
        suffix = (values[mid - 1], mid - 1, mid)
        for index in range(mid - 1, lo - 1, -1):
            total += values[index]
            suffix = better(suffix, (total, index, mid))
        total = 0
        prefix = (values[mid], mid, mid + 1)
        for index in range(mid, hi):
            total += values[index]
            prefix = better(prefix, (total, mid, index + 1))
        cross = (suffix[0] + prefix[0], suffix[1], prefix[2])
        return better(better(left, right), cross)

    return solve(0, len(values))


def main() -> int:
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    tokens = sys.stdin.read().split()
    try:
        if any(re.fullmatch(r"[+-]?[0-9]+", token) is None for token in tokens):
            raise ValueError("expected ASCII signed decimal integers")
        numbers = [int(token) for token in tokens]
        answer = maximum_subarray(numbers)
        result = None if answer is None else [str(answer[0]), answer[1], answer[2]]
        print(json.dumps(result, separators=(",", ":")))
    except (ValueError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
