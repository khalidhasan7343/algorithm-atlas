import json
import subprocess
import sys
import pytest


def test_representation_oracle(python_algorithm, oracle):
    for value in oracle.count_vectors():
        assert python_algorithm.solve(value) == oracle.bit_count(value)


def test_boundary_interpretation(python_algorithm):
    assert python_algorithm.solve(0) == 0
    assert python_algorithm.solve(-1) == 32
    assert python_algorithm.solve(-2147483648) == 1
    assert python_algorithm.solve(2147483647) == 31
    for bit in range(31):
        assert python_algorithm.solve(2**bit) == 1
        assert python_algorithm.solve(-2**bit) == 32-bit


def test_invalid(python_algorithm):
    for value in (None,True,False,1.0,"1",[],2147483648,-2147483649):
        with pytest.raises(ValueError): python_algorithm.solve(value)


def test_cli(python_algorithm, oracle):
    for value in oracle.count_vectors()[:12]:
        result = subprocess.run([sys.executable,python_algorithm.__file__],input=str(value),text=True,capture_output=True,timeout=10)
        assert result.returncode == 0 and not result.stderr
        assert json.loads(result.stdout) == oracle.bit_count(value)
    for text in ("", "0 1", "2147483648", "-2147483649", "0x10", "1.0", "true", "+", "0"*12):
        result = subprocess.run([sys.executable,python_algorithm.__file__],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode == 2 and result.stderr.startswith("error:") and not result.stdout
