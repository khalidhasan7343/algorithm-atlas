"""Execute API/CLI checks under both standard fixture parameters."""
import subprocess
import pytest
pytestmark=pytest.mark.cpp

def test_independent_vectors_and_boundaries(cpp_api,cases):
    run=cpp_api("\n    int count;std::cin >> count;std::cout << std::boolalpha;\n    while(count--) {const auto target=read_integer();const auto v=read_vector();const auto saved=v;std::cout << subset_sum(v,target) << '\\n';assert(v==saved);}\n    int rejected=0;\n    try{subset_sum({-1},0);}catch(const std::invalid_argument&){++rejected;}\n    try{subset_sum({1000000001},0);}catch(const std::invalid_argument&){++rejected;}\n    try{subset_sum({},-1);}catch(const std::invalid_argument&){++rejected;}\n    try{subset_sum({},10001);}catch(const std::invalid_argument&){++rejected;}\n    try{subset_sum(std::vector<Integer>(1001),0);}catch(const std::invalid_argument&){++rejected;}\n    try{subset_sum(std::vector<Integer>(1000),2000);}catch(const std::invalid_argument&){++rejected;}\n    assert(rejected==6);\n")
    vectors=cases.vectors()
    text=str(len(vectors))+'\n'+'\n'.join(cases.encode(args) for args,_ in vectors)+'\n'
    assert run(text)==[expected for _,expected in vectors]

def test_cli(cpp_cli):
    result=subprocess.run([str(cpp_cli)],input='9 6 3 34 4 12 5 2\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='true' and not result.stderr
    for text in ['', '-1 0', '0 1 -1', '1 1 true', '2 2 1', '1 0 extra']:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
