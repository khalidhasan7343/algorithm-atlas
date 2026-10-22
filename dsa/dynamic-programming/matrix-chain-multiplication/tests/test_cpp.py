"""Execute API/CLI checks under both standard fixture parameters."""
import subprocess
import pytest
pytestmark=pytest.mark.cpp

def test_independent_vectors_and_boundaries(cpp_api,cases):
    run=cpp_api("\n    int count;std::cin >> count;\n    while(count--) {const auto d=read_vector(101);const auto saved=d;std::cout << matrix_chain_cost(d) << '\\n';assert(d==saved);}\n    int rejected=0;\n    for(const auto& d:std::vector<std::vector<Integer>>{{2},{0,2},{-1,2},{100001,2},std::vector<Integer>(102,1)}) {\n        try {matrix_chain_cost(d);} catch(const std::invalid_argument&) {++rejected;}\n    }\n    assert(rejected==5);\n")
    vectors=cases.vectors()
    text=str(len(vectors))+'\n'+'\n'.join(cases.encode(args) for args,_ in vectors)+'\n'
    assert run(text)==[expected for _,expected in vectors]

def test_cli(cpp_cli):
    result=subprocess.run([str(cpp_cli)],input='4 10 30 5 60\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='4500' and not result.stderr
    for text in ['', '1 5', '2 0 2', '2 -1 2', '2 100001 2', '3 1 2', '0 extra']:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
