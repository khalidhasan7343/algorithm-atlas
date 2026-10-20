"""Compile and execute C++17/C++20 library and CLI behavior checks."""

import json
from pathlib import Path
import random
import subprocess

import pytest


SOURCE = Path(__file__).parents[1] / "cpp" / "solution.cpp"


@pytest.mark.cpp
def test_cpp_library_properties(cpp_compile, tmp_path) -> None:
    driver = tmp_path / "insertion_driver.cpp"
    driver.write_text(
        r'''
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
    int value;
    static int comparisons;
    bool operator<(const Counted& other) const {
        ++comparisons;
        return value < other.value;
    }
};
int Counted::comparisons = 0;

int main() {
    using algorithm_atlas::insertion_sort;
    std::vector<std::vector<long long>> cases = {
        {}, {7}, {4, 4, 4}, {1, 2, 3, 4}, {4, 3, 2, 1},
        {5, 2, 4, 2, 1}, {0, -9, 2, -9, -1},
        {std::numeric_limits<long long>::max(), 0,
         std::numeric_limits<long long>::min()}
    };
    std::mt19937 generator(7343);
    std::uniform_int_distribution<int> value(-100, 100);
    for (int length = 0; length <= 80; ++length) {
        for (int repeat = 0; repeat < 3; ++repeat) {
            std::vector<long long> values;
            for (int i = 0; i < length; ++i) { values.push_back(value(generator)); }
            cases.push_back(values);
        }
    }
    for (const auto& values : cases) {
        const auto before = values;
        auto expected = values;
        std::sort(expected.begin(), expected.end());
        auto result = insertion_sort(values);
        assert(result == expected);
        assert(values == before);
        if (!result.empty()) {
            result[0] = 123;
            assert(values == before);
        }
    }
    const std::vector<Record> records = {{2, 'a'}, {1, 'b'}, {2, 'c'}, {1, 'd'}};
    const auto stable = insertion_sort(records);
    assert(stable[0].tag == 'b' && stable[1].tag == 'd');
    assert(stable[2].tag == 'a' && stable[3].tag == 'c');
    assert(records[0].tag == 'a' && records[1].tag == 'b');
    const std::vector<std::string> words = {"pear", "apple", "plum"};
    const std::vector<std::string> expected_words = {"apple", "pear", "plum"};
    assert(insertion_sort(words) == expected_words);

    const int size = 40;
    std::vector<Counted> ascending;
    std::vector<Counted> descending;
    for (int i = 0; i < size; ++i) {
        ascending.push_back({i});
        descending.push_back({size - 1 - i});
    }
    insertion_sort(ascending);
    assert(Counted::comparisons == size - 1);
    Counted::comparisons = 0;
    insertion_sort(descending);
    assert(Counted::comparisons == size * (size - 1) / 2);
    Counted::comparisons = 0;
    std::swap(ascending[size - 1], ascending[size - 2]);
    insertion_sort(ascending);
    assert(Counted::comparisons == size);
}
'''.replace("SOURCE_PATH", json.dumps(str(SOURCE.resolve()))),
        encoding="utf-8",
    )
    executable = cpp_compile(driver, output_name="insertion_driver")
    subprocess.run(
        [str(executable)], capture_output=True, text=True, check=True, timeout=10
    )


@pytest.mark.cpp
def test_cpp_cli_valid_invalid_and_seeded_cases(cpp_compile) -> None:
    executable = cpp_compile(SOURCE, output_name="insertion_cli")
    known = [
        ("", "\n"),
        (" \n\t", "\n"),
        ("7", "7\n"),
        ("4 4 4", "4 4 4\n"),
        ("1 2 3 4", "1 2 3 4\n"),
        ("4 3 2 1", "1 2 3 4\n"),
        ("5 2 4 2 1", "1 2 2 4 5\n"),
        ("+03 -0 -7\t4\n", "-7 0 3 4\n"),
        (f"{2**63 - 1} {-2**63} 0", f"{-2**63} 0 {2**63 - 1}\n"),
    ]
    generator = random.Random(7343)
    for length in range(0, 61, 3):
        values = [generator.randint(-10**9, 10**9) for _ in range(length)]
        known.append(
            (" ".join(map(str, values)), " ".join(map(str, sorted(values))) + "\n")
        )
    for text, expected in known:
        result = subprocess.run(
            [str(executable)], input=text, capture_output=True,
            text=True, check=True, timeout=10,
        )
        assert result.stdout == expected
        assert result.stderr == ""
    invalid = [
        "1 two 3", "1.5", "0x10", "+", "-", "--2", "1_000", "12x", "١",
        str(2**63), str(-2**63 - 1),
    ]
    for text in invalid:
        result = subprocess.run(
            [str(executable)], input=text, capture_output=True, text=True, timeout=10,
        )
        assert result.returncode != 0
        assert result.stdout == ""
        assert "error:" in result.stderr
