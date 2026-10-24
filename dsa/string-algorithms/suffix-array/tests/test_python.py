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


def test_index_reuse_and_boundary(python_algorithm, oracle):
    for text in oracle.palindrome_vectors():
        index = python_algorithm.SuffixArray(text)
        saved = (list(index.sa),list(index.lcp))
        for pattern in (b"",b"a",text[:4],b"\xff\0",b"x"*10000):
            assert index.find(pattern) == oracle.occurrences(text,pattern)
        assert (index.sa,index.lcp) == saved
        assert sorted(index.sa) == list(range(len(text)))
    index = python_algorithm.SuffixArray(b"a"*10000)
    assert index.sa == list(range(9999,-1,-1))
    assert index.lcp == list(range(10000))
    assert index.find(b"a"*127) == list(range(9874))
    for pattern in ("a",b"a"*10001):
        with pytest.raises(ValueError): index.find(pattern)


