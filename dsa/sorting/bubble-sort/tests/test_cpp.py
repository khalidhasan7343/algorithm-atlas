"""Compile and execute C++17/C++20 library and CLI checks."""

from pathlib import Path
import subprocess

import pytest

SOURCE = Path(__file__).parents[1] / "cpp" / "solution.cpp"
DRIVER = r"""#include <algorithm>
#include <climits>
#include <random>
#define ALGORITHM_ATLAS_NO_MAIN
#include "SOURCE_PATH"

struct Tagged {
    int key;
    char tag;
    bool operator<(const Tagged& other) const { return key < other.key; }
};
struct Counted {
    int key;
    static int comparisons;
    bool operator<(const Counted& other) const {
        ++comparisons;
        return key < other.key;
    }
};
int Counted::comparisons = 0;

int main() {
    const std::vector<std::vector<long long>> cases = {
        {}, {4}, {2, 1}, {1, 2}, {1, 2, 3, 4}, {4, 3, 2, 1},
        {7, 7, 7}, {0, -1, 3, -1, 0}, {-5, -2, -9}, {LLONG_MIN, LLONG_MAX, 0}
    };
    for (const auto& values : cases) {
        auto expected = values;
        std::sort(expected.begin(), expected.end());
        const auto original = values;
        if (algorithm_atlas::bubble_sort(values) != expected || values != original) return 1;
    }
    std::mt19937_64 rng(7343);
    for (int trial = 0; trial < 120; ++trial) {
        std::vector<long long> values(rng() % 65);
        for (auto& value : values) value = static_cast<long long>(rng() % 2001) - 1000;
        const auto original = values;
        auto expected = values;
        std::sort(expected.begin(), expected.end());
        if (algorithm_atlas::bubble_sort(values) != expected || values != original) return 2;
    }
    const std::vector<Tagged> tagged = {{2, 'a'}, {2, 'b'}, {1, 'c'}};
    const auto result = algorithm_atlas::bubble_sort(tagged);
    if (result[0].tag != 'c' || result[1].tag != 'a' || result[2].tag != 'b') return 3;
    if (tagged[0].tag != 'a' || tagged[1].tag != 'b') return 4;
    std::vector<Counted> counted;
    for (int i = 0; i < 20; ++i) counted.push_back({i});
    algorithm_atlas::bubble_sort(counted);
    if (Counted::comparisons != 19) return 5;
    const std::vector<std::string> words = {"pear", "apple", "banana"};
    if (algorithm_atlas::bubble_sort(words) != std::vector<std::string>{"apple", "banana", "pear"}) return 6;
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
