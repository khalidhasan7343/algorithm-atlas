"""Independent oracles, documented domains, mutation and CLI checks."""
import copy
import subprocess
import sys
from pathlib import Path
import pytest

def test_independent_vectors(python_algorithm,cases):
    for args,expected in cases.vectors():
        saved=copy.deepcopy(args)
        assert python_algorithm.edit_distance(*args) == expected
        assert args==saved

def test_boundaries(python_algorithm):

    for args in [("x"*1001,""),("","x"*1001),("\ud800","x"),("x","\udfff"),(123,"x")]:
        with pytest.raises(ValueError):
            python_algorithm.edit_distance(*args)
    assert python_algorithm.edit_distance("a"*1000,"a"*1000)==0
    assert python_algorithm.edit_distance("","a"*1000)==1000
    assert python_algorithm.edit_distance("😀"*1000,"😀"*1000)==0

def test_cli():
    source=Path(__file__).parents[1]/'python/solution.py'
    result=subprocess.run([sys.executable,str(source)],input='kitten\nsitting\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='3' and not result.stderr
    for text in ['', 'one\n', 'a\nb\nextra\n', 'a\nb\n\n']:
        result=subprocess.run([sys.executable,str(source)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')

def test_invalid_utf8_cli():
    source=Path(__file__).parents[1]/"python/solution.py"
    for raw in [b'\xc0\xaf',b'\xed\xa0\x80',b'\xf4\x90\x80\x80',b'\x80',b'\xf0\x9f']:
        result=subprocess.run([sys.executable,str(source)],input=raw+b'\nx\n',capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith(b'error:')
