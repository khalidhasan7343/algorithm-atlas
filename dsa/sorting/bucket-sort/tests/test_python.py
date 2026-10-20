"""Domain, stability, distribution, custom count, and CLI behavior tests."""

from decimal import Decimal
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
import math
from pathlib import Path
import random
import subprocess
import sys

import pytest

SOURCE = Path(__file__).parents[1] / "python" / "solution.py"
SPEC = spec_from_file_location("bucket_sort_under_test", SOURCE)
assert SPEC is not None and SPEC.loader is not None
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
SORT = MODULE.bucket_sort


@pytest.mark.parametrize("values", [
    [], [0.5], [0], [1], [0.0, 1.0], [1.0, 0.0],
    [0.2, 0.1, 0.7, 0.2, 0.0, 1.0], [0.0] * 10, [1.0] * 10,
    [0.5] * 10, [0.0, 0.25, 0.5, 0.75, 1.0],
    [1.0, 0.75, 0.5, 0.25, 0.0],
    [math.nextafter(1.0, 0.0), 1.0, math.nextafter(0.0, 1.0), 0.0],
    [0.25, math.nextafter(0.25, 0.0), math.nextafter(0.25, 1.0), 0.0],
])
@pytest.mark.parametrize("bucket_count", [None, 1, 3, 20])
def test_known_order_and_input_preserved(values, bucket_count):
    original = list(values)
    result = SORT(values, bucket_count=bucket_count)
    assert result == sorted(values)
    assert isinstance(result, list)
    assert result is not values
    assert values == original


def test_tuple_input_and_original_object_stability():
    positive_zero = float("0.0")
    negative_zero = float("-0.0")
    second_negative_zero = float("-0.0")
    first_half, second_half = float("0.5"), float("0.5")
    values = (first_half, positive_zero, negative_zero, 0, second_half,
              second_negative_zero, 1)
    result = SORT(values, bucket_count=2)
    expected = [positive_zero, negative_zero, 0, second_negative_zero,
                first_half, second_half, 1]
    assert [id(value) for value in result] == [id(value) for value in expected]
    assert math.copysign(1, result[0]) == 1
    assert math.copysign(1, result[1]) == -1


def test_seeded_uniform_clustered_and_reverse_differential():
    rng = random.Random(7343)
    for _ in range(100):
        values = [rng.random() for _ in range(rng.randrange(100))]
        original = list(values)
        for bucket_count in (None, 1, 7):
            assert SORT(values, bucket_count=bucket_count) == sorted(values)
        assert values == original
    clustered = [0.5 + i * 1e-9 for i in reversed(range(500))]
    assert SORT(clustered) == sorted(clustered)
    assert SORT(clustered, bucket_count=1) == sorted(clustered)


class IntSubclass(int):
    pass


class FloatSubclass(float):
    pass


@pytest.mark.parametrize("value", [
    True, False, "0.5", None, Decimal("0.5"), Fraction(1, 2),
    IntSubclass(0), FloatSubclass(0.5),
])
def test_invalid_element_types(value):
    with pytest.raises(TypeError, match="native int/float"):
        SORT([value])


@pytest.mark.parametrize("value", [
    -0.1, 1.1, math.nextafter(1.0, math.inf),
    math.nextafter(0.0, -math.inf), float("nan"), float("inf"),
    -float("inf"), 10**1000, -10**1000,
])
def test_invalid_domain(value):
    with pytest.raises(ValueError, match="finite values"):
        SORT([0.5, value])


@pytest.mark.parametrize("count", [True, False, 1.0, "2", IntSubclass(2)])
def test_invalid_bucket_count_type_even_for_empty_input(count):
    with pytest.raises(TypeError, match="bucket_count"):
        SORT([], bucket_count=count)


@pytest.mark.parametrize("count", [0, -1, sys.maxsize + 1])
def test_invalid_bucket_count_value_even_for_empty_input(count):
    with pytest.raises(ValueError, match="bucket_count"):
        SORT([], bucket_count=count)


@pytest.mark.parametrize(("text", "expected"), [
    ("", "\n"), (" \n\t", "\n"),
    ("1 .5 0 2.5e-1 +7.5E-1", "0 0.25 0.5 0.75 1\n"),
    ("-0 +0.0 1.", "-0 0 1\n"),
])
def test_cli_known_output(text, expected):
    result = subprocess.run([sys.executable, str(SOURCE)], input=text,
                            capture_output=True, text=True, check=True, timeout=10)
    assert result.stdout == expected
    assert result.stderr == ""


def test_cli_subnormal_and_endpoint_roundtrip():
    values = [math.nextafter(1.0, 0.0), 1.0, math.nextafter(0.0, 1.0), 0.0]
    result = subprocess.run([sys.executable, str(SOURCE)],
                            input=" ".join(map(repr, values)), capture_output=True,
                            text=True, check=True, timeout=10)
    assert [float(token) for token in result.stdout.split()] == sorted(values)


@pytest.mark.parametrize("token", [
    "abc", "1x", "--1", "+-1", "+", "-", ".", "1e", "1e+", "1_0",
    "0x1", "１２", "nan", "inf", "-inf", "-0.1", "1.1", "1e999",
])
def test_cli_invalid_tokens_no_partial_output(token):
    result = subprocess.run([sys.executable, str(SOURCE)], input="0.5 " + token,
                            capture_output=True, text=True, timeout=10)
    assert result.returncode != 0
    assert result.stdout == ""
    assert "error:" in result.stderr
    assert "Traceback" not in result.stderr
