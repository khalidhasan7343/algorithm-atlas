"""Independent first-match oracles, boundaries, contracts, and CLI tests."""

import importlib.util
from itertools import product
from pathlib import Path
import random
import subprocess
import sys

import pytest

SOURCE = Path(__file__).parents[1] / "python/solution.py"
spec = importlib.util.spec_from_file_location("linear_search_module", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
search = module.linear_search
ORDERED = False


def oracle(values, target):
    return next((i for i, value in enumerate(values) if value == target), -1)


@pytest.mark.parametrize("values,target,expected", [
    ([], 0, -1), ([5], 5, 0), ([5], 4, -1), ([5], 6, -1),
    ([0, 0, 0], 0, 0), ([0, 0, 0], 1, -1),
    ([-9, -4, -4, 0, 2, 2, 8], -4, 1),
    ([-9, -4, -4, 0, 2, 2, 8], 2, 4),
    ([-9, -4, -4, 0, 2, 2, 8], -9, 0),
    ([-9, -4, -4, 0, 2, 2, 8], 8, 6),
    ([-9, -4, -4, 0, 2, 2, 8], 1, -1),
    ([-2**63, -2**63, 0, 2**63-1], -2**63, 0),
    ([-2**63, -2**63, 0, 2**63-1], 2**63-1, 3),
])
def test_known_first_index_and_input_preservation(values, target, expected):
    before = values[:]
    assert search(values, target) == expected
    assert values == before
    assert search(tuple(values), target) == expected
    if ORDERED:
        assert search(values, target, validate=False) == expected


def test_exhaustive_small_arrays_against_independent_scan():
    for size in range(8):
        for keys in product((-2, 0, 2), repeat=size):
            values = sorted(keys) if ORDERED else list(keys)
            before = values[:]
            for target in range(-3, 4):
                expected = oracle(values, target)
                assert search(values, target) == expected
                if ORDERED:
                    assert search(values, target, validate=False) == expected
            assert values == before


def test_seeded_random_large_arrays_and_missing_gaps():
    rng = random.Random(20261022)
    for size in (0, 1, 2, 3, 4, 7, 8, 9, 15, 16, 17, 31, 32,
                 33, 63, 64, 65, 127, 128, 129, 257, 1025, 65537):
        values = [rng.randrange(-1000, 1001) for _ in range(size)]
        if ORDERED:
            values.sort()
        for target in (-1001, -1000, -1, 0, 1, 1000, 1001):
            assert search(values, target) == oracle(values, target)
            if ORDERED:
                assert search(values, target, validate=False) == oracle(values, target)


def test_arbitrary_precision_keys():
    enormous = 1 << 16384
    values = [-enormous, -enormous, -1, 0, enormous]
    for target in values + [-enormous + 1, enormous - 1, enormous + 1]:
        assert search(values, target) == oracle(values, target)


@pytest.mark.parametrize("text,expected", [
    ("7", "-1\n"), ("0 0", "0\n"), ("0 -2 0 0 3", "1\n"),
    ("-4 -9 -4 -4 0 2 2 8", "1\n"), ("1 -9 -4 -4 0 2 2 8", "-1\n"),
    ("+03\n-0\t+3 3 8", "1\n"),
    ("-9223372036854775808 -9223372036854775808 9223372036854775807", "0\n"),
])
def test_cli_exact_output(text, expected):
    result = subprocess.run([sys.executable, str(SOURCE)], input=text,
                            text=True, capture_output=True, timeout=10)
    assert result.returncode == 0 and result.stdout == expected
    assert result.stderr == ""


@pytest.mark.parametrize("text", [
    "", " \n\t", "+", "1 2x", "1 2.0", "1 +", "1 ١", "1 --2",
    "1 +-2", "1 0x1", "1 1_0", "1 1e0", "1\x002",
])
def test_cli_invalid_tokens_fail_without_partial_output(text):
    result = subprocess.run([sys.executable, str(SOURCE)], input=text,
                            text=True, capture_output=True, timeout=10)
    assert result.returncode != 0 and result.stdout == ""
    assert "error:" in result.stderr


def test_cli_integer_digit_conversion_limit_is_disabled():
    huge = "9" * 5000
    result = subprocess.run([sys.executable, str(SOURCE)], input=f"{huge} 0 {huge}",
                            text=True, capture_output=True, timeout=10)
    assert result.returncode == 0 and result.stdout == "1\n"
    assert result.stderr == ""


def test_unordered_data_and_equality_without_ordering():
    values = [4, -2, 4, 0, -2]
    assert search(values, -2) == 1
    assert search([{"key": 1}, {"key": 2}, {"key": 1}], {"key": 1}) == 0
    assert search(["bee", "ant", "bee"], "bee") == 0


def test_early_match_does_not_inspect_later_elements():
    class Forbidden:
        def __eq__(self, other):
            raise AssertionError("suffix must not be inspected")

    assert search([7, Forbidden()], 7) == 0

