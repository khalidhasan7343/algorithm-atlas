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


def test_api_contract_and_preprocessing(cpp_driver, name, oracle):
    extra = ""
    if name == "knuth-morris-pratt":
        # Independently expected proper prefix/suffix lengths.
        extra = 'if(prefix_function("aabaaab")!=std::vector<int>({0,1,0,1,2,2,3}))return 3;'
    elif name == "rabin-karp":
        extra = 'std::string a("\\0\\2",2),b("\\2\\0",2); if(fingerprint(a,1,2)!=fingerprint(b,1,2)||!solve(a,b,1,2).empty())return 3; try{solve("","",0,2);return 4;}catch(const std::invalid_argument&){}'
    body = '''try{solve(std::string(10001,'a'),"");return 5;}catch(const std::invalid_argument&){}'''
    body += """try{solve("",std::string(10001,'a'));return 7;}catch(const std::invalid_argument&){}"""
    body += extra + "emit(1);"
    assert cpp_driver(body)("") == [1]
    if name == "knuth-morris-pratt":
        body = r"int q;std::cin>>q;for(int i=0;i<q;++i){auto p=read_bytes();emit(prefix_function(p));std::cout<<'\n';}"
        patterns = [p for _,p in oracle.matching_vectors()]
        actual = cpp_driver(body)(str(len(patterns))+"\n"+"\n".join(oracle.hex_token(p) for p in patterns))
        assert actual == [oracle.lps(p) for p in patterns]
    elif name == "rabin-karp":
        body = r"int q;std::cin>>q;for(int i=0;i<q;++i){auto t=read_bytes();auto p=read_bytes();emit(solve(t,p,1,2));std::cout<<'\n';}"
        cases = oracle.matching_vectors()
        actual = cpp_driver(body)(str(len(cases))+"\n"+"".join(oracle.encode(c,"match") for c in cases))
        assert actual == [oracle.occurrences(*c) for c in cases]

