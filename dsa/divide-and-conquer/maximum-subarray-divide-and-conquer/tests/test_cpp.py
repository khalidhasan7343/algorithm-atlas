import json
import subprocess
import pytest


@pytest.mark.cpp
def test_cli(cpp_cli,cases):
    for text,expected in cases.CLI_VALID:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=30)
        assert result.returncode==0 and result.stderr==""
        assert json.loads(result.stdout)==expected
    for text in ['x', '+', '1 2x', '1.0', '١', '9223372036854775808', '-9223372036854775809']:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=30)
        assert result.returncode!=0 and result.stdout=="" and "error:" in result.stderr


@pytest.mark.cpp
def test_api_exhaustive_exact_wide_sums(cpp_api,cases):
    invoke=cpp_api(r"""
    std::size_t n;
    while (std::cin >> n) {
        std::vector<long long> values(n);
        for (auto& value:values) { std::cin >> value; }
        const auto before=values;
        const auto answer=algorithm_atlas::maximum_subarray(values);
        algorithm_atlas::print_result(answer);std::cout << '\n';
        assert(values==before);
    }
    """)
    rows=cases.data()
    expected=[]
    for values in rows:
        answer=cases.oracle(values)
        expected.append(None if answer is None else [str(answer[0]),answer[1],answer[2]])
    assert invoke("\n".join(" ".join(map(str,[len(v),*v])) for v in rows))==expected
