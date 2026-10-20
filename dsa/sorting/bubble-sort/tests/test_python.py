"""Behavior, comparison-order, and standalone CLI tests."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import random
import subprocess
import sys

import pytest

SOURCE = Path(__file__).parents[1] / "python" / "solution.py"
SPEC = spec_from_file_location("bubble_sort_under_test", SOURCE)
assert SPEC is not None and SPEC.loader is not None
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
SORT = MODULE.bubble_sort


@pytest.mark.parametrize("values", [
    [], [4], [2, 1], [1, 2], [1, 2, 3, 4], [4, 3, 2, 1],
    [7, 7, 7], [0, -1, 3, -1, 0], [-5, -2, -9],
    [-(2**63), 2**63 - 1, 0], [10**120, -10**120, 0],
])
def test_expected_order_and_input_preserved(values):
    original = list(values)
    result = SORT(values)
    assert result == sorted(values)
    assert isinstance(result, list)
    assert result is not values
    assert values == original


def test_accepts_tuple_and_generic_strings():
    assert SORT(("pear", "apple", "pear", "banana")) == [
        "apple", "banana", "pear", "pear"
    ]


def test_seeded_randomized_differential():
    rng = random.Random(7343)
    for _ in range(120):
        values = [rng.randint(-1000, 1000) for _ in range(rng.randrange(65))]
        original = list(values)
        assert SORT(values) == sorted(values)
        assert values == original


class Tagged:
    def __init__(self, key, tag):
        self.key = key
        self.tag = tag

    def __lt__(self, other):
        return self.key < other.key


def test_tagged_comparison_contract():
    values = [Tagged(2, "a"), Tagged(2, "b"), Tagged(1, "c")]
    result = SORT(values)
    assert [item.key for item in result] == [1, 2, 2]
    assert [item.tag for item in result] == ['c', 'a', 'b']
    assert [item.tag for item in values] == ["a", "b", "c"]
    assert all(any(item is original for original in values) for item in result)


def test_sorted_input_comparison_count():
    class Counted:
        comparisons = 0

        def __init__(self, value):
            self.value = value

        def __lt__(self, other):
            type(self).comparisons += 1
            return self.value < other.value

    SORT([Counted(i) for i in range(20)])
    assert Counted.comparisons == 19


@pytest.mark.parametrize(("text", "expected"), [
    ("", "\n"), (" \n\t", "\n"),
    ("3 -2 +1 0 -2\n", "-2 -2 0 1 3\n"),
    ("-9223372036854775808 9223372036854775807", "-9223372036854775808 9223372036854775807\n"),
    ("+0004 -0 0002", "0 2 4\n"),
])
def test_cli_valid(text, expected):
    result = subprocess.run([sys.executable, str(SOURCE)], input=text,
                            capture_output=True, text=True, check=True, timeout=10)
    assert result.stdout == expected
    assert result.stderr == ""


def test_cli_integer_larger_than_default_digit_limit():
    text = "1" + "0" * 4500
    result = subprocess.run([sys.executable, str(SOURCE)], input=text,
                            capture_output=True, text=True, check=True, timeout=10)
    assert result.stdout == text + "\n"


@pytest.mark.parametrize("token", ["abc", "1.2", "1e3", "3x", "--1", "+-1", "+", "-", "1_000", "0xff", "１２"])
def test_cli_rejects_malformed_tokens_without_partial_output(token):
    result = subprocess.run([sys.executable, str(SOURCE)], input="1 " + token + " 2",
                            capture_output=True, text=True, timeout=10)
    assert result.returncode != 0
    assert result.stdout == ""
    assert "error:" in result.stderr
    assert "Traceback" not in result.stderr
