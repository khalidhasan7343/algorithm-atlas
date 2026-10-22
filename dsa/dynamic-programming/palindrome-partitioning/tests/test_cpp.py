"""Execute API/CLI checks under both standard fixture parameters."""
import subprocess
import pytest
pytestmark=pytest.mark.cpp

def test_independent_vectors_and_boundaries(cpp_api,cases):
    run=cpp_api('\n    int count;std::cin >> count;\n    while(count--) {std::string s;std::cin >> std::quoted(s);std::cout << minimum_palindrome_cuts(s) << \'\\n\';}\n    int rejected=0;\n    for(auto bad:std::vector<std::string>{std::string(1001,\'a\'),std::string("\\xc0\\xaf",2),std::string("\\xed\\xa0\\x80",3),std::string("\\xf4\\x90\\x80\\x80",4)}) {\n        try{minimum_palindrome_cuts(bad);}catch(const std::invalid_argument&){++rejected;}\n    }\n    assert(rejected==4);\n')
    vectors=cases.vectors()
    text=str(len(vectors))+'\n'+'\n'.join(cases.encode(args) for args,_ in vectors)+'\n'
    assert run(text)==[expected for _,expected in vectors]

def test_cli(cpp_cli):
    result=subprocess.run([str(cpp_cli)],input='aab\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='1' and not result.stderr
    for text in ['', 'a\nb\n', 'a\n\n']:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')

def test_empty_and_invalid_utf8_cli(cpp_cli):
    result=subprocess.run([str(cpp_cli)],input=b'\n',capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout==b'0\n'
    result=subprocess.run([str(cpp_cli)],input=b'\xed\xa0\x80\n',capture_output=True,timeout=10)
    assert result.returncode==2 and not result.stdout
