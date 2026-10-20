"""Tim Sort behavior, stability, run-stack regression, and galloping tests."""

from bisect import bisect_left, bisect_right
from dataclasses import dataclass
import importlib.util
from pathlib import Path
import random
import subprocess
import sys

import pytest


SOURCE = Path(__file__).parents[1] / "python" / "solution.py"
SPEC = importlib.util.spec_from_file_location("atlas_tim_sort", SOURCE)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
tim_sort = MODULE.tim_sort


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([], []), ([7], [7]), ([4, 4, 4], [4, 4, 4]),
        ([1, 2, 3, 4], [1, 2, 3, 4]),
        ([4, 3, 2, 1], [1, 2, 3, 4]),
        ([5, 2, 4, 2, 1], [1, 2, 2, 4, 5]),
        ([0, -9, 2, -9, -1], [-9, -9, -1, 0, 2]),
        ([-2**63, 2**63 - 1, 0], [-2**63, 0, 2**63 - 1]),
        ([10**120, -10**120, 0], [-10**120, 0, 10**120]),
        ((3, 1, 2), [1, 2, 3]),
        (["pear", "apple", "plum"], ["apple", "pear", "plum"]),
    ],
)
def test_known_results_and_preserved_input(values, expected) -> None:
    before = list(values)
    result = tim_sort(values)
    assert result == expected
    assert list(values) == before
    assert isinstance(result, list)
    assert result is not values


@pytest.mark.parametrize(
    ("length", "expected"),
    [(0, 0), (1, 1), (31, 31), (32, 32), (63, 63), (64, 32),
     (65, 33), (127, 64), (128, 32), (129, 33), (2112, 33)],
)
def test_classic_minrun_boundaries(length, expected) -> None:
    assert MODULE._min_run_length(length) == expected


@pytest.mark.parametrize(
    "length", [2, 31, 32, 63, 64, 65, 127, 128, 129, 255, 256, 257, 511, 1001, 4097]
)
def test_minrun_and_nonpower_merge_boundaries(length) -> None:
    generator = random.Random(7343 + length)
    values = [generator.randint(-30, 30) for _ in range(length)]
    before = values.copy()
    assert tim_sort(values) == sorted(values)
    assert values == before


def test_seeded_random_differential_and_large_input() -> None:
    generator = random.Random(7343)
    lengths = [*range(130), 256, 511, 1000, 3141, 20_003]
    for length in lengths:
        values = [generator.randint(-10**9, 10**9) for _ in range(length)]
        before = values.copy()
        assert tim_sort(values) == sorted(values)
        assert values == before


@dataclass
class Record:
    key: int
    tag: int

    def __lt__(self, other):
        return self.key < other.key


def test_seeded_record_stability_including_descending_equal_plateaus() -> None:
    generator = random.Random(7343)
    key_cases = [
        [5, 4, 4, 3, 3, 2, 1, 1],
        [key for key in reversed(range(100)) for _ in range(4)],
        [generator.randint(-20, 20) for _ in range(4097)],
    ]
    for keys in key_cases:
        records = [Record(key, index) for index, key in enumerate(keys)]
        result = tim_sort(records)
        assert result == sorted(records, key=lambda record: record.key)
        assert [record.tag for record in records] == list(range(len(records)))
        assert {id(record) for record in result} == {id(record) for record in records}


@pytest.mark.parametrize("right_first", [False, True])
def test_overlapping_equal_key_runs_and_both_gallop_directions(right_first) -> None:
    first = range(500, 1500) if right_first else range(1000)
    second = range(1000) if right_first else range(500, 1500)
    keys = [key for key in first for _ in range(3)]
    keys += [key for key in second for _ in range(3)]
    records = [Record(key, index) for index, key in enumerate(keys)]
    assert tim_sort(records) == sorted(records, key=lambda record: record.key)


def test_gallop_bounds_match_independent_bisect_including_ties() -> None:
    generator = random.Random(7343)
    for length in range(66):
        values = sorted(generator.randint(-5, 5) for _ in range(length))
        for start in sorted({0, length, *range(0, length, 5)}):
            for pivot in range(-7, 8):
                assert MODULE._gallop_bound(
                    values, start, length, pivot, upper=False
                ) == bisect_left(values, pivot, start, length)
                assert MODULE._gallop_bound(
                    values, start, length, pivot, upper=True
                ) == bisect_right(values, pivot, start, length)
    records = [Record(2, index) for index in range(20)]
    pivot = Record(2, -1)
    assert MODULE._gallop_bound(records, 3, 20, pivot, upper=False) == 3
    assert MODULE._gallop_bound(records, 3, 20, pivot, upper=True) == 20


