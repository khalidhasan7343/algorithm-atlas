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


def snapshot(machine):
    return [[machine.depth[i],machine.failure[i],machine.output_link[i],
             *machine.goto[i],*machine.terminal[i]] for i in range(len(machine.goto))]


def test_structure_and_reuse(python_algorithm, oracle, structure):
    for text,patterns in oracle.multi_vectors():
        original = list(patterns)
        machine = python_algorithm.AhoCorasick(patterns)
        saved = snapshot(machine)
        structure.automaton(patterns,saved)
        patterns.append(b"changed")
        for query in (text,b"",b"aaaaa",b"\0\xffab"):
            assert machine.find(query) == oracle.multi(query,original)
        assert snapshot(machine) == saved
    machine = python_algorithm.AhoCorasick([b"x"*4096])
    assert machine.find(b"a"*10000) == []
    assert python_algorithm.solve(b"",[b""]*256) == [[0,i,0] for i in range(256)]
    with pytest.raises(ValueError): machine.find(b"x"*10001)
    with pytest.raises(ValueError): machine.find("abc")


