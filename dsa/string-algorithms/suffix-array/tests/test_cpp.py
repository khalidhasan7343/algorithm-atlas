import json
import subprocess
import pytest

pytestmark = pytest.mark.cpp


def test_batched_api(cpp_driver, oracle, python_algorithm, name, kind):
    if kind == "palindrome": read = "auto text=read_bytes(); emit(solve(text));"
    elif kind == "multi": read = "auto text=read_bytes(); int k=read_count(); std::vector<std::string> patterns; for(int j=0;j<k;++j)patterns.push_back(read_bytes()); emit(solve(text,patterns));"
    else: read = "auto text=read_bytes(); auto pattern=read_bytes(); emit(solve(text,pattern));"
    run = cpp_driver("int q; std::cin >> q; for(int i=0;i<q;++i){"+read+r"std::cout << '\n';} end_input();")
    cases = oracle.vectors(kind)
    actual = run(str(len(cases))+"\n"+"".join(oracle.encode(c,kind) for c in cases))
    assert len(actual) == len(cases)
    for case,result in zip(cases,actual):
        args = (case,) if kind == "palindrome" else case
        assert result == oracle.expected(case,name),case
        assert result == python_algorithm.solve(*args)


def test_cli(cpp_cli, oracle, name, kind):
    for case in oracle.vectors(kind)[:7]:
        result = subprocess.run([str(cpp_cli)],input=oracle.encode(case,kind),text=True,capture_output=True,timeout=10)
        assert result.returncode == 0 and not result.stderr
        assert json.loads(result.stdout) == oracle.expected(case,name)
    for text in ("", "zz", "0", "- - extra"):
        result = subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode == 2 and result.stderr.startswith("error:") and not result.stdout


def test_index_reuse_and_bounds(cpp_driver):
    body = r'''
    try { SuffixArray bad(std::string(10001,'a')); return 2; }
    catch(const std::invalid_argument&) {}
    SuffixArray index(std::string(10000,'a'));
    for(int i=0;i<10000;++i)
        if(index.sa[i]!=9999-i || index.lcp[i]!=i) return 3;
    auto matches=index.find(std::string(127,'a'));
    if(matches.size()!=9874 || matches.front()!=0 || matches.back()!=9873) return 4;
    if(index.find("b").size()!=0 || index.find("").size()!=10001) return 5;
    try { index.find(std::string(10001,'a')); return 6; }
    catch(const std::invalid_argument&) {}
    emit(1);
    '''
    assert cpp_driver(body)("") == [1]
