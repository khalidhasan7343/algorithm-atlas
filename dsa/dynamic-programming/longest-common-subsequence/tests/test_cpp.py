"""Execute API/CLI checks under both standard fixture parameters."""
import subprocess
import pytest
pytestmark=pytest.mark.cpp

def test_independent_vectors_and_boundaries(cpp_api,cases):
    run=cpp_api('\n    int count; std::cin >> count;\n    while(count--) { std::string a,b; std::cin >> std::quoted(a) >> std::quoted(b); std::cout << lcs_length(a,b) << \'\\n\'; }\n    int rejected=0;\n    for(auto bad : std::vector<std::string>{std::string(1001,\'a\'),std::string("\\xc0\\xaf",2),std::string("\\xed\\xa0\\x80",3),std::string("\\xf4\\x90\\x80\\x80",4),std::string("\\x80",1),std::string("\\xf0\\x9f",2)}) {\n        try { lcs_length(bad, "x"); } catch(const std::invalid_argument&) { ++rejected; }\n    }\n    assert(rejected==6);\n    assert(lcs_length(std::string(1000,\'a\'),std::string(1000,\'a\'))==1000);\n    assert(lcs_length("",std::string(1000,\'a\'))==0);\n')
    vectors=cases.vectors()
    text=str(len(vectors))+'\n'+'\n'.join(cases.encode(args) for args,_ in vectors)+'\n'
    assert run(text)==[expected for _,expected in vectors]

def test_cli(cpp_cli):
    result=subprocess.run([str(cpp_cli)],input='abc\nac\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='2' and not result.stderr
    for text in ['', 'one\n', 'a\nb\nextra\n', 'a\nb\n\n']:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')

def test_invalid_utf8_cli(cpp_cli):
    for raw in [b'\xc0\xaf',b'\xed\xa0\x80',b'\xf4\x90\x80\x80',b'\x80',b'\xf0\x9f']:
        result=subprocess.run([str(cpp_cli)],input=raw+b'\nx\n',capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith(b'error:')
