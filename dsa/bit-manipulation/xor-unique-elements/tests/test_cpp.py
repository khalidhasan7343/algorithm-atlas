import json
import subprocess
import pytest

pytestmark = pytest.mark.cpp


def test_batched_frequency_and_core(cpp_driver, oracle, python_algorithm, name):
    count = 1 if name == "xor-unique-elements" else 2
    core = "xor_candidate" if count == 1 else "partition_candidates"
    body = "int q;std::cin>>q;while(q--){std::size_t n;std::cin>>n;std::vector<Value> v(n);for(auto& x:v)std::cin>>x;auto saved=v;auto a=solve(v);if(a!="+core+r"(v)||v!=saved)return 3;emit(a);std::cout<<'\n';}"
    cases = oracle.xor_vectors(count)
    actual = cpp_driver(body)(str(len(cases))+"\n"+"".join(oracle.encode(v) for v in cases))
    assert len(actual) == len(cases)
    for values,result in zip(cases,actual):
        assert result == oracle.frequencies(values,count)
        assert result == python_algorithm.solve(values)


def test_invalid_api(cpp_driver, oracle, name):
    count = 1 if name == "xor-unique-elements" else 2
    core = "xor_candidate" if count == 1 else "partition_candidates"
    body = r"int q;std::cin>>q;while(q--){std::size_t n;std::cin>>n;std::vector<Value> v(n);for(auto& x:v)std::cin>>x;int rejected=0;try{solve(v);}catch(const std::invalid_argument&){rejected=1;}emit(rejected);std::cout<<'\n';}"
    body += "try{"+core+r"({2147483648LL});return 4;}catch(const std::invalid_argument&){}"
    body += "try{"+core+r"({-2147483649LL});return 5;}catch(const std::invalid_argument&){}"
    if count == 1:
        body += 'if(xor_candidate({1,1,1})!=1)return 6;'
    else:
        body += 'if(partition_candidates({1,1,1,2})!=std::vector<Value>({1,2}))return 6;'
    cases = oracle.invalid_xor(count)+[[2147483648],[-2147483649]]
    assert cpp_driver(body)(str(len(cases))+"\n"+"".join(oracle.encode(v) for v in cases)) == [1]*len(cases)


def test_cli(cpp_cli, oracle, name):
    count = 1 if name == "xor-unique-elements" else 2
    for values in oracle.xor_vectors(count)[:6]:
        result = subprocess.run([str(cpp_cli)],input=" ".join(map(str,values)),text=True,capture_output=True,timeout=10)
        assert result.returncode == 0 and not result.stderr
        assert json.loads(result.stdout) == oracle.frequencies(values,count)
    for data in ("", "1 1", "0x10", "1_0", "1.0", "2147483648", "-2147483649", "+", "--1", "９", "0"*12):
        result = subprocess.run([str(cpp_cli)],input=data,text=True,capture_output=True,timeout=10)
        assert result.returncode == 2 and result.stderr.startswith("error:") and not result.stdout
