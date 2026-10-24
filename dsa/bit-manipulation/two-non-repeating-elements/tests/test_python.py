import json
import subprocess
import sys
import pytest


def test_frequency_oracle_and_core(python_algorithm, oracle, name):
    count = 1 if name == "xor-unique-elements" else 2
    core = python_algorithm.xor_candidate if count == 1 else python_algorithm.partition_candidates
    for values in oracle.xor_vectors(count):
        saved = list(values)
        expected = oracle.frequencies(values,count)
        assert python_algorithm.solve(values) == expected
        assert core(tuple(values)) == expected
        assert values == saved


def test_rejected_multiplicities(python_algorithm, oracle, name):
    count = 1 if name == "xor-unique-elements" else 2
    for values in oracle.invalid_xor(count):
        with pytest.raises(ValueError): python_algorithm.solve(values)
    # Numeric checks alone do not validate pair counts; only the explicitly
    # named candidate API accepts this unsupported multiplicity example.
    if count == 1:
        assert python_algorithm.xor_candidate([1,1,1]) == 1
    else:
        assert python_algorithm.partition_candidates([1,1,1,2]) == [1,2]


def test_numeric_contract(python_algorithm, name):
    count = 1 if name == "xor-unique-elements" else 2
    core = python_algorithm.xor_candidate if count == 1 else python_algorithm.partition_candidates
    for bad in (None,1,"1",{1},[True],[1.0],[-2147483649],[2147483648],[0]*10001):
        with pytest.raises(ValueError): python_algorithm.solve(bad)
        with pytest.raises(ValueError): core(bad)
    if count == 1:
        for bad in ([],[1,1]):
            with pytest.raises(ValueError): core(bad)
    else:
        for bad in ([],[1],[1,1],[0,1,2,3]):
            with pytest.raises(ValueError): core(bad)


def test_cli(python_algorithm, oracle, name):
    count = 1 if name == "xor-unique-elements" else 2
    for values in oracle.xor_vectors(count)[:6]:
        result = subprocess.run([sys.executable,python_algorithm.__file__],input=" ".join(map(str,values)),text=True,capture_output=True,timeout=10)
        assert result.returncode == 0 and not result.stderr
        assert json.loads(result.stdout) == oracle.frequencies(values,count)
    for data in ("", "1 1", "0x10", "1_0", "1.0", "2147483648", "-2147483649", "+", "--1", "９", "0"*12):
        result = subprocess.run([sys.executable,python_algorithm.__file__],input=data,text=True,capture_output=True,timeout=10)
        assert result.returncode == 2 and result.stderr.startswith("error:") and not result.stdout
