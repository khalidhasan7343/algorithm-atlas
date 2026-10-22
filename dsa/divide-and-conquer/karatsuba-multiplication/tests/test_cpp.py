import json
import subprocess
import pytest


@pytest.mark.cpp
def test_cli(cpp_cli,cases):
    for text,expected in cases.CLI_VALID:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=30)
        assert result.returncode==0 and result.stderr==""
        assert json.loads(result.stdout)==expected
    for text in ['', '1', '1 2 3', '+ 2', '1.0 2', '1_0 2', '١ 2']:
        result=subprocess.run([str(cpp_cli)],input=text,text=True,capture_output=True,timeout=30)
        assert result.returncode!=0 and result.stdout=="" and "error:" in result.stderr


@pytest.mark.cpp
def test_api_big_decimal_products(cpp_api,cases):
    invoke=cpp_api(r"""
    std::string a,b;
    while (std::cin >> a >> b) {
        const auto before_a=a,before_b=b;
        reply([&] { return algorithm_atlas::karatsuba_multiplication(a,b); });
        assert(a==before_a && b==before_b);
    }
    """)
    rows=cases.data()
    assert invoke("\n".join(f"{a} {b}" for a,b in rows))==[str(a*b) for a,b in rows]
    invalid=[("12x","1"),("+","2"),("1.0","9"),("1_0","2")]
    assert invoke("\n".join(a+" "+b for a,b in invalid))==[{"error":"invalid_argument"}]*len(invalid)
