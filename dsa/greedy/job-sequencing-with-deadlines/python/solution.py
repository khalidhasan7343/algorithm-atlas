"""Maximum-profit unit jobs: latest free slots via ranked disjoint sets."""
from collections.abc import Sequence
import json
import re
import sys


def job_sequencing(deadlines: Sequence[int], profits: Sequence[int]) -> tuple[int, list[int | None]]:
    if len(deadlines) != len(profits) or len(deadlines) > 10000:
        raise ValueError("equal deadline/profit lengths of at most 10000 required")
    if any(type(d) is not int or not 0 <= d <= 10**9 for d in deadlines):
        raise ValueError("deadlines must be integers in 0..10^9")
    if any(type(p) is not int or not -10**9 <= p <= 10**9 for p in profits):
        raise ValueError("profits must be integers in +/-10^9")
    horizon = min(len(deadlines), max(deadlines, default=0))
    parent = list(range(horizon + 1))
    rank = [0] * (horizon + 1)
    available = list(range(horizon + 1))
    slots: list[int | None] = [None] * horizon

    def find(slot: int) -> int:
        while parent[slot] != slot:
            parent[slot] = parent[parent[slot]]
            slot = parent[slot]
        return slot

    def occupy(slot: int) -> None:
        left, right = find(slot - 1), find(slot)
        if rank[left] < rank[right]:
            left, right = right, left
        parent[right] = left
        available[left] = min(available[left], available[right])
        if rank[left] == rank[right]:
            rank[left] += 1

    ordered = sorted((i for i in range(len(deadlines)) if deadlines[i] > 0 and profits[i] > 0),
                     key=lambda i: (-profits[i], i))
    total = 0
    for index in ordered:
        slot = available[find(min(deadlines[index], horizon))]
        if slot:
            slots[slot-1] = index
            total += profits[index]
            occupy(slot)
    return total, slots


if __name__ == "__main__":
    try:
        tokens = sys.stdin.read().split()
        if any(not re.fullmatch(r"[+-]?[0-9]+", x) for x in tokens):
            raise ValueError("expected ASCII decimal integers")
        numbers = [int(x) for x in tokens]
        if not numbers or not 0 <= numbers[0] <= 10000 or len(numbers) != 1 + 2*numbers[0]:
            raise ValueError("expected count and deadline/profit pairs")
        profit, slots = job_sequencing(numbers[1::2], numbers[2::2])
        print(json.dumps({"profit": profit, "slots": slots}, separators=(",", ":")))
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
