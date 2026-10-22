import copy
import json
import subprocess
import sys
import pytest


def test_independent_vectors(python_algorithm,cases):
    for case,expected in cases.vectors():
        saved=copy.deepcopy(case)
        cases.check(python_algorithm.solve(**case),expected,case)
        assert case==saved


def test_invalid_contract(python_algorithm,cases):
    for case in cases.invalid():
        with pytest.raises((ValueError,TypeError)):
            python_algorithm.solve(**case)


def test_boundaries(python_algorithm,cases):
    cases.boundaries(python_algorithm)


def test_executable(python_algorithm,cases):
    case,expected=cases.vectors()[-1]
    result=subprocess.run([sys.executable,python_algorithm.__file__],input=json.dumps(case),text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and not result.stderr
    cases.check(json.loads(result.stdout),expected,case)
    result=subprocess.run([sys.executable,python_algorithm.__file__],input=json.dumps(cases.invalid()[0]),text=True,capture_output=True,timeout=10)
    assert result.returncode==2 and result.stderr.startswith('error:')


def test_structure_after_every_operation(python_algorithm,cases):
    for case,_ in cases.vectors():
        tree=getattr(python_algorithm,cases.CLASS)(case['degree']);state=set()
        for op in case['operations']:
            if op[0]==0:tree.insert(op[1]);state.add(op[1])
            elif op[0]==1:tree.erase(op[1]);state.discard(op[1])
            cases.structure(tree,state)
