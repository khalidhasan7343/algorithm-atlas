"""Educational classic Tim Sort with natural runs and fixed-threshold galloping."""

from __future__ import annotations

from collections.abc import Sequence
import re
import sys
from typing import TypeVar


T = TypeVar("T")
_MIN_GALLOP = 7


def _min_run_length(length: int) -> int:
    """Use the classic 64-threshold rule: 32..64 for lengths >= 64."""
    discarded_bit = 0
    while length >= 64:
        discarded_bit |= length & 1
        length >>= 1
    return length + discarded_bit


def _count_run(values: list[T], start: int) -> int:
    """Find a natural run, reversing it only if it is strictly descending."""
    end = start + 1
    if end == len(values):
        return 1
    descending = values[end] < values[start]
    end += 1
    if descending:
        while end < len(values) and values[end] < values[end - 1]:
            end += 1
        left, right = start, end - 1
        while left < right:
            values[left], values[right] = values[right], values[left]
            left += 1
            right -= 1
    else:
        while end < len(values) and not values[end] < values[end - 1]:
            end += 1
    return end - start


def _binary_insertion(
    values: list[T], start: int, end: int, sorted_end: int
) -> None:
    """Extend an ordered prefix, placing new items after equivalent items."""
    for index in range(sorted_end, end):
        item = values[index]
        lower, upper = start, index
        while lower < upper:
            middle = lower + (upper - lower) // 2
            if item < values[middle]:
                upper = middle
            else:
                lower = middle + 1
        position = index
        while position > lower:
            values[position] = values[position - 1]
            position -= 1
        values[lower] = item


def _gallop_bound(
    values: list[T], start: int, end: int, pivot: T, *, upper: bool
) -> int:
    """Find upper/lower bound from start by exponential then binary search.

    Upper bound consumes keys <= pivot; lower bound consumes keys < pivot.
    Both are expressed using only <, keeping left-run ties first in a merge.
    """
    def precedes(value: T) -> bool:
        return not pivot < value if upper else value < pivot

    if start == end or not precedes(values[start]):
        return start
    lower = start + 1
    offset = 1
    while start + offset < end and precedes(values[start + offset]):
        lower = start + offset + 1
        offset = 2 * offset + 1
    upper_end = min(end, start + offset + 1)
    while lower < upper_end:
        middle = lower + (upper_end - lower) // 2
        if precedes(values[middle]):
            lower = middle + 1
        else:
            upper_end = middle
    return lower


def _merge(values: list[T], start: int, middle: int, end: int) -> None:
    """Stable forward merge with two copied runs and opportunistic gallops."""
    if not values[middle] < values[middle - 1]:
        return
    left = values[start:middle]
    right = values[middle:end]
    left_index = right_index = 0
    destination = start
    left_wins = right_wins = 0
    while left_index < len(left) and right_index < len(right):
        if right[right_index] < left[left_index]:
            values[destination] = right[right_index]
            right_index += 1
            right_wins += 1
            left_wins = 0
        else:
            values[destination] = left[left_index]
            left_index += 1
            left_wins += 1
            right_wins = 0
        destination += 1

        if left_index == len(left) or right_index == len(right):
            break
        if left_wins >= _MIN_GALLOP:
            boundary = _gallop_bound(
                left, left_index, len(left), right[right_index], upper=True
            )
            count = boundary - left_index
            values[destination:destination + count] = left[left_index:boundary]
            destination += count
            left_index = boundary
            left_wins = 0
        elif right_wins >= _MIN_GALLOP:
            boundary = _gallop_bound(
                right, right_index, len(right), left[left_index], upper=False
            )
            count = boundary - right_index
            values[destination:destination + count] = right[right_index:boundary]
            destination += count
            right_index = boundary
            right_wins = 0

    if left_index < len(left):
        values[destination:end] = left[left_index:]
    elif right_index < len(right):
        values[destination:end] = right[right_index:]


def _collapse_choice(runs: list[tuple[int, int]]) -> int | None:
    """Choose a neighboring merge using the corrected four-run lookback."""
    if len(runs) < 2:
        return None
    index = len(runs) - 2
    latest_triple_bad = (
        index > 0 and runs[index - 1][1] <= runs[index][1] + runs[index + 1][1]
    )
    previous_triple_bad = (
        index > 1 and runs[index - 2][1] <= runs[index - 1][1] + runs[index][1]
    )
    if latest_triple_bad or previous_triple_bad:
        if runs[index - 1][1] < runs[index + 1][1]:
            index -= 1
        return index
    if runs[index][1] <= runs[index + 1][1]:
        return index
    return None


class _TimSorter:
    """Own the copied sequence and the pending adjacent natural-run stack."""

    def __init__(self, values: list[T]) -> None:
        self.values = values
        self.runs: list[tuple[int, int]] = []

    def _merge_at(self, index: int) -> None:
        start, left_length = self.runs[index]
        middle, right_length = self.runs[index + 1]
        _merge(self.values, start, middle, middle + right_length)
        self.runs[index:index + 2] = [(start, left_length + right_length)]

    def _collapse(self) -> None:
        while (index := _collapse_choice(self.runs)) is not None:
            self._merge_at(index)

    def sort(self) -> list[T]:
        size = len(self.values)
        if size < 2:
            return self.values
        minimum_run = _min_run_length(size)
        start = 0
        while start < size:
            run_length = _count_run(self.values, start)
            required_length = min(minimum_run, size - start)
            if run_length < required_length:
                _binary_insertion(
                    self.values, start, start + required_length, start + run_length
                )
                run_length = required_length
            self.runs.append((start, run_length))
            self._collapse()
            start += run_length
        while len(self.runs) > 1:
            index = len(self.runs) - 2
            if index > 0 and self.runs[index - 1][1] < self.runs[index + 1][1]:
                index -= 1
            self._merge_at(index)
        return self.values


def tim_sort(values: Sequence[T]) -> list[T]:
    """Return a stable sorted copy using classic Tim Sort's run-stack policy.

    Elements need a consistent < ordering. This educational implementation
    uses full forward-merge buffers and a fixed seven-win galloping trigger.
    It does not implement CPython's newer Powersort merge policy.
    """
    return _TimSorter(list(values)).sort()


def main() -> int:
    """Read whitespace-separated signed ASCII decimal integers and sort."""
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    tokens = sys.stdin.read().split()
    if any(re.fullmatch(r"[+-]?[0-9]+", token) is None for token in tokens):
        print("error: expected signed decimal integers", file=sys.stderr)
        return 1
    values = [int(token, 10) for token in tokens]
    print(" ".join(map(str, tim_sort(values))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
