import json
import subprocess
import pytest

pytestmark=pytest.mark.cpp


def test_independent_vectors(cpp_api, cases, python_algorithm):
    vectors=cases.vectors()
    run=cpp_api(cases.DRIVER)
    outputs=run(str(len(vectors))+'\n'+''.join(cases.encode(c) for c,_ in vectors))
    assert outputs==[expected for _,expected in vectors]
    assert outputs==[python_algorithm.solve(**case) for case,_ in vectors]


def test_cli_and_invalid_tokens(cpp_cli, cases):
    case,expected=cases.vectors()[25]
    result=subprocess.run([str(cpp_cli)],input=cases.encode(case),text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and json.loads(result.stdout)==expected and not result.stderr
    for text in cases.invalid_cli():
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and result.stderr.startswith('error:'),text


def test_boundary_api(cpp_api, cases):
    assert cpp_api(cases.BOUNDARY_DRIVER)('')==[True]
