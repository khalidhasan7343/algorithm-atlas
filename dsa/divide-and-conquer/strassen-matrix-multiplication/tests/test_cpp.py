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
def test_api_all_seven_products_padding_and_boundaries(cpp_api,cases):
    invoke=cpp_api(r"""
    std::size_t n;
    while (std::cin >> n) {
        algorithm_atlas::Matrix a(n),b;
        for (auto& row:a) { std::size_t w;std::cin >> w;row.resize(w);for (auto& x:row) { std::cin >> x; } }
        std::cin >> n;b.resize(n);
        for (auto& row:b) { std::size_t w;std::cin >> w;row.resize(w);for (auto& x:row) { std::cin >> x; } }
        const auto before_a=a,before_b=b;
        try { algorithm_atlas::print_result(algorithm_atlas::strassen_multiply(a,b)); }
        catch (const std::invalid_argument&) { std::cout << R"({"error":"invalid_argument"})"; }
        std::cout << '\n';assert(a==before_a && b==before_b);
    }
    """)
    def serialize(matrix):return [len(matrix),*(x for row in matrix for x in [len(row),*row])]
    valid=cases.data()
    invalid=[v for v,e in cases.invalid() if e is ValueError]
    rows=valid+invalid
    expected=[cases.oracle(a,b) for a,b in valid]+[{"error":"invalid_argument"}]*len(invalid)
    assert invoke("\n".join(" ".join(map(str,serialize(a)+serialize(b))) for a,b in rows))==expected
