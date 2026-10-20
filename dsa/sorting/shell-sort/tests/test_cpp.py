"""Execute reusable Shell Sort and standalone input contracts in C++17/20."""

from pathlib import Path
import subprocess

import pytest


SOURCE = Path(__file__).parents[1] / "cpp/solution.cpp"


@pytest.mark.cpp
def test_cpp_api(cpp_compile, tmp_path):
    driver = tmp_path / "shell_sort_driver.cpp"
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
    static std::size_t comparisons;
    Record(int key_value, int tag_value) : key(key_value), tag(tag_value) {}
    bool operator<(const Record& other) const {
        ++comparisons;
        return key < other.key;
    }
};
std::size_t Record::comparisons = 0;

int main() {
    using algorithm_atlas::shell_sort;
    const std::vector<std::vector<long long>> cases = {
        {}, {7}, {2, 1}, {1, 2}, {2, 2}, {4, 10, 3, 5, 1},
        {23, 12, 1, 8, 34, 54, 2, 3, 7, 4},
        {3, -1, 0, -1, 3}, {6, 5, 4, 3, 2, 1},
        std::vector<long long>(40, 4),
        {0, std::numeric_limits<long long>::min(),
         std::numeric_limits<long long>::max()}
    };
    for (const auto& values : cases) {
        const auto original = values;
        auto expected = values;
        std::sort(expected.begin(), expected.end());
        assert(shell_sort(values) == expected);
        assert(values == original);
    }
    assert((shell_sort(std::vector<int>{4, 10, 3, 5, 1}) ==
            std::vector<int>{1, 3, 4, 5, 10}));
    assert((shell_sort(std::vector<std::string>{"pear", "apple", "banana"}) ==
            std::vector<std::string>{"apple", "banana", "pear"}));
    std::mt19937 generator(20261020);
    std::uniform_int_distribution<int> distribution(-1000, 1000);
    for (int length : {0, 1, 2, 3, 4, 5, 6, 11, 12, 13, 14, 15, 38, 39, 40, 41,
                       42, 120, 121, 122, 123, 364}) {
        for (int iteration = 0; iteration < 15; ++iteration) {
            std::vector<int> values;
            for (int index = 0; index < length; ++index) {
                values.push_back(distribution(generator));
            }
            const auto original = values;
            auto expected = values;
            std::sort(expected.begin(), expected.end());
            assert(shell_sort(values) == expected);
            assert(values == original);
        }
    }
    for (int ordering = 0; ordering < 4; ++ordering) {
        std::vector<int> values;
        for (int index = 0; index < 4097; ++index) {
            values.push_back(ordering == 0 ? index : ordering == 1 ? 4096 - index :
                             ordering == 2 ? index % 13 : index % 40);
        }
        auto expected = values;
        std::sort(expected.begin(), expected.end());
        assert(shell_sort(values) == expected);
    }
    const std::vector<Record> records = {{2, 0}, {2, 1}, {0, 2}, {0, 3}, {0, 4}, {3, 5}};
    const auto result = shell_sort(records);
    const std::vector<int> expected_keys = {0, 0, 0, 2, 2, 3};
    const std::vector<int> expected_tags = {4, 2, 3, 1, 0, 5};
    for (std::size_t index = 0; index < records.size(); ++index) {
        assert(result[index].key == expected_keys[index]);
        assert(result[index].tag == expected_tags[index]);
        assert(records[index].tag == static_cast<int>(index));
    }
    for (int equal = 0; equal < 2; ++equal) {
        std::vector<Record> ordered;
        for (int index = 0; index < 100; ++index) {
            ordered.emplace_back(equal ? 7 : index, index);
        }
        Record::comparisons = 0;
        assert(shell_sort(ordered).size() == ordered.size());
        assert(Record::comparisons == (100 - 40) + (100 - 13) + (100 - 4) + (100 - 1));
    }
    std::cout << "shell sort API passed\n";
}
''', encoding="utf-8",
    )
    executable = cpp_compile(driver)
    result = subprocess.run(
        [str(executable)], capture_output=True, text=True, check=True, timeout=10,
    )
    assert result.stdout == "shell sort API passed\n"


@pytest.mark.cpp
def test_cpp_cli(cpp_compile):
    executable = cpp_compile(SOURCE)
    for input_text, expected in [
        ("", "\n"), ("23 12 1 8 34 54 2 3 7 4\n", "1 2 3 4 7 8 12 23 34 54\n"),
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
