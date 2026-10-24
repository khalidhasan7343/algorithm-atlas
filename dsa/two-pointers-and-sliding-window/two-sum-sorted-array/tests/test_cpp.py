import json
import subprocess
import pytest

pytestmark=pytest.mark.cpp


def test_batched_oracles(cpp_driver, oracle, name, python_algorithm):
    read,expression=oracle.driver(name)
    body='int q;std::cin>>q;while(q--){'+read+'emit('+expression+r");std::cout<<'\n';}"
    cases=oracle.vectors(name)
    results=cpp_driver(body)(str(len(cases))+"\n"+"".join(oracle.encode(c) for c in cases))
    assert len(results)==len(cases)
    for args,result in zip(cases,results):
        assert result==oracle.expected(name,args)
        assert result==python_algorithm.solve(*args)


def test_invalid_and_boundary(cpp_driver, oracle, name):
    read,expression=oracle.driver(name)
    body='int q;std::cin>>q;while(q--){'+read+'int rejected=0;try{'+expression+';}catch(const std::invalid_argument&){rejected=1;}emit(rejected);'+r"std::cout<<'\n';}"
    body+=oracle.cpp_boundary(name)
    cases=oracle.invalid_numeric(name)
    assert cpp_driver(body)(str(len(cases))+"\n"+"".join(oracle.encode(c) for c in cases))==[1]*len(cases)


def test_cli(cpp_cli, oracle, name):
    for args in oracle.vectors(name)[:8]:
        result=subprocess.run([str(cpp_cli)],input=oracle.cli(args),text=True,capture_output=True,timeout=10)
        assert result.returncode==0 and not result.stderr
        assert json.loads(result.stdout)==oracle.expected(name,args)
    for data in oracle.invalid_cli(name):
        result=subprocess.run([str(cpp_cli)],input=data,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and result.stderr.startswith('error:') and not result.stdout
