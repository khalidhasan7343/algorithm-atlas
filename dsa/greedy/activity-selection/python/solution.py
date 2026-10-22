"""Earliest-finish maximum-cardinality selection of half-open intervals."""
from collections.abc import Sequence
import json
import re
import sys


def activity_selection(activities: Sequence[tuple[int, int]]) -> list[int]:
    """Return original indices; ties sort by (finish, start, index)."""
    if len(activities) > 10000:
        raise ValueError("at most 10000 activities required")
    for activity in activities:
        if not isinstance(activity, (list, tuple)) or len(activity) != 2:
            raise ValueError("each activity needs start and finish")
        start, finish = activity
        if any(type(t) is not int or not -10**9 <= t <= 10**9 for t in activity):
            raise ValueError("times must be integers in +/-10^9")
        if start >= finish:
            raise ValueError("require start < finish")
    ordered = sorted(range(len(activities)), key=lambda i: (activities[i][1], activities[i][0], i))
    selected = []
    last_finish = None
    for index in ordered:
        start, finish = activities[index]
        if last_finish is None or start >= last_finish:
            selected.append(index)
            last_finish = finish
    return selected


if __name__ == "__main__":
    try:
        tokens = sys.stdin.read().split()
        if any(not re.fullmatch(r"[+-]?[0-9]+", x) for x in tokens):
            raise ValueError("expected ASCII decimal integers")
        numbers = [int(x) for x in tokens]
        if not numbers or not 0 <= numbers[0] <= 10000 or len(numbers) != 1 + 2*numbers[0]:
            raise ValueError("expected count and start/finish pairs")
        activities = list(zip(numbers[1::2], numbers[2::2]))
        print(json.dumps(activity_selection(activities), separators=(",", ":")))
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
