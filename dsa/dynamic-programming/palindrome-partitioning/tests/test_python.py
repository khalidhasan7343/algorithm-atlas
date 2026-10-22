"""Independent oracles, documented domains, mutation and CLI checks."""
import copy
import subprocess
import sys
from pathlib import Path
import pytest

def test_independent_vectors(python_algorithm,cases):
    for args,expected in cases.vectors():
        saved=copy.deepcopy(args)
        assert python_algorithm.minimum_palindrome_cuts(*args) == expected
        assert args==saved

def test_boundaries(python_algorithm):

    for text in [123,"\ud800","a"*1001]:
        with pytest.raises(ValueError):python_algorithm.minimum_palindrome_cuts(text)
    assert python_algorithm.minimum_palindrome_cuts("😀"*1000)==0

def test_cli():
    source=Path(__file__).parents[1]/'python/solution.py'
    result=subprocess.run([sys.executable,str(source)],input='aab\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='1' and not result.stderr
    for text in ['', 'a\nb\n', 'a\n\n']:
        result=subprocess.run([sys.executable,str(source)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')

def test_empty_and_invalid_utf8_cli():
    source=Path(__file__).parents[1]/'python/solution.py'
    result=subprocess.run([sys.executable,str(source)],input=b'\n',capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout==b'0\n'
    result=subprocess.run([sys.executable,str(source)],input=b'\xed\xa0\x80\n',capture_output=True,timeout=10)
    assert result.returncode==2 and not result.stdout
