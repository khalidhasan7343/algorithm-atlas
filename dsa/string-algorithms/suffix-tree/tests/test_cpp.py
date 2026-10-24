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
    try { SuffixTree bad(std::string(2049,'a')); return 2; }
    catch(const std::invalid_argument&) {}
    int q;std::cin>>q;
    for(int i=0;i<q;++i) {
        auto text=read_bytes(); SuffixTree tree(text);
        auto saved=tree.find("a");
        if(tree.find("").size()!=text.size()+1 || !tree.contains(""))return 3;
        if(tree.find("a")!=saved || tree.contains("a")!=!saved.empty())return 4;
        try {tree.find(std::string(10001,'a'));return 5;}
        catch(const std::invalid_argument&) {}
        try {tree.contains(std::string(10001,'a'));return 6;}
        catch(const std::invalid_argument&) {}
        std::vector<std::vector<int>> rows;
        for(const auto& node:tree.nodes()) {
            std::vector<int> row={node.start,node.end,node.suffix};
            for(auto edge:node.children){row.push_back(edge.first);row.push_back(edge.second);}
            rows.push_back(row);
        }
        emit(rows);std::cout<<'\n';
    }
    '''
    texts = oracle.palindrome_vectors()+[b"a"*2048]
    rows = cpp_driver(body)(str(len(texts))+"\n"+"\n".join(oracle.hex_token(t) for t in texts))
    assert len(rows) == len(texts)
    for text,snapshot in zip(texts,rows): structure.suffix_tree(text,snapshot)