def test_natural_runs_reproduce_documented_merge_trace(monkeypatch) -> None:
    events = []
    original_merge = MODULE._merge

    def observed_merge(values, start, middle, end):
        events.append((start, middle, end))
        original_merge(values, start, middle, end)

    monkeypatch.setattr(MODULE, "_merge", observed_merge)
    values = [*range(96, 128), *range(64, 96), *range(32, 64), *range(32)]
    assert tim_sort(values) == list(range(128))
    assert events == [(0, 32, 64), (64, 96, 128), (0, 64, 128)]


def descending_groups(lengths):
    endpoint = sum(lengths)
    values = []
    for length in lengths:
        values.extend(range(endpoint - length, endpoint))
        endpoint -= length
    return values


def assert_stack_invariants(runs) -> None:
    lengths = [length for _, length in runs]
    assert all(left > right for left, right in zip(lengths, lengths[1:]))
    assert all(
        lengths[index] > lengths[index + 1] + lengths[index + 2]
        for index in range(len(lengths) - 2)
    )


def test_four_run_lookback_regression_checks_below_top_triple(monkeypatch) -> None:
    # Top triple 80 > 45+30 is valid; the deeper triple 120 <= 80+45 is not.
    assert MODULE._collapse_choice([(0, 120), (120, 80), (200, 45), (245, 30)]) == 2
    original_collapse = MODULE._TimSorter._collapse
    stacks = []

    def checked_collapse(self):
        original_collapse(self)
        assert_stack_invariants(self.runs)
        stacks.append([length for _, length in self.runs])

    monkeypatch.setattr(MODULE._TimSorter, "_collapse", checked_collapse)
    values = descending_groups([480, 320, 100, 80, 120])
    assert tim_sort(values) == list(range(1100))
    assert stacks[:4] == [[480], [480, 320], [480, 320, 100], [480, 320, 100, 80]]
    assert stacks[4] == [1100]


def test_many_adversarial_runs_preserve_all_stack_invariants(monkeypatch) -> None:
    original_collapse = MODULE._TimSorter._collapse

    def checked_collapse(self):
        original_collapse(self)
        assert_stack_invariants(self.runs)

    monkeypatch.setattr(MODULE._TimSorter, "_collapse", checked_collapse)
    generator = random.Random(7343)
    patterns = [
        [64] * 257,
        [128, 96, 64, 80, 65, 127] * 35,
        [generator.randint(64, 192) for _ in range(200)],
    ]
    for lengths in patterns:
        values = descending_groups(lengths)
        assert tim_sort(values) == list(range(sum(lengths)))


@pytest.mark.parametrize("ordering", ["ascending", "descending", "equal"])
def test_one_natural_run_uses_linear_comparisons(ordering) -> None:
    class Counted:
        comparisons = 0

        def __init__(self, value):
            self.value = value

        def __lt__(self, other):
            Counted.comparisons += 1
            return self.value < other.value

    size = 4096
    keys = list(range(size))
    if ordering == "descending":
        keys.reverse()
    elif ordering == "equal":
        keys = [7] * size
    result = tim_sort([Counted(key) for key in keys])
    assert Counted.comparisons == size - 1
    assert [item.value for item in result] == sorted(keys)


def test_galloping_skips_a_long_winning_run() -> None:
    class Counted:
        comparisons = 0

        def __init__(self, value):
            self.value = value

        def __lt__(self, other):
            Counted.comparisons += 1
            return self.value < other.value

    keys = [*range(2000, 4000), *range(2000)]
    result = tim_sort([Counted(key) for key in keys])
    assert [item.value for item in result] == list(range(4000))
    # Run discovery takes n-1 comparisons; galloping avoids 2000 scalar wins.
    assert Counted.comparisons < len(keys) + 140


def test_incomparable_values_raise_without_mutating_input() -> None:
    values = [1, "two"]
    with pytest.raises(TypeError):
        tim_sort(values)
    assert values == [1, "two"]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", "\n"), (" \n\t", "\n"),
        ("5 2 4 2 1", "1 2 2 4 5\n"),
        ("+03 -0 -7\t4", "-7 0 3 4\n"),
        (f"{2**63 - 1} {-2**63} 0", f"{-2**63} 0 {2**63 - 1}\n"),
        (f"{10**120} {-10**120}", f"{-10**120} {10**120}\n"),
    ],
)
def test_valid_cli(text, expected) -> None:
    result = subprocess.run(
        [sys.executable, str(SOURCE)], input=text, capture_output=True,
        text=True, check=True, timeout=10,
    )
    assert result.stdout == expected
    assert result.stderr == ""


@pytest.mark.parametrize(
    "text", ["1 two 3", "1.5", "0x10", "+", "-", "--2", "1_000", "12x", "١"]
)
def test_invalid_cli_rejects_entire_input(text) -> None:
    result = subprocess.run(
        [sys.executable, str(SOURCE)], input=text, capture_output=True,
        text=True, timeout=10,
    )
    assert result.returncode != 0
    assert result.stdout == ""
    assert "error:" in result.stderr
