import json
import subprocess
import pytest

pytestmark=pytest.mark.cpp


def test_batched_oracles(cpp_driver, oracle, python_algorithm, name):
    function,arity=oracle.FUNCTIONS[name]
    call=function+"("+",".join(f"a[{i}]" for i in range(arity))+")"
    body=f"int q;std::cin>>q;while(q--){{std::vector<Integer> a({arity});for(auto& x:a)std::cin>>x;emit({call});"+r"std::cout<<'\n';}"
    cases=oracle.vectors(name)
    actual=cpp_driver(body)(str(len(cases))+"\n"+"\n".join(" ".join(map(str,c)) for c in cases))
    assert len(actual)==len(cases)
    for args,result in zip(cases,actual):
        oracle.check(name,args,result)
        assert result==python_algorithm.solve(*args)


def test_invalid_and_boundaries(cpp_driver, oracle, name):
    function,arity=oracle.FUNCTIONS[name]
    call=function+"("+",".join(f"a[{i}]" for i in range(arity))+")"
    body=f"int q;std::cin>>q;while(q--){{std::vector<Integer> a({arity});for(auto& x:a)std::cin>>x;int rejected=0;try{{{call};}}catch(const std::invalid_argument&){{rejected=1;}}emit(rejected);"+r"std::cout<<'\n';}"
    if name=="sieve-of-eratosthenes":
        body+='auto primes=sieve(1000000);if(primes.size()!=78498 || primes.back()!=999983)return 3;'
    cases=oracle.invalid_numeric(name)
    assert cpp_driver(body)(str(len(cases))+"\n"+"\n".join(" ".join(map(str,c)) for c in cases))==[1]*len(cases)


def test_cli(cpp_cli, oracle, name):
    for args in oracle.vectors(name)[:8]:
        result=subprocess.run([str(cpp_cli)],input=" ".join(map(str,args)),text=True,capture_output=True,timeout=10)
        assert result.returncode==0 and not result.stderr
        oracle.check(name,args,json.loads(result.stdout))
    for data in ("", "0x10", "+", "1.0", "９", "1 "*4, "0"*21):
        result=subprocess.run([str(cpp_cli)],input=data,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and result.stderr.startswith("error:") and not result.stdout
