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

#include <cstdint>
#include <limits>

namespace algorithm_atlas {

static_assert(std::numeric_limits<long long>::digits == 63 &&
              std::numeric_limits<long long>::min() == (-9223372036854775807LL - 1),
              "Interpolation lesson requires full signed 64-bit long long");

namespace interpolation_search_detail {
// Compute floor(numerator * width / denominator) exactly without a wide
// multiplication. Preconditions: denominator > 0 and numerator <= denominator.
std::size_t scaled_offset(std::uint64_t numerator, std::size_t width,
                          std::uint64_t denominator) {
    if (numerator == 0 || width == 0) { return 0; }
    if (numerator == denominator) { return width; }
    std::size_t quotient = 0;
    std::uint64_t remainder = 0;
    for (unsigned bit = std::numeric_limits<std::size_t>::digits; bit > 0; --bit) {
        // Extend the processed width prefix by one bit. Quotient <= prefix,
        // hence doubling and the carry increments fit the final width.
        quotient += quotient;
        if (remainder >= denominator - remainder) {
            remainder -= denominator - remainder;
            ++quotient;
        } else {
            remainder += remainder;
        }
        if ((width >> (bit - 1)) & std::size_t{1}) {
            if (remainder >= denominator - numerator) {
                remainder -= denominator - numerator;
                ++quotient;
            } else {
                remainder += numerator;
            }
        }
    }
    return quotient;
}
}  // namespace interpolation_search_detail

std::optional<std::size_t> interpolation_search(
    const std::vector<long long>& values, long long target, bool validate = true) {
    if (validate) {
        for (std::size_t i = 1; i < values.size(); ++i) {
            if (values[i] < values[i - 1]) {
                throw std::invalid_argument("values must be nondecreasing");
            }
        }
    }
    std::size_t lower = 0;
    std::size_t upper = values.size();
    std::optional<std::size_t> found;
    while (lower < upper && values[lower] <= target && target <= values[upper - 1]) {
        if (values[lower] == values[upper - 1]) { return lower; }
        // Unsigned subtraction is the exact nonnegative distance, including
        // intervals crossing zero or spanning LLONG_MIN through LLONG_MAX.
        const auto numerator = static_cast<std::uint64_t>(target) -
                               static_cast<std::uint64_t>(values[lower]);
        const auto denominator = static_cast<std::uint64_t>(values[upper - 1]) -
                                 static_cast<std::uint64_t>(values[lower]);
        const auto offset = interpolation_search_detail::scaled_offset(
            numerator, upper - lower - 1, denominator);
        const auto position = lower + offset;
        if (values[position] < target) { lower = position + 1; }
        else {
            if (values[position] == target) { found = position; }
            upper = position;
        }
    }
    return found;
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
        const auto index = algorithm_atlas::interpolation_search(values, target);
        if (index) { std::cout << *index << '\n'; }
        else { std::cout << "-1\n"; }
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
#endif
