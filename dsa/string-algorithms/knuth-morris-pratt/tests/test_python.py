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
    if name == "knuth-morris-pratt":
        for _,pattern in oracle.matching_vectors():
            assert python_algorithm.prefix_function(pattern) == oracle.lps(pattern)
        assert python_algorithm.solve(b"a"*10000,b"a"*127) == list(range(9874))
    elif name == "rabin-karp":
        a,b = b"\x00\x02",b"\x02\x00"
        assert python_algorithm.fingerprint(a,1,2) == python_algorithm.fingerprint(b,1,2)
        assert python_algorithm.solve(a,b,1,2) == []
        for text,pattern in oracle.matching_vectors():
            assert python_algorithm.solve(text,pattern,1,2) == oracle.occurrences(text,pattern)
        for base,mod in [(0,2),(True,2),(1,1),(1000000008,2)]:
            with pytest.raises(ValueError): python_algorithm.solve(b"",b"",base,mod)
        assert python_algorithm.solve(b"a"*10000,b"b") == []
    else:
        assert python_algorithm.solve(b"a"*10000,b"a") == list(range(10000))
