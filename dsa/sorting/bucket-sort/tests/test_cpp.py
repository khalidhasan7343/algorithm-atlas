"""Execute C++17/C++20 bucket sorting, boundaries, exceptions, and CLIs."""

import math
from pathlib import Path
import subprocess

import pytest

SOURCE = Path(__file__).parents[1] / "cpp" / "solution.cpp"
DRIVER = r"""#include <algorithm>
#include <random>
#define ALGORITHM_ATLAS_NO_MAIN
#include "SOURCE_PATH"

int main() {
    const std::vector<std::vector<double>> cases = {
        {}, {0.5}, {0}, {1}, {0, 1}, {1, 0},
        {0.2, 0.1, 0.7, 0.2, 0, 1}, {0, 0, 0}, {1, 1, 1}, {0.5, 0.5, 0.5},
        {0, 0.25, 0.5, 0.75, 1}, {1, 0.75, 0.5, 0.25, 0},
        {std::nextafter(1.0, 0.0), 1, std::nextafter(0.0, 1.0), 0},
        {0.25, std::nextafter(0.25, 0.0), std::nextafter(0.25, 1.0), 0}
    };
    for (const auto& values : cases) {
        const auto original = values;
        auto expected = values;
        std::stable_sort(expected.begin(), expected.end());
        for (const std::size_t count : {0, 1, 3, 20}) {
            if (algorithm_atlas::bucket_sort(values, count) != expected || values != original) return 1;
        }
    }
    std::mt19937_64 rng(7343);
    std::uniform_real_distribution<double> uniform(0, 1);
    for (int trial = 0; trial < 100; ++trial) {
        std::vector<double> values(rng() % 100);
        for (auto& value : values) value = uniform(rng);
        const auto original = values;
        auto expected = values;
        std::sort(expected.begin(), expected.end());
        for (const std::size_t count : {0, 1, 7}) {
            if (algorithm_atlas::bucket_sort(values, count) != expected || values != original) return 2;
        }
    }
    std::vector<double> clustered;
    for (int index = 499; index >= 0; --index) clustered.push_back(0.5 + index * 1e-9);
    auto expected = clustered;
    std::sort(expected.begin(), expected.end());
    if (algorithm_atlas::bucket_sort(clustered) != expected) return 3;

    const std::vector<double> zeros = {0.5, 0.0, -0.0, 0.5, 0.0, -0.0, 1};
    const auto result = algorithm_atlas::bucket_sort(zeros, 2);
    if (std::signbit(result[0]) || !std::signbit(result[1]) ||
        std::signbit(result[2]) || !std::signbit(result[3])) return 4;
    if (std::signbit(zeros[1]) || !std::signbit(zeros[2])) return 5;

    const std::vector<double> invalid = {
        -0.1, 1.1, std::nextafter(1.0, 2.0), std::nextafter(0.0, -1.0),
        std::numeric_limits<double>::quiet_NaN(),
        std::numeric_limits<double>::infinity(), -std::numeric_limits<double>::infinity()
    };
    for (const double value : invalid) {
        bool threw = false;
        try { algorithm_atlas::bucket_sort({value}); }
        catch (const std::invalid_argument&) { threw = true; }
        if (!threw) return 6;
    }
    bool rejected_allocation = false;
    try { algorithm_atlas::bucket_sort({0.25, 0.75}, std::numeric_limits<std::size_t>::max()); }
    catch (const std::length_error&) { rejected_allocation = true; }
    catch (const std::bad_alloc&) { rejected_allocation = true; }
    if (!rejected_allocation) return 7;
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
        ("1 .5 0 2.5e-1 +7.5E-1", "0 0.25 0.5 0.75 1\n"),
        ("-0 +0.0 1.", "-0 0 1\n"),
    ]
    for text, expected in valid:
        result = subprocess.run([str(executable)], input=text, capture_output=True,
                                text=True, check=True, timeout=10)
        assert result.stdout == expected
        assert result.stderr == ""
    values = [math.nextafter(1.0, 0.0), 1.0, math.nextafter(0.0, 1.0), 0.0]
    result = subprocess.run([str(executable)], input=" ".join(map(repr, values)),
                            capture_output=True, text=True, check=True, timeout=10)
    assert [float(token) for token in result.stdout.split()] == sorted(values)
    invalid = ["abc", "1x", "--1", "+-1", "+", "-", ".", "1e", "1e+", "1_0",
               "0x1", "１２", "nan", "inf", "-inf", "-0.1", "1.1", "1e999"]
    for token in invalid:
        result = subprocess.run([str(executable)], input="0.5 " + token,
                                capture_output=True, text=True, timeout=10)
        assert result.returncode != 0
        assert result.stdout == ""
        assert "error:" in result.stderr
