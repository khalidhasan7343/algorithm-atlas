// Stable early-exit bubble sort. Standalone CLI: signed decimal long long input.
#include <cstddef>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

namespace algorithm_atlas {

template <typename T>
std::vector<T> bubble_sort(const std::vector<T>& values) {
    std::vector<T> result(values);
    for (std::size_t end = result.size(); end > 1; --end) {
        bool swapped = false;
        for (std::size_t index = 0; index + 1 < end; ++index) {
            if (result[index + 1] < result[index]) {
                std::swap(result[index], result[index + 1]);
                swapped = true;
            }
        }
        if (!swapped) {
            break;
        }
    }
    return result;
}

}  // namespace algorithm_atlas

#ifndef ALGORITHM_ATLAS_NO_MAIN
namespace {
bool parse_integer(const std::string& token, long long& value) {
    std::size_t first_digit = 0;
    if (!token.empty() && (token[0] == '+' || token[0] == '-')) {
        first_digit = 1;
    }
    if (first_digit == token.size()) {
        return false;
    }
    for (std::size_t i = first_digit; i < token.size(); ++i) {
        if (token[i] < '0' || token[i] > '9') {
            return false;
        }
    }
    try {
        std::size_t parsed_size = 0;
        value = std::stoll(token, &parsed_size, 10);
        return parsed_size == token.size();
    } catch (...) {
        return false;
    }
}
}  // namespace

int main() {
    std::vector<long long> values;
    std::string token;
    while (std::cin >> token) {
        long long value = 0;
        if (!parse_integer(token, value)) {
            std::cerr << "error: expected signed decimal integers in the long long range\n";
            return 1;
        }
        values.push_back(value);
    }
    if (std::cin.bad()) {
        std::cerr << "error: could not read input\n";
        return 1;
    }
    const auto result = algorithm_atlas::bubble_sort(values);
    for (std::size_t i = 0; i < result.size(); ++i) {
        if (i != 0) {
            std::cout << ' ';
        }
        std::cout << result[i];
    }
    std::cout << '\n';
}
#endif
