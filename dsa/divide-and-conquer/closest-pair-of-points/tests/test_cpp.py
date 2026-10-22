import json
import subprocess
import pytest


@pytest.mark.cpp
def test_cli(cpp_cli,cases):
    for text,expected in cases.CLI_VALID:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=30)
        assert result.returncode==0 and result.stderr=="" and json.loads(result.stdout)==expected
    for text in cases.CLI_INVALID:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=30)
        assert result.returncode!=0 and result.stdout=="" and "error:" in result.stderr


@pytest.mark.cpp
def test_api_oracle_exact_ties_and_bounds(cpp_api,cases):
    invoke=cpp_api(r"""
    std::size_t n;
    while (std::cin >> n) {
        std::vector<std::pair<long long,long long>> points(n);
        for (auto& p:points) { std::cin >> p.first >> p.second; }
        const auto before=points;
        try { algorithm_atlas::print_result(algorithm_atlas::closest_pair(points)); }
        catch (const std::invalid_argument&) { std::cout << R"({"error":"invalid_argument"})"; }
        std::cout << '\n';assert(points==before);
    }
    """)
    rows=cases.data()+[[(1000000001,0)],[(0,-1000000001)]]
    expected=[None if (a:=cases.oracle(v)) is None else list(a) for v in rows[:-2]]+[{"error":"invalid_argument"}]*2
    assert invoke("\n".join(" ".join(map(str,[len(v),*(x for p in v for x in p)])) for v in rows))==expected
