"""Independent positional-oracle tests, including repeated values and restoration."""
import copy
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys

import pytest


def oracle(values, k=2):
    return [list(row) for row in itertools.combinations(values, k)]


def call(module, values, k=2):
    return module.combinations(values, k)


@pytest.mark.parametrize("values", [[], [7], [2, 1], [1, 1, 2], [-2, 0, 2],
                                   [-2**63, 0, 2**63-1]])
def test_expected_order_empty_duplicates_and_no_mutation(python_algorithm, values):
    for k in range(len(values)+2):
        before=copy.deepcopy(values)
        expected=oracle(values, k)
        result=call(python_algorithm, values, k)
        assert result==expected and values==before
        assert call(python_algorithm, tuple(values), k)==expected
        if result:
            result[0].append(999)
            assert values==before
            assert call(python_algorithm, values, k)==expected


def test_exhaustive_small_and_seeded_inputs(python_algorithm):
    for size in range(6):
        for values in itertools.product((-1, 0, 1), repeat=size):
            for k in range(len(values)+2):
                assert call(python_algorithm, values, k)==oracle(values, k)
    rng=random.Random(20261023)
    for size in range(8):
        values=[rng.randrange(-3, 4) for _ in range(size)]
        for k in range(len(values)+2):
            assert call(python_algorithm, values, k)==oracle(values, k)


@pytest.mark.parametrize("value", [True, 1.0, "1", None])
def test_invalid_element_types(python_algorithm, value):
    with pytest.raises(TypeError):
        call(python_algorithm, [value])


def test_int_subclass_rejected_and_large_native_ints_supported(python_algorithm):
    class Integer(int):
        pass
    with pytest.raises(TypeError):
        call(python_algorithm, [Integer(1)])
    values=[-(1<<4096), 1<<4096]
    assert call(python_algorithm, values, 1)==oracle(values, 1)


@pytest.mark.parametrize("text", ["two", "+", "1 2x", "1 ١", "1 1.0", "1_0", "1\x002"])
def test_python_cli_invalid(text):
    source=Path(__file__).parents[1]/"python/solution.py"
    result=subprocess.run([sys.executable,str(source)],input=text,text=True,
                          capture_output=True,timeout=10)
    assert result.returncode!=0 and result.stdout=="" and "error:" in result.stderr


def test_python_cli_exact_json():
    source=Path(__file__).parents[1]/"python/solution.py"
    for text, expected in [('0', [[]]), ('1 1 1', [[1], [1]]), ('2 1 2', [[1, 2]]), ('3 1 2', [])]:
        result=subprocess.run([sys.executable,str(source)],input=text,text=True,
                              capture_output=True,timeout=10,check=True)
        assert result.stdout==json.dumps(expected,separators=(",", ":"))+"\n"
        assert result.stderr==""


@pytest.mark.parametrize("k,error", [(-1,ValueError),(True,TypeError),(1.0,TypeError),(None,TypeError)])
def test_invalid_k(python_algorithm,k,error):
    with pytest.raises(error):
        python_algorithm.combinations([],k)

