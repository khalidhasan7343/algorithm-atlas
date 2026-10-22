"""Execute both API and CLI tests under C++17 and C++20."""
import subprocess
import pytest
pytestmark=pytest.mark.cpp

def test_independent_vectors_and_api_boundaries(cpp_api,cases):
    run=cpp_api("\n    int count;std::cin >> count;\n    while(count--) {\n        const auto capacity=read_integer(),n=read_integer();std::vector<Integer>w,v;\n        for(Integer i=0;i<n;++i){w.push_back(read_integer());v.push_back(read_integer());}\n        const auto before_w=w,before_v=v;print_knapsack(fractional_knapsack(w,v,capacity));std::cout << '\\n';\n        assert(w==before_w && v==before_v);\n    }\n    int rejected=0;\n    try{fractional_knapsack({0},{1},1);}catch(const std::invalid_argument&){++rejected;}\n    try{fractional_knapsack({-1},{1},1);}catch(const std::invalid_argument&){++rejected;}\n    try{fractional_knapsack({1},{-1},1);}catch(const std::invalid_argument&){++rejected;}\n    try{fractional_knapsack({1},{},1);}catch(const std::invalid_argument&){++rejected;}\n    try{fractional_knapsack({},{},-1);}catch(const std::invalid_argument&){++rejected;}\n    try{fractional_knapsack({},{},1000000001);}catch(const std::invalid_argument&){++rejected;}\n    try{fractional_knapsack({1000001},{1},1);}catch(const std::invalid_argument&){++rejected;}\n    try{fractional_knapsack({1},{1000001},1);}catch(const std::invalid_argument&){++rejected;}\n    try{fractional_knapsack(std::vector<Integer>(10001,1),std::vector<Integer>(10001,1),0);}catch(const std::invalid_argument&){++rejected;}\n    assert(rejected==9);\n")
    vectors=cases.vectors()
    text=str(len(vectors))+'\n'+'\n'.join(cases.encode(args) for args,_ in vectors)+'\n'
    assert run(text)==[expected for _,expected in vectors]

def test_cli(cpp_cli):
    result=subprocess.run([str(cpp_cli)],input='50 3 10 60 20 100 30 120\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='{"value":[240,1],"fractions":[[1,1],[1,1],[2,3]]}' and not result.stderr
    for text in ['', '-1 0', '0 -1', '1 1 0 1', '1 1 1 -1', '1 1 1', '1 0 extra', '1 1 1_0 2']:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
