"""Signed-byte boundaries, arbitrary precision, stability, and CLI behavior."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import random
import subprocess
import sys

import pytest

SOURCE = Path(__file__).parents[1] / "python" / "solution.py"
SPEC = spec_from_file_location("radix_sort_under_test", SOURCE)
assert SPEC is not None and SPEC.loader is not None
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
SORT = MODULE.radix_sort


@pytest.mark.parametrize("values", [
    [], [4], [2, 1], [1, 2], [1, 2, 3, 4], [4, 3, 2, 1],
    [0, 0, 0], [-7, -7, -7], [0, -1, 3, -1, 0], [-5, -2, -9],
    [-(2**63), 2**63 - 1, 0, -1, -(2**63), 2**63 - 1],
    [256, 255, 257, 0, -255, -256, -257, 65536, -65536],
    [513, 258, 257, 512, 1, 0, 256],
    [10**120, -10**120, 0, 10**120 - 1, -10**120 + 1],
])
def test_order_and_input_preserved(values):
    original = list(values)
    result = SORT(values)
    assert result == sorted(values)
    assert isinstance(result, list)
    assert result is not values
    assert values == original


def test_accepts_tuple():
    assert SORT((2, -1, 0)) == [-1, 0, 2]


def test_seeded_wide_integer_differential():
    rng = random.Random(7343)
    for _ in range(150):
        values = [rng.randrange(-(2**63), 2**63) for _ in range(rng.randrange(90))]
        original = list(values)
        assert SORT(values) == sorted(values)
        assert values == original
    for _ in range(30):
        values = [rng.randrange(-(2**512), 2**512) for _ in range(30)]
        assert SORT(values) == sorted(values)


def test_equal_native_integer_objects_keep_identity_order():
    # Equal int instances created independently expose stability without
    # broadening the native-int API to tagged records or subclassed integers.
    first, second, third = [int("100000000000000000000") for _ in range(3)]
    assert first is not second and second is not third
    values = [first, -5, second, 0, third]
    result = SORT(values)
    assert result[-3] is first
    assert result[-2] is second
    assert result[-1] is third


class IntSubclass(int):
    pass


@pytest.mark.parametrize("invalid", [True, False, 1.0, "1", None, IntSubclass(1)])
def test_invalid_value_types(invalid):
    with pytest.raises(TypeError, match="native Python ints"):
        SORT([1, invalid, 0])
    with pytest.raises(TypeError):
        SORT([invalid])


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


def test_cli_large_integer_digit_limit():
    value = "1" + "0" * 4500
    result = subprocess.run([sys.executable, str(SOURCE)], input=value + " 0 -" + value,
                            capture_output=True, text=True, check=True, timeout=10)
    assert result.stdout == "-" + value + " 0 " + value + "\n"


@pytest.mark.parametrize("token", ["abc", "1.2", "1e3", "3x", "--1", "+-1", "+", "-", "1_000", "0xff", "１２"])
def test_cli_rejects_malformed_tokens(token):
    result = subprocess.run([sys.executable, str(SOURCE)], input="1 " + token + " 2",
                            capture_output=True, text=True, timeout=10)
    assert result.returncode != 0
    assert result.stdout == ""
    assert "error:" in result.stderr
    assert "Traceback" not in result.stderr
