"""Compile and execute direct API and CLI checks under C++17 and C++20."""
import subprocess
import pytest
pytestmark=pytest.mark.cpp

def test_independent_vectors_and_api_boundaries(cpp_api,cases):
    run=cpp_api("\n    int count; std::cin >> count;\n    while (count--) { Integer n; std::cin >> n; std::cout << fibonacci(n) << '\\n'; }\n    bool rejected = false;\n    try { fibonacci(-1); } catch (const std::invalid_argument&) { rejected = true; }\n    assert(rejected); rejected = false;\n    try { fibonacci(93); } catch (const std::overflow_error&) { rejected = true; }\n    assert(rejected);\n")
    vectors=cases.vectors()
    text=str(len(vectors))+'\n'+'\n'.join(cases.encode(args) for args,_ in vectors)+'\n'
    assert run(text)==[expected for _,expected in vectors]

def test_cli(cpp_cli):
    result=subprocess.run([str(cpp_cli)],input='10\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='55' and not result.stderr
    for text in ['', '-1', '93', '2 3', '1_0', 'true']:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
