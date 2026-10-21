// First-match lookup. Define ALGORITHM_ATLAS_NO_MAIN for library use.
#include <algorithm>
#include <charconv>
#include <cmath>
#include <cstddef>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <system_error>
#include <vector>

namespace algorithm_atlas {

template <typename T>
std::optional<std::size_t> linear_search(const std::vector<T>& values,
                                       const T& target) {
    for (std::size_t index = 0; index < values.size(); ++index) {
        if (values[index] == target) { return index; }
    }
    return std::nullopt;
}

}  // namespace algorithm_atlas

#ifndef ALGORITHM_ATLAS_NO_MAIN
namespace {
bool parse_integer(const std::string& token, long long& value) {
    const std::size_t first_digit =
        (!token.empty() && (token[0] == '+' || token[0] == '-')) ? 1 : 0;
    if (first_digit == token.size()) { return false; }
    for (std::size_t i = first_digit; i < token.size(); ++i) {
        if (token[i] < '0' || token[i] > '9') { return false; }
    }
    const char* begin = token.data() + (token[0] == '+' ? 1 : 0);
    const char* end = token.data() + token.size();
    const auto result = std::from_chars(begin, end, value, 10);
    return result.ec == std::errc{} && result.ptr == end;
}
}  // namespace

int main() {
    std::vector<long long> numbers;
    std::string token;
    while (std::cin >> token) {
        long long value = 0;
        if (!parse_integer(token, value)) {
            std::cerr << "error: expected target and decimal long long values\n";
            return 1;
        }
        numbers.push_back(value);
    }
    if (!std::cin.eof() || numbers.empty()) {
        std::cerr << "error: target is required and input must be readable\n";
        return 1;
    }
    const auto target = numbers.front();
    const std::vector<long long> values(numbers.begin() + 1, numbers.end());
    try {
        const auto index = algorithm_atlas::linear_search(values, target);
        if (index) { std::cout << *index << '\n'; }
        else { std::cout << "-1\n"; }
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
#endif
