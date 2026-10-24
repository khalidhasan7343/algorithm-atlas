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


def snapshot(tree):
    return [[node.start,node.end,node.suffix,
             *(x for pair in node.children.items() for x in pair)] for node in tree.nodes]


def test_structure_and_reuse(python_algorithm, oracle, structure):
    for text in oracle.palindrome_vectors():
        tree = python_algorithm.SuffixTree(text)
        saved = snapshot(tree)
        structure.suffix_tree(text,saved)
        for pattern in (b"",b"a",text[:4],b"\xff\0",b"x"*10000):
            expected = oracle.occurrences(text,pattern)
            assert tree.find(pattern) == expected
            assert tree.contains(pattern) == bool(expected)
        assert snapshot(tree) == saved
    tree = python_algorithm.SuffixTree(b"a"*2048)
    structure.suffix_tree(b"a"*2048,snapshot(tree))
    assert tree.find(b"a"*100) == list(range(1949))
    assert not tree.contains(b"a"*2049)
    with pytest.raises(ValueError): python_algorithm.SuffixTree(b"a"*2049)
    for pattern in ("a",b"a"*10001):
        with pytest.raises(ValueError): tree.find(pattern)
        with pytest.raises(ValueError): tree.contains(pattern)


