import json
import subprocess
import pytest

pytestmark = pytest.mark.cpp


def test_batched_api(cpp_driver, oracle, python_algorithm, name, kind):
    if kind == "palindrome": read = "auto text=read_bytes(); emit(solve(text));"
    elif kind == "multi": read = "auto text=read_bytes(); int k=read_count(); std::vector<std::string> patterns; for(int j=0;j<k;++j)patterns.push_back(read_bytes()); emit(solve(text,patterns));"
    else: read = "auto text=read_bytes(); auto pattern=read_bytes(); emit(solve(text,pattern));"
    run = cpp_driver("int q; std::cin >> q; for(int i=0;i<q;++i){"+read+r"std::cout << '\n';} end_input();")
    cases = oracle.vectors(kind)
    actual = run(str(len(cases))+"\n"+"".join(oracle.encode(c,kind) for c in cases))
    assert len(actual) == len(cases)
    for case,result in zip(cases,actual):
        args = (case,) if kind == "palindrome" else case
        assert result == oracle.expected(case,name),case
        assert result == python_algorithm.solve(*args)


def test_cli(cpp_cli, oracle, name, kind):
    for case in oracle.vectors(kind)[:7]:
        result = subprocess.run([str(cpp_cli)],input=oracle.encode(case,kind),text=True,capture_output=True,timeout=10)
        assert result.returncode == 0 and not result.stderr
        assert json.loads(result.stdout) == oracle.expected(case,name)
    for text in ("", "zz", "0", "- - extra"):
        result = subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=10)
        assert result.returncode == 2 and result.stderr.startswith("error:") and not result.stdout


def test_structure_and_reuse(cpp_driver, oracle, structure):
    body = r'''
    try { AhoCorasick bad({std::string(4097,'a')}); return 2; }
    catch(const std::invalid_argument&) {}
    try { AhoCorasick bad(std::vector<std::string>(257)); return 3; }
    catch(const std::invalid_argument&) {}
    AhoCorasick maximum({std::string(4096,'x')});
    if(!maximum.find(std::string(10000,'a')).empty())return 4;
    AhoCorasick empties(std::vector<std::string>(256));
    if(empties.find("").size()!=256)return 5;
    try {maximum.find(std::string(10001,'a'));return 6;}
    catch(const std::invalid_argument&) {}
    int q;std::cin>>q;
    for(int i=0;i<q;++i) {
        auto text=read_bytes(); int k=read_count(); std::vector<std::string> patterns;
        for(int j=0;j<k;++j) patterns.push_back(read_bytes());
        AhoCorasick machine(patterns);
        auto first=machine.find(text);
        patterns.clear();
        if(machine.find(text)!=first)return 7;
        std::vector<std::vector<int>> rows;
        for(const auto& node:machine.nodes()) {
            std::vector<int> row={node.depth,node.failure,node.output_link};
            row.insert(row.end(),node.next.begin(),node.next.end());
            row.insert(row.end(),node.terminal.begin(),node.terminal.end());
            rows.push_back(row);
        }
        emit(rows);std::cout<<'\n';
    }
    '''
    cases = oracle.multi_vectors()
    rows = cpp_driver(body)(str(len(cases))+"\n"+"".join(oracle.encode(case,"multi") for case in cases))
    assert len(rows) == len(cases)
    for (_,patterns),snapshot in zip(cases,rows): structure.automaton(patterns,snapshot)
