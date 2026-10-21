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

namespace exponential_search_detail {
// Caller maintains 0 < bound < size; saturate before addition can overflow.
std::size_t expanded_bound(std::size_t bound, std::size_t size) {
    return bound >= size - bound ? size : bound + bound;
}
}  // namespace exponential_search_detail

template <typename T>
std::optional<std::size_t> exponential_search(
    const std::vector<T>& values, const T& target, bool validate = true) {
    if (validate) {
        for (std::size_t i = 1; i < values.size(); ++i) {
            if (values[i] < values[i - 1]) {
                throw std::invalid_argument("values must be nondecreasing");
            }
        }
    }
    const auto size = values.size();
    if (size == 0) { return std::nullopt; }
    if (!(values[0] < target)) {
        if (!(target < values[0])) { return 0; }
        return std::nullopt;
    }
    std::size_t lower = 1;
    std::size_t bound = 1;
    while (bound < size && values[bound] < target) {
        lower = bound + 1;
        bound = exponential_search_detail::expanded_bound(bound, size);
    }
    std::size_t upper = bound < size ? bound + 1 : size;
    while (lower < upper) {
        const auto middle = lower + (upper - lower) / 2;
        if (values[middle] < target) { lower = middle + 1; }
        else { upper = middle; }
    }
    if (lower < size && !(target < values[lower])) { return lower; }
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
        const auto index = algorithm_atlas::exponential_search(values, target);
        if (index) { std::cout << *index << '\n'; }
        else { std::cout << "-1\n"; }
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
#endif
