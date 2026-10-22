"""Compile and execute direct API and CLI checks under C++17 and C++20."""
import subprocess
import pytest
pytestmark=pytest.mark.cpp

def test_independent_vectors_and_api_boundaries(cpp_api,cases):
    run=cpp_api("\n    int count; std::cin >> count;\n    while (count--) {\n        Integer capacity; std::cin >> capacity;\n        const auto n = read_integer();\n        std::vector<Integer> w, v;\n        for (Integer i=0; i<n; ++i) { w.push_back(read_integer()); v.push_back(read_integer()); }\n        auto saved_w=w, saved_v=v;\n        std::cout << knapsack(w,v,capacity) << '\\n';\n        assert(w==saved_w && v==saved_v);\n    }\n    int rejected=0;\n    try { knapsack({-1},{1},2); } catch (const std::invalid_argument&) { ++rejected; }\n    try { knapsack({1},{},1); } catch (const std::invalid_argument&) { ++rejected; }\n    try { knapsack({}, {}, -1); } catch (const std::invalid_argument&) { ++rejected; }\n    try { knapsack({}, {}, 10001); } catch (const std::invalid_argument&) { ++rejected; }\n    try { knapsack({1},{1000000001},1); } catch (const std::invalid_argument&) { ++rejected; }\n    try { knapsack(std::vector<Integer>(1001),std::vector<Integer>(1001),0); } catch (const std::invalid_argument&) { ++rejected; }\n    try { knapsack(std::vector<Integer>(1000),std::vector<Integer>(1000),2000); } catch (const std::invalid_argument&) { ++rejected; }\n    assert(rejected==7);\n")
    vectors=cases.vectors()
    text=str(len(vectors))+'\n'+'\n'.join(cases.encode(args) for args,_ in vectors)+'\n'
    assert run(text)==[expected for _,expected in vectors]

def test_cli(cpp_cli):
    result=subprocess.run([str(cpp_cli)],input='5 3 2 3 3 4 4 5\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='7' and not result.stderr
    for text in ['', '-1 0', '1 -1', '1 1 2', '0 1 -1 2', '1 0 extra']:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
