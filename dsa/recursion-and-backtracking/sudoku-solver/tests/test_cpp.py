"""Execute C++ API and standalone parser under both supported standards."""
import json
import subprocess
import pytest


@pytest.mark.cpp
def test_cpp_independent_oracles_and_invalid_values(cpp_api,cases):
    invoke=cpp_api(cases.CPP_BODY)
    rows=cases.valid_cases()+[(v,{"error":"invalid_argument"})
                              for v,e in cases.invalid_cases() if e is ValueError]
    assert invoke("\n".join(cases.serialize(v) for v,_ in rows))==[r for _,r in rows]


@pytest.mark.cpp
def test_cpp_cli_and_overflow_rejection(cpp_cli,cases):
    for text,expected in cases.CLI_VALID:
        proc=subprocess.run([str(cpp_cli)],input=text,text=True,
                            capture_output=True,timeout=20,check=True)
        assert proc.stdout==json.dumps(expected,separators=(",",":"))+"\n"
        assert proc.stderr==""
    for text in cases.CLI_INVALID+["9223372036854775808","-9223372036854775809"]:
        proc=subprocess.run([str(cpp_cli)],input=text,text=True,
                            capture_output=True,timeout=20)
        assert proc.returncode!=0 and proc.stdout=="" and "error:" in proc.stderr


@pytest.mark.cpp
def test_cpp_multiple_solutions_deterministic_and_valid(cpp_api,cases,python_algorithm):
    invoke=cpp_api(cases.CPP_BODY)
    board=[[0]*9 for _ in range(9)]
    first,second=invoke(cases.serialize(board)+"\n"+cases.serialize(board))
    cases.solved(first,board)
    assert first==second==python_algorithm.solve_sudoku(board)
