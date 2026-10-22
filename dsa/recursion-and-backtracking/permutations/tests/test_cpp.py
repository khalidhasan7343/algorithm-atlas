"""Execute C++ APIs and CLIs against independently generated Python oracles."""
import itertools
import json
import subprocess

import pytest


def oracle(values, k=2):
    return [list(row) for row in itertools.permutations(values)]


@pytest.mark.cpp
def test_cpp_api_exhaustive_order_boundaries_and_restoration(cpp_api):
    invoke=cpp_api(r"""
    std::size_t n;
    while (std::cin >> n) {
        std::vector<long long> values(n);
        for (auto& value : values) { std::cin >> value; }
        
        const auto before=values;
        reply([&] { return algorithm_atlas::permutations(values); });
        assert(values==before);
    }
    """)
    cases=[]
    for size in range(5):
        for values in itertools.product((-1, 0, 1), repeat=size):
            for k in (2,):
                cases.append((list(values),k))
    cases.append(([-2**63,0,2**63-1],2))
    cases.extend([([1,1,2],1),([],0),([9],0)])
    
    text="\n".join(" ".join(map(str,[len(v),*v])) for v,k in cases)
    expected=[oracle(v,k) if k>=0 else {"error":"invalid_argument"} for v,k in cases]
    assert invoke(text)==expected


@pytest.mark.cpp
def test_cpp_cli_protocol_errors_and_overflow(cpp_cli):
    for text,expected in [('', [[]]), ('1 2', [[1, 2], [2, 1]])]:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,
                              capture_output=True,check=True,timeout=10)
        assert result.stdout==json.dumps(expected,separators=(",", ":"))+"\n"
        assert result.stderr==""
    invalid=["two", "+", "1 2x", "1 ١", "1 1.0", "1_0", "1\x002",
             str(2**63),str(-2**63-1)]
    
    for text in invalid:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,
                              capture_output=True,timeout=10)
        assert result.returncode!=0 and result.stdout=="" and "error:" in result.stderr
