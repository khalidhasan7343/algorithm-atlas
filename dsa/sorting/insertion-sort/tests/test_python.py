"""Behavior, stability, adaptivity, and CLI tests for Python insertion sort."""

from dataclasses import dataclass
import importlib.util
from pathlib import Path
import random
import subprocess
import sys

import pytest


SOURCE = Path(__file__).parents[1] / "python" / "solution.py"
SPEC = importlib.util.spec_from_file_location("atlas_insertion_sort", SOURCE)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
insertion_sort = MODULE.insertion_sort


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([], []),
        ([7], [7]),
        ([4, 4, 4], [4, 4, 4]),
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
    result = insertion_sort(values)
    assert result == expected
    assert list(values) == before
    assert isinstance(result, list)
    assert result is not values


def test_seeded_random_differential() -> None:
    generator = random.Random(7343)
    for length in range(81):
        for _ in range(3):
            values = [generator.randint(-100, 100) for _ in range(length)]
            before = values.copy()
            assert insertion_sort(values) == sorted(values)
            assert values == before


@dataclass
class Record:
    key: int
    tag: str

    def __lt__(self, other):
        return self.key < other.key


def test_stable_with_only_less_than_comparison() -> None:
    values = [Record(2, "a"), Record(1, "b"), Record(2, "c"), Record(1, "d")]
    result = insertion_sort(values)
    assert [record.tag for record in result] == ["b", "d", "a", "c"]
    assert [record.tag for record in values] == ["a", "b", "c", "d"]
    assert {id(record) for record in result} == {id(record) for record in values}


def test_comparison_count_adapts_to_inversions() -> None:
    class Counted:
        comparisons = 0

        def __init__(self, value):
            self.value = value

        def __lt__(self, other):
            Counted.comparisons += 1
            return self.value < other.value

    size = 40
    insertion_sort([Counted(index) for index in range(size)])
    assert Counted.comparisons == size - 1
    Counted.comparisons = 0
    insertion_sort([Counted(index) for index in reversed(range(size))])
    assert Counted.comparisons == size * (size - 1) // 2
    Counted.comparisons = 0
    nearby = list(range(size))
    nearby[-1], nearby[-2] = nearby[-2], nearby[-1]
    insertion_sort([Counted(index) for index in nearby])
    assert Counted.comparisons == size


def test_incomparable_input_raises_without_mutating_input() -> None:
    values = [1, "two"]
    with pytest.raises(TypeError):
        insertion_sort(values)
    assert values == [1, "two"]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", "\n"),
        (" \n\t", "\n"),
        ("5 2 4 2 1\n", "1 2 2 4 5\n"),
        ("+03 -0 -7\t4\n", "-7 0 3 4\n"),
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
