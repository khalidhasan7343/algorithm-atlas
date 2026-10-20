"""Known answers, randomized oracles, and public-contract quicksort checks."""

import importlib.util
from pathlib import Path
import random
import subprocess
import sys

import pytest


SOURCE = Path(__file__).parents[1] / "python/solution.py"
SPEC = importlib.util.spec_from_file_location("atlas_quick_sort", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
quick_sort = MODULE.quick_sort


@pytest.mark.parametrize("values,expected", [
    ([], []), ([9], [9]), ([4, 4, 4], [4, 4, 4]),
    ([1, 2, 3], [1, 2, 3]), ([3, 2, 1], [1, 2, 3]),
    ([4, 2, 4, 1, 3], [1, 2, 3, 4, 4]),
    ([0, -9, 7, -9], [-9, -9, 0, 7]),
    ([2**63 - 1, -2**63, 0], [-2**63, 0, 2**63 - 1]),
    ([10**100, -10**100, 5], [-10**100, 5, 10**100]),
    (["pear", "apple", "pear"], ["apple", "pear", "pear"]),
])
def test_known_results_and_preserved_input(values, expected) -> None:
    before = values.copy()
    result = quick_sort(values)
    assert result == expected
    assert values == before
    assert result is not values


def test_seeded_randomized_sorting_and_permutation() -> None:
    generator = random.Random(7343)
    for length in range(101):
        for _ in range(3):
            values = [generator.randint(-1000, 1000) for _ in range(length)]
            before = values.copy()
            assert quick_sort(values) == sorted(values)
            assert values == before


def test_large_orderings_duplicates_and_tuple() -> None:
    for values in [list(range(8000)), list(range(8000, 0, -1)), [7] * 20000]:
        assert quick_sort(values) == sorted(values)
    assert quick_sort((3, 1, 2)) == [1, 2, 3]


def test_only_less_than_is_required_and_algorithm_is_unstable() -> None:
    class Record:
        def __init__(self, key, tag):
            self.key, self.tag = key, tag

        def __lt__(self, other):
            return self.key < other.key

    records = [Record(2, "a"), Record(1, "b"), Record(2, "c")]
    result = quick_sort(records)
    assert [record.key for record in result] == [1, 2, 2]
    assert [record.tag for record in result] == ["b", "c", "a"]
    assert [record.tag for record in records] == ["a", "b", "c"]


def test_equal_keys_need_one_linear_partition() -> None:
    class Counted:
        comparisons = 0

        def __lt__(self, other):
            Counted.comparisons += 1
            return False

    quick_sort([Counted() for _ in range(1000)])
    assert Counted.comparisons == 2000


@pytest.mark.parametrize("text,expected", [
    ("", "\n"), (" \t\n", "\n"), ("7", "7\n"),
    ("4 2 4 1 3", "1 2 3 4 4\n"), ("+03 -0 -7", "-7 0 3\n"),
    (f"{2**63 - 1} {-2**63}", f"{-2**63} {2**63 - 1}\n"),
])
def test_cli_known_answers(text, expected) -> None:
    result = subprocess.run([sys.executable, str(SOURCE)], input=text,
                            capture_output=True, text=True, check=True, timeout=10)
    assert result.stdout == expected
    assert result.stderr == ""


@pytest.mark.parametrize("text", ["1 two 3", "1.5", "0x10", "+", "-", "--2", "+-2", "1_000", "١"])
def test_cli_rejects_malformed_input_atomically(text) -> None:
    result = subprocess.run([sys.executable, str(SOURCE)], input=text,
                            capture_output=True, text=True, timeout=10)
    assert result.returncode != 0
    assert result.stdout == ""
    assert "error:" in result.stderr


def test_cli_arbitrary_precision_decimal_conversion() -> None:
    huge = "1" + "0" * 4500
    result = subprocess.run([sys.executable, str(SOURCE)], input=huge + " -2 0",
                            capture_output=True, text=True, check=True, timeout=10)
    assert result.stdout == "-2 0 " + huge + "\n"
