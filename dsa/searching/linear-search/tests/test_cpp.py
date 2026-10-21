"""Compile and execute independent C++ API and CLI checks in both standards."""

import json
from pathlib import Path
import subprocess

import pytest

SOURCE = Path(__file__).parents[1] / "cpp/solution.cpp"


@pytest.mark.cpp
def test_cpp_api_oracles_boundaries_and_contracts(cpp_compile, tmp_path):
    source = tmp_path / "search_driver.cpp"
    driver = r'''
#define ALGORITHM_ATLAS_NO_MAIN
#include SOURCE_PATH
#include <cassert>
#include <limits>
#include <random>

using Values = std::vector<long long>;
void check(const Values& values, long long target) {
    std::optional<std::size_t> expected;
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (values[i] == target) { expected = i; break; }
    }
    const auto before = values;
    assert(algorithm_atlas::linear_search(values, target) == expected);
    
    assert(values == before);
}

int main() {
    const auto minimum = std::numeric_limits<long long>::min();
    const auto maximum = std::numeric_limits<long long>::max();
    for (const Values values : {Values{}, Values{5}, Values{0, 0, 0},
            Values{-9, -4, -4, 0, 2, 2, 8}, Values{minimum, minimum, 0, maximum}}) {
        for (long long target : {minimum, maximum, -10LL, -9LL, -4LL, 0LL, 1LL, 8LL, 9LL}) {
            check(values, target);
        }
    }
    std::size_t combinations = 1;
    for (std::size_t size = 0; size <= 7; ++size, combinations *= 3) {
        for (std::size_t encoded = 0; encoded < combinations; ++encoded) {
            auto digits = encoded;
            Values values;
            for (std::size_t i = 0; i < size; ++i, digits /= 3) {
                values.push_back(2 * static_cast<long long>(digits % 3) - 2);
            }
            
            for (long long target = -3; target <= 3; ++target) { check(values, target); }
        }
    }
    std::mt19937 generator(20261022);
    for (const int size : {1, 2, 3, 4, 7, 8, 9, 15, 16, 17, 31, 32, 33,
                           63, 64, 65, 127, 128, 129, 257, 1025, 65537}) {
        Values values;
        for (int i = 0; i < size; ++i) { values.push_back(static_cast<int>(generator() % 2001) - 1000); }
        
        for (long long target : {-1001, -1000, -1, 0, 1, 1000, 1001}) { check(values, target); }
    }
    
    check({4, -2, 4, 0, -2}, -2);
    const std::vector<std::string> words = {"bee", "ant", "bee"};
    assert(algorithm_atlas::linear_search(words, std::string("bee")) == std::optional<std::size_t>(0));

}
'''
    source.write_text(driver.replace("SOURCE_PATH", json.dumps(str(SOURCE.resolve()))))
    executable = cpp_compile(source)
    result = subprocess.run([str(executable)], capture_output=True, text=True,
                            timeout=30, check=True)
    assert result.stderr == ""


@pytest.mark.cpp
def test_cpp_cli_valid_invalid_and_overflow(cpp_compile):
    executable = cpp_compile(SOURCE)
    valid = [("7", "-1\n"), ("0 0", "0\n"), ("0 -2 0 0 3", "1\n"),
             ("-4 -9 -4 -4 0 2 2 8", "1\n"),
             ("1 -9 -4 -4 0 2 2 8", "-1\n"),
             ("+03\n-0\t+3 3 8", "1\n"),
             (f"{-2**63} {-2**63} {2**63-1}", "0\n"),
             (f"{2**63-1} {-2**63} {2**63-1}", "1\n")]
    for text, expected in valid:
        result = subprocess.run([str(executable)], input=text, capture_output=True,
                                text=True, timeout=10, check=True)
        assert result.stdout == expected and result.stderr == ""
    invalid = ["", " \n\t", "+", "1 2x", "1 2.0", "1 +", "1 ١", "1 --2",
               "1 +-2", "1 0x1", "1 1_0", "1 1e0", "1\x002",
               str(2**63), str(-2**63-1), f"0 {2**63}", f"0 {-2**63-1}"]
    
    for text in invalid:
        result = subprocess.run([str(executable)], input=text, capture_output=True,
                                text=True, timeout=10)
        assert result.returncode != 0 and result.stdout == ""
        assert "error:" in result.stderr
