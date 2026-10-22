"""Execute API/CLI checks under both standard fixture parameters."""
import subprocess
import pytest
pytestmark=pytest.mark.cpp

def test_independent_vectors_and_boundaries(cpp_api,cases):
    run=cpp_api("\n    int count; std::cin >> count;\n    while(count--) { const auto values=read_vector(); const auto saved=values; std::cout << lis_length(values) << '\\n'; assert(values==saved); }\n    int rejected=0;\n    try { lis_length({1000000001}); } catch(const std::invalid_argument&) { ++rejected; }\n    try { lis_length(std::vector<Integer>(1001)); } catch(const std::invalid_argument&) { ++rejected; }\n    assert(rejected==2);\n    std::vector<Integer> increasing; for(Integer i=0;i<1000;++i) increasing.push_back(i);\n    assert(lis_length(increasing)==1000); std::reverse(increasing.begin(),increasing.end()); assert(lis_length(increasing)==1);\n")
    vectors=cases.vectors()
    text=str(len(vectors))+'\n'+'\n'.join(cases.encode(args) for args,_ in vectors)+'\n'
    assert run(text)==[expected for _,expected in vectors]

def test_cli(cpp_cli):
    result=subprocess.run([str(cpp_cli)],input='8 10 9 2 5 3 7 101 18\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='4' and not result.stderr
    for text in ['', '-1', '1', '1 1 2', '1 true', '1 1000000001']:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
