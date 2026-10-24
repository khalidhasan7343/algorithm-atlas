import json
import subprocess
import pytest

pytestmark = pytest.mark.cpp


def test_batched_representation_oracle(cpp_driver, python_algorithm, oracle):
    # Fixed 32-position division/remainder is independent of clearing set bits.
    body = r'''int q;std::cin>>q;while(q--){Value v;std::cin>>v;auto n=solve(v);Word word=static_cast<Word>(v);Value reference=0;for(int i=0;i<32;++i){reference+=word%2;word/=2;}if(n!=reference)return 3;emit(n);std::cout<<'\n';}'''
    values = oracle.count_vectors()
    actual = cpp_driver(body)(str(len(values))+"\n"+"\n".join(map(str,values)))
    assert len(actual) == len(values)
    assert actual == [oracle.bit_count(v) for v in values]
    assert actual == [python_algorithm.solve(v) for v in values]


def test_invalid_api(cpp_driver):
    body = r'''for(Value v:{2147483648LL,-2147483649LL}){try{solve(v);return 3;}catch(const std::invalid_argument&){}}emit(1);'''
    assert cpp_driver(body)("") == [1]


def test_cli(cpp_cli, oracle):
    for value in oracle.count_vectors()[:12]:
        result = subprocess.run([str(cpp_cli)],input=str(value),text=True,capture_output=True,timeout=10)
        assert result.returncode == 0 and not result.stderr
        assert json.loads(result.stdout) == oracle.bit_count(value)
    for text in ("", "0 1", "2147483648", "-2147483649", "0x10", "1.0", "true", "+", "0"*12):
        result = subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode == 2 and result.stderr.startswith("error:") and not result.stdout
