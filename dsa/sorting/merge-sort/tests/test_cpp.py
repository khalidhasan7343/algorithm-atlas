"""Compile and execute the merge sort API and CLI in both C++ standards."""

from pathlib import Path
import subprocess

import pytest


SOURCE = Path(__file__).parents[1] / "cpp/solution.cpp"


@pytest.mark.cpp
def test_cpp_api(cpp_compile, tmp_path):
    driver = tmp_path / "merge_sort_driver.cpp"
    driver.write_text(
        '#define ALGORITHM_ATLAS_NO_MAIN\n'
        f'#include "{SOURCE.as_posix()}"\n'
        r'''
#include <algorithm>
#include <cassert>
#include <limits>
#include <random>

struct Record {
    int key;
    int tag;
    Record(int key_value, int tag_value) : key(key_value), tag(tag_value) {}
    bool operator<(const Record& other) const { return key < other.key; }
};

int main() {
    using algorithm_atlas::merge_sort;
    const std::vector<std::vector<long long>> cases = {
        {}, {7}, {2, 1}, {1, 2}, {2, 2}, {5, 1, 4, 2, 8},
        {3, -1, 0, -1, 3}, {8, 7, 6, 5, 4, 3, 2, 1},
        std::vector<long long>(33, 4),
        {0, std::numeric_limits<long long>::min(),
         std::numeric_limits<long long>::max()}
    };
    for (const auto& values : cases) {
        const auto original = values;
        auto expected = values;
        std::stable_sort(expected.begin(), expected.end());
        assert(merge_sort(values) == expected);
        assert(values == original);
    }
    assert((merge_sort(std::vector<int>{5, 1, 4, 2, 8}) ==
            std::vector<int>{1, 2, 4, 5, 8}));
    assert((merge_sort(std::vector<std::string>{"pear", "apple", "banana"}) ==
            std::vector<std::string>{"apple", "banana", "pear"}));
    std::mt19937 generator(20261020);
    std::uniform_int_distribution<int> distribution(-1000, 1000);
    for (int length : {0, 1, 2, 3, 5, 7, 9, 31, 32, 33, 63, 65, 257}) {
        for (int iteration = 0; iteration < 15; ++iteration) {
            std::vector<int> values;
            for (int index = 0; index < length; ++index) {
                values.push_back(distribution(generator));
            }
            const auto original = values;
            auto expected = values;
            std::stable_sort(expected.begin(), expected.end());
            assert(merge_sort(values) == expected);
            assert(values == original);
        }
    }
    const std::vector<Record> records = {
        {2, 0}, {1, 1}, {2, 2}, {1, 3}, {2, 4}, {0, 5}, {1, 6}
    };
    const auto result = merge_sort(records);
    const std::vector<int> expected_keys = {0, 1, 1, 1, 2, 2, 2};
    const std::vector<int> expected_tags = {5, 1, 3, 6, 0, 2, 4};
    for (std::size_t index = 0; index < result.size(); ++index) {
        assert(result[index].key == expected_keys[index]);
        assert(result[index].tag == expected_tags[index]);
        assert(records[index].tag == static_cast<int>(index));
    }
    std::cout << "merge sort API passed\n";
}
''', encoding="utf-8",
    )
    executable = cpp_compile(driver)
    result = subprocess.run(
        [str(executable)], capture_output=True, text=True, check=True, timeout=10,
    )
    assert result.stdout == "merge sort API passed\n"


@pytest.mark.cpp
def test_cpp_cli(cpp_compile):
    executable = cpp_compile(SOURCE)
    for input_text, expected in [
        ("", "\n"),
        ("5 1 4 2 8\n", "1 2 4 5 8\n"),
        ("  +2\n-3 0001 -0\t", "-3 0 1 2\n"),
        ("9223372036854775807 -9223372036854775808 0",
         "-9223372036854775808 0 9223372036854775807\n"),
    ]:
        result = subprocess.run(
            [str(executable)], input=input_text, capture_output=True,
            text=True, check=True, timeout=10,
        )
        assert result.stdout == expected
        assert result.stderr == ""
    for invalid in [
        "1 two 3", "1.5", "0x10", "+", "-", "--2", "+-2", "1_000", "１２",
        "9223372036854775808", "-9223372036854775809",
    ]:
        result = subprocess.run(
            [str(executable)], input=invalid, capture_output=True,
            text=True, timeout=10,
        )
        assert result.returncode != 0
        assert result.stdout == ""
        assert "Invalid input" in result.stderr
