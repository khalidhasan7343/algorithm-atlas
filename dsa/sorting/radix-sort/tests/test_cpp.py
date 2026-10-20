"""Compile/execute full signed 64-bit library and CLI cases in C++17/C++20."""

from pathlib import Path
import subprocess

import pytest

SOURCE = Path(__file__).parents[1] / "cpp" / "solution.cpp"
DRIVER = r"""#include <algorithm>
#include <climits>
#include <random>
#define ALGORITHM_ATLAS_NO_MAIN
#include "SOURCE_PATH"

int main() {
    const std::vector<std::vector<long long>> cases = {
        {}, {4}, {2, 1}, {1, 2}, {1, 2, 3, 4}, {4, 3, 2, 1},
        {0, 0, 0}, {-7, -7, -7}, {0, -1, 3, -1, 0}, {-5, -2, -9},
        {LLONG_MIN, LLONG_MAX, 0, -1, LLONG_MIN, LLONG_MAX},
        {256, 255, 257, 0, -255, -256, -257, 65536, -65536},
        {513, 258, 257, 512, 1, 0, 256}
    };
    for (const auto& values : cases) {
        const auto original = values;
        auto expected = values;
        std::sort(expected.begin(), expected.end());
        if (algorithm_atlas::radix_sort(values) != expected || values != original) return 1;
    }
    std::mt19937_64 rng(7343);
    std::uniform_int_distribution<long long> wide(LLONG_MIN, LLONG_MAX);
    for (int trial = 0; trial < 200; ++trial) {
        std::vector<long long> values(rng() % 100);
        for (auto& value : values) value = wide(rng);
        const auto original = values;
        auto expected = values;
        std::sort(expected.begin(), expected.end());
        if (algorithm_atlas::radix_sort(values) != expected || values != original) return 2;
    }
    std::vector<long long> byte_boundaries;
    for (unsigned shift = 0; shift < 63; shift += 8) {
        const long long power = 1LL << shift;
        byte_boundaries.push_back(power);
        byte_boundaries.push_back(power - 1);
        byte_boundaries.push_back(-power);
        byte_boundaries.push_back(-power - 1);
    }
    auto expected = byte_boundaries;
    std::sort(expected.begin(), expected.end());
    if (algorithm_atlas::radix_sort(byte_boundaries) != expected) return 3;
    std::cout << "all C++ assertions passed\n";
}
"""


@pytest.mark.cpp
def test_cpp_library_contract(cpp_compile, tmp_path):
    driver = tmp_path / "driver.cpp"
    driver.write_text(DRIVER.replace("SOURCE_PATH", SOURCE.as_posix()))
    executable = cpp_compile(driver)
    result = subprocess.run([str(executable)], capture_output=True, text=True,
                            check=True, timeout=10)
    assert result.stdout == "all C++ assertions passed\n"
    assert result.stderr == ""


@pytest.mark.cpp
def test_cpp_cli(cpp_compile):
    executable = cpp_compile(SOURCE)
    valid = [
        ("", "\n"), (" \n\t", "\n"),
        ("3 -2 +1 0 -2\n", "-2 -2 0 1 3\n"),
        ("-9223372036854775808 9223372036854775807", "-9223372036854775808 9223372036854775807\n"),
        ("+0004 -0 0002", "0 2 4\n"),
    ]
    for text, expected in valid:
        result = subprocess.run([str(executable)], input=text, capture_output=True,
                                text=True, check=True, timeout=10)
        assert result.stdout == expected
        assert result.stderr == ""
    invalid = ["abc", "1.2", "1e3", "3x", "--1", "+-1", "+", "-",
               "1_000", "0xff", "１２", "9223372036854775808", "-9223372036854775809"]
    for token in invalid:
        result = subprocess.run([str(executable)], input="1 " + token + " 2",
                                capture_output=True, text=True, timeout=10)
        assert result.returncode != 0
        assert result.stdout == ""
        assert "error:" in result.stderr
