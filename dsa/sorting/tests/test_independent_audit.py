"""Independent final-review oracles; built-in sorting is used only in tests.

Seed 20261021 intentionally differs from the implementation suites' seed.
Exhaustive bounds are small enough for the default suite and CI.
"""

from bisect import bisect_left, bisect_right
import importlib.util
from itertools import product
import math
from pathlib import Path
import random
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
INTEGER_NAMES = (
    "bubble-sort", "selection-sort", "insertion-sort", "merge-sort",
    "quick-sort", "heap-sort", "counting-sort", "radix-sort",
    "shell-sort", "tim-sort",
)
ALL_NAMES = (*INTEGER_NAMES, "bucket-sort")
STABLE_GENERIC = ("bubble-sort", "insertion-sort", "merge-sort", "tim-sort")


def load(name):
    spec = importlib.util.spec_from_file_location(
        "audit_" + name.replace("-", "_"), ROOT / name / "python/solution.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULES = {name: load(name) for name in ALL_NAMES}


def function(name):
    return getattr(MODULES[name], name.replace("-", "_"))


@pytest.mark.parametrize("name", INTEGER_NAMES)
def test_exhaustive_integer_oracle_and_no_mutation(name):
    sort = function(name)
    checked = 0
    for size in range(9):
        for items in product((-2, 0, 2), repeat=size):
            source = list(items)
            result = sort(source)
            assert result == sorted(items), (name, items)
            assert source == list(items)
            assert result is not source
            checked += 1
    assert checked == 9841


def test_exhaustive_bucket_oracle_all_endpoints_and_counts():
    checked = 0
    sort = function("bucket-sort")
    for size in range(8):
        for items in product((0.0, 0.25, 0.5, 1.0), repeat=size):
            source = list(items)
            for count in (None, 1, 3, 7):
                assert sort(source, bucket_count=count) == sorted(items)
                assert source == list(items)
                checked += 1
    assert checked == 87380


@pytest.mark.parametrize("name", INTEGER_NAMES)
def test_seeded_patterns_boundaries_and_large_input(name):
    rng = random.Random(20261021)
    sort = function(name)
    maximum = 512 if name in ("bubble-sort", "selection-sort", "insertion-sort") else 8193
    for size in (0, 1, 2, 31, 32, 63, 64, 65, 127, 128, 129, 257, maximum):
        cases = [list(range(size)), list(range(size - 1, -1, -1)), [7] * size,
                 [rng.randrange(-16, 17) for _ in range(size)]]
        for source in cases:
            before = source[:]
            assert sort(source) == sorted(source)
            assert source == before
    if name == "counting-sort":
        for center in (-(2**63), 2**63 - 5, -(2**16384), 2**16384):
            source = [center + rng.randrange(5) for _ in range(257)]
            assert sort(source, max_range=5) == sorted(source)
            with pytest.raises(ValueError):
                sort([center, center + 5], max_range=5)
    else:
        source = [-(2**63), 2**63 - 1, 0, -1, 1] * 13
        source += [rng.getrandbits(bits) * rng.choice((-1, 1))
                   for bits in (512, 1024, 4096) for _ in range(12)]
        assert sort(source) == sorted(source)


class Record:
    def __init__(self, key, tag):
        self.key, self.tag = key, tag

    def __lt__(self, other):
        return self.key < other.key


@pytest.mark.parametrize("name", STABLE_GENERIC)
def test_tagged_stability_against_independent_oracle(name):
    rng = random.Random(20261021)
    for size in (0, 1, 2, 31, 63, 64, 65, 127, 128, 129, 513):
        keys = [rng.randrange(9) for _ in range(size)]
        for sequence in (keys, list(reversed(sorted(keys)))):
            source = [Record(key, tag) for tag, key in enumerate(sequence)]
            result = function(name)(source)
            assert result == sorted(source, key=lambda item: item.key)
            assert [item.tag for item in source] == list(range(size))


def test_bucket_identity_stability_signed_zero_and_index_boundaries():
    rng = random.Random(20261021)
    values = [-0.0, 0.0, 0, float("1"), 1, math.nextafter(1.0, 0.0),
              math.nextafter(0.0, 1.0)] * 17
    values += [rng.random() for _ in range(1001)]
    expected = sorted(values)
    for count in (None, 1, 2, 3, 17, 1024):
        result = function("bucket-sort")(values, bucket_count=count)
        assert all(actual is wanted for actual, wanted in zip(result, expected))
        assert len(result) == len(expected)


@pytest.mark.parametrize("name", ("counting-sort", "radix-sort"))
def test_native_integer_occurrences_preserve_identity_order(name):
    # Separate conversions create distinguishable native ints with equal keys.
    source = [int(text) for text in ("10001", "-10002", "10001", "-10002")]
    assert source[0] is not source[2] and source[1] is not source[3]
    result = function(name)(source)
    expected = sorted(source)
    assert all(actual is wanted for actual, wanted in zip(result, expected))


@pytest.mark.parametrize(("name", "source", "expected"), (
    ("bubble-sort", [5, 1, 4, 2], [1, 2, 4, 5]),
    ("selection-sort", [5, 1, 4, 2], [1, 2, 4, 5]),
    ("insertion-sort", [5, 2, 4, 2, 1], [1, 2, 2, 4, 5]),
    ("merge-sort", [5, 1, 4, 2, 8], [1, 2, 4, 5, 8]),
    ("quick-sort", [4, 2, 4, 1, 3], [1, 2, 3, 4, 4]),
    ("heap-sort", [4, 10, 3, 5, 1], [1, 3, 4, 5, 10]),
    ("counting-sort", [2, -1, 2, 0, -1], [-1, -1, 0, 2, 2]),
    ("radix-sort", [256, -2, 1, -1, 0, 255], [-2, -1, 0, 1, 255, 256]),
    ("bucket-sort", [.42, .17, .39, .26, .72, .94, 1.0],
     [.17, .26, .39, .42, .72, .94, 1.0]),
    ("shell-sort", [23, 12, 1, 8, 34, 54, 2, 3, 7, 4],
     [1, 2, 3, 4, 7, 8, 12, 23, 34, 54]),
    ("tim-sort", [*range(96, 128), *range(64, 96), *range(32, 64), *range(32)],
     list(range(128))),
))
def test_documented_dry_run_results(name, source, expected):
    if name == "bucket-sort":
        assert function(name)(source, bucket_count=4) == expected
    else:
        assert function(name)(source) == expected


def minimum_pivot_adversary(size):
    """Assign ranks to symbolic items after simulating each minimum pivot.

    This constructs an input, not an expected-output oracle. Every remaining
    non-pivot item is greater, so the same swaps can be simulated symbolically.
    """
    positions = list(range(size))
    ranks = [None] * size
    for start in range(size):
        pivot = positions[start + (size - start) // 2]
        ranks[pivot] = start
        current, upper = start, size
        while current < upper:
            if positions[current] == pivot:
                current += 1
            else:
                upper -= 1
                positions[current], positions[upper] = positions[upper], positions[current]
    return ranks


def test_quick_worst_case_comparisons_and_bounded_actual_recursion():
    class Counted(Record):
        comparisons = 0

        def __lt__(self, other):
            Counted.comparisons += 1
            return self.key < other.key

    size = 256
    source = [Counted(key, i) for i, key in enumerate(minimum_pivot_adversary(size))]
    depth = peak = 0
    quick_path = str(ROOT / "quick-sort/python/solution.py")

    def profile(frame, event, arg):
        nonlocal depth, peak
        if frame.f_code.co_filename == quick_path and frame.f_code.co_name == "sort_range":
            if event == "call":
                depth += 1
                peak = max(peak, depth)
            elif event == "return":
                depth -= 1

    old_profile = sys.getprofile()
    try:
        sys.setprofile(profile)
        result = function("quick-sort")(source)
    finally:
        sys.setprofile(old_profile)
    assert [item.key for item in result] == list(range(size))
    assert Counted.comparisons >= size * size // 2
    assert 0 < peak <= math.ceil(math.log2(size)) + 2
    assert depth == 0


def test_tim_subrange_gallops_and_run_stack_invariants():
    tim = MODULES["tim-sort"]
    rng = random.Random(20261021)
    # Unlike suffix-only checks, both endpoints vary, including empty ranges.
    for size in range(33):
        values = sorted(rng.randrange(-5, 6) for _ in range(size))
        for start in range(size + 1):
            for end in range(start, size + 1):
                for pivot in (-6, -2, 0, 2, 6):
                    assert tim._gallop_bound(values, start, end, pivot, upper=False) == bisect_left(values, pivot, start, end)
                    assert tim._gallop_bound(values, start, end, pivot, upper=True) == bisect_right(values, pivot, start, end)
    # Independently check every pending pair/triple after each push/collapse.
    for _ in range(100):
        runs = []
        offset = 0
        for _ in range(200):
            length = rng.randrange(1, 1025)
            runs.append((offset, length))
            offset += length
            while (index := tim._collapse_choice(runs)) is not None:
                left, right = runs[index:index + 2]
                assert left[0] + left[1] == right[0]
                runs[index:index + 2] = [(left[0], left[1] + right[1])]
            assert all(a[1] > b[1] for a, b in zip(runs, runs[1:]))
            assert all(a[1] > b[1] + c[1] for a, b, c in zip(runs, runs[1:], runs[2:]))


@pytest.mark.parametrize("name", ALL_NAMES)
def test_python_cli_additional_token_contracts(name):
    command = [sys.executable, str(ROOT / name / "python/solution.py")]
    invalid = ("1e0", "1\x002", "++1", "−1", "1_0", "+-0", "1.0")
    valid = "+0001 -0 0 +1"
    if name == "bucket-sort":
        invalid = ("NaN", "Infinity", "0x1p-1", "1\x002", "1e+", "1.000001", "-0.001")
        valid = "+.0 1. .25 5e-1"
    expected = sorted(float(value) for value in valid.split())
    result = subprocess.run(command, input=valid, text=True, capture_output=True, timeout=10)
    assert result.returncode == 0 and result.stderr == ""
    assert list(map(float, result.stdout.split())) == expected
    for token in invalid:
        result = subprocess.run(command, input=token, text=True, capture_output=True, timeout=10)
        assert result.returncode != 0 and result.stdout == "" and result.stderr


@pytest.mark.cpp
def test_cpp_independent_exhaustive_randomized_and_boundary_matrix(cpp_compile):
    executable = cpp_compile(Path(__file__).parent / "fixtures/independent_audit.cpp")
    result = subprocess.run([str(executable)], text=True, capture_output=True, timeout=60, check=True)
    assert result.stderr == ""
    assert "integer_exhaustive=98410 bucket_exhaustive=87380" in result.stdout


@pytest.mark.cpp
@pytest.mark.parametrize("name", ALL_NAMES)
def test_cpp_cli_additional_overflow_and_token_contracts(name, cpp_compile):
    executable = cpp_compile(ROOT / name / "cpp/solution.cpp")
    invalid = ("9223372036854775808", "-9223372036854775809", "1e0", "1\x002", "++1", "−1", "+-0")
    valid = "+0001 -0 0 +1"
    if name == "bucket-sort":
        invalid = ("NaN", "Infinity", "0x1p-1", "1\x002", "1e+", "1.000001", "-0.001")
        valid = "+.0 1. .25 5e-1"
    result = subprocess.run([str(executable)], input=valid, text=True, capture_output=True, timeout=10)
    assert result.returncode == 0 and result.stderr == ""
    assert list(map(float, result.stdout.split())) == sorted(map(float, valid.split()))
    for token in invalid:
        result = subprocess.run([str(executable)], input=token, text=True, capture_output=True, timeout=10)
        assert result.returncode != 0 and result.stdout == "" and result.stderr
