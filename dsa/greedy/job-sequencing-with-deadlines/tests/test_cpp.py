"""Execute both API and CLI tests under C++17 and C++20."""
import subprocess
import pytest
pytestmark=pytest.mark.cpp

def test_independent_vectors_and_api_boundaries(cpp_api,cases):
    run=cpp_api("\n    int count;std::cin >> count;\n    while(count--){\n        const auto n=read_integer();std::vector<Integer>d,p;\n        for(Integer i=0;i<n;++i){d.push_back(read_integer());p.push_back(read_integer());}\n        const auto before_d=d,before_p=p;const auto result=job_sequencing(d,p);\n        assert(d==before_d && p==before_p);\n        std::vector<bool>seen(d.size(),false);Integer profit=0;\n        for(std::size_t slot=0;slot<result.slots.size();++slot)if(result.slots[slot]){\n            const auto index=*result.slots[slot];assert(index<d.size() && !seen[index] && p[index]>0);\n            assert(static_cast<Integer>(slot+1)<=d[index]);seen[index]=true;profit+=p[index];\n        }\n        assert(profit==result.profit);std::cout << result.profit << '\\n';\n    }\n    int rejected=0;\n    try{job_sequencing({-1},{1});}catch(const std::invalid_argument&){++rejected;}\n    try{job_sequencing({1000000001},{1});}catch(const std::invalid_argument&){++rejected;}\n    try{job_sequencing({1},{1000000001});}catch(const std::invalid_argument&){++rejected;}\n    try{job_sequencing({1},{-1000000001});}catch(const std::invalid_argument&){++rejected;}\n    try{job_sequencing({1},{});}catch(const std::invalid_argument&){++rejected;}\n    try{job_sequencing(std::vector<Integer>(10001,1),std::vector<Integer>(10001,1));}catch(const std::invalid_argument&){++rejected;}\n    assert(rejected==6);\n    auto tie=job_sequencing({2,2},{5,5});assert(tie.profit==10 && tie.slots[0]==1 && tie.slots[1]==0);\n    auto omitted=job_sequencing({2,2},{-1,0});assert(omitted.profit==0 && !omitted.slots[0] && !omitted.slots[1]);\n")
    vectors=cases.vectors()
    text=str(len(vectors))+'\n'+'\n'.join(cases.encode(args) for args,_ in vectors)+'\n'
    assert run(text)==[expected for _,expected in vectors]

def test_cli(cpp_cli):
    result=subprocess.run([str(cpp_cli)],input='5 2 100 1 19 2 27 1 25 3 15\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and result.stdout.strip()=='{"profit":142,"slots":[2,0,4]}' and not result.stderr
    for text in ['', '-1', '1 1', '1 -1 5', '1 1 true', '0 extra', '1 1000000001 1']:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')

def test_cross_language_slot_witnesses(cpp_api,cases,python_algorithm):
    run=cpp_api(r'''
        int count;std::cin >> count;
        while(count--){const auto n=read_integer();std::vector<Integer>d,p;
            for(Integer i=0;i<n;++i){d.push_back(read_integer());p.push_back(read_integer());}
            print_schedule(job_sequencing(d,p));std::cout << '\n';}
    ''')
    vectors=cases.vectors()
    results=run(str(len(vectors))+'\n'+'\n'.join(cases.encode(args) for args,_ in vectors)+'\n')
    assert len(results)==len(vectors)
    for result,(args,expected) in zip(results,vectors):
        cases.validate(result,args,expected)
        assert (result['profit'],result['slots'])==python_algorithm.job_sequencing(*args)
