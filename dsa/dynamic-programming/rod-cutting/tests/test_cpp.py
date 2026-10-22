"""Compile and execute direct API and CLI checks under C++17 and C++20."""
import subprocess
import pytest
pytestmark=pytest.mark.cpp

def test_independent_vectors_and_api_boundaries(cpp_api,cases):
    run=cpp_api('\n    int count; std::cin >> count;\n    while(count--) {\n        Integer length; std::cin >> length; const auto n=read_integer();\n        std::vector<std::optional<Integer>> prices;\n        for(Integer i=0;i<n;++i) { std::string s; std::cin >> s; prices.push_back(s=="x" ? std::nullopt : std::optional<Integer>(parse_integer(s))); }\n        const auto saved=prices; emit(rod_cutting(prices,length)); std::cout << \'\\n\'; assert(prices==saved);\n    }\n    int rejected=0;\n    try { rod_cutting({},-1); } catch (const std::invalid_argument&) { ++rejected; }\n    try { rod_cutting({},10001); } catch (const std::invalid_argument&) { ++rejected; }\n    try { rod_cutting({1000000001},1); } catch (const std::invalid_argument&) { ++rejected; }\n    try { rod_cutting(std::vector<std::optional<Integer>>(1001),0); } catch (const std::invalid_argument&) { ++rejected; }\n    try { rod_cutting(std::vector<std::optional<Integer>>(1000),2000); } catch (const std::invalid_argument&) { ++rejected; }\n    assert(rejected==5);\n')
    vectors=cases.vectors()
    text=str(len(vectors))+'\n'+'\n'.join(cases.encode(args) for args,_ in vectors)+'\n'
    assert run(text)==[expected for _,expected in vectors]

def test_cli(cpp_cli):
    result=subprocess.run([str(cpp_cli)],input='4 4 2 5 7 8\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='10' and not result.stderr
    for text in ['', '-1 0', '1 -1', '1 1', '1 1 none', '1 0 extra']:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
