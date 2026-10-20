"""Shell sort contracts, gap boundaries, tagged records, and CLI behavior."""

import importlib.util
from pathlib import Path
import random
import subprocess
import sys

import pytest


SOURCE = Path(__file__).parents[1] / "python/solution.py"
SPEC = importlib.util.spec_from_file_location("atlas_shell_sort", SOURCE)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
shell_sort = MODULE.shell_sort


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([], []), ([7], [7]), ([2, 1], [1, 2]), ([1, 2], [1, 2]),
        ([2, 2], [2, 2]), ([4, 10, 3, 5, 1], [1, 3, 4, 5, 10]),
        ([23, 12, 1, 8, 34, 54, 2, 3, 7, 4], [1, 2, 3, 4, 7, 8, 12, 23, 34, 54]),
        ([3, -1, 0, -1, 3], [-1, -1, 0, 3, 3]),
        ([6, 5, 4, 3, 2, 1], [1, 2, 3, 4, 5, 6]),
        ([4] * 40, [4] * 40),
        ([0, -(2**63), 2**63 - 1], [-(2**63), 0, 2**63 - 1]),
        ([10**100, -(10**100), 0], [-(10**100), 0, 10**100]),
    ],
)
def test_known_answers_and_input_preservation(values, expected):
    original = values.copy()
    result = shell_sort(values)
    assert result == expected
    assert values == original
    assert result is not values


def test_tuple_and_strings():
    values = ("pear", "apple", "apple", "banana")
    assert shell_sort(values) == ["apple", "apple", "banana", "pear"]


def test_seeded_random_around_knuth_gap_boundaries():
    randomizer = random.Random(20261020)
    lengths = [0, 1, 2, 3, 4, 5, 6, 11, 12, 13, 14, 15, 38, 39, 40, 41, 42, 120, 121, 122, 123, 364]
    for length in lengths:
        for _ in range(15):
            values = [randomizer.randint(-1000, 1000) for _ in range(length)]
            original = values.copy()
            assert shell_sort(values) == sorted(values)
            assert values == original


def test_large_ordered_reversed_and_gap_spaced_patterns():
    for values in [
        list(range(2049)), list(range(2048, -1, -1)),
        [index % 13 for index in range(2049)],
        [index % 40 for index in range(2049)],
    ]:
        assert shell_sort(values) == sorted(values)


def test_tagged_records_prove_instability_using_only_less_than():
    class Record:
        def __init__(self, key, tag):
            self.key = key
            self.tag = tag

        def __lt__(self, other):
            return self.key < other.key

    records = [Record(key, tag) for tag, key in enumerate([2, 2, 0, 0, 0, 3])]
    result = shell_sort(records)
    assert [(item.key, item.tag) for item in result] == [
        (0, 4), (0, 2), (0, 3), (2, 1), (2, 0), (3, 5)
    ]
    assert [item.tag for item in records] == list(range(6))


def test_sorted_and_equal_data_visit_each_gap_pass():
    class Record:
        comparisons = 0

        def __init__(self, key):
            self.key = key

        def __lt__(self, other):
            Record.comparisons += 1
            return self.key < other.key

    for keys in [list(range(100)), [7] * 100]:
        records = [Record(key) for key in keys]
        Record.comparisons = 0
        assert [record.key for record in shell_sort(records)] == keys
        # For n=100, the gap sequence used is 40, 13, 4, 1.
        assert Record.comparisons == sum(100 - gap for gap in [40, 13, 4, 1])


def test_incomparable_values_leave_input_unchanged():
    values = [1, "two"]
    with pytest.raises(TypeError):
        shell_sort(values)
    assert values == [1, "two"]


def test_python_cli():
    for input_text, expected in [
        ("", "\n"), ("23 12 1 8 34 54 2 3 7 4\n", "1 2 3 4 7 8 12 23 34 54\n"),
        ("  +2\n-3 0001 -0\t", "-3 0 1 2\n"),
        (f"{2**90} {-2**90}", f"{-2**90} {2**90}\n"),
    ]:
        result = subprocess.run(
            [sys.executable, str(SOURCE)], input=input_text, capture_output=True,
            text=True, check=True, timeout=10,
        )
        assert result.stdout == expected
        assert result.stderr == ""
    for invalid in ["1 two 3", "1.5", "0x10", "+", "-", "--2", "+-2", "1_000", "１２"]:
        result = subprocess.run(
            [sys.executable, str(SOURCE)], input=invalid, capture_output=True,
            text=True, timeout=10,
        )
        assert result.returncode != 0
        assert result.stdout == ""
        assert "Invalid input" in result.stderr
