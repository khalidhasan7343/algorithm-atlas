import subprocess
import sys
import pytest


def test_independent_oracles(python_algorithm, oracle, name, kind):
    for case in oracle.vectors(kind):
        args = (case,) if kind == "palindrome" else case
        assert python_algorithm.solve(*args) == oracle.expected(case,name), case


def test_invalid_contract(python_algorithm, kind):
    if kind == "palindrome":
        bad = [("abc",),(bytearray(b"a"),),(b"x"*10001,)]
    elif kind == "multi":
        bad = [(b"", "abc"),(b"", ["a"]),(b"", [b""]*257),(b"", [b"x"*4097]),(b"x"*10001,[])]
    else:
        bad = [("abc", b""),(b"", "a"),(None,b""),(bytearray(b"a"),b""),(b"",b"a"*10001),(b"x"*10001,b"")]
    for args in bad:
        with pytest.raises(ValueError): python_algorithm.solve(*args)


def test_executable(python_algorithm, oracle, name, kind):
    import json
    for case in oracle.vectors(kind)[:7]:
        result = subprocess.run([sys.executable,python_algorithm.__file__],input=oracle.encode(case,kind),text=True,capture_output=True,timeout=10)
        assert result.returncode == 0 and not result.stderr
        assert json.loads(result.stdout) == oracle.expected(case,name)
    for text in ("", "zz", "0", "- - extra"):
        result = subprocess.run([sys.executable,python_algorithm.__file__],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode == 2 and result.stderr.startswith("error:") and not result.stdout


def test_preprocessing_and_boundaries(python_algorithm, oracle, name):
    if name == "z-algorithm":
        for text,_ in oracle.matching_vectors():
            assert python_algorithm.z_array(text) == oracle.z_values(text)
        assert python_algorithm.z_array(b"a"*10000) == [0]+list(range(9999,0,-1))
    elif name == "boyer-moore":
        for _,pattern in oracle.matching_vectors():
            assert python_algorithm.good_suffix(pattern) == oracle.good_shifts(pattern)
            last = [-1]*256
            for i,ch in enumerate(pattern): last[ch] = i
            assert python_algorithm.bad_character(pattern) == last
        assert python_algorithm.solve(b"a"*10000,b"a"*127) == list(range(9874))
    else:
        odd,even,best = python_algorithm.solve(b"a"*10000)
        assert best == [0,10000]
        assert odd == [min(i+1,10000-i) for i in range(10000)]
        assert even == [min(i,10000-i) for i in range(10000)]
        assert python_algorithm.solve(b"babad")[2] == [0,3]
