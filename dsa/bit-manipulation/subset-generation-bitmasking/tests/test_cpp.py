import json
import subprocess
import pytest

pytestmark = pytest.mark.cpp


def test_batched_recursive_oracle(cpp_driver, python_algorithm, oracle):
    body = r'''int q;std::cin>>q;while(q--){std::size_t n;std::cin>>n;std::vector<Value> v(n);for(auto& x:v)std::cin>>x;auto saved=v;auto result=solve(v);if(v!=saved)return 3;emit(result);std::cout<<'\n';}'''
    values = oracle.subset_vectors()
    actual = cpp_driver(body)(str(len(values))+"\n"+"".join(oracle.encode(v) for v in values))
    assert len(actual) == len(values)
    for v,rows in zip(values,actual):
        assert rows == oracle.recursive_subsets(v)
        assert rows == python_algorithm.solve(v)


def test_invalid_api(cpp_driver):
    body = r'''for(std::size_t n:{17,32}){try{solve(std::vector<Value>(n));return 3;}catch(const std::invalid_argument&){}}for(Value v:{2147483648LL,-2147483649LL}){try{solve({v});return 4;}catch(const std::invalid_argument&){}}emit(1);'''
    assert cpp_driver(body)("") == [1]


def test_cli(cpp_cli, oracle):
    for values in oracle.subset_vectors()[:6]:
        result = subprocess.run([str(cpp_cli)],input=" ".join(map(str,values)),text=True,capture_output=True,timeout=10)
        assert result.returncode == 0 and not result.stderr
        assert json.loads(result.stdout) == oracle.recursive_subsets(values)
    for text in ("2147483648", "-2147483649", "0x10", "1.0", "true", "+", "0"*12, " ".join(["0"]*17)):
        result = subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode == 2 and result.stderr.startswith("error:") and not result.stdout
