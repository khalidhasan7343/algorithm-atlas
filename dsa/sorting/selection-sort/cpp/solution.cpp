// Swap-based selection sort. Standalone CLI: signed decimal long long input.
#include <charconv>
#include <cstddef>
#include <iostream>
#include <string>
#include <system_error>
#include <utility>
#include <vector>

namespace algorithm_atlas {

template <typename T>
std::vector<T> selection_sort(const std::vector<T>& values) {
    std::vector<T> result(values);
    for (std::size_t start = 0; start + 1 < result.size(); ++start) {
        std::size_t minimum = start;
        for (std::size_t index = start + 1; index < result.size(); ++index) {
            if (result[index] < result[minimum]) {
                minimum = index;
            }
        }
        if (minimum != start) {
            std::swap(result[start], result[minimum]);
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
    const char* begin = token.data() + (token[0] == '+' ? 1 : 0);
    const char* end = token.data() + token.size();
    const auto parsed = std::from_chars(begin, end, value);
    return parsed.ec == std::errc{} && parsed.ptr == end;
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
    const auto result = algorithm_atlas::selection_sort(values);
    for (std::size_t i = 0; i < result.size(); ++i) {
        if (i != 0) {
            std::cout << ' ';
        }
        std::cout << result[i];
    }
    std::cout << '\n';
}
#endif
