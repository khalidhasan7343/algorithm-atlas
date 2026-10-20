"""Counting-sort correctness, range boundaries, types, and CLI behavior."""

import importlib.util
from pathlib import Path
import random
import subprocess
import sys

import pytest


SOURCE = Path(__file__).parents[1] / "python" / "solution.py"
SPEC = importlib.util.spec_from_file_location("atlas_counting_sort", SOURCE)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
counting_sort = MODULE.counting_sort


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([], []), ([4], [4]), ([2, 2, 2], [2, 2, 2]),
        ([-3, -2, -1, 0], [-3, -2, -1, 0]),
        ([3, 2, 1, 0], [0, 1, 2, 3]),
        ([2, -1, 2, 0, -1], [-1, -1, 0, 2, 2]),
        ((3, -1, 1), [-1, 1, 3]),
        ([-2**63 + 2, -2**63, -2**63 + 1],
         [-2**63, -2**63 + 1, -2**63 + 2]),
        ([2**63 - 1, 2**63 - 2], [2**63 - 2, 2**63 - 1]),
        ([10**100 + 2, 10**100, 10**100 + 1],
         [10**100, 10**100 + 1, 10**100 + 2]),
    ],
)
def test_known_results_and_input_preservation(values, expected) -> None:
    before = list(values)
    result = counting_sort(values)
    assert result == expected
    assert list(values) == before
    assert isinstance(result, list)
    assert result is not values


def test_seeded_differential_and_multiset() -> None:
    generator = random.Random(7343)
    for length in range(81):
        for _ in range(3):
            values = [generator.randint(-50, 50) for _ in range(length)]
            before = values.copy()
            assert counting_sort(values) == sorted(values)
            assert values == before


def test_custom_limit_includes_both_endpoints() -> None:
    assert counting_sort([3, -2, 1], max_range=6) == [-2, 1, 3]
    with pytest.raises(ValueError, match="key range"):
        counting_sort([3, -2, 1], max_range=5)
    assert counting_sort([42, 42], max_range=1) == [42, 42]
    with pytest.raises(ValueError, match="key range"):
        counting_sort([42, 43], max_range=1)


def test_default_limit_exact_boundary_and_rejection_before_allocation() -> None:
    assert counting_sort([999_999, 0]) == [0, 999_999]
    for values in ([0, 1_000_000], [-2**63, 2**63 - 1], [0, 10**100]):
        before = list(values)
        with pytest.raises(ValueError, match="key range"):
            counting_sort(values)
        assert values == before


@pytest.mark.parametrize("max_range", [0, -1, -100])
@pytest.mark.parametrize("values", [[], [1]])
def test_invalid_numeric_range_limit_even_for_empty(values, max_range) -> None:
    with pytest.raises(ValueError, match="positive"):
        counting_sort(values, max_range=max_range)


@pytest.mark.parametrize("max_range", [True, False, 3.0, "3", None])
def test_invalid_range_limit_types(max_range) -> None:
    with pytest.raises(TypeError, match="native integer"):
        counting_sort([], max_range=max_range)


@pytest.mark.parametrize("value", [True, False, 2.0, "2", None, complex(2, 0)])
def test_invalid_value_types(value) -> None:
    values = [1, value]
    with pytest.raises(TypeError, match="native integers"):
        counting_sort(values)
    assert values[1] is value


def test_integer_subclasses_are_not_native_integers() -> None:
    class DerivedInt(int):
        pass

    with pytest.raises(TypeError, match="native integers"):
        counting_sort([DerivedInt(1)])
    with pytest.raises(TypeError, match="native integer"):
        counting_sort([], max_range=DerivedInt(5))


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", "\n"), (" \t\n", "\n"),
        ("2 -1 2 0 -1", "-1 -1 0 2 2\n"),
        ("+03 -0 -7\n", "-7 0 3\n"),
        (f"{-2**63 + 1} {-2**63}", f"{-2**63} {-2**63 + 1}\n"),
        (f"{10**100 + 1} {10**100}", f"{10**100} {10**100 + 1}\n"),
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
    "text",
    ["1 two 3", "1.5", "0x10", "+", "-", "--2", "1_000", "12x", "١",
     "0 1000000", f"{-2**63} {2**63 - 1}"],
)
def test_cli_rejects_invalid_tokens_or_excessive_range(text) -> None:
    result = subprocess.run(
        [sys.executable, str(SOURCE)], input=text, capture_output=True,
        text=True, timeout=10,
    )
    assert result.returncode != 0
    assert result.stdout == ""
    assert "error:" in result.stderr
