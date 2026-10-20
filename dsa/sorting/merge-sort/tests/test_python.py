"""Behavior, stability, boundary, and executable tests for merge sort."""

import importlib.util
from pathlib import Path
import random
import subprocess
import sys

import pytest


SOURCE = Path(__file__).parents[1] / "python/solution.py"
SPEC = importlib.util.spec_from_file_location("atlas_merge_sort", SOURCE)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
merge_sort = MODULE.merge_sort


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([], []),
        ([7], [7]),
        ([2, 1], [1, 2]),
        ([1, 2], [1, 2]),
        ([2, 2], [2, 2]),
        ([5, 1, 4, 2, 8], [1, 2, 4, 5, 8]),
        ([3, -1, 0, -1, 3], [-1, -1, 0, 3, 3]),
        ([8, 7, 6, 5, 4, 3, 2, 1], list(range(1, 9))),
        ([4] * 33, [4] * 33),
        ([0, -(2**63), 2**63 - 1], [-(2**63), 0, 2**63 - 1]),
        ([10**100, -(10**100), 0], [-(10**100), 0, 10**100]),
    ],
)
def test_known_answers_and_unchanged_input(values, expected):
    original = values.copy()
    actual = merge_sort(values)
    assert actual == expected
    assert values == original
    assert actual is not values


def test_tuple_and_generic_string_records():
    values = ("pear", "apple", "apple", "banana")
    assert merge_sort(values) == ["apple", "apple", "banana", "pear"]
    assert values == ("pear", "apple", "apple", "banana")


def test_seeded_random_and_odd_length_ranges():
    randomizer = random.Random(20261020)
    for length in [0, 1, 2, 3, 5, 7, 9, 31, 32, 33, 63, 65, 257]:
        for _ in range(15):
            values = [randomizer.randint(-1000, 1000) for _ in range(length)]
            original = values.copy()
            assert merge_sort(values) == sorted(values)
            assert values == original


def test_stability_with_less_than_only_records():
    class Record:
        def __init__(self, key, tag):
            self.key = key
            self.tag = tag

        def __lt__(self, other):
            return self.key < other.key

    records = [Record(key, index) for index, key in enumerate([2, 1, 2, 1, 2, 0, 1])]
    result = merge_sort(records)
    assert [(record.key, record.tag) for record in result] == [
        (0, 5), (1, 1), (1, 3), (1, 6), (2, 0), (2, 2), (2, 4)
    ]
    assert [record.tag for record in records] == list(range(7))
    assert all(any(record is original for original in records) for record in result)


def test_incomparable_elements_raise_without_changing_input():
    values = [1, "two"]
    with pytest.raises(TypeError):
        merge_sort(values)
    assert values == [1, "two"]


def test_python_cli():
    for input_text, expected in [
        ("", "\n"),
        ("5 1 4 2 8\n", "1 2 4 5 8\n"),
        ("  +2\n-3 0001 -0\t", "-3 0 1 2\n"),
        (f"{2**90} {-2**90}", f"{-2**90} {2**90}\n"),
    ]:
        result = subprocess.run(
            [sys.executable, str(SOURCE)], input=input_text,
            capture_output=True, text=True, check=True, timeout=10,
        )
        assert result.stdout == expected
        assert result.stderr == ""
    for invalid in ["1 two 3", "1.5", "0x10", "+", "--2", "+-2", "1_000", "１２"]:
        result = subprocess.run(
            [sys.executable, str(SOURCE)], input=invalid,
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode != 0
        assert result.stdout == ""
        assert "Invalid input" in result.stderr
