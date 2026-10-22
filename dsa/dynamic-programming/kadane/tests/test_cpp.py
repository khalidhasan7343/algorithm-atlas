"""Execute API/CLI checks under both standard fixture parameters."""
import subprocess
import pytest
pytestmark=pytest.mark.cpp

def test_independent_vectors_and_boundaries(cpp_api,cases):
    run=cpp_api('\n    int count;std::cin >> count;\n    while(count--) {\n        const auto v=read_vector(10000); const auto saved=v; const auto r=maximum_subarray(v);\n        if(r)std::cout << \'[\' << r->sum << \',\' << r->start << \',\' << r->end << "]\\n";else std::cout << "null\\n";\n        assert(v==saved);\n    }\n    int rejected=0;\n    try{maximum_subarray({1000000001});}catch(const std::invalid_argument&){++rejected;}\n    try{maximum_subarray({-1000000001});}catch(const std::invalid_argument&){++rejected;}\n    try{maximum_subarray(std::vector<Integer>(10001));}catch(const std::invalid_argument&){++rejected;}\n    assert(rejected==3);\n')
    vectors=cases.vectors()
    text=str(len(vectors))+'\n'+'\n'.join(cases.encode(args) for args,_ in vectors)+'\n'
    assert run(text)==[list(expected) if expected is not None else None for _,expected in vectors]

def test_cli(cpp_cli):
    result=subprocess.run([str(cpp_cli)],input='9 -2 1 -3 4 -1 2 1 -5 4\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='["6",3,7]' and not result.stderr
    for text in ['', '-1', '1', '1 true', '1 1000000001', '1 1 2']:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
