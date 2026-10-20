"""Heap sort contracts, heap boundaries, complexity nuance, and CLI."""

import importlib.util
from pathlib import Path
import random
import subprocess
import sys

import pytest


SOURCE = Path(__file__).parents[1] / "python/solution.py"
SPEC = importlib.util.spec_from_file_location("atlas_heap_sort", SOURCE)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
heap_sort = MODULE.heap_sort


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([], []), ([7], [7]), ([2, 1], [1, 2]), ([1, 2], [1, 2]),
        ([2, 2], [2, 2]), ([4, 10, 3, 5, 1], [1, 3, 4, 5, 10]),
        ([3, -1, 0, -1, 3], [-1, -1, 0, 3, 3]),
        ([6, 5, 4, 3, 2, 1], [1, 2, 3, 4, 5, 6]),
        ([4] * 33, [4] * 33),
        ([0, -(2**63), 2**63 - 1], [-(2**63), 0, 2**63 - 1]),
        ([10**100, -(10**100), 0], [-(10**100), 0, 10**100]),
    ],
)
def test_known_answers_and_unchanged_input(values, expected):
    original = values.copy()
    result = heap_sort(values)
    assert result == expected
    assert values == original
    assert result is not values


def test_tuple_and_strings():
    assert heap_sort(("pear", "apple", "apple", "banana")) == [
        "apple", "apple", "banana", "pear"
    ]


def test_seeded_random_heap_boundaries():
    randomizer = random.Random(20261020)
    for length in [0, 1, 2, 3, 4, 5, 7, 8, 9, 31, 32, 33, 63, 64, 65, 257]:
        for _ in range(15):
            values = [randomizer.randint(-1000, 1000) for _ in range(length)]
            original = values.copy()
            assert heap_sort(values) == sorted(values)
            assert values == original


def test_large_adversarial_orderings():
    for values in [
        list(range(2049)), list(range(2048, -1, -1)),
        [index % 3 for index in range(2049)],
        list(range(1024)) + list(range(1024, -1, -1)),
    ]:
        assert heap_sort(values) == sorted(values)


def test_tagged_records_show_instability_with_less_than_only():
    class Record:
        def __init__(self, key, tag):
            self.key = key
            self.tag = tag

        def __lt__(self, other):
            return self.key < other.key

    values = [Record(2, tag) for tag in range(3)]
    result = heap_sort(values)
    assert [item.key for item in result] == [2, 2, 2]
    assert [item.tag for item in result] == [1, 2, 0]
    assert [item.tag for item in values] == [0, 1, 2]


def test_all_equal_keys_need_only_linear_comparisons():
    class Record:
        comparisons = 0

        def __lt__(self, other):
            Record.comparisons += 1
            return False

    values = [Record() for _ in range(512)]
    assert len(heap_sort(values)) == len(values)
    assert Record.comparisons <= 3 * len(values)


def test_incomparable_items_leave_input_unchanged():
    values = [1, "two"]
    with pytest.raises(TypeError):
        heap_sort(values)
    assert values == [1, "two"]


def test_python_cli():
    for input_text, expected in [
        ("", "\n"), ("4 10 3 5 1\n", "1 3 4 5 10\n"),
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
