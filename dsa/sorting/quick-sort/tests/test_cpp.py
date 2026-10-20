"""Execute independent C++ library and standalone-CLI oracles in both standards."""

import json
from pathlib import Path
import random
import subprocess

import pytest


SOURCE = Path(__file__).parents[1] / "cpp/solution.cpp"


@pytest.mark.cpp
def test_cpp_api_boundaries_randomized_records_and_duplicates(cpp_compile, tmp_path) -> None:
    driver = tmp_path / "quick_driver.cpp"
    driver.write_text(r'''
#define ALGORITHM_ATLAS_NO_MAIN
#include SOURCE_PATH
#include <algorithm>
#include <cassert>
#include <limits>
#include <random>

struct Record {
    int key;
    char tag;
    bool operator<(const Record& other) const { return key < other.key; }
};
struct Counted {
    static int comparisons;
    bool operator<(const Counted&) const { ++comparisons; return false; }
};
int Counted::comparisons = 0;

int main() {
    using algorithm_atlas::quick_sort;
    std::vector<std::vector<long long>> cases = {
        {}, {7}, {4,4,4}, {1,2,3}, {3,2,1}, {4,2,4,1,3}, {0,-9,7,-9},
        {std::numeric_limits<long long>::min(), std::numeric_limits<long long>::max(), 0}
    };
    std::mt19937 generator(7343);
    std::uniform_int_distribution<int> value(-1000,1000);
    for (int length = 0; length <= 100; ++length) {
        for (int repeat = 0; repeat < 3; ++repeat) {
            std::vector<long long> input;
            for (int index = 0; index < length; ++index) input.push_back(value(generator));
            cases.push_back(input);
        }
    }
    std::vector<long long> ascending;
    for (int value = 0; value < 8000; ++value) ascending.push_back(value);
    cases.push_back(ascending);
    std::reverse(ascending.begin(), ascending.end());
    cases.push_back(ascending);
    cases.push_back(std::vector<long long>(20000, 7));
    for (const auto& input : cases) {
        const auto before = input;
        auto expected = input;
        std::sort(expected.begin(), expected.end());
        const auto actual = quick_sort(input);
        assert(actual == expected);
        assert(input == before);
    }
    const auto records = quick_sort(std::vector<Record>{{2,'a'},{1,'b'},{2,'c'}});
    assert(records[0].tag == 'b' && records[1].tag == 'c' && records[2].tag == 'a');
    assert((quick_sort(std::vector<std::string>{"pear","apple"}) ==
            std::vector<std::string>{"apple","pear"}));
    quick_sort(std::vector<Counted>(1000));
    assert(Counted::comparisons == 2000);
}
'''.replace("SOURCE_PATH", json.dumps(str(SOURCE.resolve()))), encoding="utf-8")
    executable = cpp_compile(driver)
    subprocess.run([str(executable)], capture_output=True, text=True, check=True, timeout=10)


@pytest.mark.cpp
def test_cpp_cli_valid_invalid_and_randomized(cpp_compile) -> None:
    executable = cpp_compile(SOURCE)
    cases = [[], [7], [4, 4, 4], [1, 2, 3], [3, 2, 1], [4, 2, 4, 1, 3],
             [0, -9, 7, -9], [-2**63, 2**63 - 1, 0]]
    generator = random.Random(7343)
    cases += [[generator.randint(-10**12, 10**12) for _ in range(length)]
              for length in range(0, 101, 5)]
    for values in cases:
        result = subprocess.run([str(executable)], input=" ".join(map(str, values)),
                                capture_output=True, text=True, check=True, timeout=10)
        assert result.stdout == " ".join(map(str, sorted(values))) + "\n"
        assert result.stderr == ""
    result = subprocess.run([str(executable)], input="+03 -0 -7",
                            capture_output=True, text=True, check=True, timeout=10)
    assert result.stdout == "-7 0 3\n"
    for text in ["1 two 3", "1.5", "0x10", "+", "-", "--2", "+-2", "1_000", "١",
                 str(2**63), str(-2**63 - 1)]:
        result = subprocess.run([str(executable)], input=text,
                                capture_output=True, text=True, timeout=10)
        assert result.returncode != 0
        assert result.stdout == ""
        assert "error:" in result.stderr
