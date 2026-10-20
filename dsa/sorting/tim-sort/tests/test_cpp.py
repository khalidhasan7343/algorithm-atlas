"""Compile and execute classic Tim Sort under C++17 and C++20."""

import json
from pathlib import Path
import random
import subprocess

import pytest


SOURCE = Path(__file__).parents[1] / "cpp" / "solution.cpp"


@pytest.mark.cpp
def test_cpp_library_stability_stack_and_galloping(cpp_compile, tmp_path) -> None:
    driver = tmp_path / "tim_driver.cpp"
    driver.write_text(
        r'''
#define ALGORITHM_ATLAS_NO_MAIN
#include SOURCE_PATH
#include <cassert>
#include <limits>
#include <random>

struct Record {
    int key;
    int tag;
    Record() = delete;
    Record(int key_value, int tag_value) : key(key_value), tag(tag_value) {}
    bool operator<(const Record& other) const { return key < other.key; }
};
struct Counted {
    int value;
    static int comparisons;
    explicit Counted(int key) : value(key) {}
    bool operator<(const Counted& other) const {
        ++comparisons;
        return value < other.value;
    }
};
int Counted::comparisons = 0;

void check_records(const std::vector<Record>& records) {
    auto expected = records;
    std::stable_sort(expected.begin(), expected.end());
    const auto result = algorithm_atlas::tim_sort(records);
    assert(result.size() == expected.size());
    for (std::size_t i = 0; i < result.size(); ++i) {
        assert(result[i].key == expected[i].key && result[i].tag == expected[i].tag);
        assert(records[i].tag == static_cast<int>(i));
    }
}

void verify_stack(const std::vector<algorithm_atlas::tim_sort_detail::Run>& runs) {
    for (std::size_t i = 1; i < runs.size(); ++i) {
        assert(runs[i - 1].length > runs[i].length);
    }
    for (std::size_t i = 2; i < runs.size(); ++i) {
        assert(runs[i - 2].length > runs[i - 1].length + runs[i].length);
    }
}

int main() {
    using algorithm_atlas::tim_sort;
    namespace detail = algorithm_atlas::tim_sort_detail;
    const std::vector<std::pair<std::size_t, std::size_t>> minruns = {
        {0, 0}, {1, 1}, {31, 31}, {32, 32}, {63, 63}, {64, 32},
        {65, 33}, {127, 64}, {128, 32}, {129, 33}, {2112, 33}
    };
    for (const auto& example : minruns) {
        assert(detail::min_run_length(example.first) == example.second);
    }
    std::vector<std::vector<long long>> cases = {
        {}, {7}, {4, 4, 4}, {1, 2, 3, 4}, {4, 3, 2, 1},
        {5, 2, 4, 2, 1}, {0, -9, 2, -9, -1},
        {std::numeric_limits<long long>::max(), 0,
         std::numeric_limits<long long>::min()}
    };
    std::mt19937 generator(7343);
    std::uniform_int_distribution<int> value(-100, 100);
    for (int length = 0; length <= 140; ++length) {
        std::vector<long long> values;
        for (int i = 0; i < length; ++i) { values.push_back(value(generator)); }
        cases.push_back(values);
    }
    for (const int length : {255, 256, 257, 511, 1001, 4097, 20003, 100003}) {
        std::vector<long long> values;
        for (int i = 0; i < length; ++i) { values.push_back(value(generator)); }
        cases.push_back(values);
    }
    for (const auto& values : cases) {
        const auto before = values;
        auto expected = values;
        std::sort(expected.begin(), expected.end());
        auto result = tim_sort(values);
        assert(result == expected && values == before);
        if (!result.empty()) { result[0] = 123; assert(values == before); }
    }
    const std::vector<std::string> words = {"pear", "apple", "plum"};
    assert((tim_sort(words) == std::vector<std::string>{"apple", "pear", "plum"}));

    std::vector<Record> random_records;
    for (int i = 0; i < 4097; ++i) { random_records.emplace_back(value(generator), i); }
    check_records(random_records);
    std::vector<Record> plateaus;
    for (int i = 0; i < 400; ++i) { plateaus.emplace_back(99 - i / 4, i); }
    check_records(plateaus);
    for (const bool right_first : {false, true}) {
        std::vector<Record> records;
        const int first = right_first ? 500 : 0;
        const int second = right_first ? 0 : 500;
        for (const int base : {first, second}) {
            for (int key = base; key < base + 1000; ++key) {
                for (int repeat = 0; repeat < 3; ++repeat) {
                    records.emplace_back(key, static_cast<int>(records.size()));
                }
            }
        }
        check_records(records);
    }

    // Gallop boundary oracles include empty suffixes, plateaus, and exhaustion.
    for (int length = 0; length < 66; ++length) {
        std::vector<long long> values;
        for (int i = 0; i < length; ++i) { values.push_back(value(generator) % 6); }
        std::sort(values.begin(), values.end());
        for (std::size_t start = 0; start <= values.size(); ++start) {
            for (long long pivot = -7; pivot <= 7; ++pivot) {
                const auto lower = static_cast<std::size_t>(std::lower_bound(
                    values.begin() + start, values.end(), pivot) - values.begin());
                const auto upper = static_cast<std::size_t>(std::upper_bound(
                    values.begin() + start, values.end(), pivot) - values.begin());
                assert(detail::gallop_bound(
                    values, start, values.size(), pivot, false) == lower);
                assert(detail::gallop_bound(
                    values, start, values.size(), pivot, true) == upper);
            }
        }
    }
    std::vector<Record> equal_records;
    for (int i = 0; i < 20; ++i) { equal_records.emplace_back(2, i); }
    assert(detail::gallop_bound(equal_records, 3, 20, Record(2, -1), false) == 3);
    assert(detail::gallop_bound(equal_records, 3, 20, Record(2, -1), true) == 20);

    // This stack's top triple is valid but its preceding triple is violated.
    const std::vector<detail::Run> regression = {
        {0, 120}, {120, 80}, {200, 45}, {245, 30}
    };
    assert(detail::collapse_choice(regression) == 2);
    std::vector<std::vector<std::size_t>> patterns = {
        {480, 320, 100, 80, 120}, std::vector<std::size_t>(257, 64)
    };
    std::vector<std::size_t> irregular;
    for (int i = 0; i < 200; ++i) { irregular.push_back(64 + generator() % 129); }
    patterns.push_back(irregular);
    for (const auto& lengths : patterns) {
        std::size_t total = 0;
        for (const auto length : lengths) { total += length; }
        std::size_t endpoint = total;
        std::vector<long long> values;
        std::vector<detail::Run> stack;
        std::size_t base = 0;
        for (const auto length : lengths) {
            for (std::size_t i = endpoint - length; i < endpoint; ++i) {
                values.push_back(static_cast<long long>(i));
            }
            endpoint -= length;
            stack.push_back({base, length});
            base += length;
            while (const auto choice = detail::collapse_choice(stack)) {
                stack[*choice].length += stack[*choice + 1].length;
                stack.erase(stack.begin() + *choice + 1);
            }
            verify_stack(stack);
        }
        const auto result = tim_sort(values);
        for (std::size_t i = 0; i < total; ++i) {
            assert(result[i] == static_cast<long long>(i));
        }
    }

    for (const int order : {0, 1, 2}) {
        std::vector<Counted> values;
        for (int i = 0; i < 4096; ++i) {
            values.emplace_back(order == 0 ? i : (order == 1 ? 4095 - i : 7));
        }
        Counted::comparisons = 0;
        const auto result = tim_sort(values);
        assert(Counted::comparisons == 4095);
        for (int i = 0; i < 4096; ++i) {
            assert(result[i].value == (order == 2 ? 7 : i));
        }
    }
    std::vector<Counted> winning_runs;
    for (int i = 2000; i < 4000; ++i) { winning_runs.emplace_back(i); }
    for (int i = 0; i < 2000; ++i) { winning_runs.emplace_back(i); }
    Counted::comparisons = 0;
    const auto galloped = tim_sort(winning_runs);
    assert(Counted::comparisons < 4140);
    for (int i = 0; i < 4000; ++i) { assert(galloped[i].value == i); }
}
'''.replace("SOURCE_PATH", json.dumps(str(SOURCE.resolve()))),
        encoding="utf-8",
    )
    executable = cpp_compile(driver, output_name="tim_driver")
    subprocess.run(
        [str(executable)], capture_output=True, text=True, check=True, timeout=20
    )


@pytest.mark.cpp
def test_cpp_cli(cpp_compile) -> None:
    executable = cpp_compile(SOURCE, output_name="tim_cli")
    valid = [
        ("", "\n"), (" \n\t", "\n"), ("7", "7\n"),
        ("4 4 4", "4 4 4\n"), ("5 2 4 2 1", "1 2 2 4 5\n"),
        ("+03 -0 -7\t4", "-7 0 3 4\n"),
        (f"{2**63 - 1} {-2**63} 0", f"{-2**63} 0 {2**63 - 1}\n"),
    ]
    generator = random.Random(7343)
    for length in [31, 32, 63, 64, 65, 127, 128, 129, 511, 1001, 4097]:
        values = [generator.randint(-10**9, 10**9) for _ in range(length)]
        valid.append(
            (" ".join(map(str, values)), " ".join(map(str, sorted(values))) + "\n")
        )
    for text, expected in valid:
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
            [str(executable)], input=text, capture_output=True, text=True, timeout=10
        )
        assert result.returncode != 0
        assert result.stdout == ""
        assert "error:" in result.stderr
