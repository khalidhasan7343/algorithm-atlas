"""Execute both API and CLI tests under C++17 and C++20."""
import subprocess
import pytest
pytestmark=pytest.mark.cpp

def test_independent_vectors_and_api_boundaries(cpp_api,cases):
    run=cpp_api("\n    int count;std::cin >> count;\n    while(count--) {\n        const auto n=read_integer();std::vector<Activity> activities;\n        for(Integer i=0;i<n;++i){const auto start=read_integer();const auto finish=read_integer();activities.push_back({start,finish});}\n        const auto before=activities;print_vector(activity_selection(activities));std::cout << '\\n';\n        for(std::size_t i=0;i<before.size();++i)assert(activities[i].start==before[i].start && activities[i].finish==before[i].finish);\n    }\n    int rejected=0;\n    for(auto activity:std::vector<Activity>{{1,1},{2,1},{0,1000000001},{-1000000001,0}}) {\n        try{activity_selection({activity});}catch(const std::invalid_argument&){++rejected;}\n    }\n    try{activity_selection(std::vector<Activity>(10001,{0,1}));}catch(const std::invalid_argument&){++rejected;}\n    assert(rejected==5);\n")
    vectors=cases.vectors()
    text=str(len(vectors))+'\n'+'\n'.join(cases.encode(args) for args,_ in vectors)+'\n'
    assert run(text)==[expected for _,expected in vectors]

def test_cli(cpp_cli):
    result=subprocess.run([str(cpp_cli)],input='5 1 3 2 5 3 4 4 7 5 6\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='[0,2,4]' and not result.stderr
    for text in ['', '-1', '1 0', '1 1 1', '1 2 1', '1 0 true', '0 extra', '1 0 1000000001']:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
