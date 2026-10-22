"""Compiled API optimality/round trips, malformed-stream rejection, strict CLI."""
import subprocess
import pytest
pytestmark=pytest.mark.cpp

def test_oracles_and_cross_language_codes(cpp_api,cases,python_algorithm):
    run=cpp_api(r'''
        int count;std::cin >> count;
        while(count--){
            const auto n=read_integer();std::vector<std::pair<Integer,Integer>> frequencies;
            for(Integer i=0;i<n;++i){const auto s=read_integer(),f=read_integer();frequencies.emplace_back(s,f);}
            const auto m=read_integer();std::vector<Integer> message;
            for(Integer i=0;i<m;++i)message.push_back(read_integer());
            const auto before=frequencies;HuffmanCodec codec(frequencies);print_huffman(codec,message);std::cout << '\n';assert(frequencies==before);
        }
    ''')
    vectors=cases.vectors()
    results=run(str(len(vectors))+'\n'+'\n'.join(cases.encode(args) for args,_ in vectors)+'\n')
    assert len(results)==len(vectors)
    for result,(args,expected) in zip(results,vectors):
        cases.validate(result,args,expected)
        codec=python_algorithm.HuffmanCodec(args[0])
        assert dict(result['codes'])==codec.codes
        assert result['bits']==codec.encode(args[1])

def test_invalid_streams_and_api_limits(cpp_api):
    run=cpp_api(r'''
        int rejected=0;
        for(auto frequencies:std::vector<std::vector<std::pair<Integer,Integer>>>{{{0,0}},{{0,-1}},{{0,1000000001}},{{-1,1}},{{256,1}},{{65,1},{65,2}},std::vector<std::pair<Integer,Integer>>(257,{0,1})}){
            try{HuffmanCodec codec(frequencies);}catch(const std::invalid_argument&){++rejected;}
        }
        HuffmanCodec codec({{65,5},{66,2},{67,1}});
        for(const auto& bits:std::vector<std::string>{"0","2","01x",std::string(1000001,'0')}){
            try{codec.decode(bits);}catch(const std::invalid_argument&){++rejected;}
        }
        for(const auto& message:std::vector<std::vector<Integer>>{{66,256},{-1},{90},std::vector<Integer>(10001,65)}){
            try{codec.encode(message);}catch(const std::invalid_argument&){++rejected;}
        }
        HuffmanCodec empty(std::vector<std::pair<Integer,Integer>>{});
        assert(empty.decode("").empty() && empty.encode({}).empty());
        try{empty.decode("0");}catch(const std::invalid_argument&){++rejected;}
        HuffmanCodec single({{65,1}});
        for(const auto& bits:std::vector<std::string>{"1",std::string(10001,'0')}){
            try{single.decode(bits);}catch(const std::invalid_argument&){++rejected;}
        }
        assert(single.decode(single.encode(std::vector<Integer>(10000,65))).size()==10000);
        assert(rejected==18);std::cout << "true\n";
    ''')
    assert run('')==[True]

def test_cli(cpp_cli):
    result=subprocess.run([str(cpp_cli)],input='3 65 5 66 2 67 1 4 65 66 67 65\n',text=True,capture_output=True,timeout=10)
    assert result.returncode==0 and not result.stderr
    assert result.stdout.strip()=='{"codes":[[65,"1"],[66,"01"],[67,"00"]],"bits":"101001","decoded":[65,66,67,65],"cost":11}'
    for text in ['', '-1', '1 65 0 0','2 65 1 65 2 0','1 65 1 1 66','0 1 256','0 0 extra','1 256 1 0','1 65 1 1','0 0_0']:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode==2 and not result.stdout and result.stderr.startswith('error:')
