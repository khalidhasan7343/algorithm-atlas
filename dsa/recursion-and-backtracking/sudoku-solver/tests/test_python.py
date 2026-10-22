"""Contract and independent-oracle tests for this algorithm."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import pytest


def test_independent_cases_order_and_input_restoration(python_algorithm, cases):
    for value,expected in cases.valid_cases():
        before=copy.deepcopy(value)
        result=cases.call(python_algorithm,value)
        assert result==expected and value==before
        assert cases.call(python_algorithm,value)==expected
        if isinstance(result,list) and result:
            if isinstance(result[0],list):
                result[0].append(999)
            else:
                result.append("changed")
            assert value==before and cases.call(python_algorithm,value)==expected


def test_invalid_inputs(python_algorithm, cases):
    for value,error in cases.invalid_cases():
        before=copy.deepcopy(value)
        with pytest.raises(error):
            cases.call(python_algorithm,value)
        assert value==before


def test_cli_valid_and_invalid(cases):
    source=Path(__file__).parents[1]/"python/solution.py"
    for text,expected in cases.CLI_VALID:
        proc=subprocess.run([sys.executable,str(source)],input=text,text=True,
                            capture_output=True,timeout=20,check=True)
        assert proc.stdout==json.dumps(expected,separators=(",",":"))+"\n"
        assert proc.stderr==""
    for text in cases.CLI_INVALID:
        proc=subprocess.run([sys.executable,str(source)],input=text,text=True,
                            capture_output=True,timeout=20)
        assert proc.returncode!=0 and proc.stdout=="" and "error:" in proc.stderr


def test_multiple_solutions_empty_board_and_immutable_rows(python_algorithm,cases):
    board=tuple(tuple(0 for _ in range(9)) for _ in range(9))
    result=python_algorithm.solve_sudoku(board)
    cases.solved(result,board)
    assert result[0]==list(range(1,10))
    assert python_algorithm.solve_sudoku(board)==result


def test_int_subclass_rejected(python_algorithm):
    class Integer(int): pass
    board=[[0]*9 for _ in range(9)];board[0][0]=Integer(1)
    with pytest.raises(TypeError): python_algorithm.solve_sudoku(board)
