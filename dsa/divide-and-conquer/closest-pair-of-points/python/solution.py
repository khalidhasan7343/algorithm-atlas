"""Direct divide-and-conquer implementation with exact integer contracts."""
from collections.abc import Sequence
import json
import re
import sys


COORDINATE_LIMIT = 10**9


def closest_pair(points: Sequence[Sequence[int]]) -> tuple[int, int, int] | None:
    """Return (squared distance, first index, second index), lexicographically min.

    Points are integer coordinate pairs in [-10**9,10**9]. Preserve caller
    order/storage. Distinct positions with identical coordinates are valid.
    """
    ordered = []
    for index, point in enumerate(points):
        if len(point) != 2:
            raise ValueError("each point must have two coordinates")
        x, y = point
        if type(x) is not int or type(y) is not int:
            raise TypeError("coordinates must be native ints")
        if abs(x) > COORDINATE_LIMIT or abs(y) > COORDINATE_LIMIT:
            raise ValueError("coordinate outside [-10**9,10**9]")
        ordered.append((x, y, index))
    if len(ordered) < 2:
        return None
    ordered.sort()  # Initial order only; recursive combines merge by y.
    duplicate = None
    for a, b in zip(ordered, ordered[1:]):
        if a[:2] == b[:2]:
            candidate = (0, min(a[2], b[2]), max(a[2], b[2]))
            duplicate = candidate if duplicate is None else min(duplicate, candidate)
    if duplicate is not None:
        return duplicate

    def candidate(a, b):
        return ((a[0] - b[0])**2 + (a[1] - b[1])**2,
                min(a[2], b[2]), max(a[2], b[2]))

    def ykey(point):
        return point[1], point[0], point[2]

    def solve(lo, hi):
        if hi - lo <= 3:
            best = min(candidate(ordered[i], ordered[j])
                       for i in range(lo, hi) for j in range(i + 1, hi))
            return best, sorted(ordered[lo:hi], key=ykey)
        mid = lo + (hi - lo) // 2
        split_x = ordered[mid][0]
        left, ly = solve(lo, mid)
        right, ry = solve(mid, hi)
        best = min(left, right)
        merged = []
        i = j = 0
        while i < len(ly) and j < len(ry):
            if ykey(ly[i]) <= ykey(ry[j]):
                merged.append(ly[i]); i += 1
            else:
                merged.append(ry[j]); j += 1
        merged.extend(ly[i:]); merged.extend(ry[j:])
        strip = [p for p in merged if (p[0] - split_x)**2 <= best[0]]
        for i, point in enumerate(strip):
            j = i + 1
            # Inclusive boundaries are necessary to examine equal-distance ties.
            while j < len(strip) and (strip[j][1] - point[1])**2 <= best[0]:
                best = min(best, candidate(point, strip[j]))
                j += 1
        return best, merged

    return solve(0, len(ordered))[0]


def main() -> int:
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    tokens = sys.stdin.read().split()
    try:
        if any(re.fullmatch(r"[+-]?[0-9]+", token) is None for token in tokens):
            raise ValueError("expected ASCII signed decimal integers")
        numbers = [int(token) for token in tokens]
        if not numbers or numbers[0] < 0 or len(numbers) != 1 + 2*numbers[0]:
            raise ValueError("n and exactly n coordinate pairs required")
        result = closest_pair([numbers[i:i + 2] for i in range(1, len(numbers), 2)])
        print(json.dumps(result, separators=(",", ":")))
    except (ValueError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
