"""Compile and execute direct API and CLI checks under C++17 and C++20."""
import subprocess
import pytest
pytestmark=pytest.mark.cpp

def test_independent_vectors_and_api_boundaries(cpp_api,cases):
    run=cpp_api('\n    int count; std::cin >> count;\n    while(count--) {\n        Integer amount; std::cin >> amount; auto coins=read_vector(); auto saved=coins;\n        std::cout << \'[\'; emit(minimum_coins(coins,amount)); std::cout << \',\' << count_combinations(coins,amount) << "]\\n";\n        assert(coins==saved);\n    }\n    int rejected=0;\n    for (auto bad : std::vector<std::vector<Integer>>{{0},{-1},{1000000001}}) {\n        try { minimum_coins(bad,1); } catch (const std::invalid_argument&) { ++rejected; }\n        try { count_combinations(bad,1); } catch (const std::invalid_argument&) { ++rejected; }\n    }\n    try { minimum_coins({},-1); } catch (const std::invalid_argument&) { ++rejected; }\n    try { count_combinations({},10001); } catch (const std::invalid_argument&) { ++rejected; }\n    try { count_combinations(std::vector<Integer>(1001,1),0); } catch (const std::invalid_argument&) { ++rejected; }\n    try { minimum_coins(std::vector<Integer>(1000,1),2000); } catch (const std::invalid_argument&) { ++rejected; }\n    std::vector<Integer> many; for(Integer i=1;i<=500;++i) many.push_back(i);\n    try { count_combinations(many,500); } catch (const std::overflow_error&) { ++rejected; }\n    assert(rejected==11);\n    assert(minimum_coins({1},10000)==10000 && count_combinations({1},10000)==1);\n')
    vectors=cases.vectors()
    text=str(len(vectors))+'\n'+'\n'.join(cases.encode(args) for args,_ in vectors)+'\n'
    assert run(text)==[expected for _,expected in vectors]

def test_cli(cpp_cli):
    result=subprocess.run([str(cpp_cli)],input='6 3 1 3 4\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='[2,4]' and not result.stderr
    for text in ['', '-1 0', '1 1 0', '1 1 -2', '1 2 1', '1 0 extra']:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
