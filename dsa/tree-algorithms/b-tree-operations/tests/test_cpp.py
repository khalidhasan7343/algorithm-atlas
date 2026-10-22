import json
import subprocess
import pytest

pytestmark=pytest.mark.cpp


def test_independent_vectors(cpp_api,cases,python_algorithm):
    vectors=cases.vectors();run=cpp_api(cases.DRIVER)
    actual=run(str(len(vectors))+'\n'+''.join(cases.encode(case) for case,_ in vectors))
    assert len(actual)==len(vectors)
    for output,(case,expected) in zip(actual,vectors):
        cases.check(output,expected,case)
        assert output==python_algorithm.solve(**case)


def test_cli_and_invalid(cpp_cli,cases):
    case,expected=cases.vectors()[-1]
    result=subprocess.run([str(cpp_cli)],input=cases.encode(case),text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and not result.stderr
    cases.check(json.loads(result.stdout),expected,case)
    for text in cases.invalid_cli():
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and result.stderr.startswith('error:'),text


def test_boundary_api(cpp_api,cases):
    assert cpp_api(cases.BOUNDARY_DRIVER)('')==[True]


def test_structure_after_every_operation(cpp_api,cases):
    vectors=cases.vectors()
    outputs=cpp_api(cases.INVARIANT_DRIVER)(str(len(vectors))+'\n'+''.join(cases.encode(case) for case,_ in vectors))
    for snapshots,(case,_) in zip(outputs,vectors):
        state=set();assert len(snapshots)==len(case['operations'])
        for snapshot,op in zip(snapshots,case['operations']):
            if op[0]==0:state.add(op[1])
            elif op[0]==1:state.discard(op[1])
            cases._o.check_multiway_snapshot(snapshot,state,case['degree'],cases.PLUS)
    assert len(outputs)==len(vectors)
